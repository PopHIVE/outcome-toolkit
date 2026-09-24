import dagster as dg
import pandas as pd

from .assets import veradigm_ascvd_v2_raw_df_asset
from ..base.assets import valid_ascvd_mids_asset, ValidMorpheusIDs
from datastore.utils.serialize import df_to_metadata


@dg.asset_check(
    asset=veradigm_ascvd_v2_raw_df_asset,
    description="Check if missing MIDs"
)
def veradigm_v2_raw_df_missing_mids_asset_check(context: dg.AssetCheckExecutionContext, raw_df: pd.DataFrame) -> dg.AssetCheckResult:
    """ Checks if the Veradigm raw v2 is missing mids

    Parameters
    ----------
    context : dg.AssetCheckExecutionContext
        _description_
    raw_df : pd.DataFrame
        _description_

    Returns
    -------
    dg.AssetCheckResult
        _description_
    """

    ValidMIDS = valid_ascvd_mids_asset().value
    raw_df['is_valid'] = raw_df.zip3.apply(lambda x: ValidMIDS.is_valid(f'ZCTA3 {x}', 'ZCTA3'))
    invalid_mids = raw_df.loc[~raw_df['is_valid']].copy()

    return dg.AssetCheckResult(
        passed=True,
        severity=dg.AssetCheckSeverity.WARN,
        metadata=df_to_metadata(invalid_mids, n=1000)
    )
