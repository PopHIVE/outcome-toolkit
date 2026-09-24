import zipfile
from sqlalchemy.sql import text
from sqlalchemy import func, and_
from typing import List, Dict, Union, Any
import pandas as pd
import dagster as dg
from ..veradigm_ascvd_v1.partitions import VERADIGM_ASCVD_V1_PARTITIONS, VERADIGM_ASCVD_V1_BINS_PARTITIONS
from datastore.resources.postgres_resource import PostgresConnectionResource
from datastore.models.data_source import DataDelivery
from db.datasets.ascvd.ascvd_tables import ASCVDScore_v2
from db.datasets.demographics.demographics_tables import CBDemographics
from datastore.utils.serialize import (
    partition_key_to_dict, extract_sas_file_from_zipfile, df_to_metadata,
    first_day_month, last_day_month, parse_yearmon_to_start_end
)
from datastore.ops.moving_avg_ops import (
    generate_moving_avgs_sql, 
    generate_moving_avgs_columns_sql,
    generate_moving_avgs_rank_sql
)
from datastore.utils.consts import Replacements, BinLabels
from datastore.pipelines.ascvd.base.assets import valid_ascvd_mids_asset, ValidMorpheusIDs
from datetime import datetime
from ..veradigm_ascvd_v1.assets import veradigm_ascvd_v1_data_delivery_asset
from datastore.utils.consts import COUNTRY_MID, rankify
from datastore.pipelines.tables.assets import create_ascvd_v2_table_asset
from datastore.pipelines.base.bins.assets import insert_into_bins_factory


@dg.asset(
    partitions_def=VERADIGM_ASCVD_V1_PARTITIONS,
    ins={"data_delivery": dg.AssetIn(veradigm_ascvd_v1_data_delivery_asset.key)},
    group_name="ASCVD",
    automation_condition=dg.AutomationCondition.eager()
)
def veradigm_ascvd_v2_raw_df_asset(
    context: dg.AssetExecutionContext,
    data_delivery: DataDelivery
) -> dg.Output[pd.DataFrame]:
    """ 

    Parameters
    ----------
    context : dg.AssetExecutionContext
    veradigm_ascvd_v1_data_delivery_asset : DataDelivery

    Returns
    -------
    dg.Output[pd.DataFrame]
    """

    partition_key = context.partition_key
    excel = pd.ExcelFile(data_delivery.get_full_path())
    
    dfs = {
        sheet_name: excel.parse(sheet_name, dtype=str).replace({'.': None}).replace(Replacements.JAVASCRIPT_SAFE)
        for sheet_name in excel.sheet_names
    }

    # Since Veradigm has an error in their format for recent submissions
    dfs['MONTH BY ZIP3'].columns = [c.replace('24OBS', '24_OBS') for c in dfs['MONTH BY ZIP3'].columns]
    df = dfs['MONTH BY ZIP3'].copy()

    return dg.Output(df, metadata=df_to_metadata(df))


