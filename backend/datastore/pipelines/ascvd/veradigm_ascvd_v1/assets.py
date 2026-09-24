import zipfile
from typing import List, Dict, Union, Any
from sqlalchemy.sql import text
from sqlalchemy import func, and_
import pandas as pd
import dagster as dg
from .partitions import VERADIGM_ASCVD_V1_PARTITIONS, VERADIGM_ASCVD_V1_BINS_PARTITIONS
from datastore.resources.postgres_resource import PostgresConnectionResource
from datastore.models.data_source import DataDelivery
from db.datasets.ascvd.ascvd_tables import ASCVDScore
from db.datasets.demographics.demographics_tables import CBDemographics
from datastore.utils.serialize import (
    partition_key_to_dict, extract_sas_file_from_zipfile, df_to_metadata,
    first_day_month, last_day_month
)
from datastore.ops.moving_avg_ops import (
    generate_moving_avgs_sql, 
    generate_moving_avgs_rank_sql
)
from datastore.utils.consts import Replacements, BinLabels
from datastore.pipelines.ascvd.base.assets import valid_ascvd_mids_asset, ValidMorpheusIDs
from datetime import datetime
from datastore.utils.consts import COUNTRY_MID, rankify
from datastore.pipelines.tables.assets import create_ascvd_v1_table_asset
from datastore.pipelines.base.bins.assets import insert_into_bins_factory


@dg.asset(
    partitions_def=VERADIGM_ASCVD_V1_PARTITIONS,
    group_name="ASCVD",
    automation_condition=dg.AutomationCondition.eager()
)
def veradigm_ascvd_v1_data_delivery_asset(context: dg.AssetExecutionContext) -> dg.Output[DataDelivery]:
    """ Generate Data Delivery Object for Veradigm ASCVD v2 Monthly delivery. """
    partition_key = context.partition_key
    context.log.info(partition_key)

    data_delivery = DataDelivery(**partition_key_to_dict(partition_key))
    context.log.info(data_delivery)

    return dg.Output(
        data_delivery,
        metadata={'preview': dg.MetadataValue.md(str(data_delivery))}
    )


