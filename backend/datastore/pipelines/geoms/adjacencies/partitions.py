import dagster as dg

CENSUS_ADJACENCY_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="CENSUS_ADJACENCY_PARTITIONS"
)

