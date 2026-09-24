import dagster as dg


# Create the PartitionDefinition
VERADIGM_ASCVD_V1_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="VERADIGM_ASCVD_V1_PARTITIONS"
)

# Create the PartitionDefinition
VERADIGM_ASCVD_V1_BINS_PARTITIONS = dg.DynamicPartitionsDefinition(
    name="VERADIGM_ASCVD_V1_BINS_PARTITIONS"
)