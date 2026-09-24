import zipfile
from typing import List, Dict
from sqlalchemy.sql import text
import pandas as pd
import dagster as dg
from .partitions import NEMSIS_OPIOID_V1_PARTITIONS, NEMSIS_OPIOID_V1_BINS_PARTITIONS
from datastore.resources.postgres_resource import PostgresConnectionResource
from datastore.models.data_source import ZippedDataDelivery, ZippedBinDataDelivery
from datastore.utils.serialize import (
    partition_key_to_dict, extract_sas_file_from_zipfile, df_to_metadata,
    first_day_month, last_day_month
)
from datastore.pipelines.base.bins.assets import insert_into_bins_factory
from datastore.ops.moving_avg_ops import generate_fill_nemsis_rates_sql
from datetime import datetime
from datastore.ops.moving_avg_ops import (
    generate_fill_nemsis_rates_sql,
    generate_moving_avgs_sql,
    generate_moving_avgs_columns_sql,
    generate_moving_avgs_rank_sql
)
from datastore.pipelines.tables.assets import create_opioid_v1_table_asset
from datastore.pipelines.opioid.base.assets import valid_opioid_mids_asset, ValidMorpheusIDs
from db.datasets.opioid.opioid_tables import NEMSISOpioid


@dg.asset(
    partitions_def=NEMSIS_OPIOID_V1_PARTITIONS,
    group_name="Opioid",
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_opioid_v1_data_delivery_asset(context: dg.AssetExecutionContext) -> dg.Output[ZippedDataDelivery]:
    """ Generate Data Delivery Object for NEMSIS v2 Monthly delivery. """
    partition_key = context.partition_key
    context.log.info(partition_key)

    data_delivery = ZippedDataDelivery(**partition_key_to_dict(partition_key))
    context.log.info(data_delivery)

    return dg.Output(
        data_delivery,
        metadata={'preview': dg.MetadataValue.md(str(data_delivery))}
    )


@dg.asset(
    partitions_def=NEMSIS_OPIOID_V1_PARTITIONS,
    ins={"data_delivery": dg.AssetIn(nemsis_opioid_v1_data_delivery_asset.key)},
    group_name="Opioid",
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_opioid_v1_raw_df_asset(
    context: dg.AssetExecutionContext,
    data_delivery: ZippedDataDelivery
) -> dg.Output[pd.DataFrame]:
    """ 

    Parameters
    ----------
    context : dg.AssetExecutionContext
    nemsis_v2_data_delivery_asset : ZippedDataDelivery

    Returns
    -------
    dg.Output[pd.DataFrame]
    """
    
    partition_key = context.partition_key
    df = extract_sas_file_from_zipfile(data_delivery.get_full_path(), data_delivery.get_filename(), encoding='latin1')

    # Generate Data Lineage
    df['row_num'] = df.index
    df['source_file'] = data_delivery.get_filename()
    df['data_release'] = data_delivery.data_provider
    df['data_provider'] = data_delivery.data_provider

    return dg.Output(df, metadata=df_to_metadata(df))

@dg.asset(
    partitions_def=NEMSIS_OPIOID_V1_PARTITIONS,
    ins={
        "raw_df": dg.AssetIn(nemsis_opioid_v1_raw_df_asset.key),
        "ValidMIDS": dg.AssetIn(valid_opioid_mids_asset.key)
    },
    group_name='Opioid',
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_opioid_v1_clean_df_asset(
    context: dg.AssetExecutionContext,
    raw_df: pd.DataFrame,
    ValidMIDS: ValidMorpheusIDs
) -> dg.Output[pd.DataFrame]:
    """ Clean DF Asset

    Parameters
    ----------
    context : dg.AssetExecutionContext
    raw_df : pd.DataFrame

    Returns
    -------
    dg.Output[pd.DataFrame]
    """

    partition_key = context.partition_key


    df_wide = pd.pivot(
        raw_df,
        index=['CountyName', 'CountyFIPS', 'population', 'Yearmonth', 'source_file', 'data_release', 'data_provider'],
        columns=['MeasureName'],
        values=['Rank', 'RankValue', 'row_num'],
    )
    df_wide.columns = [f'{pair[1]} ({pair[0]})' for pair in df_wide.columns]
    df_wide.reset_index(inplace=True)
    df_wide['row_num'] = df_wide['Opioid Rate (row_num)']
    

    # Generate start and end dates
    df_wide['start_date'] = df_wide['Yearmonth'].apply(
        lambda row: first_day_month(int(row[:4]), int(row[4:]))
    )
    df_wide['end_date'] = df_wide['Yearmonth'].apply(
        lambda row: last_day_month(int(row[:4]), int(row[4:]))
    )
    
    # Generate MID
    df_wide['mid'] = df_wide["CountyFIPS"].apply(lambda fips: f"COUNTY {fips}")
    df_wide['type'] = 'COUNTY'
    
    # Other
    df_wide['outcome'] = 'opioid'
    df_wide['measure'] = 'opioid_rate_rank'
    df_wide['county_name'] = df_wide['CountyFIPS']
    df_wide['county_fips'] = df_wide['CountyFIPS']

    rank_col_source = 'Opioid Rate (Rank)'
    rank_value_col_source = 'Opioid Rate (RankValue)'

    context.log.info(df_wide.columns)

    df_wide['opioid_rate_rank'] = df_wide[rank_col_source]
    df_wide['opioid_rate_rank_value'] = df_wide[rank_value_col_source]
    df_wide['is_valid_county'] = df_wide['mid'].apply(lambda mid: ValidMIDS.is_valid(mid, 'COUNTY'))
    context.log.info(df_wide['is_valid_county'].value_counts())
    context.log.info(df_wide.shape)
    df_wide = df_wide.loc[df_wide['is_valid_county']].copy()
    context.log.info(df_wide.shape)


    # Filter Columns
    columns = [
        'start_date',
        'end_date',
        'county_name',
        'county_fips',
        'opioid_rate_rank',
        'opioid_rate_rank_value',
        'mid',
        'type',
        'source_file',
        'row_num',
        'data_release',
        'data_provider'
    ]
    clean_df = df_wide[columns].copy()
    
    return dg.Output(clean_df, metadata=df_to_metadata(clean_df))

#######################################################################################

@dg.asset(
    partitions_def=NEMSIS_OPIOID_V1_BINS_PARTITIONS,
    group_name="Opioid",
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_opioid_v1_bins_data_delivery_asset(context: dg.AssetExecutionContext) -> dg.Output[ZippedBinDataDelivery]:
    """ Generate Data Delivery Object for NEMSIS v2 Monthly delivery. """
    partition_key = context.partition_key
    context.log.info(partition_key)

    data_delivery = ZippedBinDataDelivery(**partition_key_to_dict(partition_key))
    context.log.info(data_delivery)

    return dg.Output(
        data_delivery,
        metadata={'preview': dg.MetadataValue.md(str(data_delivery))}
    )


@dg.asset(
    partitions_def=NEMSIS_OPIOID_V1_BINS_PARTITIONS,
    ins={"data_delivery": dg.AssetIn(nemsis_opioid_v1_bins_data_delivery_asset.key)},
    group_name="Opioid",
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_opioid_v1_bins_clean_df_asset(
    context: dg.AssetExecutionContext,
    data_delivery: ZippedBinDataDelivery
) -> dg.Output[pd.DataFrame]:
    """ 

    Parameters
    ----------
    context : dg.AssetExecutionContext
    nemsis_v2_data_delivery_asset : ZippedBinDataDelivery

    Returns
    -------
    dg.Output[pd.DataFrame]
    """
    
    partition_key = context.partition_key
    

    metrics_df = extract_sas_file_from_zipfile(
        data_delivery.get_full_path(),
        data_delivery.metrics_file_name,
        encoding='latin1'
    )
    unique_yearmonths = sorted(metrics_df.Yearmonth.unique())


    # Constants to convert NEMSIS language into Outcome Toolkit terms
    BIN_STATS = ['N', 'MIN', 'MEAN', 'MEDIAN', 'MAX']
    BIN_STATS_MEASURE_CONVERTER = {
        'alcohol': {
            'AllAlcoholSchematic': 'alcohol_rate',
        },
        'opioid': {
            'AllOpioidSchematic': 'opioid_rate',
        },
    }
    RANK_CONVERTER = {
        0: 'Zero or No/Limited Data Available',
        1: 'Significantly Lower Than National Average',
        2: 'Much Lower than National Average',
        3: 'Lower than National Average',
        4: 'Slightly Lower than National Average',
        5: 'Slightly Higher than National Average',
        6: 'Higher than National Average',
        7: 'Much Higher than National Average',
        8: 'Significantly Higher than National Average',
        9: 'High Outlier',
    }

    archive = zipfile.ZipFile(data_delivery.get_full_path(), 'r')
    with archive.open(data_delivery.get_filename()) as f:
        df = pd.read_excel(f, sheet_name='AllOpioidSchematic')
        df['ROW_NUM'] = (df.index + 1).astype(str)
        
    
    results_dfs = []
    
    for yearmonth in unique_yearmonths:

        start_date = first_day_month(int(yearmonth[:4]), int(yearmonth[4:]))
        end_date = last_day_month(int(yearmonth[:4]), int(yearmonth[4:]))

        df_wide = pd.pivot(
            df.loc[df._TYPE_.isin(BIN_STATS)],
            index=['MeasureRank'],
            columns=['_TYPE_'],
            values=['_VALUE_', 'ROW_NUM'],
        )

        df_wide.columns = [f'{pair[1]} ({pair[0]})' for pair in df_wide.columns]
        df_wide.reset_index(inplace=True)

        df_wide['start_date'] = start_date
        df_wide['end_date'] = end_date

        df_wide_sorted = df_wide.sort_values(by=['start_date', 'end_date', 'MeasureRank'])

        df_wide_sorted['next_min'] = df_wide_sorted.groupby(['start_date', 'end_date'])['MIN (_VALUE_)'].shift(-1)
        df_wide_sorted['next_max'] = df_wide_sorted.groupby(['start_date', 'end_date'])['MAX (_VALUE_)'].shift(-1)

        df_wide_sorted['next_min'] = df_wide_sorted['next_min'].fillna(df_wide_sorted['MAX (_VALUE_)'])
            
        # Format some columns
        df_wide_sorted['outcome'] = 'opioid'
        df_wide_sorted['measure'] = 'opioid_rate'
        df_wide_sorted['rankValue'] = df_wide_sorted['MeasureRank'].apply(lambda x: RANK_CONVERTER[x])
        df_wide_sorted['type'] = 'COUNTY'
        df_wide_sorted['source_file'] = data_delivery.get_filename()
        df_wide_sorted['row_num'] = df_wide_sorted.apply(
            lambda row: ','.join(
                map(str, [row[col] for col in df_wide_sorted.columns if ('ROW_NUM' in col)])
            ),
            axis=1
        )
        df_wide_sorted['data_release'] = data_delivery.data_provider
        df_wide_sorted['data_provider'] = data_delivery.data_provider
        df_wide_sorted['midpoint'] = (df_wide_sorted['MIN (_VALUE_)'] + df_wide_sorted['MAX (_VALUE_)']) / 2.0

        # Clean up columns and filter:
        df_wide_sorted.rename(columns={
            'MeasureRank': 'rank',
            'N (_VALUE_)': 'n',
            'MIN (_VALUE_)': 'min',
            'MEDIAN (_VALUE_)': 'median',
            'MEAN (_VALUE_)': 'mean',
            'next_min': 'max',
        }, inplace=True)

        keep_cols = [
            'start_date',
            'end_date',
            'outcome',
            'measure',
            'rank',
            'rankValue',
            'n',
            'min',
            'median',
            'mean',
            'midpoint',
            'max',
            'type',
            'source_file',
            'data_release',
            'data_provider',
            'row_num'
        ]
        
        result_df_monthly = df_wide_sorted[keep_cols].copy()
        results_dfs.append(result_df_monthly.copy())

    result_df = pd.concat(results_dfs)

    return dg.Output(result_df, metadata=df_to_metadata(result_df))


@dg.asset(
    ins={
        "clean_dfs": dg.AssetIn(nemsis_opioid_v1_clean_df_asset.key, partition_mapping=dg.AllPartitionMapping()),
    },
    group_name='Opioid',
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_opioid_table(
    db: PostgresConnectionResource,
    clean_dfs: Dict[str, pd.DataFrame]
) -> None:
    """
    This function creates and populates the NEMSISAlcoholTable in the database.

    Parameters:
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.
    clean_dfs: List[pd.DataFrame]

    """

    df = pd.concat([*clean_dfs.values()])

    NEMSISOpioid.__table__.drop(bind=db.engine, checkfirst=True)
    NEMSISOpioid.__table__.create(bind=db.engine, checkfirst=True)

    records = []

    for _, row in df.iterrows():
        records.append(NEMSISOpioid(**row.to_dict()))

    with db.session() as session, session.begin():
        for record in records:
            session.merge(record)
        session.commit()



nemsis_opioid_v1_bins_table_asset = insert_into_bins_factory(
    input_asset=nemsis_opioid_v1_bins_clean_df_asset,
    asset_key="nemsis_opioid_v1_bins_table_asset",
    asset_group="Opioid",
    partitioned=True
)

@dg.asset(
    deps=[nemsis_opioid_table],
    group_name='Opioid',
    automation_condition=dg.AutomationCondition.eager()
)
def fill_nemsis_opioid_v1(
    db: PostgresConnectionResource,
) -> None:
    """
    This function Fills NEMSIS null rates.

    Parameters:
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.

    """
    
    sql_query = generate_fill_nemsis_rates_sql(
        target_table=NEMSISOpioid.__tablename__,
        rate_col='opioid_rate',
        rep_value='midpoint',
        rank_col='opioid_rate_rank',
        rank_value_col='opioid_rate_rank_value',
        measure='opioid_rate'
    )
    
    with db.session() as session, session.begin():
        session.execute(text(sql_query))
        session.commit()
    
    return None

#######################################################################################

@dg.asset(
    deps=[fill_nemsis_opioid_v1],
    group_name='Opioid',
    automation_condition=dg.AutomationCondition.eager()
)
def load_moving_avgs_nemsis_opioid_v1(
    db: PostgresConnectionResource,
) -> None:
    """
    This function Fills NEMSIS null rates.

    Parameters:
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.

    """
    
    sql_query = generate_moving_avgs_sql(
        target_table=NEMSISOpioid.__tablename__,
        metric_col='opioid_rate',
        target_col='opioid_rate_6mo',
        num_months=6
    )
    
    with db.session() as session, session.begin():
        session.execute(text(sql_query))
        session.commit()
    
    return None
