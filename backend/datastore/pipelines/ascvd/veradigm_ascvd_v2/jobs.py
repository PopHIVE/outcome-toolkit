import dagster as dg

from ..base.assets import valid_ascvd_mids_asset
from .assets import (
    veradigm_ascvd_v1_data_delivery_asset,
    # veradigm_ascvd_v2_raw_df_asset,
    # veradigm_ascvd_v2_clean_df_asset,
    # veradigm_ascvd_v2_bins_clean_df_asset,
    # veradigm_ascvd_v2_aggregated_table,
    # ascvd_generate_moving_avg_v2,
    # moving_avgs_veradigm_ascvd_cols_v2,
    # load_moving_avgs_veradigm_ascvd_bins_rank_v2,
    # load_national_veradigm_ascvd_data_v2_table,
    # load_national_veradigm_ascvd_data_v2
)
from ..veradigm_ascvd_v1.jobs import (
    veradigm_ascvd_v1_data_delivery_asset,
    # veradigm_ascvd_v1_raw_df_asset,
    # veradigm_ascvd_v1_clean_df_asset,
    # veradigm_ascvd_v1_bins_clean_df_asset,
    # veradigm_ascvd_v1_aggregated_table,
    # ascvd_generate_moving_avg_cols_v1,
    # load_moving_avgs_veradigm_ascvd_bins_rank_v1,
    # load_national_veradigm_ascvd_data_v1,
    # load_national_veradigm_ascvd_data_v1_table
)

# Create a partitioned asset job
veradigm_ascvd_v2_monthly_job = dg.define_asset_job(
    name="veradigm_ascvd_v2_monthly_job",
    selection=[
        valid_ascvd_mids_asset,
        veradigm_ascvd_v1_data_delivery_asset,
        # veradigm_ascvd_v2_raw_df_asset,
        # veradigm_ascvd_v2_clean_df_asset,
        # veradigm_ascvd_v2_bins_clean_df_asset,
        # veradigm_ascvd_v2_aggregated_table,
        # load_national_veradigm_ascvd_data_v2_table,
        # load_national_veradigm_ascvd_data_v2,
        # ascvd_generate_moving_avg_v2,
        # moving_avgs_veradigm_ascvd_cols_v2,
        # load_moving_avgs_veradigm_ascvd_bins_rank_v2,
    ],
)

# TODO: Clean This up.
ascvd_all_job = dg.define_asset_job(
    name="ascvd_all_job",
    selection=[
        valid_ascvd_mids_asset,
        veradigm_ascvd_v1_data_delivery_asset,
        # veradigm_ascvd_v2_raw_df_asset,
        # veradigm_ascvd_v2_clean_df_asset,
        # veradigm_ascvd_v2_bins_clean_df_asset,
        # veradigm_ascvd_v2_aggregated_table,
        # load_national_veradigm_ascvd_data_v2_table,
        # load_national_veradigm_ascvd_data_v2,
        # ascvd_generate_moving_avg_v2,
        # moving_avgs_veradigm_ascvd_cols_v2,
        # load_moving_avgs_veradigm_ascvd_bins_rank_v2,
        veradigm_ascvd_v1_data_delivery_asset,
        # veradigm_ascvd_v1_raw_df_asset,
        # veradigm_ascvd_v1_clean_df_asset,
        # veradigm_ascvd_v1_bins_clean_df_asset,
        # veradigm_ascvd_v1_aggregated_table,
        # load_national_veradigm_ascvd_data_v1,
        # load_national_veradigm_ascvd_data_v1_table,
        # ascvd_generate_moving_avg_cols_v1,
        # load_moving_avgs_veradigm_ascvd_bins_rank_v1
    ]
)