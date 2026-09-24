import os
import dagster as dg
import pandas as pd
import geopandas as gpd
import numpy as np
from typing import Any
from datetime import datetime
from .partitions import CENSUS_GEOMS_PARTITIONS
from datastore.utils.consts import Replacements
from datastore.models.data_source import CensusGeomsDataDelivery
from datastore.utils.serialize import (
    partition_key_to_dict
)
from datastore.resources.postgres_resource import PostgresConnectionResource
from db.datasets.geoms.geoms_tables import CBGeom, CBGeomIndex
from datastore.utils.serialize import df_to_metadata
from datastore.utils.mid_generation_utils import mid_from_geoid, zcta5_to_zcta3
from datastore.pipelines.tables.assets import create_geoms_table_asset, create_geoms_index_table_asset


@dg.asset(
    deps=[
        create_geoms_table_asset
    ],
    partitions_def=CENSUS_GEOMS_PARTITIONS,
    group_name="Geoms",
    automation_condition=dg.AutomationCondition.eager()
)
def census_geoms_clean_df_asset(context: dg.AssetExecutionContext) -> dg.Output[pd.DataFrame]:
    """ Load Demographic Profile

    Parameters
    ----------
    context : dg.AssetExecutionContext
    
    Returns
    -------
    dg.Output[pd.DataFrame]
    """

    partition_key = context.partition_key
    data_delivery = CensusGeomsDataDelivery(**partition_key_to_dict(partition_key))

    results = gpd.read_file(f"zip://{data_delivery.get_full_path()}", dtype=str)
    results['MID'] = results[data_delivery.geoid_col].apply(
        lambda geoid: f"{data_delivery.geo_type} {geoid}" if not ((geoid is None) or (pd.isna(geoid))) else None
    )

    records = []
    for index, row in results.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        record = {
            'mid': row.MID,
            'geoid': row[data_delivery.geoid_col],
            'affgeoid': row[data_delivery.affgeoid_col],
            'geometry': row.geometry.wkt,
            'type': data_delivery.geo_type,
            'row_num': index + 1,
            'source_file': data_delivery.get_filename(),
            'data_release': data_delivery.data_release,
            'data_provider': data_delivery.data_provider
        }
        records.append(record)

    df = pd.DataFrame(records)
    return dg.Output(df, metadata=df_to_metadata(df))


@dg.asset(
    ins={
        "clean_dfs": dg.AssetIn(census_geoms_clean_df_asset.key, partition_mapping=dg.AllPartitionMapping()),
    },
    group_name='Geoms',
    automation_condition=dg.AutomationCondition.eager()
)
def census_geoms_clean_table_asset(
    db: PostgresConnectionResource,
    clean_dfs: Any
) -> None:
    """
    This function creates and populates the RawDemographicsData in the database.

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

    CBGeom.__table__.drop(bind=db.engine, checkfirst=True)
    CBGeom.__table__.create(bind=db.engine, checkfirst=True)

    records = []

    for _, row in df.iterrows():
        records.append(CBGeom(**row.to_dict()))

    with db.session() as session, session.begin():
        for record in records:
            session.merge(record)
        session.commit()

#######################################################################################



@dg.asset(
    deps=[
        create_geoms_index_table_asset
    ],
    group_name="Geoms",
    automation_condition=dg.AutomationCondition.eager()
)
def census_geoid_index_clean_df_asset() -> dg.Output[pd.DataFrame]:
    """_summary_

    Returns
    -------
    dg.Output[pd.DataFrame]
        _description_
    """
    
    states_geos_file = os.path.join(os.environ['DATA_BUNDLE_DIR'], 'cb_2020_us_state_500k.zip')
    county_geos_file = os.path.join(os.environ['DATA_BUNDLE_DIR'], 'cb_2020_us_county_500k.zip')
    relationship_file = os.path.join(os.environ['DATA_BUNDLE_DIR'], 'tab20_zcta520_county20_natl.txt')

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
            'STATE_MID': mid_from_geoid(row.GEOID, 'STATE'),
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
            'COUNTY_MID': mid_from_geoid(row.GEOID, 'COUNTY'),
            'COUNTY_ROW_NUM': idx + 1,
        }
        county_index[row.GEOID].update(state_index[row.STATEFP])

    zcta_index = []
    for idx, row in zctas.iterrows():
        new_row = {
            'ZCTA5_GEOID': row.GEOID_ZCTA5_20,
            'ZCTA5_NAME': row.NAMELSAD_ZCTA5_20,
            'ZCTA5_MID': mid_from_geoid(row.GEOID_ZCTA5_20, 'ZCTA5'),
            'ZCTA3_GEOID': row.GEOID_ZCTA5_20[:3] if not pd.isna(row.GEOID_ZCTA5_20) else row.GEOID_ZCTA5_20,
            'ZCTA3_NAME': zcta5_to_zcta3(row.NAMELSAD_ZCTA5_20)
            if not pd.isna(row.GEOID_ZCTA5_20)
            else row.NAMELSAD_ZCTA5_20,
            'ZCTA5_ROW_NUM': idx + 1,
        }
        new_row.update(county_index[row.GEOID_COUNTY_20])
        new_row['ZCTA3_MID'] = mid_from_geoid(new_row['ZCTA3_GEOID'], 'ZCTA3')
        zcta_index.append(new_row.copy())

    index_df = pd.DataFrame(zcta_index)

    records = []

    for index, row in index_df.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        record = {
            'zcta3_name': row.ZCTA3_NAME,
            'zcta3_geoid': row.ZCTA3_GEOID,
            'zcta3_mid': row.ZCTA3_MID,
            'zcta5_name': row.ZCTA5_NAME,
            'zcta5_geoid': row.ZCTA5_GEOID,
            'zcta5_mid': row.ZCTA5_MID,
            'county_namelsad': row.COUNTY_NAMELSAD,
            'county_name': row.COUNTY_NAME,
            'county_fips': row.COUNTY_FIPS,
            'county_geoid': row.COUNTY_GEOID,
            'county_mid': row.COUNTY_MID,
            'state_fips': row.STATE_FIPS,
            'state_usps': row.STATE_USPS,
            'state_name': row.STATE_NAME,
            'state_geoid': row.STATE_GEOID,
            'state_mid': row.STATE_MID,
            'source_file': f'{states_geos_file}|{county_geos_file}|{relationship_file}',
            'row_num': f'{row.STATE_ROW_NUM}|{row.COUNTY_ROW_NUM}|{row.ZCTA5_ROW_NUM}',
            'data_release': '2020',
            'data_provider': 'CEnsus Bureau Relationship File'
        }
        records.append(record)

    df = pd.DataFrame(records)
    return dg.Output(df, metadata=df_to_metadata(df))


@dg.asset(
    ins={"clean_df": dg.AssetIn(census_geoid_index_clean_df_asset.key)},
    group_name="Geoms",
    automation_condition=dg.AutomationCondition.eager()
)
def census_geoid_index_table_asset(db: PostgresConnectionResource, clean_df: pd.DataFrame) -> None:
    """_summary_

    Parameters
    ----------
    db : PostgresConnectionResource
        _description_
    """
    
    CBGeomIndex.__table__.drop(bind=db.engine, checkfirst=True)
    CBGeomIndex.__table__.create(bind=db.engine, checkfirst=True)

    records = []

    for _, row in clean_df.iterrows():
        records.append(CBGeomIndex(**row.to_dict()))

    with db.session() as session, session.begin():
        session.bulk_save_objects(records)
        session.commit()