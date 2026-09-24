import argparse
import requests
import pandas as pd
from app.utilities.identifiers import zcta5_to_zcta3


class CensusBureau:
    BASE_URL = 'https://api.census.gov/data/2020/dec/dp'
    FIELDS = {
        'NAME': 'name',
        'DP1_0001C': 'total_population',  # Count!!SEX AND AGE!!Total population
        'DP1_0002C': 'pop_0_5',  # Count!!SEX AND AGE!!Total population!!Under 5 years
        'DP1_0003C': 'pop_5_9',  # Count!!SEX AND AGE!!Total population!!5 to 9 years
        'DP1_0004C': 'pop_10_14',  # Count!!SEX AND AGE!!Total population!!10 to 14 years
        'DP1_0005C': 'pop_15_19',  # Count!!SEX AND AGE!!Total population!!15 to 19 years
        'DP1_0006C': 'pop_20_24',  # Count!!SEX AND AGE!!Total population!!20 to 24 years
        'DP1_0007C': 'pop_25_29',  # Count!!SEX AND AGE!!Total population!!25 to 29 years
        'DP1_0008C': 'pop_30_34',  # Count!!SEX AND AGE!!Total population!!30 to 34 years
        'DP1_0009C': 'pop_35_39',  # Count!!SEX AND AGE!!Total population!!35 to 39 years
        'DP1_0010C': 'pop_40_44',  # Count!!SEX AND AGE!!Total population!!40 to 44 years
        'DP1_0011C': 'pop_45_49',  # Count!!SEX AND AGE!!Total population!!45 to 49 years
        'DP1_0012C': 'pop_50_54',  # Count!!SEX AND AGE!!Total population!!50 to 54 years
        'DP1_0013C': 'pop_55_59',  # Count!!SEX AND AGE!!Total population!!55 to 59 years
        'DP1_0014C': 'pop_60_64',  # Count!!SEX AND AGE!!Total population!!60 to 64 years
        'DP1_0015C': 'pop_65_69',  # Count!!SEX AND AGE!!Total population!!65 to 69 years
        'DP1_0016C': 'pop_70_74',  # Count!!SEX AND AGE!!Total population!!70 to 74 years
        'DP1_0017C': 'pop_75_79',  # Count!!SEX AND AGE!!Total population!!75 to 79 years
        'DP1_0018C': 'pop_80_84',  # Count!!SEX AND AGE!!Total population!!80 to 84 years
        'DP1_0019C': 'pop_85_over',  # Count!!SEX AND AGE!!Total population!!85 years and over
        'DP1_0025C': 'male_population',  # Count!!SEX AND AGE!!Male population
        'DP1_0049C': 'female_population',  # Count!!SEX AND AGE!!Female population
        # SOC Related Columns
        'DP1_0053C': 'female_pop_15_19',  # Count!!SEX AND AGE!!Female population!!15 to 19 years
        'DP1_0054C': 'female_pop_20_24',  # Count!!SEX AND AGE!!Female population!!20 to 24 years
        'DP1_0055C': 'female_pop_25_29',  # Count!!SEX AND AGE!!Female population!!25 to 29 years
        'DP1_0056C': 'female_pop_30_34',  # Count!!SEX AND AGE!!Female population!!30 to 34 years
        'DP1_0057C': 'female_pop_35_39',  # Count!!SEX AND AGE!!Female population!!35 to 39 years
        'DP1_0058C': 'female_pop_40_44',  # Count!!SEX AND AGE!!Female population!!40 to 44 years
        'DP1_0059C': 'female_pop_45_49',  # Count!!SEX AND AGE!!Female population!!45 to 49 years
        'DP1_0078C': 'pop_white',  # Count!!RACE!!Total population!!One Race!!White
        'DP1_0079C': 'pop_black',  # Count!!RACE!!Total population!!One Race!!Black or African American
        'DP1_0080C': 'pop_american_indian',  # Count!!RACE!!Total population!!One Race!!American Indian and Alaska Native
        'DP1_0081C': 'pop_asian',  # Count!!RACE!!Total population!!One Race!!Asian
        'DP1_0082C': 'pop_pacific_isl',  # Count!!RACE!!Total population!!One Race!!Native Hawaiian and Other Pacific Islander
        'DP1_0083C': 'pop_other',  # Count!!RACE!!Total population!!One Race!!Some Other Race
        'DP1_0084C': 'pop_multi',  # Count!!RACE!!Total population!!Two or More Races
    }
    SUPPORTED_GEOGRAPHIES = {
        'state': 'state',
        'county': 'county',
        'zcta5': 'zip code tabulation area',
        'zcta3': 'zip code tabulation area',
    }

    def __init__(self, fields=None, geography='county'):
        self.fields = fields or CensusBureau.FIELDS.keys()
        self.geography = geography

    @classmethod
    def convert_geography(cls, geography):
        return cls.SUPPORTED_GEOGRAPHIES[geography]

    def download(self):
        params = {
            'get': ','.join(self.fields),
            'for': CensusBureau.convert_geography(self.geography),
        }
        response = requests.get(self.BASE_URL, params=params).json()
        header, data = response[0], response[1:]
        df = pd.DataFrame([{k: v for k, v in zip(header, row)} for row in data])
        return df


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

    cb = CensusBureau(geography=args.geography.lower())
    results = cb.download()
    results['TYPE'] = args.geography.upper()

    if args.geography.upper() == 'STATE':
        results['GEOID'] = results['state'].copy()
        results.drop(columns=['state'], inplace=True)
        results['ROW_NUM'] = pd.Series(results.index + 1).astype(str)

    elif args.geography.upper() == 'COUNTY':
        results['GEOID'] = results.apply(lambda row: f'{row.state}{row.county}', axis=1)
        results.drop(columns=['state', 'county'], inplace=True)
        results['ROW_NUM'] = pd.Series(results.index + 1).astype(str)

    elif args.geography.upper() == 'ZCTA5':
        results['GEOID'] = results['zip code tabulation area'].copy()
        results.drop(columns=['zip code tabulation area'], inplace=True)
        results['ROW_NUM'] = pd.Series(results.index + 1).astype(str)

    elif args.geography.upper() == 'ZCTA3':
        non_numerics = ['NAME', 'GEOID', 'TYPE', 'ROW_NUM']
        results['NAME'] = results['NAME'].apply(lambda x: zcta5_to_zcta3(x))
        results['GEOID'] = results['zip code tabulation area'].apply(lambda x: x[:3])
        results['TYPE'] = 'ZCTA3'
        results['ROW_NUM'] = pd.Series(results.index + 1).apply(lambda x: f'{x}|')
        results.drop(columns=['zip code tabulation area'], inplace=True)

        for col in results.columns:
            if col not in non_numerics:
                if col[-1] == 'C':
                    results[col] = results[col].apply(lambda x: int(x))
                else:
                    results[col] = results[col].apply(lambda x: float(x))

        results = results.groupby(['NAME', 'GEOID', 'TYPE']).sum().reset_index()

    results.to_csv(args.output_file, index=None)