@dg.asset(
    partitions_def=VERADIGM_ASCVD_V1_PARTITIONS,
    ins={"data_delivery": dg.AssetIn(veradigm_ascvd_v1_data_delivery_asset.key)},
    group_name="ASCVD",
    automation_condition=dg.AutomationCondition.eager()
)
def veradigm_ascvd_v1_raw_df_asset(
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
    
    df = excel.parse('ASCVD BY ZIP3', dtype=str).replace({'.': None}).replace(Replacements.JAVASCRIPT_SAFE)

    return dg.Output(df, metadata=df_to_metadata(df))


@dg.asset(
    partitions_def=VERADIGM_ASCVD_V1_PARTITIONS,
    ins={"raw_df": dg.AssetIn(veradigm_ascvd_v1_raw_df_asset.key), "ValidMIDS": dg.AssetIn(valid_ascvd_mids_asset.key)},
    group_name='ASCVD',
    automation_condition=dg.AutomationCondition.eager()
)
def veradigm_ascvd_v1_clean_df_asset(
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

    # TO DO: Determine this info based on data release
    gender_or_sex = 'sex' if data_delivery.data_release >= '2025-03' else 'gender'

    raw_df['mid'] = raw_df['zip3'].apply(lambda x: f"ZCTA3 {x}")
    raw_df['is_valid_zip3'] = raw_df['mid'].apply(lambda mid: ValidMIDS.is_valid(mid, 'ZCTA3'))
    raw_df['row_num'] = raw_df.index + 1

    raw_df['total_mean_bin_rank'] = (
        pd.qcut(raw_df['MeanASCVD'].astype(float), 10, labels=BinLabels.LABELS.keys())
        .astype(float)
        .replace(Replacements.JAVASCRIPT_SAFE)
    )

    raw_df['start_date'] = raw_df['StartDate'].apply(datetime.fromisoformat)
    raw_df['end_date'] = raw_df['EndDate'].apply(datetime.fromisoformat)
    
    rename_cols = {
        'MeanASCVD_obs': 'total_obs',
        'MeanASCVD': 'total_mean',
        'MeanASCVD_age_40_to_49_obs': 'age_40_to_49_obs',
        'MeanASCVD_age_40_to_49': 'age_40_to_49_mean',
        'MeanASCVD_age_50_to_59_obs': 'age_50_to_59_obs',
        'MeanASCVD_age_50_to_59': 'age_50_to_59_mean',
        'MeanASCVD_age_60_to_69_obs': 'age_60_to_69_obs',
        'MeanASCVD_age_60_to_69': 'age_60_to_69_mean',
        'MeanASCVD_age_70_obs': 'age_70_obs',
        'MeanASCVD_age_70': 'age_70_mean',
        f'MeanASCVD_{gender_or_sex}_female_obs': 'female_obs',
        f'MeanASCVD_{gender_or_sex}_female': 'female_mean',
        f'MeanASCVD_{gender_or_sex}_male_obs': 'male_obs',
        f'MeanASCVD_{gender_or_sex}_male': 'male_mean',
        'MeanASCVD_race_asian_obs': 'asian_obs',
        'MeanASCVD_race_asian': 'asian_mean',
        'MeanASCVD_race_asian_obs': 'asian_obs',
        'MeanASCVD_race_black_obs': 'black_obs',
        'MeanASCVD_race_black': 'black_mean',
        'MeanASCVD_race_null_obs': 'null_race_obs',
        'MeanASCVD_race_null': 'null_race_mean',
        'MeanASCVD_race_other_obs': 'other_obs',
        'MeanASCVD_race_other': 'other_mean',
        'MeanASCVD_race_white_obs': 'white_obs',
        'MeanASCVD_race_white': 'white_mean'
    }

    raw_df.rename(columns=rename_cols, inplace=True)

    raw_df['type'] = 'ZCTA3'
    raw_df['outcome'] = 'cardio'
    raw_df['measure'] = 'total_mean'

    # Generate Data Lineage
    raw_df['row_num'] = raw_df.index + 1
    raw_df['source_file'] = data_delivery.get_filename()
    raw_df['data_release'] = data_delivery.data_release
    raw_df['data_provider'] = data_delivery.data_provider

    keep_cols = [
        'zip3',
        'start_date',
        'end_date',
        'mid',
        *rename_cols.values(),
        'type',
        'row_num',
        'source_file',
        'data_release',
        'data_provider'
    ]
    
    clean_df = raw_df[keep_cols].loc[raw_df['is_valid_zip3']].copy()

    return dg.Output(clean_df, metadata=df_to_metadata(clean_df))


@dg.asset(
    partitions_def=VERADIGM_ASCVD_V1_PARTITIONS,
    ins={"raw_df": dg.AssetIn(veradigm_ascvd_v1_raw_df_asset.key), "ValidMIDS": dg.AssetIn(valid_ascvd_mids_asset.key)},
    group_name='ASCVD',
    automation_condition=dg.AutomationCondition.eager()
)
def veradigm_ascvd_v1_bins_clean_df_asset(
    context: dg.AssetExecutionContext,
    raw_df: pd.DataFrame,
    ValidMIDS: ValidMorpheusIDs
) -> dg.Output[pd.DataFrame]:
    """ Generate Veradigm ASCVD V1 Bins

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

    raw_df['mid'] = raw_df['zip3'].apply(lambda x: f"ZCTA3 {x}")
    raw_df['is_valid_zip3'] = raw_df['mid'].apply(lambda mid: ValidMIDS.is_valid(mid, 'ZCTA3'))
    raw_df['ROW_NUM'] = raw_df.index + 1
    raw_df['MeanASCVD'] = raw_df['MeanASCVD'].astype(float)

    raw_df['start_date'] = raw_df['StartDate'].apply(datetime.fromisoformat)
    raw_df['end_date'] = raw_df['EndDate'].apply(datetime.fromisoformat)

    raw_df['total_mean_bin_rank'] = (
        pd.qcut(raw_df['MeanASCVD'].astype(float), 10, labels=BinLabels.LABELS.keys())
        .astype(float)
        .replace(Replacements.JAVASCRIPT_SAFE)
    )

    bin_stats = (
        raw_df.loc[raw_df.is_valid_zip3]
        .groupby(['total_mean_bin_rank', 'start_date', 'end_date'])
        .agg(
            bin_mean=('MeanASCVD', 'mean'),
            bin_median=('MeanASCVD', 'median'),
            bin_min=('MeanASCVD', 'min'),
            bin_max=('MeanASCVD', 'max'),
            bin_count=('MeanASCVD', lambda x: len(x)),
        )
        .reset_index()
    )

    bin_stats['bin_midpoint'] = (bin_stats['bin_max'] + bin_stats['bin_min']) / 2.0

    bin_stats_sorted = bin_stats.sort_values(by=['start_date', 'end_date', 'total_mean_bin_rank'])

    bin_stats_sorted['next_min'] = bin_stats_sorted.groupby(['start_date', 'end_date'])['bin_min'].shift(-1)
    bin_stats_sorted['next_max'] = bin_stats_sorted.groupby(['start_date', 'end_date'])['bin_max'].shift(-1)

    bin_stats_sorted['next_min'] = bin_stats_sorted['next_min'].fillna(bin_stats_sorted['bin_max'])
    bin_stats_sorted['total_mean_bin_rank_value'] = bin_stats_sorted['total_mean_bin_rank'].apply(lambda x: BinLabels.LABELS[x])


    bin_stats_sorted.rename(columns={
        'total_mean_bin_rank': 'rank',
        'total_mean_bin_rank_value': 'rankValue',
        'bin_mean': 'mean',
        'bin_median': 'median',
        'bin_min': 'min',
        'bin_mean': 'mean',
        'next_min': 'max',
        'bin_count': 'n',
        'bin_midpoint': 'midpoint'
    }, inplace=True)

    bin_stats_sorted['type'] = 'ZCTA3'
    bin_stats_sorted['outcome'] = 'cardio'
    bin_stats_sorted['measure'] = 'total_mean'

    # Generate Data Lineage
    bin_stats_sorted['row_num'] = bin_stats_sorted.index + 1
    bin_stats_sorted['source_file'] = data_delivery.get_filename()
    bin_stats_sorted['data_release'] = data_delivery.data_release
    bin_stats_sorted['data_provider'] = data_delivery.data_provider

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

    clean_bins_dfs = bin_stats_sorted[keep_cols].copy()

    return dg.Output(clean_bins_dfs, metadata=df_to_metadata(clean_bins_dfs))

veradigm_ascvd_v1_bins_table_asset = insert_into_bins_factory(
    input_asset=veradigm_ascvd_v1_bins_clean_df_asset,
    asset_key="veradigm_ascvd_v1_bins_table_asset",
    asset_group="ASCVD",
    partitioned=True
)


@dg.asset(
    deps=[
        create_ascvd_v1_table_asset
    ],
    ins={
        "clean_dfs": dg.AssetIn(veradigm_ascvd_v1_clean_df_asset.key, partition_mapping=dg.AllPartitionMapping()),
    },
    group_name='ASCVD',
    automation_condition=dg.AutomationCondition.eager()
)
def veradigm_ascvd_v1_aggregated_table(
    db: PostgresConnectionResource,
    clean_dfs: Any
) -> None:
    """
    This function creates and populates the NEMSISAlcoholTable in the database.

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

    ASCVDScore.__table__.drop(bind=db.engine, checkfirst=True)
    ASCVDScore.__table__.create(bind=db.engine, checkfirst=True)

    records = []

    for _, row in df.iterrows():
        records.append(ASCVDScore(**row.to_dict()))

    with db.session() as session, session.begin():
        for record in records:
            session.merge(record)
        session.commit()

#######################################################################################

@dg.asset(
    deps=[veradigm_ascvd_v1_aggregated_table],
    group_name="ASCVD",
    automation_condition=dg.AutomationCondition.eager()
)
def load_national_veradigm_ascvd_data_v1(db: PostgresConnectionResource,) -> dg.Output[pd.DataFrame]:
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
                ASCVDScore.start_date,
                ASCVDScore.end_date,
                (func.sum(ASCVDScore.total_obs)).label('total_obs'),
                (
                    func.sum(CBDemographics.total_population * ASCVDScore.total_mean) / func.sum(CBDemographics.total_population)
                ).label('total_mean'),
                (
                    func.sum(CBDemographics.total_population * ASCVDScore.total_mean_rank)
                    / func.sum(CBDemographics.total_population)
                ).label('total_mean_rank'),
            )
            .join(CBDemographics, CBDemographics.mid == ASCVDScore.mid)
            .group_by(
                ASCVDScore.start_date,
                ASCVDScore.end_date,
            )
            .filter(and_(ASCVDScore.type == 'ZCTA3', ASCVDScore.start_date >= datetime(year=1975, month=1, day=1)))
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
        "clean_df": dg.AssetIn(load_national_veradigm_ascvd_data_v1.key),
    },
    group_name='ASCVD',
    automation_condition=dg.AutomationCondition.eager()
)
def load_national_veradigm_ascvd_data_v1_table(
    db: PostgresConnectionResource,
    clean_df: Any
) -> None:
    """
    This function creates and populates the ASCVDScore in the database.

    Parameters:
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.
    clean_dfs: List[pd.DataFrame]

    """

    records = []

    for _, row in clean_df.iterrows():
        records.append(ASCVDScore(**row.to_dict()))

    with db.session() as session, session.begin():
        for record in records:
            session.merge(record)
        session.commit()

#######################################################################################

@dg.asset(
    deps=[
        veradigm_ascvd_v1_aggregated_table,
        load_national_veradigm_ascvd_data_v1
    ],
    group_name='ASCVD',
    automation_condition=dg.AutomationCondition.eager()
)
def ascvd_generate_moving_avg_cols_v1(db: PostgresConnectionResource) -> None:
    """ Generate Moving Average columns

    Parameters
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.
    """
    

    sql_query = generate_moving_avgs_sql(
        target_table=ASCVDScore.__tablename__,
        metric_col='total_mean',
        target_col='total_mean_6mo',
        num_months=6
    )
    
    with db.session() as session, session.begin():
        session.execute(text(sql_query))
        session.commit()
    
    return None

@dg.asset(
    deps=[ascvd_generate_moving_avg_cols_v1, load_national_veradigm_ascvd_data_v1_table],
    group_name='ASCVD',
    automation_condition=dg.AutomationCondition.eager()
)
def load_moving_avgs_veradigm_ascvd_bins_rank_v1(
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
        target_table=ASCVDScore.__tablename__,
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
