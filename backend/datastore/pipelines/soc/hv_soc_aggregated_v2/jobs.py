import dagster as dg

from .assets import (
    hv_soc_v2_data_delivery_asset,
    # hv_soc_v2_raw_df_asset,
    # hv_soc_v2_clean_df_asset,
    # hv_soc_v2_bins_clean_df_asset,
    # hv_soc_v2_aggregated_table,
    # hv_soc_v2_bins_table_asset,
    # soc_generate_moving_avg_cols_v2,
    # load_moving_avgs_hv_soc_bins_v2,
    # load_moving_avgs_hv_soc_bins_rank_v2,
    # hv_soc_v2_trendlines,
    # hv_soc_v2_trendlines_table
)

# Create a partitioned asset job
hv_soc_v2_monthly_job = dg.define_asset_job(
    name="hv_soc_v2_monthly_job",
    selection=[
        hv_soc_v2_data_delivery_asset, 
        # hv_soc_v2_raw_df_asset,
        # hv_soc_v2_clean_df_asset,
        # hv_soc_v2_bins_clean_df_asset,
        # hv_soc_v2_aggregated_table,
        # hv_soc_v2_bins_table_asset,
        # load_moving_avgs_hv_soc_bins_v2,
        # load_moving_avgs_hv_soc_bins_rank_v2,
        # soc_generate_moving_avg_cols_v2,
        # soc_generate_moving_avg_cols_v2,
        # hv_soc_v2_trendlines,
        # hv_soc_v2_trendlines_table
    ],
)