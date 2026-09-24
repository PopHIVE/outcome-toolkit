import dagster as dg
from .assets import (
    nemsis_alcohol_v2_data_delivery_asset,
    # nemsis_alcohol_v2_raw_df_asset,
    # nemsis_alcohol_v2_clean_df_asset,
    # nemsis_alcohol_monthly_table,
    nemsis_alcohol_v2_bins_data_delivery_asset,
    # nemsis_alcohol_v2_bins_clean_df_asset,
    nemsis_alcohol_v2_trendlines_data_delivery_asset,
    # nemsis_alcohol_v2_trendlines_clean_df_asset,
    # nemsis_alcohol_trendlines_table,
    # nemsis_alcohol_v2_bins_table_asset,
    # load_moving_avgs_nemsis_alcohol_bins_rank_v2,
    # load_moving_avgs_nemsis_alcohol_bins_v2,
    # fill_nemsis_alcohol_v2,
    # load_moving_avgs_nemsis_alcohol_v2
)

# Create a partitioned asset job
nemsis_alcohol_v2_monthly_job = dg.define_asset_job(
    name="nemsis_alcohol_v2_monthly_job",
    selection=[
        nemsis_alcohol_v2_data_delivery_asset, 
        # nemsis_alcohol_v2_raw_df_asset,
        # nemsis_alcohol_v2_clean_df_asset,
        # nemsis_alcohol_monthly_table,
        # fill_nemsis_alcohol_v2,
        # load_moving_avgs_nemsis_alcohol_v2
    ],
)

# Create a partitioned asset job
nemsis_alcohol_v2_bins_monthly_job = dg.define_asset_job(
    name="nemsis_alcohol_v2_bins_monthly_job",
    selection=[
        nemsis_alcohol_v2_bins_data_delivery_asset,
        # nemsis_alcohol_v2_bins_clean_df_asset,
        # nemsis_alcohol_v2_bins_table_asset,
        # load_moving_avgs_nemsis_alcohol_bins_v2,
        # load_moving_avgs_nemsis_alcohol_bins_rank_v2,
    ],
)

# Create a partitioned asset job
nemsis_alcohol_v2_trendlines_job = dg.define_asset_job(
    name="nemsis_alcohol_v2_trendlines_job",
    selection=[
        nemsis_alcohol_v2_trendlines_data_delivery_asset,
        # nemsis_alcohol_v2_trendlines_clean_df_asset,
        # nemsis_alcohol_trendlines_table
    ],
)