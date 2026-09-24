import dagster as dg
from .assets import census_acs_clean_df_asset, census_acs_clean_table_asset


census_acs_job = dg.define_asset_job(
    name="census_acs_job",
    selection=[
        census_acs_clean_df_asset, census_acs_clean_table_asset
    ]
)

