import pandas as pd
from datetime import datetime
from sqlalchemy import func, and_
from db.datasets.demographics.demographics_tables import CBDemographics
from db.datasets.alcohol.alcohol_tables import NEMSISAlcohol_v2, NEMSISAlcohol
from db.datasets.opioid.opioid_tables import NEMSISOpioid_v2, NEMSISOpioid
from datastore.utils.consts import COUNTRY_MID, rankify, BinLabels


def load_national_nemsis_data(db_session, outcome: str, aggregated: bool = False) -> pd.DataFrame:
    """Generate National NEMSIS Data via population weighted methodology.

    Parameters
    ----------
    outcome : str
        opioid or alcohol outcomes supported.
    aggregated : bool, optional
        which table to run the aggregation on, by default False

    Returns
    -------
    List[Row]

    """

    if outcome == 'opioid':
        if aggregated:
            TBL = NEMSISOpioid
        else:
            TBL = NEMSISOpioid_v2
        METRIC_COL = TBL.opioid_rate_rank
    elif outcome == 'alcohol':
        if aggregated:
            TBL = NEMSISAlcohol
        else:
            TBL = NEMSISAlcohol_v2
        METRIC_COL = TBL.alcohol_rate_rank
    else:
        raise ValueError('Unsuported Outcome')

    results = (
        db_session.query(
            TBL.start_date,
            TBL.end_date,
            (func.sum(TBL.population_estimate)).label('population_estimate'),
            (func.sum(CBDemographics.total_population * METRIC_COL) / func.sum(CBDemographics.total_population)).label(
                'weighted_metric_value'
            ),
        )
        .join(CBDemographics, CBDemographics.mid == TBL.mid)
        .group_by(
            TBL.start_date,
            TBL.end_date,
        )
        .filter(and_(TBL.type == 'COUNTY', TBL.start_date >= datetime(year=1975, month=1, day=1)))
    )

    records = []

    for row in results:
        if outcome == 'opioid':
            record = {
                'mid': COUNTRY_MID,
                'type': 'COUNTRY',
                'start_date': row.start_date,
                'end_date': row.end_date,
                'population_estimate': row.population_estimate,
                'opioid_rate_rank': rankify(row.weighted_metric_value),
                'opioid_rate_rank_value': BinLabels.LABELS.get(rankify(row.weighted_metric_value), 'No Data'),
            }
            records.append(record)
        else:
            record = {
                'mid': COUNTRY_MID,
                'type': 'COUNTRY',
                'start_date': row.start_date,
                'end_date': row.end_date,
                'population_estimate': row.population_estimate,
                'alcohol_rate_rank': rankify(row.weighted_metric_value),
                'alcohol_rate_rank_value': BinLabels.LABELS.get(rankify(row.weighted_metric_value), 'No Data'),
            }
            records.append(record)

    return records