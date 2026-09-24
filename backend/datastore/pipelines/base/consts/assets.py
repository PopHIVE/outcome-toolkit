import os
from typing import Iterable, Tuple, Dict, Any
import dagster as dg
import pandas as pd
from datastore.utils.serialize import df_to_metadata
from db.datasets.core import Area
from datastore.resources.postgres_resource import PostgresConnectionResource
from datastore.pipelines.tables.assets import create_area_table_asset
from datastore.pipelines.tables.assets import create_user_table_asset


class ValidMorpheusIDs(object):

    def __init__(self, valid_mids: Dict[str, str]):
        self.VALID_MIDS: Dict[str, str] = valid_mids

    def is_valid(self, mid: str, geography: str = None) -> bool:
        if mid not in self.VALID_MIDS:
            return False

        if geography is not None:
            return self.VALID_MIDS[mid] == geography

        return True
    
    def mids(self) -> Iterable[Tuple[str, str]]:
        return self.VALID_MIDS.items()


@dg.asset(
    group_name="configs"
)
def valid_mids_asset() -> dg.Output[ValidMorpheusIDs]:
    """ Valid MIDs Object. """

    static_valid_mids = pd.read_csv(os.path.join('/opt/dagster/app/datastore/static', 'valid_mids.csv'))
    valid_mids = {
        row.mid: row.type
        for _, row in static_valid_mids.iterrows()
    }
    return dg.Output(ValidMorpheusIDs(valid_mids), metadata=df_to_metadata(static_valid_mids))
    

@dg.asset(
    deps=[create_user_table_asset],
    group_name="configs",
    automation_condition=dg.AutomationCondition.eager(),
    ins={
        "area_tbl": dg.AssetIn(create_area_table_asset.key)
    }
)
def load_area_table_asset(
    db: PostgresConnectionResource,
    area_tbl: Any
) -> None:
    """_summary_

    Parameters
    ----------
    valid_mids : pd.DataFrame
        _description_
    """

    valid_mids_df = pd.read_csv(os.path.join('/opt/dagster/app/datastore/static', 'valid_mids.csv'))

    records = []

    for _, row in valid_mids_df.iterrows():
        records.append(Area(**row.to_dict()))

    with db.session() as session, session.begin():
        for record in records:
            session.merge(record)
        session.commit()
    