import dagster as dg
import pandas as pd
import numpy as np
from typing import Any
from datetime import datetime
from .partitions import CENSUS_DEMOGRAPHIC_PROFILE_PARTITIONS
from datastore.utils.consts import Replacements
from datastore.models.data_source import CensusDataDelivery
from datastore.utils.serialize import (
    partition_key_to_dict
)
from datastore.resources.postgres_resource import PostgresConnectionResource
from db.datasets.demographics.demographics_tables import CBDemographics
from datastore.utils.serialize import df_to_metadata


@dg.asset(
   partitions_def=CENSUS_DEMOGRAPHIC_PROFILE_PARTITIONS,
   group_name="Demographics",
    automation_condition=dg.AutomationCondition.eager()
)
def census_demographic_profile_clean_df_asset(context: dg.AssetExecutionContext) -> dg.Output[pd.DataFrame]:
    """ Load Demographic Profile

    Parameters
    ----------
    context : dg.AssetExecutionContext
    
    Returns
    -------
    dg.Output[pd.DataFrame]
    """

    partition_key = context.partition_key
    data_delivery = CensusDataDelivery(**partition_key_to_dict(partition_key))
    

    start_date = datetime.fromisoformat('2020-01-01')
    end_date = datetime.fromisoformat('2020-12-31')

    results = pd.read_csv(data_delivery.get_full_path(), dtype=str)
    results['MID'] = results['GEOID'].apply(
        lambda geoid: f"{data_delivery.geo_type} {geoid}" if not ((geoid is None) or (pd.isna(geoid))) else None
    )

    records = []
    for _, row in results.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        record = {
            'start_date': start_date,
            'end_date': end_date,
            'name': row.NAME,
            'total_population': row.DP1_0001C,
            'pop_0_5': row.DP1_0002C,
            'pop_5_9': row.DP1_0003C,
            'pop_10_14': row.DP1_0004C,
            'pop_15_19': row.DP1_0005C,
            'pop_20_24': row.DP1_0006C,
            'pop_25_29': row.DP1_0007C,
            'pop_30_34': row.DP1_0008C,
            'pop_35_39': row.DP1_0009C,
            'pop_40_44': row.DP1_0010C,
            'pop_45_49': row.DP1_0011C,
            'pop_50_54': row.DP1_0012C,
            'pop_55_59': row.DP1_0013C,
            'pop_60_64': row.DP1_0014C,
            'pop_65_69': row.DP1_0015C,
            'pop_70_74': row.DP1_0016C,
            'pop_75_79': row.DP1_0017C,
            'pop_80_84': row.DP1_0018C,
            'pop_85_over': row.DP1_0019C,
            'male_population': row.DP1_0025C,
            'female_population': row.DP1_0049C,
            'pop_white': row.DP1_0078C,
            'pop_black': row.DP1_0079C,
            'pop_american_indian': row.DP1_0080C,
            'pop_asian': row.DP1_0081C,
            'pop_pacific_isl': row.DP1_0082C,
            'pop_other': row.DP1_0083C,
            'pop_multi': row.DP1_0084C,
            'geoid': row.GEOID,
            'type': row.TYPE,
            'mid': row.MID,
            'source_file': data_delivery.get_filename(),
            'row_num': row.ROW_NUM,
            'data_release': data_delivery.data_release,
            'data_provider': data_delivery.data_provider
        }
        records.append(record)

    # US-Territories
    if data_delivery.geo_type == 'STATE':
        territories = [
            ('STATE 60', 'American Samoa'),
            ('STATE 66', 'Guam'),
            ('STATE 69', 'Northern Mariana Islands '),
            # ('STATE 72', 'Puerto Rico'), # Included in the 2020 Census.
            ('STATE 78', 'Virgin Islands'),
        ]

        manual_additions = []
        for mid, name in territories:
            record = {
                'start_date': start_date,
                'end_date': start_date,
                'name': name,
                'geoid': mid.split(' ')[-1],
                'mid': mid,
                'type': 'STATE',
                'source_file': 'NA',
                'row_num': 'NA',
                'data_release': '2020-01',
                'data_provider': 'Internal'
            }
            for k in records[-1].keys():
                if k not in record.keys():
                    record[k] = None
            manual_additions.append(record)
        records.extend(manual_additions)

    df = pd.DataFrame(records)
    return dg.Output(df, metadata=df_to_metadata(df))


@dg.asset(
    ins={
        "clean_dfs": dg.AssetIn(census_demographic_profile_clean_df_asset.key, partition_mapping=dg.AllPartitionMapping()),
    },
    group_name='Demographics',
    automation_condition=dg.AutomationCondition.eager()
)
def census_demographic_profile_clean_table_asset(
    db: PostgresConnectionResource,
    clean_dfs: Any
) -> None:
    """
    This function creates and populates the CBDemographics in the database.

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

    CBDemographics.__table__.drop(bind=db.engine, checkfirst=True)
    CBDemographics.__table__.create(bind=db.engine, checkfirst=True)

    records = []

    for _, row in df.iterrows():
        records.append(CBDemographics(**row.to_dict()))

    with db.session() as session, session.begin():
        for record in records:
            session.merge(record)
        session.commit()
