import os
import dagster as dg
import pandas as pd
import numpy as np
from typing import Any
from datetime import datetime
from .partitions import CENSUS_ADJACENCY_PARTITIONS
from datastore.utils.consts import Replacements
from datastore.models.data_source import CensusDataDelivery
from datastore.utils.serialize import (
    partition_key_to_dict
)
from datastore.resources.postgres_resource import PostgresConnectionResource
from db.datasets.geoms.geoms_tables import AdjacencyEdgeList
from datastore.pipelines.tables.assets import create_geoms_adjacency_table_asset
from datastore.utils.serialize import df_to_metadata


@dg.asset(
    deps=[create_geoms_adjacency_table_asset],
    partitions_def=CENSUS_ADJACENCY_PARTITIONS,
    group_name="Geoms",
    automation_condition=dg.AutomationCondition.eager()
)
def census_adjacency_edge_list_clean_df_asset(context: dg.AssetExecutionContext) -> dg.Output[pd.DataFrame]:
    """ Load Demographic Profile

    Parameters
    ----------
    context : dg.AssetExecutionContext
    
    Returns
    -------
    dg.Output[pd.DataFrame]
    """

    partition_key = context.partition_key
    data_delivery = CensusDataDelivery(**partition_key_to_dict(partition_key))

    results = pd.read_csv(data_delivery.get_full_path())

    records = []
    for index, row in results.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        record = {
            'mid': row.MID,
            'adjacent_mid': row.ADJACENT_MID,
            'distance': row.DISTANCE,
            'type': row.TYPE,
            'source_file': data_delivery.get_filename(),
            'row_num': index + 1,
            'data_release': data_delivery.data_release,
            'data_provider': data_delivery.data_provider
        }
        records.append(record)

    df = pd.DataFrame(records)
    return dg.Output(df, metadata=df_to_metadata(df))


@dg.asset(
    group_name="Geoms",
    automation_condition=dg.AutomationCondition.eager()
)
def adjacency_edge_list_exemptions(context: dg.AssetExecutionContext) -> dg.Output[pd.DataFrame]:
    """ Load Demographic Profile

    Parameters
    ----------
    context : dg.AssetExecutionContext
    
    Returns
    -------
    dg.Output[pd.DataFrame]
    """
    records = []
    exemptions_df = pd.read_csv(os.path.join('/opt/dagster/app/datastore/static', 'adjacency_edge_list_exemptions.csv'))

    for index, row in exemptions_df.iterrows():
        record = {
            'mid': row.MID,
            'adjacent_mid': row.ADJACENT_MID,
            'distance': -1,
            'type': row.TYPE,
            'source_file': 'adjacency_edge_list_exemptions.csv',
            'row_num': index + 1,
            'data_release': '2020-01',
            'data_provider': 'Internal'
        }
        records.append(record)
        
    df = pd.DataFrame(records)
    return dg.Output(df, metadata=df_to_metadata(df))


@dg.asset(
    ins={
        "clean_dfs": dg.AssetIn(census_adjacency_edge_list_clean_df_asset.key, partition_mapping=dg.AllPartitionMapping()),
        "exemptions_df": dg.AssetIn(adjacency_edge_list_exemptions.key)
    },
    group_name='Geoms',
    automation_condition=dg.AutomationCondition.eager()
)
def census_adjacency_edge_list_clean_table_asset(
    db: PostgresConnectionResource,
    clean_dfs: Any,
    exemptions_df: pd.DataFrame
) -> None:
    """
    This function creates and populates the AdjacencyEdgeList in the database.

    Parameters:
    ----------
    db : PostgresConnectionResource
        A resource object that provides a connection to the PostgreSQL database.
    clean_dfs: List[pd.DataFrame]

    """

    if isinstance(clean_dfs, dict):
        df = pd.concat([*clean_dfs.values()])
    else:
        df = clean_dfs.copy()

    AdjacencyEdgeList.__table__.drop(bind=db.engine, checkfirst=True)
    AdjacencyEdgeList.__table__.create(bind=db.engine, checkfirst=True)

    records = []

    for _, row in df.iterrows():
        records.append(AdjacencyEdgeList(**row.to_dict()))

    with db.session() as session, session.begin():
        session.bulk_save_objects(records)
        session.commit()

    # Exemptions
    exemptions_records = []
    for _, row in exemptions_df.iterrows():
        exemptions_records.append(AdjacencyEdgeList(**row.to_dict()))

    with db.session() as session, session.begin():
        for record in exemptions_records:
            session.merge(record)
        session.commit()