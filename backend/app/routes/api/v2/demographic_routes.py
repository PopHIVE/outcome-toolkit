from flask import Blueprint, request
from sqlalchemy import (
    Column,
    String,
    or_,
    and_,
)
from app.models.common import Geography
from db.datasets.demographics.demographics_tables import (
    CBACSEstimates,
    CBDemographics
)
from db.datasets.geoms.geoms_tables import CBGeomIndex
from app.db.database import db_session
from db.datasets.core import Area
from db.datasets.geoms.geoms_tables import AdjacencyEdgeList

from app.models.responses import OverviewResponseV2, DemographicsResponse
from app.ext.cache import cache
from app.ext.exceptions.errors import InvalidColumn
from app.configs.settings import DATA_DICTIONARY, GeometrySettings


# Blueprint Example for Scalability
bp = Blueprint('demographics', __name__)

DEMOGRAPHIC_DATASOURCES = {'census': CBDemographics, 'acs': CBACSEstimates}


@bp.route('/demographics', methods=['GET'])
@cache.cached()
def get_demographics():
    """
    Take no params, return all demographics for every geometry type
    """

    ## form the metadata section, col headers per category
    demographic_area_types = ['STATE', 'ZCTA3', 'COUNTY']

    results = db_session.query(Area).filter(Area.type.in_(demographic_area_types))

    response = DemographicsResponse()

    exclude_columns = [
        "geoid",
        "type",
        "mid",
        "start_date",
        "end_date",
        "created",
        "data_provider",
        "data_release",
        "data_bundle",
        "source_file",
        "row_num",
        "etl_version",
    ]

    # Used to prevent showing in category bands
    exclude_from_categories = [
        "metadata",
        "general",
        "sex"
    ]

    # Metadata section
    response.add_source('Data for income is from ACS 5-year survey as of 2022. Other data is from the 2020 Census.')

    # CENSUS Metadata
    for col, metadata in DATA_DICTIONARY.mappings['cb_demographics'].items():
        if (metadata['characteristic'] not in exclude_from_categories) and (DATA_DICTIONARY.mappings['cb_demographics'][col]['include'].lower() == 'yes'):
            response.add_demographic_category(f'census.{col}', metadata['characteristic'])
            response.add_display_name(f'census.{col}', metadata['display_name'])
            

    # ACS Metadata
    for col, metadata in DATA_DICTIONARY.mappings['cb_acs_estimates'].items():
        if (metadata['characteristic'] not in exclude_from_categories) and (DATA_DICTIONARY.mappings['cb_acs_estimates'][col]['include'].lower() == 'yes'):
            response.add_demographic_category(f'acs.{col}', metadata['characteristic'])
            response.add_display_name(f'acs.{col}', metadata['display_name'])
            
    # Adjacency List Metadata
    # Adjacency is not added to demographic category bands

    # Data section
    for result in results:
        try:
            # CENSUS Data
            demographic_row = result.demographics[0].to_dict()
            for col, value in demographic_row.items():
                if (col not in exclude_columns) and (
                    DATA_DICTIONARY.mappings['cb_demographics'][col]['include'].lower() == 'yes'
                ):
                    response.add_value(demographic_row['mid'], f'census.{col}', value)
            # ACS Data
            income_row = result.income[0].to_dict()
            for col, value in income_row.items():
                if (col not in exclude_columns) and (
                    DATA_DICTIONARY.mappings['cb_acs_estimates'][col]['include'].lower() == 'yes'
                ):
                    response.add_value(income_row['mid'], f'acs.{col}', value)
        except Exception as e:
            print(f"{result.mid} is missing ACS or Census Info.")
            continue

    # Adjacency List Data
    adjacency_results = (
        db_session.query(AdjacencyEdgeList)
        .filter(AdjacencyEdgeList.distance <= GeometrySettings.ADJACENCY_TOLERANCE_METERS)
        .filter(AdjacencyEdgeList.type.in_(demographic_area_types))
        .all()
    )
    for adjacency_edge in adjacency_results:
        response.add_adjacency_value(adjacency_edge.mid, adjacency_edge.adjacent_mid)
    
    # Intersection Data
    for source_geography in demographic_area_types:
        for target_geography in demographic_area_types:
            if source_geography == target_geography:
                continue
            intersection_results = CBGeomIndex.query_intersections(source_geography, target_geography)

            for row in intersection_results:
                response.add_intersections_value(
                    row[0],
                    target_geography,
                    row[1]
                )

    return response.to_response(compress=True)


@bp.route('/demographics/overview', methods=['GET'])
@cache.cached(query_string=True)
def get_demographic_overview():
    """
    Return MID Demographic Overviews.

    Parameters
    ----------
    # mids: List[str]
    metric: str
    geography: str
    datasource: str

    Returns
    -------
    Dict[str, Any]

    """

    metric = request.args.get('metric')
    datasource = request.args.get('datasource', 'census')
    geography = Geography(type_=request.args.get('geography', ''))
    # mids = [MorpheusID(mid=m).mid for m in request.json.get('mids', [])]

    if datasource not in DEMOGRAPHIC_DATASOURCES:
        raise InvalidColumn(datasource, list(DEMOGRAPHIC_DATASOURCES.keys()))

    demographic_table = DEMOGRAPHIC_DATASOURCES.get(datasource, CBDemographics)

    if not hasattr(demographic_table, metric):
        raise InvalidColumn(metric, list(demographic_table.__table__.columns.keys()))

    query = db_session.query(demographic_table).filter(demographic_table.type == geography.type_)

    # if len(mids) > 0:
    #   query = query.filter(demographic_table.mid.in_(mids))

    response = OverviewResponseV2()

    results = query.all()

    for row in results:
        response.add_value(row.mid, getattr(row, metric, None))

    return response.to_response(compress=True)
