import pandas as pd
from typing import List
from sqlalchemy.engine import Row
from app.utilities.identifiers import mid_from_geoid
from db.datasets.demographics.demographics_tables import (
    CBACSEstimates,
    CBDemographics,
)
from app.db.database import registry
from app.configs.consts import ValidMorpheusIDs, Replacements
from datetime import datetime


@registry.register('load_acs_estimates', version='2.0')
def load_acs_estimates(input_file: str, geography: str, start_date: str, end_date: str) -> List[Row]:
    """ETL Scripts to Load ACS Estimates Data.

    Parameters
    ----------
    input_file : str
    geography : str
        Geographic Resolution.

    Returns
    -------
    List[Rows]
        List of Rows to be inserted into the DB.
    """

    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)

    results = pd.read_csv(input_file, dtype=str)
    results['MID'] = results['GEOID'].apply(lambda geoid: mid_from_geoid(geoid, geography))
    results['is_valid_mid'] = results['MID'].apply(lambda x: ValidMorpheusIDs.is_valid(x, geography))

    records = []
    for index, row in results.loc[results.is_valid_mid].replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        record = CBACSEstimates(
            start_date=start_date,
            end_date=end_date,
            name=row.NAME,
            total_households=row.B19001_001E,
            less_than_10k=row.B19001_002E,
            between_10k_15k=row.B19001_003E,
            between_15k_20k=row.B19001_004E,
            between_20k_25k=row.B19001_005E,
            between_25k_30k=row.B19001_006E,
            between_30k_35k=row.B19001_007E,
            between_35k_40k=row.B19001_008E,
            between_40k_45k=row.B19001_009E,
            between_45k_50k=row.B19001_010E,
            between_50k_60k=row.B19001_011E,
            between_60k_75k=row.B19001_012E,
            between_75k_100k=row.B19001_013E,
            between_100k_125k=row.B19001_014E,
            between_125k_150k=row.B19001_015E,
            between_150k_200k=row.B19001_016E,
            over_200k=row.B19001_017E,
            total_population_race=row.B02001_001E,
            pop_white=row.B02001_002E,
            pop_black=row.B02001_003E,
            pop_american_indian=row.B02001_004E,
            pop_asian=row.B02001_005E,
            pop_pacific_isl=row.B02001_006E,
            pop_other=row.B02001_007E,
            pop_multi=row.B02001_008E,
            pop_multi_including_other=row.B02001_009E,
            pop_multi_excluding_other=row.B02001_010E,
            total_population_age_sex=row.B01001_001E,
            total_male=row.B01001_002E,
            male_pop_0_5=row.B01001_003E,
            male_pop_5_9=row.B01001_004E,
            male_pop_10_14=row.B01001_005E,
            male_pop_15_17=row.B01001_006E,
            male_pop_18_19=row.B01001_007E,
            male_pop_20=row.B01001_008E,
            male_pop_21=row.B01001_009E,
            male_pop_22_24=row.B01001_010E,
            male_pop_25_29=row.B01001_011E,
            male_pop_30_34=row.B01001_012E,
            male_pop_35_39=row.B01001_013E,
            male_pop_40_44=row.B01001_014E,
            male_pop_45_49=row.B01001_015E,
            male_pop_50_54=row.B01001_016E,
            male_pop_55_59=row.B01001_017E,
            male_pop_60_61=row.B01001_018E,
            male_pop_62_64=row.B01001_019E,
            male_pop_65_66=row.B01001_020E,
            male_pop_67_69=row.B01001_021E,
            male_pop_70_74=row.B01001_022E,
            male_pop_75_79=row.B01001_023E,
            male_pop_80_84=row.B01001_024E,
            male_pop_85_over=row.B01001_025E,
            total_female=row.B01001_026E,
            female_pop_0_5=row.B01001_027E,
            female_pop_5_9=row.B01001_028E,
            female_pop_10_14=row.B01001_029E,
            female_pop_15_17=row.B01001_030E,
            female_pop_18_19=row.B01001_031E,
            female_pop_20=row.B01001_032E,
            female_pop_21=row.B01001_033E,
            female_pop_22_24=row.B01001_034E,
            female_pop_25_29=row.B01001_035E,
            female_pop_30_34=row.B01001_036E,
            female_pop_35_39=row.B01001_037E,
            female_pop_40_44=row.B01001_038E,
            female_pop_45_49=row.B01001_039E,
            female_pop_50_54=row.B01001_040E,
            female_pop_55_59=row.B01001_041E,
            female_pop_60_61=row.B01001_042E,
            female_pop_62_64=row.B01001_043E,
            female_pop_65_66=row.B01001_044E,
            female_pop_67_69=row.B01001_045E,
            female_pop_70_74=row.B01001_046E,
            female_pop_75_79=row.B01001_047E,
            female_pop_80_84=row.B01001_048E,
            female_pop_85_over=row.B01001_049E,
            geoid=row.GEOID,
            type=row.TYPE,
            mid=row.MID,
            source_file=input_file,
            row_num=row.ROW_NUM[:-1],
        )
        records.append(record)

    return records


