from flask import Blueprint, request

from db.datasets.core import Area
from app.ext.cache import cache
from app.models.responses import GeoJSONResponse
from app.models.common import Geography


# Blueprint Example for Scalability
bp = Blueprint('latest_geometries', __name__)


@bp.route('/<string:geography>/geometries', methods=['GET'])
@cache.cached(query_string=True)
def get_geometries(geography: str):
    """
    Get GeoJSON results at County Level filtered by States. Response is in
    GeoJSON Feature Collection format.

    Parameters
    ----------
    geography: str (path)
        Geography to Filter on.
    states: List[str] (Query String)
        Provide List of States like: state=MA&state=VT...
    start_date: int (YYYY)
        Starting year bookend for geography data search
    end_date: int (YYYY)
        Ending year bookend for geography data search

    Returns
    -------
    GeoJSONFeatureCollection (Most recent in given timeframe)

    """

    args = request.args.to_dict(flat=False)
    states = args.get('state', [])
    geography = Geography(type_=geography)

    # start_date = parse_time(request.args.get('start_date'))
    # end_date = parse_time(request.args.get('end_date'))

    if len(states) > 0:
        results = Area.query_by_state_usps(state_usps=states, geography=geography.type_)
    else:
        results = Area.query_by_geography(geography=geography.type_)

    geojson_response = GeoJSONResponse()

    for area in results:
        geojson_response.add_area(area)

    return geojson_response.to_response(compress=True)
