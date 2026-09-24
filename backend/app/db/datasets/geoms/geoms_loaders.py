import numpy as np
import pandas as pd
import geopandas as gpd
from typing import List
from sqlalchemy.engine import Row
from app.configs.consts import ValidGeographies, Replacements
from app.utilities.identifiers import mid_from_geoid, zcta5_to_zcta3
from db.datasets.geoms.geoms_tables import AdjacencyEdgeList, CBGeomIndex, CBGeom
from app.db.database import registry


@registry.register('load_adjacency_list', version='2.0')
def load_adjacency_list(input_file: str) -> List[Row]:
    """ETL Scripts to Load Adjacency Edge List Data.

    Parameters
    ----------
    input_file : str

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    df = pd.read_csv(input_file)
    records = []
    for index, row in df.iterrows():
        records.append(
            AdjacencyEdgeList(
                mid=row.MID,
                adjacent_mid=row.ADJACENT_MID,
                distance=row.DISTANCE,
                type=row.TYPE,
            )
        )

    return records


@registry.register('load_adjacency_exemptions', version='1.0')
def load_adjacency_exemptions(local_input_file: str) -> List[Row]:
    """ETL Scripts to Load Adjacency Edge List Exemptions.

    Parameters
    ----------
    local_input_file : str

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    df = pd.read_csv(local_input_file)
    records = []
    for index, row in df.iterrows():
        records.append(AdjacencyEdgeList(mid=row.MID, adjacent_mid=row.ADJACENT_MID, distance=-1, type=row.TYPE))
        records.append(AdjacencyEdgeList(mid=row.ADJACENT_MID, adjacent_mid=row.MID, distance=-1, type=row.TYPE))

    return records


@registry.register('construct_geoid_index', version='1.0')
def construct_geoid_index(states_geos_file: str, county_geos_file: str, relationship_file: str) -> List[Row]:
    """ETL Scripts to Construct County/ZCTA5 Intersections.

    Parameters
    ----------
    states_geos_file : str
        States Geometries ShapeFile
    county_geos_file : str
        County Geometries ShapeFile
    relationship_file : str
        The Census Intersections/Crosstab File repreenting intersections.

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    states = gpd.read_file(f'zip://{states_geos_file}', dtype=str)
    counties = gpd.read_file(f'zip://{county_geos_file}', dtype=str)
    zctas = pd.read_csv(relationship_file, dtype=str, sep='|')

    # Populate index with State Info
    state_index = {}
    for idx, row in states.iterrows():
        state_index[row.STATEFP] = {
            'STATE_GEOID': row.GEOID,
            'STATE_NAME': row.NAME,
            'STATE_USPS': row.STUSPS,
            'STATE_FIPS': row.STATEFP,
            'STATE_MID': mid_from_geoid(row.GEOID, ValidGeographies.STATE),
            'STATE_ROW_NUM': idx + 1,
        }

    # Populate a county Index
    county_index = {}
    for idx, row in counties.iterrows():
        county_index[row.GEOID] = {
            'COUNTY_GEOID': row.GEOID,
            'COUNTY_FIPS': row.COUNTYFP,
            'COUNTY_NAME': row.NAME,
            'COUNTY_NAMELSAD': row.NAMELSAD,
            'COUNTY_MID': mid_from_geoid(row.GEOID, ValidGeographies.COUNTY),
            'COUNTY_ROW_NUM': idx + 1,
        }
        county_index[row.GEOID].update(state_index[row.STATEFP])

    zcta_index = []
    for idx, row in zctas.iterrows():
        new_row = {
            'ZCTA5_GEOID': row.GEOID_ZCTA5_20,
            'ZCTA5_NAME': row.NAMELSAD_ZCTA5_20,
            'ZCTA5_MID': mid_from_geoid(row.GEOID_ZCTA5_20, ValidGeographies.ZCTA5),
            'ZCTA3_GEOID': row.GEOID_ZCTA5_20[:3] if not pd.isna(row.GEOID_ZCTA5_20) else row.GEOID_ZCTA5_20,
            'ZCTA3_NAME': zcta5_to_zcta3(row.NAMELSAD_ZCTA5_20)
            if not pd.isna(row.GEOID_ZCTA5_20)
            else row.NAMELSAD_ZCTA5_20,
            'ZCTA5_ROW_NUM': idx + 1,
        }
        new_row.update(county_index[row.GEOID_COUNTY_20])
        new_row['ZCTA3_MID'] = mid_from_geoid(new_row['ZCTA3_GEOID'], ValidGeographies.ZCTA3)
        zcta_index.append(new_row.copy())

    index_df = pd.DataFrame(zcta_index)

    records = []

    for index, row in index_df.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        record = CBGeomIndex(
            zcta3_name=row.ZCTA3_NAME,
            zcta3_geoid=row.ZCTA3_GEOID,
            zcta3_mid=row.ZCTA3_MID,
            zcta5_name=row.ZCTA5_NAME,
            zcta5_geoid=row.ZCTA5_GEOID,
            zcta5_mid=row.ZCTA5_MID,
            county_namelsad=row.COUNTY_NAMELSAD,
            county_name=row.COUNTY_NAME,
            county_fips=row.COUNTY_FIPS,
            county_geoid=row.COUNTY_GEOID,
            county_mid=row.COUNTY_MID,
            state_fips=row.STATE_FIPS,
            state_usps=row.STATE_USPS,
            state_name=row.STATE_NAME,
            state_geoid=row.STATE_GEOID,
            state_mid=row.STATE_MID,
            source_file=f'{states_geos_file}|{county_geos_file}|{relationship_file}',
            row_num=f'{row.STATE_ROW_NUM}|{row.COUNTY_ROW_NUM}|{row.ZCTA5_ROW_NUM}',
        )
        records.append(record)

    return records


@registry.register('load_zipped_census_geos', version='1.0')
def load_zipped_census_geos(
    input_file: str,
    geography: str,
    geoid_col: str = 'GEOID',
    affgeoid_col: str = 'AFFGEOID',
) -> List[Row]:
    """_summary_

    Parameters
    ----------
    input_file : str
    geography : str
    geoid_col : str, optional
        GEOID Column. Census Changes the Column Name for some ShapeFiles, by default 'GEOID'
    affgeoid_col : str, optional
        AFFGEOID Column. Varies Based on which SHapeFile, by default 'AFFGEOID'

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    zipfile = f'zip://{input_file}'
    gdf = gpd.read_file(zipfile)
    records = []

    if 'row_num' not in gdf.columns:
        gdf['row_num'] = gdf.index + 1

    for index, row in gdf.replace({np.nan: None}).iterrows():
        record = CBGeom(
            mid=f'{geography} {row[geoid_col]}',
            geoid=row[geoid_col],
            affgeoid=row[affgeoid_col],
            geometry=row.geometry.wkt,
            type=geography,
            source_file=input_file,
            row_num=row['row_num'],
        )
        records.append(record)

    return records
