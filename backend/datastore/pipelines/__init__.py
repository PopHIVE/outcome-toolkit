import dagster as dg
from datastore.utils.dagster_import_utils import recursively_find_instances


REGISTERED_ASSETS = recursively_find_instances(root="datastore/pipelines", types=(dg.AssetsDefinition,))
REGISTERED_ASSET_CHECKS = recursively_find_instances(root="datastore/pipelines", types=(dg.AssetChecksDefinition,))
REGISTERED_JOBS = recursively_find_instances(root="datastore/pipelines", types=(dg.JobDefinition,))
REGISTERED_SENSORS = recursively_find_instances(root="datastore/pipelines", types=(dg.SensorDefinition,))