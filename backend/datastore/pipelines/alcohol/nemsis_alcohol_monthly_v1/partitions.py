import dagster as dg

# Create the PartitionDefinition
NEMSIS_ALCOHOL_V1_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="NEMSIS_ALCOHOL_V1_PARTITIONS"
)

# Create the PartitionDefinition
NEMSIS_ALCOHOL_V1_BINS_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="NEMSIS_ALCOHOL_V1_BINS_PARTITIONS"
)