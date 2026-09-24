import dagster as dg
# from ..nemsis_alcohol_monthly_v2.assets import (
#     nemsis_alcohol_monthly_table,
# )

from .assets import (
    nemsis_alcohol_v1_data_delivery_asset,
    # nemsis_alcohol_v1_raw_df_asset,
    # nemsis_alcohol_v1_clean_df_asset,
    nemsis_alcohol_v1_bins_data_delivery_asset,
    # nemsis_alcohol_v1_bins_clean_df_asset,
    # nemsis_alcohol_table,
    # nemsis_alcohol_v1_bins_table_asset,
    # fill_nemsis_alcohol_v1,
    # load_moving_avgs_nemsis_alcohol_v1,
)
from ..base.assets import valid_alcohol_mids_asset

# Create a partitioned asset job
nemsis_alcohol_v1_monthly_job = dg.define_asset_job(
    name="nemsis_alcohol_v1_monthly_job",
    selection=[
        valid_alcohol_mids_asset,
        nemsis_alcohol_v1_data_delivery_asset, 
        # nemsis_alcohol_v1_raw_df_asset,
        # nemsis_alcohol_v1_clean_df_asset,
        # nemsis_alcohol_monthly_table,
        # nemsis_alcohol_table,
        # fill_nemsis_alcohol_v1,
        # load_moving_avgs_nemsis_alcohol_v1
    ],
)

# Create a partitioned asset job
nemsis_alcohol_v1_bins_monthly_job = dg.define_asset_job(
    name="nemsis_alcohol_v1_bins_monthly_job",
    selection=[
        nemsis_alcohol_v1_bins_data_delivery_asset,
        # nemsis_alcohol_v1_bins_clean_df_asset,
        # nemsis_alcohol_v1_bins_table_asset
    ],
)