from dagster import EnvVar, Definitions
import warnings
import dagster
import dagster as dg
import dagster as dg

# Turn off Experimental Features warning for now
# warnings.filterwarnings("ignore", category=dagster.ExperimentalWarning)



from .pipelines import (
    REGISTERED_ASSETS,
    REGISTERED_ASSET_CHECKS,
    REGISTERED_JOBS,
    REGISTERED_SENSORS
)


from .pipelines import (
    REGISTERED_ASSETS,
    REGISTERED_JOBS,
    REGISTERED_SENSORS
)
from .resources.postgres_resource import PostgresConnectionResource

defs = Definitions(
    assets=[*REGISTERED_ASSETS],
    asset_checks=[*REGISTERED_ASSET_CHECKS],
    jobs=[*REGISTERED_JOBS],
    sensors=[
        *REGISTERED_SENSORS,
        dg.AutomationConditionSensorDefinition(
            name="automation_condition_sensor",
            target=dg.AssetSelection.all(),
            default_status=dg.DefaultSensorStatus.RUNNING,
            minimum_interval_seconds=5,
        )
    ],
    resources={
        'db': PostgresConnectionResource(
            username=EnvVar('DATASTORE_USER'),
            password=EnvVar('DATASTORE_PASSWORD'),
            database=EnvVar('DATASTORE_DB'),
            host='postgres',
            port='5432',
        )
    },
)