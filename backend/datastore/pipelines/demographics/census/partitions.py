import dagster as dg

CENSUS_DEMOGRAPHIC_PROFILE_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="CENSUS_DEMOGRAPHIC_PROFILE_PARTITIONS"
)

