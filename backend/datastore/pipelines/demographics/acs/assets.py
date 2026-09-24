import dagster as dg
import pandas as pd
import numpy as np
from typing import Any
from datetime import datetime
from .partitions import CENSUS_ACS_PARTITIONS
from datastore.utils.consts import Replacements
from datastore.models.data_source import CensusDataDelivery
from datastore.utils.serialize import (
    partition_key_to_dict
)
from datastore.resources.postgres_resource import PostgresConnectionResource
from db.datasets.demographics.demographics_tables import CBACSEstimates
from datastore.utils.serialize import df_to_metadata
from datastore.pipelines.base.consts.assets import valid_mids_asset, ValidMorpheusIDs


@dg.asset(
    ins={
        "ValidMIDS": dg.AssetIn(valid_mids_asset.key)
    },
    partitions_def=CENSUS_ACS_PARTITIONS,
    group_name="Demographics",
    automation_condition=dg.AutomationCondition.eager()
)
def census_acs_clean_df_asset(context: dg.AssetExecutionContext, ValidMIDS: ValidMorpheusIDs) -> dg.Output[pd.DataFrame]:
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
    

    start_date = datetime.fromisoformat('2022-01-01')
    end_date = datetime.fromisoformat('2022-12-31')

    results = pd.read_csv(data_delivery.get_full_path(), dtype=str)
    results['MID'] = results['GEOID'].apply(
        lambda geoid: f"{data_delivery.geo_type} {geoid}" if not ((geoid is None) or (pd.isna(geoid))) else None
    )

    results['is_valid_mid'] = results['MID'].apply(lambda x: ValidMIDS.is_valid(x, data_delivery.geo_type))

    records = []
    for _, row in results.loc[results['is_valid_mid']].replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        record = {
            'start_date': start_date,
            'end_date': end_date,
            'name': row.NAME,
            'total_households': row.B19001_001E,
            'less_than_10k': row.B19001_002E,
            'between_10k_15k': row.B19001_003E,
            'between_15k_20k': row.B19001_004E,
            'between_20k_25k': row.B19001_005E,
            'between_25k_30k': row.B19001_006E,
            'between_30k_35k': row.B19001_007E,
            'between_35k_40k': row.B19001_008E,
            'between_40k_45k': row.B19001_009E,
            'between_45k_50k': row.B19001_010E,
            'between_50k_60k': row.B19001_011E,
            'between_60k_75k': row.B19001_012E,
            'between_75k_100k': row.B19001_013E,
            'between_100k_125k': row.B19001_014E,
            'between_125k_150k': row.B19001_015E,
            'between_150k_200k': row.B19001_016E,
            'over_200k': row.B19001_017E,
            'total_population_race': row.B02001_001E,
            'pop_white': row.B02001_002E,
            'pop_black': row.B02001_003E,
            'pop_american_indian': row.B02001_004E,
            'pop_asian': row.B02001_005E,
            'pop_pacific_isl': row.B02001_006E,
            'pop_other': row.B02001_007E,
            'pop_multi': row.B02001_008E,
            'pop_multi_including_other': row.B02001_009E,
            'pop_multi_excluding_other': row.B02001_010E,
            'total_population_age_sex': row.B01001_001E,
            'total_male': row.B01001_002E,
            'male_pop_0_5': row.B01001_003E,
            'male_pop_5_9': row.B01001_004E,
            'male_pop_10_14': row.B01001_005E,
            'male_pop_15_17': row.B01001_006E,
            'male_pop_18_19': row.B01001_007E,
            'male_pop_20': row.B01001_008E,
            'male_pop_21': row.B01001_009E,
            'male_pop_22_24': row.B01001_010E,
            'male_pop_25_29': row.B01001_011E,
            'male_pop_30_34': row.B01001_012E,
            'male_pop_35_39': row.B01001_013E,
            'male_pop_40_44': row.B01001_014E,
            'male_pop_45_49': row.B01001_015E,
            'male_pop_50_54': row.B01001_016E,
            'male_pop_55_59': row.B01001_017E,
            'male_pop_60_61': row.B01001_018E,
            'male_pop_62_64': row.B01001_019E,
            'male_pop_65_66': row.B01001_020E,
            'male_pop_67_69': row.B01001_021E,
            'male_pop_70_74': row.B01001_022E,
            'male_pop_75_79': row.B01001_023E,
            'male_pop_80_84': row.B01001_024E,
            'male_pop_85_over': row.B01001_025E,
            'total_female': row.B01001_026E,
            'female_pop_0_5': row.B01001_027E,
            'female_pop_5_9': row.B01001_028E,
            'female_pop_10_14': row.B01001_029E,
            'female_pop_15_17': row.B01001_030E,
            'female_pop_18_19': row.B01001_031E,
            'female_pop_20': row.B01001_032E,
            'female_pop_21': row.B01001_033E,
            'female_pop_22_24': row.B01001_034E,
            'female_pop_25_29': row.B01001_035E,
            'female_pop_30_34': row.B01001_036E,
            'female_pop_35_39': row.B01001_037E,
            'female_pop_40_44': row.B01001_038E,
            'female_pop_45_49': row.B01001_039E,
            'female_pop_50_54': row.B01001_040E,
            'female_pop_55_59': row.B01001_041E,
            'female_pop_60_61': row.B01001_042E,
            'female_pop_62_64': row.B01001_043E,
            'female_pop_65_66': row.B01001_044E,
            'female_pop_67_69': row.B01001_045E,
            'female_pop_70_74': row.B01001_046E,
            'female_pop_75_79': row.B01001_047E,
            'female_pop_80_84': row.B01001_048E,
            'female_pop_85_over': row.B01001_049E,
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
        "clean_dfs": dg.AssetIn(census_acs_clean_df_asset.key, partition_mapping=dg.AllPartitionMapping()),
    },
    group_name='Demographics',
    automation_condition=dg.AutomationCondition.eager()
)
def census_acs_clean_table_asset(
    db: PostgresConnectionResource,
    clean_dfs: Any
) -> None:
    """
    This function creates and populates the CBACSEstimates in the database.

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

    CBACSEstimates.__table__.drop(bind=db.engine, checkfirst=True)
    CBACSEstimates.__table__.create(bind=db.engine, checkfirst=True)

    records = []

    for _, row in df.iterrows():
        records.append(CBACSEstimates(**row.to_dict()))

    with db.session() as session, session.begin():
        for record in records:
            session.merge(record)
        session.commit()
