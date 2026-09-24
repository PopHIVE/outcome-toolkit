from flask import Blueprint, request

from app.models.common import Outcome
from db.datasets.core import Area
from app.models.responses import DetailsResponseV2, DataDetailsResponse
from app.models.common import MorpheusID
from app.configs.consts import ValidOutcomes
from app.ext.cache import cache, make_details_key


# Blueprint Example for Scalability
bp = Blueprint('details', __name__)


@bp.route('/details', methods=['POST'])
@cache.cached(make_cache_key=make_details_key)
def get_details():
    """
    Get Detailed Metric Values filtered by outcome and MID.

    Parameters
    ----------
    outcome: str Body
    mids: List[str] Body
    metrics: List[str] Body
    aggregate: bool Body

    Returns
    -------
    Dict[str, Any]
    """

    outcome_arg = request.json.get('outcome')
    outcome = Outcome(outcome=outcome_arg)

    aggregate = request.json.get('aggregate', False)

    mids = [MorpheusID(mid=m).mid for m in request.json.get('mids', [])]
    metrics = [outcome.get_metric_mappings(m) for m in request.json.get('metrics', [])]

    rows = Area.query_outcome(outcome.outcome, mids, include_aggregate=aggregate)

    response = DetailsResponseV2()

    for row in rows:
        for metric in metrics:
            response.add_value(
                mid=row.mid,
                metric=metric['metric'],
                start_date=row.start_date,
                end_date=row.end_date,
                value=getattr(row, metric['metric'], None),
                bin_rank=getattr(row, metric['bin_rank'], None),
            )

    return response.to_response(compress=True)

@bp.route('/data-details', methods=['POST'])
def get_data_details():
    """
    Get Data Details filtered by outcome.

    Parameters
    ----------
    outcome: str

    Returns
    -------
    Dict[str, Any]
    """

    all_outcome_results = []
    outcomes = [ValidOutcomes.ALCOHOL, ValidOutcomes.CARDIO, ValidOutcomes.OPIOID, ValidOutcomes.SOC]

    for outcome in outcomes:
        result = Area.query_data_details(outcome)
        all_outcome_results.append(result)


    response = DataDetailsResponse()

    for row in all_outcome_results:
        response.add_value(
            outcome=row.outcome,
            earliest_date=row.earliest_date,
            latest_date=row.latest_date,
            data_release=row.data_release,
        )
    
    return response.to_response(compress=True)