import zipfile
from typing import List, Dict, Union, Any
from sqlalchemy.sql import text
import pandas as pd
import dagster as dg
from .partitions import HV_SOC_V1_PARTITIONS, HV_SOC_V1_BINS_PARTITIONS
from datastore.resources.postgres_resource import PostgresConnectionResource
from datastore.models.data_source import DataDelivery
from db.datasets.soc.soc_tables import AggregatedSOCV1
from datastore.utils.serialize import (
    partition_key_to_dict, extract_sas_file_from_zipfile, df_to_metadata,
    first_day_month, last_day_month
)
from datastore.ops.moving_avg_ops import generate_moving_avgs_sql, generate_moving_avgs_rank_sql
from datastore.pipelines.soc.base.assets import valid_soc_mids_asset, ValidMorpheusIDs
from datetime import datetime
from datastore.pipelines.tables.assets import create_soc_v1_table_asset

@dg.asset(
    partitions_def=HV_SOC_V1_PARTITIONS,
    group_name="SOC",
    automation_condition=dg.AutomationCondition.eager()
)
def hv_soc_v1_data_delivery_asset(context: dg.AssetExecutionContext) -> dg.Output[DataDelivery]:
    """ Generate Data Delivery Object for NEMSIS v2 Monthly delivery. """
    partition_key = context.partition_key
    context.log.info(partition_key)

    data_delivery = DataDelivery(**partition_key_to_dict(partition_key))
    context.log.info(data_delivery)

    return dg.Output(
        data_delivery,
        metadata={'preview': dg.MetadataValue.md(str(data_delivery))}
    )


@dg.asset(
    partitions_def=HV_SOC_V1_PARTITIONS,
    ins={"data_delivery": dg.AssetIn(hv_soc_v1_data_delivery_asset.key)},
    group_name="SOC",
    automation_condition=dg.AutomationCondition.eager()
)
def hv_soc_v1_raw_df_asset(
    context: dg.AssetExecutionContext,
    data_delivery: DataDelivery
) -> dg.Output[pd.DataFrame]:
    """ 

    Parameters
    ----------
    context : dg.AssetExecutionContext
    hv_soc_v1_data_delivery_asset : DataDelivery

    Returns
    -------
    dg.Output[pd.DataFrame]
    """

    partition_key = context.partition_key
    df = pd.read_parquet(data_delivery.get_full_path())

    return dg.Output(df, metadata=df_to_metadata(df))


