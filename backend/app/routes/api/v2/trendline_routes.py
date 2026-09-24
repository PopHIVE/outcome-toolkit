from flask import Blueprint, request

from app.models.common import Outcome
from app.db.database import db_session
from app.models.responses import TrendlinesResponseV2
from app.ext.cache import cache, make_trendlines_key
from db.datasets.trendlines.trendline_tables import Trendlines

# Blueprint Example for Scalability
bp = Blueprint('trendlines', __name__)


@bp.route('/trendlines/national', methods=['POST'])
@cache.cached(make_cache_key=make_trendlines_key)
def get_details():
    """
    Get Trendline Values filtered by outcome and MID.

    Parameters
    ----------
    outcome: str Body
    metrics: List[str] Body

    Returns
    -------
    Dict[str, Any]
    """

    outcome_arg = request.json.get('outcome')
    outcome = Outcome(outcome=outcome_arg)

    # metrics = [outcome.get_metric_mappings(m) for m in request.json.get('metrics', [])]

    rows = db_session.query(Trendlines).filter((Trendlines.outcome == outcome.outcome)).all()

    response = TrendlinesResponseV2()

    for row in rows:
        response.add_value(
            metric=row.measure,
            start_date=row.start_date,
            end_date=row.end_date,
            value=row.value,
        )

    return response.to_response(compress=True)
