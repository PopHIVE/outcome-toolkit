import os
import dagster as dg
import pandas as pd
from datastore.pipelines.base.consts.assets import ValidMorpheusIDs
from datastore.utils.serialize import df_to_metadata


@dg.asset(
    group_name="Opioid",
    automation_condition=dg.AutomationCondition.eager()
)
def valid_opioid_mids_asset() -> dg.Output[ValidMorpheusIDs]:
    """ Valid MIDs Object. """

    static_valid_mids = pd.read_csv(os.path.join('/opt/dagster/app/datastore/static', 'valid_mids.csv'))
    valid_mids = {
        row.mid: row.type
        for _, row in static_valid_mids.loc[static_valid_mids.type == 'COUNTY'].iterrows()
    }
    return dg.Output(ValidMorpheusIDs(valid_mids), metadata=df_to_metadata(static_valid_mids))
