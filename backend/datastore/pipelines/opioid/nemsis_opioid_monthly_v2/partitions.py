import dagster as dg


# Create the PartitionDefinition
NEMSIS_OPIOID_V2_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="NEMSIS_OPIOID_V2_PARTITIONS"
)

# Create the PartitionDefinition
NEMSIS_OPIOID_V2_BINS_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="NEMSIS_OPIOID_V2_BINS_PARTITIONS"
)

# Create the PartitionDefinition
NEMSIS_OPIOID_V2_TRENDLINES_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="NEMSIS_OPIOID_V2_TRENDLINES_PARTITIONS"
)