import datetime
from typing import List, Dict, Any
from sqlalchemy.sql import text
import pandas as pd
import pandas.api.types as ptypes
import dagster as dg
from .partitions import (
    NEMSIS_ALCOHOL_V2_PARTITIONS,
    NEMSIS_ALCOHOL_V2_BINS_PARTITIONS,
    NEMSIS_ALCOHOL_V2_TRENDLINES_PARTITIONS
)
from ..nemsis_alcohol_monthly_v1.assets import nemsis_alcohol_v1_clean_df_asset
from datastore.resources.postgres_resource import PostgresConnectionResource
from datastore.models.data_source import ZippedDataDelivery
from datastore.utils.serialize import (
    partition_key_to_dict,
    extract_sas_file_from_zipfile,
    df_to_metadata,
    first_day_month,
    last_day_month
)
from datastore.ops.moving_avg_ops import (
    generate_fill_nemsis_rates_sql,
    generate_moving_avgs_sql,
    generate_moving_avgs_columns_sql,
    generate_moving_avgs_rank_sql
)
from datastore.pipelines.base.bins.assets import insert_into_bins_factory
from datastore.pipelines.tables.assets import create_alcohol_v2_table_asset, create_trendlines_table_asset
from datastore.pipelines.alcohol.base.assets import valid_alcohol_mids_asset, ValidMorpheusIDs
from db.datasets.alcohol.alcohol_tables import NEMSISAlcohol_v2


