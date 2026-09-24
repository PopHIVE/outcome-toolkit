import dagster as dg


# Create the PartitionDefinition
HV_SOC_V2_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="HV_SOC_V2_PARTITIONS"
)

# Create the PartitionDefinition
HV_SOC_V2_BINS_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="HV_SOC_V2_BINS_PARTITIONS"
)