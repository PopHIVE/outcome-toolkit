import argparse
import requests
import pandas as pd
from collections import defaultdict
from app.utilities.identifiers import zcta5_to_zcta3


class CensusBureauACS:
    BASE_URL = 'https://api.census.gov/data/2022/acs/acs5'
    FIELDS = {
        'NAME': 'name',
        # https://api.census.gov/data/2022/acs/acs5/variables.html
        'B19001_001E': 'total_households',  # Estimate!!Total:
        'B19001_002E': 'less_than_10k',  # Estimate!!Total:!!Less than $10,000
        'B19001_003E': 'between_10k_15k',  # Estimate!!Total:!!$10,000 to $14,999
        'B19001_004E': 'between_15k_20k',  # Estimate!!Total:!!$15,000 to $19,999
        'B19001_005E': 'between_20k_25k',  # Estimate!!Total:!!$20,000 to $24,999
        'B19001_006E': 'between_25k_30k',  # Estimate!!Total:!!$25,000 to $29,999
        'B19001_007E': 'between_30k_35k',  # Estimate!!Total:!!$30,000 to $34,999
        'B19001_008E': 'between_35k_40k',  # Estimate!!Total:!!$35,000 to $39,999
        'B19001_009E': 'between_40k_45k',  # Estimate!!Total:!!$40,000 to $44,999
        'B19001_010E': 'between_45k_50k',  # Estimate!!Total:!!$45,000 to $49,999
        'B19001_011E': 'between_50k_60k',  # Estimate!!Total:!!$50,000 to $59,999
        'B19001_012E': 'between_60k_75k',  # Estimate!!Total:!!$60,000 to $74,999
        'B19001_013E': 'between_75k_100k',  # Estimate!!Total:!!$75,000 to $99,999
        'B19001_014E': 'between_100k_125k',  # Estimate!!Total:!!$100,000 to $124,999
        'B19001_015E': 'between_125k_150k',  # Estimate!!Total:!!$125,000 to $149,999
        'B19001_016E': 'between_150k_200k',  # Estimate!!Total:!!$150,000 to $199,999
        'B19001_017E': 'over_200k',  # Estimate!!Total:!!$200,000 or more
        'B02001_001E': 'total_population_race',  # Estimate!!Total:
        'B02001_002E': 'pop_white',  # Estimate!!Total:!!White alone
        'B02001_003E': 'pop_black',  # Estimate!!Total:!!Black or African American alone
        'B02001_004E': 'pop_american_indian',  # Estimate!!Total:!!American Indian and Alaska Native alone
        'B02001_005E': 'pop_asian',  # Estimate!!Total:!!Asian alone
        'B02001_006E': 'pop_pacific_isl',  # Estimate!!Total:!!Native Hawaiian and Other Pacific Islander alone
        'B02001_007E': 'pop_other',  # Estimate!!Total:!!Some Other Race alone
        'B02001_008E': 'pop_multi',  # Estimate!!Total:!!Two or More Races:
        'B02001_009E': 'pop_multi_including_other',  # Estimate!!Total:!!Two or More Races:!!Two races including Some Other Race
        'B02001_010E': 'pop_multi_excluding_other',  # Estimate!!Total:!!Two or More Races:!!Two races excluding Some Other Race, and three or more races
        'B01001_001E': 'total_population_age_sex',  # Estimate!!Total:
        'B01001_002E': 'total_male',  # Estimate!!Total:!!Male:
        'B01001_003E': 'male_pop_0_5',  # Estimate!!Total:!!Male:!!Under 5 years
        'B01001_004E': 'male_pop_5_9',  # Estimate!!Total:!!Male:!!5 to 9 years
        'B01001_005E': 'male_pop_10_14',  # Estimate!!Total:!!Male:!!10 to 14 years
        'B01001_006E': 'male_pop_15_17',  # Estimate!!Total:!!Male:!!15 to 17 years
        'B01001_007E': 'male_pop_18_19',  # Estimate!!Total:!!Male:!!18 and 19 years
        'B01001_008E': 'male_pop_20',  # Estimate!!Total:!!Male:!!20 years
        'B01001_009E': 'male_pop_21',  # Estimate!!Total:!!Male:!!21 years
        'B01001_010E': 'male_pop_22_24',  # Estimate!!Total:!!Male:!!22 to 24 years
        'B01001_011E': 'male_pop_25_29',  # Estimate!!Total:!!Male:!!25 to 29 years
        'B01001_012E': 'male_pop_30_34',  # Estimate!!Total:!!Male:!!30 to 34 years
        'B01001_013E': 'male_pop_35_39',  # Estimate!!Total:!!Male:!!35 to 39 years
        'B01001_014E': 'male_pop_40_44',  # Estimate!!Total:!!Male:!!40 to 44 years
        'B01001_015E': 'male_pop_45_49',  # Estimate!!Total:!!Male:!!45 to 49 years
        'B01001_016E': 'male_pop_50_54',  # Estimate!!Total:!!Male:!!50 to 54 years
        'B01001_017E': 'male_pop_55_59',  # Estimate!!Total:!!Male:!!55 to 59 years
        'B01001_018E': 'male_pop_60_61',  # Estimate!!Total:!!Male:!!60 and 61 years
        'B01001_019E': 'male_pop_62_64',  # Estimate!!Total:!!Male:!!62 to 64 years
        'B01001_020E': 'male_pop_65_66',  # Estimate!!Total:!!Male:!!65 and 66 years
        'B01001_021E': 'male_pop_67_69',  # Estimate!!Total:!!Male:!!67 to 69 years
        'B01001_022E': 'male_pop_70_74',  # Estimate!!Total:!!Male:!!70 to 74 years
        'B01001_023E': 'male_pop_75_79',  # Estimate!!Total:!!Male:!!75 to 79 years
        'B01001_024E': 'male_pop_80_84',  # Estimate!!Total:!!Male:!!80 to 84 years
        'B01001_025E': 'male_pop_85_over',  # Estimate!!Total:!!Male:!!85 years and over
        'B01001_026E': 'total_female',  # Estimate!!Total:!!Female:
        'B01001_027E': 'female_pop_0_5',  # Estimate!!Total:!!Female:!!Under 5 years
        'B01001_028E': 'female_pop_5_9',  # Estimate!!Total:!!Female:!!5 to 9 years
        'B01001_029E': 'female_pop_10_14',  # Estimate!!Total:!!Female:!!10 to 14 years
        'B01001_030E': 'female_pop_15_17',  # Estimate!!Total:!!Female:!!15 to 17 years
        'B01001_031E': 'female_pop_18_19',  # Estimate!!Total:!!Female:!!18 and 19 years
        'B01001_032E': 'female_pop_20',  # Estimate!!Total:!!Female:!!20 years
        'B01001_033E': 'female_pop_21',  # Estimate!!Total:!!Female:!!21 years
        'B01001_034E': 'female_pop_22_24',  # Estimate!!Total:!!Female:!!22 to 24 years
        'B01001_035E': 'female_pop_25_29',  # Estimate!!Total:!!Female:!!25 to 29 years
        'B01001_036E': 'female_pop_30_34',  # Estimate!!Total:!!Female:!!30 to 34 years
        'B01001_037E': 'female_pop_35_39',  # Estimate!!Total:!!Female:!!35 to 39 years
        'B01001_038E': 'female_pop_40_44',  # Estimate!!Total:!!Female:!!40 to 44 years
        'B01001_039E': 'female_pop_45_49',  # Estimate!!Total:!!Female:!!45 to 49 years
        'B01001_040E': 'female_pop_50_54',  # Estimate!!Total:!!Female:!!50 to 54 years
        'B01001_041E': 'female_pop_55_59',  # Estimate!!Total:!!Female:!!55 to 59 years
        'B01001_042E': 'female_pop_60_61',  # Estimate!!Total:!!Female:!!60 and 61 years
        'B01001_043E': 'female_pop_62_64',  # Estimate!!Total:!!Female:!!62 to 64 years
        'B01001_044E': 'female_pop_65_66',  # Estimate!!Total:!!Female:!!65 and 66 years
        'B01001_045E': 'female_pop_67_69',  # Estimate!!Total:!!Female:!!67 to 69 years
        'B01001_046E': 'female_pop_70_74',  # Estimate!!Total:!!Female:!!70 to 74 years
        'B01001_047E': 'female_pop_75_79',  # Estimate!!Total:!!Female:!!75 to 79 years
        'B01001_048E': 'female_pop_80_84',  # Estimate!!Total:!!Female:!!80 to 84 years
        'B01001_049E': 'female_pop_85_over',  # Estimate!!Total:!!Female:!!85 years and over
    }
    SUPPORTED_GEOGRAPHIES = {
        'state': 'state',
        'county': 'county',
        'zcta5': 'zip code tabulation area',
        'zcta3': 'zip code tabulation area',
    }

    def __init__(self, fields=None, geography='county'):
        self.fields = fields or CensusBureauACS.FIELDS.keys()
        self.geography = geography

    @classmethod
    def convert_geography(cls, geography):
        return cls.SUPPORTED_GEOGRAPHIES[geography]

    def get_groups(self):
        variable_grouping = defaultdict(lambda: 0)
        for field in self.fields:
            if '_' in field:
                group_ = field.split('_')[0]
                variable_grouping[group_] += 1

        group_w_largest_variables = max(variable_grouping, key=variable_grouping.get)

        new_fields = set()
        for field in self.fields:
            group_ = field.split('_')[0]
            if group_ == group_w_largest_variables:
                new_fields.add(f'group({group_})')
            else:
                new_fields.add(field)

        return list(new_fields)

    def download(self):
        # There is a limit of 50 Variables per request
        if len(self.fields) < 50:
            params = {
                'get': ','.join(self.fields),
                'for': CensusBureauACS.convert_geography(self.geography),
            }
        else:
            params = {
                'get': ','.join(self.get_groups()),
                'for': CensusBureauACS.convert_geography(self.geography),
            }

        raw_response = requests.get(self.BASE_URL, params=params)
        response = raw_response.json()
        header, data = response[0], response[1:]

        df = pd.DataFrame([{k: v for k, v in zip(header, row)} for row in data])
        keep_cols = list(self.fields) + list(
            set(df.columns).intersection(set(['GEO_ID', 'state', 'county', 'zip code tabulation area']))
        )
        return df[keep_cols]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output_file', default='./', type=str, help='Output CSV File Name')
    parser.add_argument(
        '-g',
        '--geography',
        default='county',
        type=str,
        help='Choose state|county|zcta5',
    )
    args = parser.parse_args()

    cb = CensusBureauACS(geography=args.geography.lower())
    results = cb.download()
    results['TYPE'] = args.geography.upper()

    if args.geography.upper() == 'STATE':
        results['GEOID'] = results['state'].copy()
        results.drop(columns=['state', 'GEO_ID'], inplace=True)
        results['ROW_NUM'] = pd.Series(results.index + 1).astype(str)

    elif args.geography.upper() == 'COUNTY':
        results['GEOID'] = results.apply(lambda row: f'{row.state}{row.county}', axis=1)
        results.drop(columns=['state', 'county', 'GEO_ID'], inplace=True)
        results['ROW_NUM'] = pd.Series(results.index + 1).astype(str)

    elif args.geography.upper() == 'ZCTA5':
        results['GEOID'] = results['zip code tabulation area'].copy()
        results.drop(columns=['zip code tabulation area', 'GEO_ID'], inplace=True)
        results['ROW_NUM'] = pd.Series(results.index + 1).astype(str)

    elif args.geography.upper() == 'ZCTA3':
        non_numerics = ['NAME', 'GEOID', 'TYPE', 'ROW_NUM']

        results['NAME'] = results['NAME'].apply(lambda x: zcta5_to_zcta3(x))
        results['GEOID'] = results['zip code tabulation area'].apply(lambda x: x[:3])
        results['ROW_NUM'] = pd.Series(results.index + 1).apply(lambda x: f'{x}|')
        results.drop(columns=['zip code tabulation area', 'GEO_ID'], inplace=True)

        for col in results.columns:
            if col not in non_numerics:
                results[col] = results[col].apply(lambda x: float(x))

        results = results.groupby(['NAME', 'GEOID', 'TYPE']).sum().reset_index()

    results.to_csv(args.output_file, index=None)