@registry.register('load_demographic_profile', version='2.0')
def load_demographic_profile(input_file: str, geography: str, start_date: str, end_date: str) -> List[Row]:
    """ETL Scripts to Load Census Demographic Profile Data.

    Parameters
    ----------
    input_file : str
    geography : str
        Geographic Resolution.

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)

    results = pd.read_csv(input_file, dtype=str)
    results['MID'] = results['GEOID'].apply(lambda geoid: mid_from_geoid(geoid, geography))

    records = []
    for index, row in results.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        record = CBDemographics(
            start_date=start_date,
            end_date=end_date,
            name=row.NAME,
            total_population=row.DP1_0001C,
            pop_0_5=row.DP1_0002C,
            pop_5_9=row.DP1_0003C,
            pop_10_14=row.DP1_0004C,
            pop_15_19=row.DP1_0005C,
            pop_20_24=row.DP1_0006C,
            pop_25_29=row.DP1_0007C,
            pop_30_34=row.DP1_0008C,
            pop_35_39=row.DP1_0009C,
            pop_40_44=row.DP1_0010C,
            pop_45_49=row.DP1_0011C,
            pop_50_54=row.DP1_0012C,
            pop_55_59=row.DP1_0013C,
            pop_60_64=row.DP1_0014C,
            pop_65_69=row.DP1_0015C,
            pop_70_74=row.DP1_0016C,
            pop_75_79=row.DP1_0017C,
            pop_80_84=row.DP1_0018C,
            pop_85_over=row.DP1_0019C,
            male_population=row.DP1_0025C,
            female_population=row.DP1_0049C,
            pop_white=row.DP1_0078C,
            pop_black=row.DP1_0079C,
            pop_american_indian=row.DP1_0080C,
            pop_asian=row.DP1_0081C,
            pop_pacific_isl=row.DP1_0082C,
            pop_other=row.DP1_0083C,
            pop_multi=row.DP1_0084C,
            geoid=row.GEOID,
            type=row.TYPE,
            mid=row.MID,
            source_file=input_file,
            row_num=row.ROW_NUM,
        )
        records.append(record)

    # US-Territories
    if geography == 'STATE':
        territories = [
            ('STATE 60', 'American Samoa'),
            ('STATE 66', 'Guam'),
            ('STATE 69', 'Northern Mariana Islands '),
            # ('STATE 72', 'Puerto Rico'), # Included in the 2020 Census.
            ('STATE 78', 'Virgin Islands'),
        ]

        for mid, name in territories:
            records.append(
                CBDemographics(
                    start_date=start_date,
                    end_date=start_date,
                    name=name,
                    geoid=mid.split(' ')[-1],
                    mid=mid,
                    type='STATE',
                )
            )

    return records
