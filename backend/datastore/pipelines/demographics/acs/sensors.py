import dagster as dg
from typing import List, Dict
from .jobs import census_acs_job
from datastore.utils.serialize import dict_to_partition_key
from .partitions import CENSUS_ACS_PARTITIONS

def get_census_acs_files() -> List[Dict[str, str]]:
    """ Functrion to generate list of Demographic Profile Files.

    Returns
    -------
    List[Dict[str, str]]
    """

    discovered_acs_files = [
        {"data_release": "2022-01", "relative_path": "cb_acs_county_2022.csv", "geo_type": "COUNTY", "data_provider": "Census Bureau"},
        {"data_release": "2022-01", "relative_path": "cb_acs_state_2022.csv", "geo_type": "STATE", "data_provider": "Census Bureau"},
        {"data_release": "2022-01", "relative_path": "cb_acs_zcta3_2022.csv", "geo_type": "ZCTA3", "data_provider": "Census Bureau"},
        {"data_release": "2022-01", "relative_path": "cb_acs_zcta5_2022.csv", "geo_type": "ZCTA5", "data_provider": "Census Bureau"},
    ]

    return discovered_acs_files


@dg.sensor(
    job=census_acs_job,
    minimum_interval_seconds=300,
    default_status=dg.DefaultSensorStatus.RUNNING
)
def detect_census_acs_partitions(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    """ Generate the NEMSIS Alcohol Partitions.

    Parameters
    ----------
    context : dg.SensorEvaluationContext

    Returns
    -------
    dg.SensorResult
    """

    # Get Discovered Files
    discovered_acs_files = get_census_acs_files()

    # Generate Run Requests
    run_requests = [
        dg.RunRequest(
            run_key=dict_to_partition_key(file_info),
            partition_key=dict_to_partition_key(file_info)
        )
        for file_info in discovered_acs_files
    ]

    # Generate Dynamic Partition Requests
    dynamic_partition_requests = [
        CENSUS_ACS_PARTITIONS.build_add_request([dict_to_partition_key(file_info) for file_info in discovered_acs_files])
    ]
    
    return dg.SensorResult(
        run_requests=run_requests,
        dynamic_partitions_requests=dynamic_partition_requests,
    )
