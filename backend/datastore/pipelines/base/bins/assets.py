import dagster as dg
import pandas as pd
from typing import Any
from sqlalchemy import Table
from datastore.resources.postgres_resource import PostgresConnectionResource
from datastore.pipelines.tables.assets import create_bins_table_asset


def insert_into_bins_factory(
    input_asset: dg.asset,
    asset_key: str,
    asset_group: str,
    partitioned: bool = True
) -> dg.asset:
    
    if partitioned:
        asset_in = dg.AssetIn(input_asset.key, partition_mapping=dg.AllPartitionMapping())
    else:
        asset_in = dg.AssetIn(input_asset.key)

    @dg.asset(
        ins={
            "clean_dfs": asset_in,
            "bins_tbl": dg.AssetIn(create_bins_table_asset.key)
        },
        name=asset_key,
        group_name=asset_group,
        automation_condition=dg.AutomationCondition.eager()
    )
    def insert_into_bins_table(
        context: dg.AssetExecutionContext,
        db: PostgresConnectionResource,
        clean_dfs: Any,
        bins_tbl: Any
    ) -> None:
        
        if isinstance(clean_dfs, dict):
            df = pd.concat([*clean_dfs.values()])
        else:
            df = clean_dfs.copy()
        
        records = []
        
        for _, row in df.iterrows():
            records.append(bins_tbl(**row.to_dict()))

        with db.session() as session, session.begin():
            for record in records:
                session.merge(record)
            session.commit()
    
    return insert_into_bins_table