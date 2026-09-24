import dagster as dg
from .assets import census_demographic_profile_clean_df_asset, census_demographic_profile_clean_table_asset


census_demographic_profile_job = dg.define_asset_job(
    name="census_demographic_profile_job",
    selection=[
        census_demographic_profile_clean_df_asset, 
        census_demographic_profile_clean_table_asset
    ]
)

