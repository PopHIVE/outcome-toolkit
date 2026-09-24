from flask import Blueprint, request

from app.models.common import Outcome
from app.db.database import db_session
from db.datasets.opioid.opioid_tables import Bins
from app.models.responses import BinsResponseV2
from app.ext.cache import cache

# Blueprint Example for Scalability
bp = Blueprint('bins', __name__)


@bp.route('/bins', methods=['GET'])
@cache.cached(query_string=True)
def get_bins():
    """
    Get Bins data filtered by outcome.

    Parameters
    ----------
    outcome: str (path)

    Returns
    -------
    Dict[str, Any]
    """

    outcome_arg = request.args.get('outcome')
    outcome = Outcome(outcome=outcome_arg)

    rows = (
        db_session.query(Bins)
        .filter(Bins.outcome == outcome.outcome)
        .order_by(Bins.end_date.desc(), Bins.start_date.asc(), Bins.rank.asc())
        .all()
    )

    response = BinsResponseV2()

    for row in rows:
        response.add_value(
            outcome=outcome.outcome,
            metric=row.measure,
            start_date=row.start_date,
            end_date=row.end_date,
            bin_stats={
                'rank': row.rank,
                'rank_value': row.rankValue,
                'min': row.min,
                'max': row.max,
                'median': row.median,
                'mean': row.mean,
                'midpoint': row.midpoint,
                'representative': row.midpoint,
            },
        )

    return response.to_response(compress=True)