@dg.asset(
    partitions_def=VERADIGM_ASCVD_V1_PARTITIONS,
    ins={"raw_df": dg.AssetIn(veradigm_ascvd_v2_raw_df_asset.key), "ValidMIDS": dg.AssetIn(valid_ascvd_mids_asset.key)},
    group_name='ASCVD',
    automation_condition=dg.AutomationCondition.eager()
)
def veradigm_ascvd_v2_clean_df_asset(
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
    data_delivery = DataDelivery(**partition_key_to_dict(partition_key))

    yearmonths = set([col.split('_')[0] for col in raw_df.columns[1:]])

    valid_mids = raw_df.zip3.apply(lambda x: ValidMIDS.is_valid(f'ZCTA3 {x}', 'ZCTA3'))

    for yearmonth in yearmonths:
        raw_df[f'{yearmonth}_RANK'] = (
            pd.qcut(
                raw_df[f'{yearmonth}_MEAN'].astype(float),
                10,
                labels=BinLabels.LABELS.keys(),
            )
            .astype(float)
            .replace(Replacements.JAVASCRIPT_SAFE)
        )


    records = []

    for index, row in raw_df.loc[valid_mids].iterrows():
        for yearmonth in yearmonths:
            start_date, end_date = parse_yearmon_to_start_end(yearmonth)

            record = {
                'start_date': start_date,
                'end_date': end_date,
                'zip3': row.zip3,
                'mid': f'ZCTA3 {row.zip3}',
                'total_obs': row[f'{yearmonth}_OBS'],
                'total_mean': row[f'{yearmonth}_MEAN'],
                'total_mean_rank': row[f'{yearmonth}_RANK'],
                'total_mean_rank_value': BinLabels.LABELS.get(row[f'{yearmonth}_RANK']),
                'type': 'ZCTA3',
                'source_file': data_delivery.get_filename(),
                'row_num': index + 1,
                'data_release': data_delivery.data_release,
                'data_provider': data_delivery.data_provider
            }
            records.append(record)

    clean_df = pd.DataFrame(records).replace(Replacements.JAVASCRIPT_SAFE)

    return dg.Output(clean_df, metadata=df_to_metadata(clean_df))


@dg.asset(
    partitions_def=VERADIGM_ASCVD_V1_PARTITIONS,
    ins={"raw_df": dg.AssetIn(veradigm_ascvd_v2_raw_df_asset.key), "ValidMIDS": dg.AssetIn(valid_ascvd_mids_asset.key)},
    group_name='ASCVD',
    automation_condition=dg.AutomationCondition.eager()
)
def veradigm_ascvd_v2_bins_clean_df_asset(
    context: dg.AssetExecutionContext,
    raw_df: pd.DataFrame,
    ValidMIDS: ValidMorpheusIDs
) -> dg.Output[pd.DataFrame]:
    """ Generate Veradigm ASCVD V2 Bins

    Parameters
    ----------
    context : dg.AssetExecutionContext
    clean_df : pd.DataFrame

    Returns
    -------
    dg.Output[pd.DataFrame]
    """

    partition_key = context.partition_key
    data_delivery = DataDelivery(**partition_key_to_dict(partition_key))

    yearmonths = set([col.split('_')[0] for col in raw_df.columns[1:]])

    records = []

    for yearmonth in yearmonths:
        raw_df[f'{yearmonth}_MEAN'] = raw_df[f'{yearmonth}_MEAN'].astype(float)
        raw_df[f'{yearmonth}_RANK'] = (
            pd.qcut(
                raw_df[f'{yearmonth}_MEAN'],
                10,
                labels=BinLabels.LABELS.keys(),
            )
            .astype(float)
            .replace(Replacements.JAVASCRIPT_SAFE)
        )

        bin_stats = (
            raw_df
            .groupby([f'{yearmonth}_RANK'])
            .agg(
                bin_mean=(f'{yearmonth}_MEAN', 'mean'),
                bin_median=(f'{yearmonth}_MEAN', 'median'),
                bin_min=(f'{yearmonth}_MEAN', 'min'),
                bin_max=(f'{yearmonth}_MEAN', 'max'),
                bin_count=(f'{yearmonth}_MEAN', lambda x: len(x)),
            )
            .reset_index()
        )
        bin_stats['bin_midpoint'] = (bin_stats['bin_max'] + bin_stats['bin_min']) / 2.0

        start_date, end_date = parse_yearmon_to_start_end(yearmonth)

        bin_stats['next_min'] = bin_stats['bin_min'].shift(-1)
        bin_stats['next_max'] = bin_stats['bin_max'].shift(-1)

        for index, row in bin_stats.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
            if not pd.isna(row['next_min']):
                max=row['next_min']
            else:
                max=row['bin_max']
            records.append({
                'start_date': start_date,
                'end_date': end_date,
                'outcome': 'cardio',
                'measure': 'total_mean',
                'rank': row[f'{yearmonth}_RANK'],
                'rankValue': BinLabels.LABELS[row[f'{yearmonth}_RANK']],
                'n': row['bin_count'],
                'min': row['bin_min'],
                'median': row['bin_median'],
                'mean': row['bin_mean'],
                'midpoint': row['bin_midpoint'],
                'max': max,
                'type': 'ZCTA3',
                'source_file': 'Internal',
                'row_num': 'NA',
                'data_release': data_delivery.data_release,
                'data_provider': data_delivery.data_provider
            })

    clean_bins_dfs = pd.DataFrame(records).replace(Replacements.JAVASCRIPT_SAFE)

    return dg.Output(clean_bins_dfs, metadata=df_to_metadata(clean_bins_dfs))


veradigm_ascvd_v2_bins_table_asset = insert_into_bins_factory(
    input_asset=veradigm_ascvd_v2_bins_clean_df_asset,
    asset_key="veradigm_ascvd_v2_bins_table_asset",
    asset_group="ASCVD",
    partitioned=True
)


@dg.asset(
    deps=[
        create_ascvd_v2_table_asset
    ],
    ins={
        "clean_dfs": dg.AssetIn(veradigm_ascvd_v2_clean_df_asset.key, partition_mapping=dg.AllPartitionMapping()),
    },
    group_name='ASCVD',
    automation_condition=dg.AutomationCondition.eager()
)
def veradigm_ascvd_v2_aggregated_table(
    db: PostgresConnectionResource,
    clean_dfs: Any
) -> None:
    """
    This function creates and populates the ASCVDScore_v2 in the database.

    Parameters:
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.
    clean_dfs: List[pd.DataFrame]

    """

    if isinstance(clean_dfs, dict):
        df = pd.concat([*clean_dfs.values()])
    else:
        df = clean_dfs.copy()

    ASCVDScore_v2.__table__.drop(bind=db.engine, checkfirst=True)
    ASCVDScore_v2.__table__.create(bind=db.engine, checkfirst=True)

    records = []

    for _, row in df.iterrows():
        records.append(ASCVDScore_v2(**row.to_dict()))

    with db.session() as session, session.begin():
        for record in records:
            session.merge(record)
        session.commit()


#######################################################################################

@dg.asset(
    deps=[veradigm_ascvd_v2_aggregated_table],
    group_name="ASCVD",
    automation_condition=dg.AutomationCondition.eager()
)
def load_national_veradigm_ascvd_data_v2(db: PostgresConnectionResource,) -> dg.Output[pd.DataFrame]:
    """_summary_

    Parameters
    ----------
    db : PostgresConnectionResource
        _description_

    Returns
    -------
    dg.Output[pd.DataFrame]
        _description_
    """

    with db.session() as session, session.begin():
        results = (
            session.query(
                ASCVDScore_v2.start_date,
                ASCVDScore_v2.end_date,
                (func.sum(ASCVDScore_v2.total_obs)).label('total_obs'),
                (
                    func.sum(CBDemographics.total_population * ASCVDScore_v2.total_mean) / func.sum(CBDemographics.total_population)
                ).label('total_mean'),
                (
                    func.sum(CBDemographics.total_population * ASCVDScore_v2.total_mean_rank)
                    / func.sum(CBDemographics.total_population)
                ).label('total_mean_rank'),
            )
            .join(CBDemographics, CBDemographics.mid == ASCVDScore_v2.mid)
            .group_by(
                ASCVDScore_v2.start_date,
                ASCVDScore_v2.end_date,
            )
            .filter(and_(ASCVDScore_v2.type == 'ZCTA3', ASCVDScore_v2.start_date >= datetime(year=1975, month=1, day=1)))
        )
        session.commit()

    records = []

    for row in results:
        record = {
            'mid': COUNTRY_MID,
            'type': 'COUNTRY',
            'outcome': 'alcohol',
            'measure': 'alcohol_rate',
            'start_date': row.start_date,
            'end_date': row.end_date,
            'total_obs': row.total_obs,
            'total_mean': row.total_mean,
            'total_mean_rank': rankify(row.total_mean_rank),
            'total_mean_rank_value': BinLabels.LABELS.get(rankify(row.total_mean_rank), 'No Data'),
        }
        records.append(record)

    df = pd.DataFrame(records)

    return dg.Output(df, metadata=df_to_metadata(df))

@dg.asset(
    ins={
        "clean_df": dg.AssetIn(load_national_veradigm_ascvd_data_v2.key),
    },
    group_name='ASCVD',
    automation_condition=dg.AutomationCondition.eager()
)
def load_national_veradigm_ascvd_data_v2_table(
    db: PostgresConnectionResource,
    clean_df: Any
) -> None:
    """
    This function creates and populates the ASCVDScore_v2 in the database.

    Parameters:
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.
    clean_dfs: List[pd.DataFrame]

    """

    records = []

    for _, row in clean_df.iterrows():
        records.append(ASCVDScore_v2(**row.to_dict()))

    with db.session() as session, session.begin():
        for record in records:
            session.merge(record)
        session.commit()

#######################################################################################

@dg.asset(
    deps=[
        veradigm_ascvd_v2_aggregated_table,
        load_national_veradigm_ascvd_data_v2_table
    ],
    group_name='ASCVD',
    automation_condition=dg.AutomationCondition.eager()
)
def ascvd_generate_moving_avg_v2(db: PostgresConnectionResource) -> None:
    """ Generate Moving Average columns

    Parameters
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.
    """
    

    sql_query = generate_moving_avgs_sql(
        target_table=ASCVDScore_v2.__tablename__,
        metric_col='total_mean',
        target_col='total_mean_6mo',
        num_months=6
    )
    
    with db.session() as session, session.begin():
        session.execute(text(sql_query))
        session.commit()
    
    return None

#######################################################################################

@dg.asset(
    deps=[ascvd_generate_moving_avg_v2, load_national_veradigm_ascvd_data_v2_table],
    group_name='ASCVD',
    automation_condition=dg.AutomationCondition.eager()
)
def moving_avgs_veradigm_ascvd_cols_v2(
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
        outcome='cardio',
        measure='total_mean',
        target='total_mean_6mo'
    )
    
    with db.session() as session, session.begin():
        session.execute(text(sql_query))
        session.commit()
    
    return None

@dg.asset(
    deps=[moving_avgs_veradigm_ascvd_cols_v2, load_national_veradigm_ascvd_data_v2_table],
    group_name='ASCVD',
    automation_condition=dg.AutomationCondition.eager()
)
def load_moving_avgs_veradigm_ascvd_bins_rank_v2(
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
        target_table=ASCVDScore_v2.__tablename__,
        source_col='total_mean_6mo',
        target_rank_col='total_mean_6mo_rank',
        target_rank_value_col='total_mean_6mo_rank_value',
        rank_match=False
    )
    
    with db.session() as session, session.begin():
        session.execute(text(sql_query))
        session.commit()
    
    return None

#######################################################################################
