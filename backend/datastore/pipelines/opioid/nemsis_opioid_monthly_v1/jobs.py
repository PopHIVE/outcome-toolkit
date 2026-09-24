import dagster as dg
# from ..nemsis_opioid_monthly_v2.assets import (
#     nemsis_opioid_monthly_table,
# )

from ..base.assets import valid_opioid_mids_asset
from .assets import (
    nemsis_opioid_v1_data_delivery_asset,
    # nemsis_opioid_v1_raw_df_asset,
    # nemsis_opioid_v1_clean_df_asset,
    nemsis_opioid_v1_bins_data_delivery_asset,
    # nemsis_opioid_v1_bins_clean_df_asset,
    # nemsis_opioid_table,
    # fill_nemsis_opioid_v1,
    # load_moving_avgs_nemsis_opioid_v1,
    # nemsis_opioid_v1_bins_table_asset
)

# Create a partitioned asset job
nemsis_opioid_v1_monthly_job = dg.define_asset_job(
    name="nemsis_opioid_v1_monthly_job",
    selection=[
        valid_opioid_mids_asset,
        nemsis_opioid_v1_data_delivery_asset, 
        # nemsis_opioid_v1_raw_df_asset,
        # nemsis_opioid_v1_clean_df_asset,
        # nemsis_opioid_monthly_table,
        # nemsis_opioid_table,
        # fill_nemsis_opioid_v1,
        # load_moving_avgs_nemsis_opioid_v1
    ],
)

# Create a partitioned asset job
nemsis_opioid_v1_bins_monthly_job = dg.define_asset_job(
    name="nemsis_opioid_v1_bins_monthly_job",
    selection=[
        nemsis_opioid_v1_bins_data_delivery_asset,
        # nemsis_opioid_v1_bins_clean_df_asset,
        # nemsis_opioid_v1_bins_table_asset
    ],
)