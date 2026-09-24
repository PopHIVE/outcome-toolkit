from flask import Blueprint, request

from app.models.common import Outcome
from db.datasets.core import Area
from app.db.database import db_session
from app.models.responses import OverviewResponseV2
from app.ext.cache import cache
from app.configs.consts import ValidOutcomes
from app.utilities.serialize import parse_time
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.orm import contains_eager


# Blueprint Example for Scalability
bp = Blueprint('overview', __name__)


@bp.route('/overview', methods=['GET'])
@cache.cached(query_string=True)
def get_overview():
    """
    Return MID Overviews.

    Parameters
    ----------
    outcome: str
    metric: str
    start_date: datetime
    end_date: datetime

    Returns
    -------
    Dict[str, Any]

    """

    outcome = Outcome(outcome=request.args.get('outcome'))
    metric = outcome.get_metric_mappings(request.args.get('metric'))
    start_date = parse_time(request.args.get('start_date'))
    end_date = parse_time(request.args.get('end_date'))

    # Handle Any Nulled/Malformed Rows
    origin_date = datetime(1970, 1, 1)

    outcome_relationship, outcome_table = Area.outcome_relationships(outcome.outcome)

    areas = (
        db_session.query(Area)
        .join(outcome_relationship)
        .filter(
            and_(
                (outcome_table.start_date >= start_date),
                (outcome_table.end_date <= end_date),
                (outcome_table.start_date > origin_date),
            )
        )
        .options(contains_eager(outcome_relationship))
        .populate_existing()
        .all()
    )

    response = OverviewResponseV2()

    for area in areas:
        if outcome.outcome == ValidOutcomes.ALCOHOL:
            bin_rank = getattr(area.alcohol[0], metric['metric'], None)

        elif outcome.outcome == ValidOutcomes.CARDIO:
            bin_rank = getattr(area.ascvd[0], metric['metric'], None)

        elif outcome.outcome == ValidOutcomes.OPIOID:
            bin_rank = getattr(area.opioid[0], metric['metric'], None)

        elif outcome.outcome == ValidOutcomes.SOC:
            bin_rank = getattr(area.soc[0], metric['metric'], None)

        response.add_value(mid=area.mid, bin_rank=bin_rank)

    return response.to_response(compress=True)
