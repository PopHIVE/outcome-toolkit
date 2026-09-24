import pandas as pd
import geopandas as gpd
import argparse


def generate_zcta3_geos(input_file: str, output_file: str):
    zipfile = f'zip://{input_file}'
    zcta5 = gpd.read_file(zipfile)
    zcta5['zcta3'] = zcta5['GEOID20'].apply(lambda x: x[:3])
    zcta5['row_num'] = pd.Series(zcta5.index + 1).apply(lambda x: f'{x}|')

    zcta5_subset = zcta5[['zcta3', 'geometry', 'row_num']].copy()

    zcta3 = zcta5_subset.dissolve(by='zcta3', aggfunc='sum').reset_index()
    zcta3['GEOID'] = zcta3['zcta3']
    zcta3['AFFGEOID'] = ''

    zcta3.to_file(filename=output_file, driver='ESRI Shapefile')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', type=str, help='Input ZCTA5 Geos File')
    parser.add_argument('-o', '--output_file', type=str, help='Output ZCTA3 Geos File')
    args = parser.parse_args()

    generate_zcta3_geos(input_file=args.input_file, output_file=args.output_file)
