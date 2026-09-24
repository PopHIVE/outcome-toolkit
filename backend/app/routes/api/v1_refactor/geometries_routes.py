from flask import Blueprint, request
# from app.routes.schemas import GeoJSONFeatureCollection, MidProperties
# from app.routes.schemas import PropertiesResponse
# from app.utilities.exceptions import validate_mids

from db.datasets.core import Area
from app.models.responses import GeoJSONResponse
from app.models.common import Geography
from app.ext.cache import cache


# Blueprint Example for Scalability
bp = Blueprint('geometries', __name__)


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

    Returns
    -------
    GeoJSONFeatureCollection

    """

    args = request.args.to_dict(flat=False)
    states = args.get('state', [])
    geography = Geography(type_=geography)

    if len(states) > 0:
        results = Area.query_by_state_usps(state_usps=states, geography=geography.type_)
    else:
        results = Area.query_by_geography(geography=geography.type_)

    geojson_response = GeoJSONResponse()

    for area in results:
        geojson_response.add_area(area)

    return geojson_response.to_response(compress=True)
