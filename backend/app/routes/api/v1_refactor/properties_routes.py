from flask import Blueprint, request
# from app.routes.schemas import GeoJSONFeatureCollection, MidProperties
# from app.routes.schemas import PropertiesResponse
# from app.utilities.exceptions import validate_mids

from typing import Dict, Any
from db.datasets.geoms.geoms_tables import AdjacencyEdgeList
from db.datasets.core import Area
from app.models.responses import StandardV1Response
from app.models.common import Geography, MorpheusID
from app.configs.consts import ValidGeographies
from app.configs.settings import MAPPINGS, GeometrySettings
from app.ext.cache import cache, make_properties_key


# Blueprint Example for Scalability
bp = Blueprint('properties', __name__)


@bp.route('/<string:geography>/properties', methods=['POST'])
@cache.cached(make_cache_key=make_properties_key)
def get_properties(geography: str) -> Dict[str, Any]:
    """
    Get Properties response: (demographics, acs_estimates, opioid, alcohol, soc, ascvd_scores, ...)


    Parameters
    ----------
    geography: str (path)
        Geography to Filter on.
    states: List[str] (Query String)
        Provide List of States like: state=MA&state=VT...
    mids: List[str]
        In JSON Body i.e. {'mids': [...]}

    Returns
    -------
    Dict[str, Any]
    """

    args = request.args.to_dict(flat=False)
    states = args.get('state', [])

    # Sanitze Inputs
    geography = Geography(type_=geography)
    mids = [MorpheusID(mid=m, type_=geography.type_).mid for m in request.json.get('mids', [])]

    results = Area.query(
        geography=geography.type_,
        mids=mids,
        state_usps=states,
    )

    response = StandardV1Response()

    for index, area in enumerate(results):
        response.add_area(area)

        # Demographics
        response[area].demographics.add_row(
            area.demographics[0], MAPPINGS[area.demographics[0].__data_dictionary_key__]
        )

        # ACS Estimates
        response[area].acs_estimates.add_row(area.income[0], MAPPINGS[area.income[0].__data_dictionary_key__])

        # TO DO:
        # Adjacencies Seem to be Slow when adding like this???
        # Is this a pydantic performance bug??? (perhaps its validating the entire list)
        # response[area].adjacency = list(set([edge.adjacent_mid for edge in area.adjacencies]))

        # Intersections
        response[area].intersections.add_area(area)

        if geography.type_ == ValidGeographies.ZCTA3:
            # SOC
            response[area].soc.add_row(area.soc[0], MAPPINGS[area.soc[0].__data_dictionary_key__])

            # ASCVD Scores
            response[area].ascvd_scores.add_row(area.ascvd[0], MAPPINGS[area.ascvd[0].__data_dictionary_key__])

        if geography.type_ == ValidGeographies.COUNTY:
            # Opioid
            response[area].opioid.add_row(area.opioid[0], MAPPINGS[area.opioid[0].__data_dictionary_key__])

            # Alcohol
            response[area].alcohol.add_row(area.alcohol[0], MAPPINGS[area.alcohol[0].__data_dictionary_key__])

    # TO DO: Not Sure why this is faster than the above ... ???
    # Adjacencies are Slow and need to be optimized
    results = AdjacencyEdgeList.query(
        geography=geography.type_,
        mids=mids,
        distance_m=GeometrySettings.ADJACENCY_TOLERANCE_METERS,
    )

    for row in results:
        response.data[row.mid].adjacency.append(row.adjacent_mid)

    return response.to_response(compress=True)
