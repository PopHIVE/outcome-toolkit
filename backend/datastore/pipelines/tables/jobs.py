import dagster as dg

all_configs_job = dg.define_asset_job(
    name="all_configs_job",
    selection='group:"configs"'
)
