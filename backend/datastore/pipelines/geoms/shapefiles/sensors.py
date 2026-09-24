import dagster as dg
from typing import List, Dict
from .jobs import census_geoms_job
from datastore.utils.serialize import dict_to_partition_key
from .partitions import CENSUS_GEOMS_PARTITIONS

def get_census_geoms_files() -> List[Dict[str, str]]:
    """ Functrion to generate list of Demographic Profile Files.

    Returns
    -------
    List[Dict[str, str]]
    """

    discovered_census_geoms_files = [
        {"data_release": "2020-01", "relative_path": "cb_2020_us_county_500k.zip", "geo_type": "COUNTY", "geoid_col": "GEOID", "affgeoid_col": "AFFGEOID", "data_provider": "Census Bureau"},
        {"data_release": "2020-01", "relative_path": "cb_2020_us_state_500k.zip", "geo_type": "STATE", "geoid_col": "GEOID", "affgeoid_col": "AFFGEOID", "data_provider": "Census Bureau"},
        {"data_release": "2020-01", "relative_path": "cb_2020_us_zcta3_500k.shp.zip", "geo_type": "ZCTA3", "geoid_col": "GEOID", "affgeoid_col": "AFFGEOID", "data_provider": "Census Bureau"},
        {"data_release": "2020-01", "relative_path": "cb_2020_us_zcta520_500k.zip", "geo_type": "ZCTA5", "geoid_col": "GEOID20", "affgeoid_col": "AFFGEOID20", "data_provider": "Census Bureau"},
    ]

    return discovered_census_geoms_files


@dg.sensor(
    job=census_geoms_job,
    minimum_interval_seconds=300,
    default_status=dg.DefaultSensorStatus.RUNNING
)
def detect_census_geoms_partitions(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    """ Generate the NEMSIS Alcohol Partitions.

    Parameters
    ----------
    context : dg.SensorEvaluationContext

    Returns
    -------
    dg.SensorResult
    """

    # Get Discovered Files
    discovered_census_geoms_files = get_census_geoms_files()

    # Generate Run Requests
    run_requests = [
        dg.RunRequest(
            run_key=dict_to_partition_key(file_info),
            partition_key=dict_to_partition_key(file_info)
        )
        for file_info in discovered_census_geoms_files
    ]

    # Generate Dynamic Partition Requests
    dynamic_partition_requests = [
        CENSUS_GEOMS_PARTITIONS.build_add_request([dict_to_partition_key(file_info) for file_info in discovered_census_geoms_files])
    ]
    
    return dg.SensorResult(
        run_requests=run_requests,
        dynamic_partitions_requests=dynamic_partition_requests,
    )
