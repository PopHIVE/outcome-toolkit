import dagster as dg

from .assets import (
    veradigm_ascvd_v1_data_delivery_asset
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
veradigm_ascvd_v1_monthly_job = dg.define_asset_job(
    name="veradigm_ascvd_v1_monthly_job",
    selection=[
        veradigm_ascvd_v1_data_delivery_asset
        # veradigm_ascvd_v1_raw_df_asset,
        # veradigm_ascvd_v1_clean_df_asset,
        # veradigm_ascvd_v1_bins_clean_df_asset,
        # veradigm_ascvd_v1_aggregated_table,
        # ascvd_generate_moving_avg_cols_v1,
        # load_moving_avgs_veradigm_ascvd_bins_rank_v1,
        # load_national_veradigm_ascvd_data_v1,
        # load_national_veradigm_ascvd_data_v1_table
    ],
)