import dagster as dg
from .assets import (
    census_geoms_clean_df_asset, 
    census_geoms_clean_table_asset,
    census_geoid_index_clean_df_asset,
    census_geoid_index_table_asset
)


census_geoms_job = dg.define_asset_job(
    name="census_geoms_job",
    selection=[
        census_geoms_clean_df_asset, 
        census_geoms_clean_table_asset,
        census_geoid_index_clean_df_asset,
        census_geoid_index_table_asset
    ]
)