@dg.asset(
    partitions_def=NEMSIS_ALCOHOL_V2_PARTITIONS,
    group_name="Alcohol",
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_alcohol_v2_data_delivery_asset(context: dg.AssetExecutionContext) -> dg.Output[ZippedDataDelivery]:
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
    partitions_def=NEMSIS_ALCOHOL_V2_PARTITIONS,
    ins={"data_delivery": dg.AssetIn(nemsis_alcohol_v2_data_delivery_asset.key)},
    group_name="Alcohol",
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_alcohol_v2_raw_df_asset(
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

    # Since there is variation in this column
    if 'CountyFIPS' in df.columns:
        df.rename(columns={'CountyFIPS': 'Countyfips'}, inplace=True)

    # Generate Data Lineage
    df['row_num'] = df.index
    df['source_file'] = data_delivery.get_filename()
    df['data_release'] = data_delivery.data_provider
    df['data_provider'] = data_delivery.data_provider

    return dg.Output(df, metadata=df_to_metadata(df))


@dg.asset(
    partitions_def=NEMSIS_ALCOHOL_V2_PARTITIONS,
    ins={
        "raw_df": dg.AssetIn(nemsis_alcohol_v2_raw_df_asset.key),
        "ValidMIDS": dg.AssetIn(valid_alcohol_mids_asset.key)
    },
    group_name='Alcohol',
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_alcohol_v2_clean_df_asset(
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

    # Generate start and end dates
    raw_df['start_date'] = raw_df['Yearmonth'].apply(
        lambda row: first_day_month(int(row[:4]), int(row[4:]))
    )
    raw_df['end_date'] = raw_df['Yearmonth'].apply(
        lambda row: last_day_month(int(row[:4]), int(row[4:]))
    )
    
    # Generate MID
    raw_df['mid'] = raw_df["Countyfips"].apply(lambda fips: f"COUNTY {fips}")
    raw_df['type'] = 'COUNTY'
    
    # Other
    raw_df['outcome'] = 'alcohol'
    raw_df['measure'] = 'alcohol_rate_rank'
    raw_df['county_name'] = raw_df['Countyfips']
    raw_df['county_fips'] = raw_df['Countyfips']

    cols = set(raw_df.columns)
    rank_col_source = 'Rank' if 'Rank' in cols else 'RankAlcoholRate'
    rank_value_col_source = 'RankValue' if 'RankValue' in cols else 'RankValueAlcoholRate'

    raw_df['alcohol_rate_rank'] = raw_df[rank_col_source]
    raw_df['alcohol_rate_rank_value'] = raw_df[rank_value_col_source]

    raw_df['is_valid_county'] = raw_df['mid'].apply(lambda mid: ValidMIDS.is_valid(mid, 'COUNTY'))
    raw_df = raw_df.loc[raw_df['is_valid_county']].copy()

    # Filter Columns
    columns = [
        'start_date',
        'end_date',
        'county_name',
        'county_fips',
        'alcohol_rate_rank',
        'alcohol_rate_rank_value',
        'mid',
        'type',
        'source_file',
        'row_num',
        'data_release',
        'data_provider'
    ]
    clean_df = raw_df[columns].copy()
    
    return dg.Output(clean_df, metadata=df_to_metadata(clean_df))


@dg.asset(
    ins={
        "clean_dfs": dg.AssetIn(nemsis_alcohol_v2_clean_df_asset.key, partition_mapping=dg.AllPartitionMapping()),
        "clean_dfs_v1": dg.AssetIn(nemsis_alcohol_v1_clean_df_asset.key, partition_mapping=dg.AllPartitionMapping()),
        "nemsis_alcohol_v2_tbl": dg.AssetIn(create_alcohol_v2_table_asset.key)
    },
    group_name='Alcohol',
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_alcohol_monthly_table(
    db: PostgresConnectionResource,
    clean_dfs: Dict[str, pd.DataFrame],
    clean_dfs_v1: Dict[str, pd.DataFrame],
    nemsis_alcohol_v2_tbl: Any
) -> None:
    """
    This function creates and populates the NEMSISAlcoholTable in the database.

    Parameters:
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.
    clean_dfs: List[pd.DataFrame]

    """

    df = pd.concat([*clean_dfs.values(), *clean_dfs_v1.values()])

    # nemsis_alcohol_v2_tbl.__table__.drop(bind=db.engine, checkfirst=True)
    # nemsis_alcohol_v2_tbl.__table__.create(bind=db.engine, checkfirst=True)

    records = []

    for _, row in df.iterrows():
        records.append(nemsis_alcohol_v2_tbl(**row.to_dict()))

    with db.session() as session, session.begin():
        for record in records:
            session.merge(record)
        session.commit()

#######################################################################################

@dg.asset(
    partitions_def=NEMSIS_ALCOHOL_V2_BINS_PARTITIONS,
    group_name="Alcohol",
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_alcohol_v2_bins_data_delivery_asset(context: dg.AssetExecutionContext) -> dg.Output[ZippedDataDelivery]:
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
    partitions_def=NEMSIS_ALCOHOL_V2_BINS_PARTITIONS,
    ins={"data_delivery": dg.AssetIn(nemsis_alcohol_v2_bins_data_delivery_asset.key)},
    group_name="Alcohol",
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_alcohol_v2_bins_clean_df_asset(
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


    df = extract_sas_file_from_zipfile(
        data_delivery.get_full_path(), 
        data_delivery.get_filename(), 
        encoding='latin1'
    )
    df = df.loc[df.Metric == 'RankAlcoholRate'].copy()

    if ptypes.is_numeric_dtype(df.StartDate):
        df['start_date'] = df['StartDate'].apply(
            lambda x: first_day_month(datetime.datetime.fromtimestamp(x).year - 10, datetime.datetime.fromtimestamp(x).month) 
        )
        df['end_date'] = df['EndDate'].apply(
            lambda x: last_day_month(datetime.datetime.fromtimestamp(x).year - 10, datetime.datetime.fromtimestamp(x).month) 
        )
    else:
        df['start_date'] = df['StartDate']
        df['end_date'] = df['EndDate']

    # Misc
    df['outcome'] = 'alcohol'
    df['measure'] = 'alcohol_rate'
    df['type'] = 'COUNTY'
    df['midpoint'] = (df['MIN'] + df['MAX']) / 2.0
    df['n'] = None # TO DO: NEED VENDOR TO ADD THIS COLUMN
    df['rankValue'] = df['Rank'].apply(lambda x: RANK_CONVERTER[x])
    df['source_file'] = data_delivery.get_filename()
    df['data_release'] = data_delivery.data_release
    df['data_provider'] = data_delivery.data_provider
    df['row_num'] = df.index + 1
    
    df.rename(columns={
        'Rank': 'rank',
        'MIN': 'min',
        'MEDIAN': 'median',
        'MEAN': 'mean',
        'MAX': 'max',
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

    df = df[keep_cols].copy()

    return dg.Output(df, metadata=df_to_metadata(df, n=1000))

#######################################################################################

@dg.asset(
    partitions_def=NEMSIS_ALCOHOL_V2_TRENDLINES_PARTITIONS,
    group_name="Alcohol",
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_alcohol_v2_trendlines_data_delivery_asset(context: dg.AssetExecutionContext) -> dg.Output[ZippedDataDelivery]:
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
    partitions_def=NEMSIS_ALCOHOL_V2_TRENDLINES_PARTITIONS,
    ins={"data_delivery": dg.AssetIn(nemsis_alcohol_v2_trendlines_data_delivery_asset.key)},
    group_name="Alcohol",
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_alcohol_v2_trendlines_clean_df_asset(
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

    trendlines = extract_sas_file_from_zipfile(data_delivery.get_full_path(), data_delivery.get_filename())

    trendlines = trendlines.loc[trendlines.Metric == 'Alcohol'].copy()

    records = []

    for index, row in trendlines.iterrows():
        year = int(row['year'])
        month = int(row['month'])

        records.append({
            'start_date': first_day_month(year, month),
            'end_date': last_day_month(year, month),
            'value': row['monthlyRate'] * 100_000,
            'outcome': 'alcohol',
            'measure': 'alcohol_rate',
            'source_file': data_delivery.get_full_path(),
            'row_num': index + 1,
            'data_provider': data_delivery.data_provider,
            'data_release': data_delivery.data_release
        })

    df = pd.DataFrame(records)

    return dg.Output(df, metadata=df_to_metadata(df))


@dg.asset(
    ins={
        "clean_dfs": dg.AssetIn(nemsis_alcohol_v2_trendlines_clean_df_asset.key, partition_mapping=dg.AllPartitionMapping()),
        "trendlines_tbl": dg.AssetIn(create_trendlines_table_asset.key)
    },
    group_name='Alcohol',
    automation_condition=dg.AutomationCondition.eager()
)
def nemsis_alcohol_trendlines_table(
    db: PostgresConnectionResource,
    clean_dfs: Any,
    trendlines_tbl: Any
) -> None:
    """
    This function creates and populates the Alcohol Trendlines in the database.

    Parameters:
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.
    clean_dfs: List[pd.DataFrame]

    """

    if isinstance(clean_dfs, dict):
        df = pd.concat([*clean_dfs.values()])
    else:
        df = clean_dfs

    records = []

    for _, row in df.iterrows():
        records.append(trendlines_tbl(**row.to_dict()))

    with db.session() as session, session.begin():
        for record in records:
            session.merge(record)
        session.commit()

#######################################################################################

nemsis_alcohol_v2_bins_table_asset = insert_into_bins_factory(
    input_asset=nemsis_alcohol_v2_bins_clean_df_asset,
    asset_key="nemsis_alcohol_v2_bins_table_asset",
    asset_group="Alcohol",
    partitioned=True
)

@dg.asset(
    deps=[nemsis_alcohol_monthly_table],
    group_name='Alcohol',
    automation_condition=dg.AutomationCondition.eager(),
    ins={
        "nemsis_alcohol_v2_tbl": dg.AssetIn(create_alcohol_v2_table_asset.key)
    }
)
def fill_nemsis_alcohol_v2(
    db: PostgresConnectionResource,
    nemsis_alcohol_v2_tbl: Any
) -> None:
    """
    This function Fills NEMSIS null rates.

    Parameters:
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.

    """
    
    sql_query = generate_fill_nemsis_rates_sql(
        target_table=nemsis_alcohol_v2_tbl.__tablename__,
        rate_col='alcohol_rate',
        rep_value='midpoint',
        rank_col='alcohol_rate_rank',
        rank_value_col='alcohol_rate_rank_value',
        measure='alcohol_rate'
    )
    
    with db.session() as session, session.begin():
        session.execute(text(sql_query))
        session.commit()
    
    return None

#######################################################################################

@dg.asset(
    deps=[fill_nemsis_alcohol_v2],
    group_name='Alcohol',
    automation_condition=dg.AutomationCondition.eager(),
    ins={
        "nemsis_alcohol_v2_tbl": dg.AssetIn(create_alcohol_v2_table_asset.key)
    }
)
def load_moving_avgs_nemsis_alcohol_v2(
    db: PostgresConnectionResource,
    nemsis_alcohol_v2_tbl: Any
) -> None:
    """
    This function Fills NEMSIS null rates.

    Parameters:
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.

    """
    
    sql_query = generate_moving_avgs_sql(
        target_table=nemsis_alcohol_v2_tbl.__tablename__,
        metric_col='alcohol_rate',
        target_col='alcohol_rate_6mo',
        num_months=6
    )
    
    with db.session() as session, session.begin():
        session.execute(text(sql_query))
        session.commit()
    
    return None

#######################################################################################

@dg.asset(
    deps=[nemsis_alcohol_v2_bins_table_asset],
    group_name='Alcohol',
    automation_condition=dg.AutomationCondition.eager()
)
def load_moving_avgs_nemsis_alcohol_bins_v2(
    db: PostgresConnectionResource,
) -> None:
    """
    This function Fills NEMSIS null rates.

    Parameters:
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.

    """
    
    sql_query = generate_moving_avgs_columns_sql(
        outcome='alcohol', 
        measure='alcohol_rate',
        target='alcohol_rate_6mo'
    )
    
    with db.session() as session, session.begin():
        session.execute(text(sql_query))
        session.commit()
    
    return None


@dg.asset(
    deps=[load_moving_avgs_nemsis_alcohol_bins_v2],
    group_name='Alcohol',
    automation_condition=dg.AutomationCondition.eager()
)
def load_moving_avgs_nemsis_alcohol_bins_rank_v2(
    db: PostgresConnectionResource,
) -> None:
    """
    This function Fills NEMSIS null rates.

    Parameters:
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.

    """
    
    sql_query = generate_moving_avgs_rank_sql(
        target_table=NEMSISAlcohol_v2.__tablename__,
        source_col='alcohol_rate_6mo',
        target_rank_col='alcohol_rate_6mo_rank',
        target_rank_value_col='alcohol_rate_6mo_rank_value',
        rank_match=False
    )
    
    with db.session() as session, session.begin():
        session.execute(text(sql_query))
        session.commit()
    
    return None

#######################################################################################
