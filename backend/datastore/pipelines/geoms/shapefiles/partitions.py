import dagster as dg

CENSUS_GEOMS_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="CENSUS_GEOMS_PARTITIONS"
)

