import dagster as dg
from typing import List, Dict
from .jobs import census_demographic_profile_job
from datastore.utils.serialize import dict_to_partition_key
from .partitions import CENSUS_DEMOGRAPHIC_PROFILE_PARTITIONS

def get_census_demographic_profile_files() -> List[Dict[str, str]]:
    """ Functrion to generate list of Demographic Profile Files.

    Returns
    -------
    List[Dict[str, str]]
    """

    discovered_demographic_profile_files = [
        {"data_release": "2020-01", "relative_path": "cb_demographics_county_2020.csv", "geo_type": "COUNTY", "data_provider": "Census Bureau"},
        {"data_release": "2020-01", "relative_path": "cb_demographics_state_2020.csv", "geo_type": "STATE", "data_provider": "Census Bureau"},
        {"data_release": "2020-01", "relative_path": "cb_demographics_zcta3_2020.csv", "geo_type": "ZCTA3", "data_provider": "Census Bureau"},
        {"data_release": "2020-01", "relative_path": "cb_demographics_zcta5_2020.csv", "geo_type": "ZCTA5", "data_provider": "Census Bureau"},
    ]

    return discovered_demographic_profile_files


@dg.sensor(
    job=census_demographic_profile_job,
    minimum_interval_seconds=300,
    default_status=dg.DefaultSensorStatus.RUNNING
)
def detect_census_demographic_profile_partitions(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    """ Generate the NEMSIS Alcohol Partitions.

    Parameters
    ----------
    context : dg.SensorEvaluationContext

    Returns
    -------
    dg.SensorResult
    """

    # Get Discovered Files
    discovered_demographic_profile_files = get_census_demographic_profile_files()

    # Generate Run Requests
    run_requests = [
        dg.RunRequest(
            run_key=dict_to_partition_key(file_info),
            partition_key=dict_to_partition_key(file_info)
        )
        for file_info in discovered_demographic_profile_files
    ]

    # Generate Dynamic Partition Requests
    dynamic_partition_requests = [
        CENSUS_DEMOGRAPHIC_PROFILE_PARTITIONS.build_add_request([dict_to_partition_key(file_info) for file_info in discovered_demographic_profile_files])
    ]
    
    return dg.SensorResult(
        run_requests=run_requests,
        dynamic_partitions_requests=dynamic_partition_requests,
    )
