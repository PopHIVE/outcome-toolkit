import dagster as dg

CENSUS_ACS_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="CENSUS_ACS_PARTITIONS"
)

