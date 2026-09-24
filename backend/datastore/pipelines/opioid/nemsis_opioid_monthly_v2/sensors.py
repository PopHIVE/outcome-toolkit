import json
from typing import List, Dict
import dagster as dg
import pandas as pd
from .jobs import nemsis_opioid_v2_monthly_job, nemsis_opioid_v2_bins_monthly_job, nemsis_opioid_v2_trendlines_job
from .partitions import NEMSIS_OPIOID_V2_PARTITIONS, NEMSIS_OPIOID_V2_BINS_PARTITIONS, NEMSIS_OPIOID_V2_TRENDLINES_PARTITIONS
from datastore.utils.serialize import dict_to_partition_key


def get_nemsis_opioid_v2_files() -> List[Dict[str, str]]:
    """ Function to generate list of NEMSIS Opioid V2 Zip Files.

    Returns
    -------
    List[Dict[str, str]]
    """
    # TO DO: Have this search the data bundle/directory
    discovered_nemsis_opioid_v2_files = [
        {'data_release': '2024-09', 'relative_path': 'NEMSIS_Monthly_county_level_data_2023.zip', 'file_name': 'allopioid_county_tosend_2023.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2024-08', 'relative_path': 'NEMSIS_Monthly_county_level_data_2024_JUL.zip', 'file_name': 'allopioid_county_tosend_2024july.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2024-09', 'relative_path': 'NEMSIS_Monthly_county_level_data_2024_AUG.zip', 'file_name': 'opioidmeasure.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2024-10', 'relative_path': 'NEMSIS_Monthly_county_level_data_2024_SEP.zip', 'file_name': 'opioidmeasure.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2024-11', 'relative_path': 'NEMSIS_Monthly_county_level_data_2024_OCT.zip', 'file_name': 'opioidmeasure.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2024-12', 'relative_path': 'data_submission_NEMSIS_2025-01-03.zip', 'file_name': 'opioidmeasure.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2025-01', 'relative_path': 'data_submission_NEMSIS_2025-01-31.zip', 'file_name': 'opioidmeasure.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2025-02', 'relative_path': 'data_submission_NEMSIS_2025-02-28.zip', 'file_name': 'opioidmeasure_cp25.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2025-03', 'relative_path': 'data_submission_NEMSIS_2025-03-31.zip', 'file_name': 'opioidmeasure_cp25.sas7bdat', 'data_provider': 'NEMSIS'},
    ]

    return discovered_nemsis_opioid_v2_files


