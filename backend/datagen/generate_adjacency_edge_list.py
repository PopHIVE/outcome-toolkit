import argparse
import geopandas as gpd
from app.utilities.identifiers import mid_from_geoid
from app.utilities.geo_utils import generate_adjacency_edge_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', type=str, help='Input Demographic File')
    parser.add_argument('-g', '--geography', type=str, help='Geography')
    parser.add_argument('-e', '--geoid', type=str, default='GEOID', help='GEOID Col')
    parser.add_argument('-d', '--distance', type=float, default=0.5, help='Max Distance Miles')
    parser.add_argument('-o', '--output_file', type=str, help='Output CSV File')
    args = parser.parse_args()

    zipfile = f'zip://{args.input_file}'
    geos = gpd.read_file(zipfile)
    geos['MID'] = geos[args.geoid].apply(lambda x: mid_from_geoid(x, args.geography))

    edge_list = generate_adjacency_edge_list(geos, args.distance, base_column='MID')
    edge_list['TYPE'] = args.geography
    edge_list.to_csv(args.output_file, index=None)
