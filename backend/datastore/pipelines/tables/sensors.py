import dagster as dg
from .jobs import all_configs_job


@dg.sensor(
    job=all_configs_job,
    minimum_interval_seconds=10,
    default_status=dg.DefaultSensorStatus.RUNNING
)
def all_configs_sensor(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    """_summary_

    Parameters
    ----------
    context : dg.SensorEvaluationContext
        _description_

    Returns
    -------
    dg.SensorResult
        _description_
    """

    run_requests = [
        dg.RunRequest(run_key="FIRST_RUN")
    ]

    return dg.SensorResult(run_requests=run_requests)
