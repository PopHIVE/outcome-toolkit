from typing import List, Any
import dagster as dg
from sqlalchemy.engine.reflection import Inspector
from datastore.resources.postgres_resource import PostgresConnectionResource
from db.datasets.core import Area


def table_asset_factory(
    tbl: Any,
    asset_key: str,
    group_name: str,
    deps: List[dg.asset] = None
) -> dg.asset:


    @dg.asset(
        name=asset_key,
        deps=deps,
        group_name=group_name,
        automation_condition=dg.AutomationCondition.eager()
    )
    def generic_table_asset(context: dg.AssetExecutionContext, db: PostgresConnectionResource) -> dg.Output[Any]:

        inspector = Inspector.from_engine(db.engine)
        
        context.log.info(f"Creating Table: {tbl.__tablename__}...")
        tbl.__table__.create(bind=db.engine, checkfirst=True)
        
        return dg.Output(tbl)

    return generic_table_asset
        
