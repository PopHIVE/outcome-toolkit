import geopandas as gpd
import pandas as pd
from typing import Set, Tuple


def miles_to_meters(miles: float) -> float:
    """Convert Miles to Meters"""
    return miles * 1609.344


def meters_to_miles(meters: float) -> float:
    """Convert Meters to Miles"""
    return meters * 0.0006213712


def generate_adjacency_edge_list(
    gdf: gpd.GeoDataFrame, max_distance_miles: float = 1.0, base_column: str = 'MID'
) -> Set[Tuple]:
    """
    Generates an Adjacency Edge List for geometries that are within max_distance_miles of eachother. This function
    converts the geodataframe to the CRS=ESRI:102003 and buffers on max_distance_meters / 2.0 to form intersections.
    It returns a set of tuples (base_column_left, base_column_right, distance_m).

    Parameters
    ----------
    gdf: gpd.GeoDataFrame
    max_distance_miles: float
    base_column: str

    Returns
    -------

    """
    max_distance_meters = miles_to_meters(max_distance_miles)

    # Convert to Meters
    gdf_meters = gdf.to_crs('ESRI:102003')
    gdf_meters['geometry_meters'] = gdf_meters['geometry']
    gdf_meters['geometry'] = gdf_meters['geometry'].buffer(max_distance_meters / 2.0)

    # Spatial Join with Itself
    intersections = gdf_meters.sjoin(gdf_meters, how='inner')
    intersections['distance_m'] = intersections['geometry_meters_left'].distance(
        intersections['geometry_meters_right']
    )

    # Yield Edge List
    edge_list = set()
    for index, row in intersections.iterrows():
        mid, adjacent_mid = row[f'{base_column}_left'], row[f'{base_column}_right']
        distance = row['distance_m']
        if mid != adjacent_mid:
            edge_list.add((mid, adjacent_mid, distance))

    df = pd.DataFrame(edge_list, columns=['MID', 'ADJACENT_MID', 'DISTANCE'])
    return df