@dg.sensor(
    job=nemsis_opioid_v2_monthly_job,
    minimum_interval_seconds=300,
    default_status=dg.DefaultSensorStatus.RUNNING
)
def detect_nemsis_opioid_v2_partitions(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    """ Generate the NEMSIS Alcohol Partitions.

    Parameters
    ----------
    context : dg.SensorEvaluationContext

    Returns
    -------
    dg.SensorResult
    """

    # Get Discovered Files
    discovered_nemsis_opioid_v2_files = get_nemsis_opioid_v2_files()

    # Generate Run Requests
    run_requests = [
        dg.RunRequest(
            run_key=dict_to_partition_key(file_info),
            partition_key=dict_to_partition_key(file_info)
        )
        for file_info in discovered_nemsis_opioid_v2_files
    ]

    # Generate Dynamic Partition Requests
    dynamic_partition_requests = [
        NEMSIS_OPIOID_V2_PARTITIONS.build_add_request([dict_to_partition_key(file_info) for file_info in discovered_nemsis_opioid_v2_files])
    ]
    
    return dg.SensorResult(
        run_requests=run_requests,
        dynamic_partitions_requests=dynamic_partition_requests,
    )

#######################################################################################

def get_nemsis_opioid_v2_bins_files() -> List[Dict[str, str]]:
    """ Function to generate list of NEMSIS Opioid V2 Zip Files.

    Returns
    -------
    List[Dict[str, str]]
    """
    # TO DO: Have this search the data bundle/directory
    discovered_nemsis_opioid_v2_bin_files = [
        {'data_release': '2024-09', 'relative_path': 'NEMSIS_Monthly_county_level_data_2024_AUG.zip', 'file_name': 'opioidallrange.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2024-10', 'relative_path': 'NEMSIS_Monthly_county_level_data_2024_SEP.zip', 'file_name': 'opioidallrange.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2024-11', 'relative_path': 'NEMSIS_Monthly_county_level_data_2024_OCT.zip', 'file_name': 'opioidallrange.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2024-12', 'relative_path': 'data_submission_NEMSIS_2025-01-03.zip', 'file_name': 'opioidallrange.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2025-01', 'relative_path': 'data_submission_NEMSIS_2025-01-31.zip', 'file_name': 'opioidallrange.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2025-02', 'relative_path': 'data_submission_NEMSIS_2025-02-28.zip', 'file_name': 'opioidallrange_cp25.sas7bdat', 'data_provider': 'NEMSIS'},
        {'data_release': '2025-03', 'relative_path': 'data_submission_NEMSIS_2025-03-31.zip', 'file_name': 'opioidallrange_cp25.sas7bdat', 'data_provider': 'NEMSIS'},
    ]

    return discovered_nemsis_opioid_v2_bin_files


@dg.sensor(
    job=nemsis_opioid_v2_bins_monthly_job,
    minimum_interval_seconds=300,
    default_status=dg.DefaultSensorStatus.RUNNING
)
def detect_nemsis_opioid_v2_bins_partitions(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    """ Generate the NEMSIS Opioid Partitions.

    Parameters
    ----------
    context : dg.SensorEvaluationContext

    Returns
    -------
    dg.SensorResult
    """

    # Get Discovered Files
    discovered_nemsis_opioid_v2_bin_files = get_nemsis_opioid_v2_bins_files()

    # Generate Run Requests
    run_requests = [
        dg.RunRequest(
            run_key=dict_to_partition_key(file_info),
            partition_key=dict_to_partition_key(file_info)
        )
        for file_info in discovered_nemsis_opioid_v2_bin_files
    ]

    # Generate Dynamic Partition Requests
    dynamic_partition_requests = [
        NEMSIS_OPIOID_V2_BINS_PARTITIONS.build_add_request([dict_to_partition_key(file_info) for file_info in discovered_nemsis_opioid_v2_bin_files])
    ]
    
    return dg.SensorResult(
        run_requests=run_requests,
        dynamic_partitions_requests=dynamic_partition_requests,
    )


#######################################################################################

def get_nemsis_opioid_trendlines_v2_files() -> List[Dict[str, str]]:
    """ Function to generate list of NEMSIS Opioid V2 Zip Files.

    Returns
    -------
    List[Dict[str, str]]
    """
    # TO DO: Have this search the data bundle/directory
    discovered_nemsis_opioid_trendlines_v2_files = [
        {'data_release': '2025-03', 'relative_path': 'data_submission_NEMSIS_2025-03-31.zip',
         'file_name': 'alltrendline2224.sas7bdat', 'data_provider': 'NEMSIS'},
    ]

    return discovered_nemsis_opioid_trendlines_v2_files


@dg.sensor(
    job=nemsis_opioid_v2_trendlines_job,
    minimum_interval_seconds=300,
    default_status=dg.DefaultSensorStatus.RUNNING
)
def detect_nemsis_opioid_trendlines_v2_bins_partitions(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    """ Generate the NEMSIS Alcohol Partitions.

    Parameters
    ----------
    context : dg.SensorEvaluationContext

    Returns
    -------
    dg.SensorResult
    """

    # Get Discovered Files
    discovered_nemsis_opioid_trendlines_v2_files = get_nemsis_opioid_trendlines_v2_files()

    # Generate Run Requests
    run_requests = [
        dg.RunRequest(
            run_key=dict_to_partition_key(file_info),
            partition_key=dict_to_partition_key(file_info)
        )
        for file_info in discovered_nemsis_opioid_trendlines_v2_files
    ]

    # Generate Dynamic Partition Requests
    dynamic_partition_requests = [
        NEMSIS_OPIOID_V2_TRENDLINES_PARTITIONS.build_add_request(
            [dict_to_partition_key(file_info) for file_info in discovered_nemsis_opioid_trendlines_v2_files])
    ]

    return dg.SensorResult(
        run_requests=run_requests,
        dynamic_partitions_requests=dynamic_partition_requests,
    )
