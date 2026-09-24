import json
from typing import List, Dict
import dagster as dg
import pandas as pd
from .jobs import nemsis_alcohol_v1_monthly_job, nemsis_alcohol_v1_bins_monthly_job
from .partitions import NEMSIS_ALCOHOL_V1_PARTITIONS, NEMSIS_ALCOHOL_V1_BINS_PARTITIONS
from datastore.utils.serialize import dict_to_partition_key


def get_nemsis_alcohol_v1_files() -> List[Dict[str, str]]:
    """ Function to generate list of NEMSIS Alcohol V2 Zip Files.

    Returns
    -------
    List[Dict[str, str]]
    """
    # TO DO: Have this search the data bundle/directory
    discovered_nemsis_alcohol_v1_files = [
        {'data_release': '2024-07', 'relative_path': 'NEMSIS_Monthly_county_level_data_2024_Q1.zip', 'file_name': 'allalcohol_county_tosend_2024.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2024-08', 'relative_path': 'NEMSIS_Monthly_county_level_data_2024_Q2.zip', 'file_name': 'allalcohol_county_tosend_2024.sas7bdat', 'data_provider': 'NEMSIS'},
    ]

    return discovered_nemsis_alcohol_v1_files


@dg.sensor(
    job=nemsis_alcohol_v1_monthly_job,
    minimum_interval_seconds=300,
    default_status=dg.DefaultSensorStatus.RUNNING
)
def detect_nemsis_alcohol_v1_partitions(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    """ Generate the NEMSIS Alcohol Partitions.

    Parameters
    ----------
    context : dg.SensorEvaluationContext

    Returns
    -------
    dg.SensorResult
    """

    # Get Discovered Files
    discovered_nemsis_alcohol_v2_files = get_nemsis_alcohol_v1_files()

    # Generate Run Requests
    run_requests = [
        dg.RunRequest(
            run_key=dict_to_partition_key(file_info),
            partition_key=dict_to_partition_key(file_info)
        )
        for file_info in discovered_nemsis_alcohol_v2_files
    ]

    # Generate Dynamic Partition Requests
    dynamic_partition_requests = [
        NEMSIS_ALCOHOL_V1_PARTITIONS.build_add_request([dict_to_partition_key(file_info) for file_info in discovered_nemsis_alcohol_v2_files])
    ]
    
    return dg.SensorResult(
        run_requests=run_requests,
        dynamic_partitions_requests=dynamic_partition_requests,
    )

#######################################################################################

def get_nemsis_alcohol_v1_bins_files() -> List[Dict[str, str]]:
    """ Function to generate list of NEMSIS Alcohol V2 Zip Files.

    Returns
    -------
    List[Dict[str, str]]
    """
    # TO DO: Have this search the data bundle/directory
    discovered_nemsis_alcohol_v1_bin_files = [
        {'data_release': '2024-09', 'relative_path': 'NEMSIS_Monthly_county_level_data_2023.zip', 'file_name': 'CountyAlcoholBins_2023.xlsx', 'metrics_file_name': 'allalcohol_county_tosend_2023.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2024-07', 'relative_path': 'NEMSIS_Monthly_county_level_data_2024_Q1.zip', 'file_name': 'CountyAlcoholBins_2024.xlsx', 'metrics_file_name': 'allalcohol_county_tosend_2024.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2024-08', 'relative_path': 'NEMSIS_Monthly_county_level_data_2024_Q2.zip', 'file_name': 'CountyAlcoholBins_2024.xlsx', 'metrics_file_name': 'allalcohol_county_tosend_2024.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2024-08', 'relative_path': 'NEMSIS_Monthly_county_level_data_2024_JUL.zip', 'file_name': 'CountyAlcoholBins_2024July.xlsx', 'metrics_file_name': 'allalcohol_county_tosend_202407.sas7bdat', 'data_provider': 'NEMSIS'},
    ]

    return discovered_nemsis_alcohol_v1_bin_files


@dg.sensor(
    job=nemsis_alcohol_v1_bins_monthly_job,
    minimum_interval_seconds=300,
    default_status=dg.DefaultSensorStatus.RUNNING
)
def detect_nemsis_alcohol_v1_bins_partitions(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    """ Generate the NEMSIS Alcohol Partitions.

    Parameters
    ----------
    context : dg.SensorEvaluationContext

    Returns
    -------
    dg.SensorResult
    """

    # Get Discovered Files
    discovered_nemsis_alcohol_v1_bin_files = get_nemsis_alcohol_v1_bins_files()

    # Generate Run Requests
    run_requests = [
        dg.RunRequest(
            run_key=dict_to_partition_key(file_info),
            partition_key=dict_to_partition_key(file_info)
        )
        for file_info in discovered_nemsis_alcohol_v1_bin_files
    ]

    # Generate Dynamic Partition Requests
    dynamic_partition_requests = [
        NEMSIS_ALCOHOL_V1_BINS_PARTITIONS.build_add_request([dict_to_partition_key(file_info) for file_info in discovered_nemsis_alcohol_v1_bin_files])
    ]
    
    return dg.SensorResult(
        run_requests=run_requests,
        dynamic_partitions_requests=dynamic_partition_requests,
    )