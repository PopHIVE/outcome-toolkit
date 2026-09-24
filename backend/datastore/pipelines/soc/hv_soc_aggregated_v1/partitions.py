import dagster as dg


# Create the PartitionDefinition
HV_SOC_V1_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="HV_SOC_V1_PARTITIONS"
)

# Create the PartitionDefinition
HV_SOC_V1_BINS_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="HV_SOC_V1_BINS_PARTITIONS"
)