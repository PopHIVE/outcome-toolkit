import dagster as dg

from ..base.assets import valid_soc_mids_asset
from .assets import (
    hv_soc_v1_data_delivery_asset,
    # hv_soc_v1_raw_df_asset,
    # hv_soc_v1_clean_df_asset,
    # hv_soc_v1_bins_clean_df_asset,
    # hv_soc_v1_aggregated_table,
    # soc_generate_moving_avg_cols_v1,
    # load_moving_avgs_hv_soc_bins_rank_v1
)

# Create a partitioned asset job
hv_soc_v1_monthly_job = dg.define_asset_job(
    name="hv_soc_v1_monthly_job",
    selection=[
        valid_soc_mids_asset,
        hv_soc_v1_data_delivery_asset, 
        # hv_soc_v1_raw_df_asset,
        # hv_soc_v1_clean_df_asset,
        # hv_soc_v1_bins_clean_df_asset,
        # hv_soc_v1_aggregated_table,
        # soc_generate_moving_avg_cols_v1,
        # load_moving_avgs_hv_soc_bins_rank_v1
    ],
)