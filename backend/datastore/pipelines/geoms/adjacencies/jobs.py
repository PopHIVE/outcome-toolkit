import dagster as dg
from .assets import (
    census_adjacency_edge_list_clean_df_asset,
    census_adjacency_edge_list_clean_table_asset,
    adjacency_edge_list_exemptions
)


census_adjacency_edge_list_job = dg.define_asset_job(
    name="census_adjacency_edge_list_job",
    selection=[
        census_adjacency_edge_list_clean_df_asset,
        adjacency_edge_list_exemptions,
        census_adjacency_edge_list_clean_table_asset
    ]
)

