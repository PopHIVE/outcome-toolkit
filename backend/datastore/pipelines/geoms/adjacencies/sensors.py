import dagster as dg
from typing import List, Dict
from .jobs import census_adjacency_edge_list_job
from datastore.utils.serialize import dict_to_partition_key
from .partitions import CENSUS_ADJACENCY_PARTITIONS

def get_census_adjacency_edge_list_files() -> List[Dict[str, str]]:
    """ Functrion to generate list of Demographic Profile Files.

    Returns
    -------
    List[Dict[str, str]]
    """

    discovered_adjacency_edge_list_files = [
        {"data_release": "2020-01", "relative_path": "adjacency_edge_list_county.csv", "geo_type": "COUNTY", "data_provider": "Census Bureau"},
        {"data_release": "2020-01", "relative_path": "adjacency_edge_list_state.csv", "geo_type": "STATE", "data_provider": "Census Bureau"},
        {"data_release": "2020-01", "relative_path": "adjacency_edge_list_zcta3.csv", "geo_type": "ZCTA3", "data_provider": "Census Bureau"},
        {"data_release": "2020-01", "relative_path": "adjacency_edge_list_zcta5.csv", "geo_type": "ZCTA5", "data_provider": "Census Bureau"},
    ]

    return discovered_adjacency_edge_list_files


@dg.sensor(
    job=census_adjacency_edge_list_job,
    minimum_interval_seconds=300,
    default_status=dg.DefaultSensorStatus.RUNNING
)
def detect_census_adjacency_edge_list_partitions(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    """ Generate the NEMSIS Alcohol Partitions.

    Parameters
    ----------
    context : dg.SensorEvaluationContext

    Returns
    -------
    dg.SensorResult
    """

    # Get Discovered Files
    discovered_adjacency_edge_list_files = get_census_adjacency_edge_list_files()

    # Generate Run Requests
    run_requests = [
        dg.RunRequest(
            run_key=dict_to_partition_key(file_info),
            partition_key=dict_to_partition_key(file_info)
        )
        for file_info in discovered_adjacency_edge_list_files
    ]

    # Generate Dynamic Partition Requests
    dynamic_partition_requests = [
        CENSUS_ADJACENCY_PARTITIONS.build_add_request([dict_to_partition_key(file_info) for file_info in discovered_adjacency_edge_list_files])
    ]
    
    return dg.SensorResult(
        run_requests=run_requests,
        dynamic_partitions_requests=dynamic_partition_requests,
    )