@dg.asset(
    partitions_def=HV_SOC_V1_PARTITIONS,
    ins={"raw_df": dg.AssetIn(hv_soc_v1_raw_df_asset.key), "ValidMIDS": dg.AssetIn(valid_soc_mids_asset.key)},
    group_name='SOC',
    automation_condition=dg.AutomationCondition.eager()
)
def hv_soc_v1_clean_df_asset(
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

    raw_df['row_num'] = (raw_df.index + 1).astype(str)

    excluded = ['date_delivery', 'race_ethnicity', 'age_category', 'state']
    keepers = [c for c in raw_df.columns if c not in excluded]

    start_date = first_day_month(*map(int, raw_df['date_delivery'].min().split('-')))
    end_date = last_day_month(*map(int, raw_df['date_delivery'].max().split('-')))

    aggregated_results = raw_df[keepers].groupby(['zip3']).sum().reset_index()
    aggregated_results['mid'] = aggregated_results['zip3'].apply(lambda x: f'ZCTA3 {x}')
    aggregated_results['is_valid'] = aggregated_results['mid'].apply(ValidMIDS.is_valid)

    # Calculate the SOC Rate (This Line Needs to change if we normalize to per 10k...)
    aggregated_results['any_soc_rate'] = (
        10_000 * aggregated_results['any_SOC'] / aggregated_results['dist_hvid_cnt']
    )

    rank_converter = {
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

    aggregated_results['any_soc_rate_rank'] = pd.qcut(
        aggregated_results['any_soc_rate'], 10, labels=rank_converter.keys()
    )

    aggregated_results['any_soc_rate_rank_value'] = aggregated_results['any_soc_rate_rank'].apply(lambda x: rank_converter[x])
    
    aggregated_results.rename(columns={
        'ARDS': 'ards',
        'DIC': 'dic',
        'HF_arrest_during_surgery': 'hf_arrest_during_surgery',
        'puerperal_CVD': 'puerperal_cvd',
        'PE_acute_HF': 'pe_acute_hf',
        'any_SOC': 'any_soc',
        'any_SOC_mortality': 'any_soc_mortality'
    }, inplace=True)

    aggregated_results['start_date'] = start_date
    aggregated_results['end_date'] = end_date
    aggregated_results['type'] = 'ZCTA3'
    aggregated_results['outcome'] = 'soc'
    aggregated_results['measure'] = 'any_soc_rate'

    # Generate Data Lineage
    aggregated_results['row_num'] = aggregated_results.index + 1
    aggregated_results['source_file'] = data_delivery.get_filename()
    aggregated_results['data_release'] = data_delivery.data_release
    aggregated_results['data_provider'] = data_delivery.data_provider

    keep_cols = [
        'zip3',
        'start_date',
        'end_date',
        'mid',
        'dist_hvid_cnt',
        'acute_myocardial_infarction',
        'aneurysm',
        'acute_renal_failure',
        'ards',
        'amniotic_fluid_embolism',
        'cardiac_arrest_vfib',
        'convert_cardiac_rhythm',
        'dic',
        'transfusion',
        'eclampsia',
        'hf_arrest_during_surgery',
        'puerperal_cvd',
        'pe_acute_hf',
        'anesthesia_comp',
        'sepsis',
        'shock',
        'sickle_cell_crisis',
        'air_thrombotic_embolism',
        'hysterectomy',
        'tracheostomy',
        'ventilation',
        'exclude_transfusion',
        'any_soc',
        'any_soc_rate',
        'any_soc_rate_rank',
        'any_soc_rate_rank_value',
        'mortality',
        'mh_suicide_self_harm',
        'mh_abuse',
        'mh_sud',
        'mh_spmi',
        'any_soc_mortality',
        'type',
        'row_num',
        'source_file',
        'data_release',
        'data_provider'
    ]
    
    clean_df = aggregated_results[keep_cols].loc[aggregated_results['is_valid']].copy()

    return dg.Output(clean_df, metadata=df_to_metadata(clean_df))


@dg.asset(
    partitions_def=HV_SOC_V1_PARTITIONS,
    ins={"clean_df": dg.AssetIn(hv_soc_v1_clean_df_asset.key)},
    group_name='SOC',
    automation_condition=dg.AutomationCondition.eager()
)
def hv_soc_v1_bins_clean_df_asset(
    context: dg.AssetExecutionContext,
    clean_df: pd.DataFrame
) -> dg.Output[pd.DataFrame]:
    """ Generate HV SOC V1 Bins

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

    rank_converter = {
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

    bin_stats = (
        clean_df
        .groupby(['any_soc_rate_rank', 'start_date', 'end_date'])
        .agg(
            bin_mean=('any_soc_rate', 'mean'),
            bin_median=('any_soc_rate', 'median'),
            bin_min=('any_soc_rate', 'min'),
            bin_max=('any_soc_rate', 'max'),
            bin_count=('any_soc_rate', len),
        )
        .reset_index()
    )
    bin_stats['bin_midpoint'] = (bin_stats['bin_max'] + bin_stats['bin_min']) / 2.0
    bin_stats_sorted = bin_stats.sort_values(by=['start_date', 'end_date', 'any_soc_rate_rank'])

    bin_stats_sorted['next_min'] = bin_stats_sorted.groupby(['start_date', 'end_date'])['bin_min'].shift(-1)
    bin_stats_sorted['next_max'] = bin_stats_sorted.groupby(['start_date', 'end_date'])['bin_max'].shift(-1)

    bin_stats_sorted['next_min'] = bin_stats_sorted['next_min'].fillna(bin_stats_sorted['bin_max'])
    bin_stats_sorted['any_soc_rate_rank_value'] = bin_stats_sorted['any_soc_rate_rank'].apply(lambda x: rank_converter[x])

    bin_stats_sorted.rename(columns={
        'any_soc_rate_rank': 'rank',
        'any_soc_rate_rank_value': 'rankValue',
        'bin_mean': 'mean',
        'bin_median': 'median',
        'bin_min': 'min',
        'bin_mean': 'mean',
        'next_min': 'max',
        'bin_count': 'n',
        'bin_midpoint': 'midpoint'
    }, inplace=True)

    bin_stats_sorted['type'] = 'ZCTA3'
    bin_stats_sorted['outcome'] = 'soc'
    bin_stats_sorted['measure'] = 'any_soc_rate'

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


@dg.asset(
    deps=[create_soc_v1_table_asset],
    ins={
        "clean_dfs": dg.AssetIn(hv_soc_v1_clean_df_asset.key, partition_mapping=dg.AllPartitionMapping()),
    },
    group_name='SOC',
    automation_condition=dg.AutomationCondition.eager()
)
def hv_soc_v1_aggregated_table(
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

    AggregatedSOCV1.__table__.drop(bind=db.engine, checkfirst=True)
    AggregatedSOCV1.__table__.create(bind=db.engine, checkfirst=True)

    records = []

    for _, row in df.iterrows():
        records.append(AggregatedSOCV1(**row.to_dict()))

    with db.session() as session, session.begin():
        for record in records:
            session.merge(record)
        session.commit()


#######################################################################################

@dg.asset(
    deps=[
        hv_soc_v1_aggregated_table
    ],
    group_name='SOC',
    automation_condition=dg.AutomationCondition.eager()
)
def soc_generate_moving_avg_cols_v1(db: PostgresConnectionResource) -> None:
    """ Generate Moving Average columns

    Parameters
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.
    """
    

    sql_query = generate_moving_avgs_sql(
        target_table=AggregatedSOCV1.__tablename__,
        metric_col='any_soc_rate',
        target_col='any_soc_rate_6mo',
        num_months=6
    )
    
    with db.session() as session, session.begin():
        session.execute(text(sql_query))
        session.commit()
    
    return None


@dg.asset(
    deps=[soc_generate_moving_avg_cols_v1],
    group_name='SOC',
    automation_condition=dg.AutomationCondition.eager()
)
def load_moving_avgs_hv_soc_bins_rank_v1(
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
        target_table=AggregatedSOCV1.__tablename__,
        source_col='any_soc_rate_6mo',
        target_rank_col='any_soc_rate_6mo_rank',
        target_rank_value_col='any_soc_rate_6mo_rank_value',
        rank_match=False
    )
    
    with db.session() as session, session.begin():
        session.execute(text(sql_query))
        session.commit()
    
    return None

#######################################################################################
