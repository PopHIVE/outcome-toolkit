from typing import List, Any
import dagster as dg
from .factories import table_asset_factory
from db.datasets.core import Area
from db.datasets.alcohol.alcohol_tables import NEMSISAlcohol, NEMSISAlcohol_v2
from db.datasets.opioid.opioid_tables import NEMSISOpioid, NEMSISOpioid_v2, Bins
from db.datasets.ascvd.ascvd_tables import ASCVDScore, ASCVDScore_v2
from db.datasets.demographics.demographics_tables import CBACSEstimates, CBDemographics
from db.datasets.geoms.geoms_tables import CBGeom, CBGeomIndex, AdjacencyEdgeList
from db.datasets.soc.soc_tables import RawSOCData, AggregatedSOCV1, AggregatedSOCV2
from db.datasets.trendlines.trendline_tables import Trendlines
from db.datasets.associations.association_tables import ProjectAreaAssociation, UserProjectAssociation
from db.datasets.target_payouts.target_payout_tables import TargetPayoutRate
from db.datasets.metrics.payout_metrics_tables import ProjectMeasurement, MidMetric
from db.datasets.projects.project_tables import Project
from db.datasets.users.users_tables import User


# Area + Bins Table
create_area_table_asset = table_asset_factory(
    tbl=Area,
    asset_key='create_area_table_asset',
    group_name='configs'
)

create_bins_table_asset = table_asset_factory(
    tbl=Bins,
    asset_key='create_bins_table_asset',
    group_name='configs'
)

# Alcohol Tables
create_alcohol_v1_table_asset = table_asset_factory(
    tbl=NEMSISAlcohol,
    asset_key='create_alcohol_v1_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

create_alcohol_v2_table_asset = table_asset_factory(
    tbl=NEMSISAlcohol_v2,
    asset_key='create_alcohol_v2_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

# Opioid Tables
create_opioid_v1_table_asset = table_asset_factory(
    tbl=NEMSISOpioid,
    asset_key='create_opioid_v1_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

create_opioid_v2_table_asset = table_asset_factory(
    tbl=NEMSISOpioid_v2,
    asset_key='create_opioid_v2_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

# ASCVD Tables
create_ascvd_v1_table_asset = table_asset_factory(
    tbl=ASCVDScore,
    asset_key='create_ascvd_v1_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

create_ascvd_v2_table_asset = table_asset_factory(
    tbl=ASCVDScore_v2,
    asset_key='create_ascvd_v2_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

# Demographics Tables
create_census_demographics_table_asset = table_asset_factory(
    tbl=CBDemographics,
    asset_key='create_census_demographics_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

create_census_acs_table_asset = table_asset_factory(
    tbl=CBACSEstimates,
    asset_key='create_census_acs_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

# Geoms Tables
create_geoms_table_asset = table_asset_factory(
    tbl=CBGeom,
    asset_key='create_geoms_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

create_geoms_index_table_asset = table_asset_factory(
    tbl=CBGeomIndex,
    asset_key='create_geoms_index_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

create_geoms_adjacency_table_asset = table_asset_factory(
    tbl=AdjacencyEdgeList,
    asset_key='create_geoms_adjacency_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

# SOC Tables
create_soc_raw_table_asset = table_asset_factory(
    tbl=RawSOCData,
    asset_key='create_soc_raw_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

create_soc_v1_table_asset = table_asset_factory(
    tbl=AggregatedSOCV1,
    asset_key='create_soc_v1_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

create_soc_v2_table_asset = table_asset_factory(
    tbl=AggregatedSOCV2,
    asset_key='create_soc_v2_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

# Trendlines Tables
create_trendlines_table_asset = table_asset_factory(
    tbl=Trendlines,
    asset_key='create_trendlines_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

# Project Related Tables
create_user_table_asset = table_asset_factory(
    tbl=User,
    asset_key='create_user_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

create_mid_metric_table_asset = table_asset_factory(
    tbl=MidMetric,
    asset_key='create_mid_metric_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

create_project_measurement_table_asset = table_asset_factory(
    tbl=ProjectMeasurement,
    asset_key='create_project_measurement_table_asset',
    group_name='configs',
    deps=[create_area_table_asset]
)

create_user_project_association_table_asset = table_asset_factory(
    tbl=UserProjectAssociation,
    asset_key='create_user_project_association_table_asset',
    group_name='configs',
    deps=[create_user_table_asset, create_area_table_asset]
)

create_project_area_association_table_asset = table_asset_factory(
    tbl=ProjectAreaAssociation,
    asset_key='create_project_area_association_table_asset',
    group_name='configs',
    deps=[create_user_table_asset, create_area_table_asset]
)

create_target_payout_table_asset = table_asset_factory(
    tbl=TargetPayoutRate,
    asset_key='create_target_payout_table_asset',
    group_name='configs',
    deps=[create_user_table_asset, create_area_table_asset]
)

create_project_table_asset = table_asset_factory(
    tbl=Project,
    asset_key='create_project_table_asset',
    group_name='configs',
    deps=[create_user_table_asset, create_area_table_asset]
)
