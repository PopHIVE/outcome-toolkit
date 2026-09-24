import json
from typing import List, Dict
import dagster as dg
import pandas as pd
from ..veradigm_ascvd_v2.jobs import ascvd_all_job
from .partitions import VERADIGM_ASCVD_V1_PARTITIONS, VERADIGM_ASCVD_V1_BINS_PARTITIONS
from datastore.utils.serialize import dict_to_partition_key



def get_veradigm_ascvd_v1_files() -> List[Dict[str, str]]:
    """ Function to generate list of NEMSIS Alcohol V2 Zip Files.

    Returns
    -------
    List[Dict[str, str]]
    """
    # TO DO: Have this search the data bundle/directory
    discovered_veradigm_ascvd_v1_files = [
        {'data_release': '2025-03', 'relative_path': 'data_submission_VERADIGM_2025-03.xlsx', 'data_provider': 'HV'},
    ]

    return discovered_veradigm_ascvd_v1_files


@dg.sensor(
    job=ascvd_all_job,
    minimum_interval_seconds=300,
    default_status=dg.DefaultSensorStatus.RUNNING
)
def detect_veradigm_ascvd_v1_monthly_job_partitions(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    """ Generate the Veradigm ASCVD Partitions.

    Parameters
    ----------
    context : dg.SensorEvaluationContext

    Returns
    -------
    dg.SensorResult
    """

    # Get Discovered Files
    discovered_veradigm_ascvd_v1_files = get_veradigm_ascvd_v1_files()

    # Generate Run Requests
    run_requests = [
        dg.RunRequest(
            run_key=dict_to_partition_key(file_info),
            partition_key=dict_to_partition_key(file_info)
        )
        for file_info in discovered_veradigm_ascvd_v1_files
    ]

    # Generate Dynamic Partition Requests
    dynamic_partition_requests = [
        VERADIGM_ASCVD_V1_PARTITIONS.build_add_request([dict_to_partition_key(file_info) for file_info in discovered_veradigm_ascvd_v1_files])
    ]
    
    return dg.SensorResult(
        run_requests=run_requests,
        dynamic_partitions_requests=dynamic_partition_requests,
    )

#######################################################################################