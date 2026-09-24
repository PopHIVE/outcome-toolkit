from collections import defaultdict
from math import floor
from flask import Blueprint, jsonify, request, g
from app.utilities.loggerfactory import LoggerFactory
from typing import Dict, Any
from app.utilities.generate_labels import ZCTA3PicklistLabel, CountyPicklistLabel
from sqlalchemy import func


from app.configs.settings import MAPPINGS
from app.configs.consts import constants
from app.models.responses import StandardV1Response, StandardV1DataKindBundle
from app.db.database import db_session
from db.datasets.geoms.geoms_tables import CBGeomIndex
from db.datasets.demographics.demographics_tables import (
    CBDemographics,
    CBACSEstimates,
)
from db.datasets.opioid.opioid_tables import Bins
from app.models.common import Outcome
from app.ext.cache import cache, make_properties_key

from db.datasets.core import Area

logger = LoggerFactory.getLogger(__name__, log_level='DEBUG')

# Blueprint Example for Scalability
bp = Blueprint('misc', __name__)


@bp.route('/state/tree')
@cache.cached(query_string=True)
def get_states_tree() -> Dict[str, Any]:
    """
    Constructs the metadata for the States Tree:

    Returns
    -------
    Dict[str, Any]

    """

    # ZCTA3 Metadata
    zcta3_results = (
        db_session.query(
            CBGeomIndex.state_mid,
            CBGeomIndex.state_usps,
            CBGeomIndex.zcta3_mid,
            CBGeomIndex.zcta3_geoid,
            CBGeomIndex.county_namelsad,
            CBDemographics.total_population,
        )
        .distinct()
        .join(CBDemographics, CBDemographics.mid == CBGeomIndex.zcta3_mid)
        .filter(CBGeomIndex.zcta3_geoid.is_not(None))
    )

    # County Metadata
    county_results = (
        db_session.query(
            CBGeomIndex.state_mid,
            CBGeomIndex.county_mid,
            CBGeomIndex.county_geoid,
            CBGeomIndex.county_namelsad,
            CBGeomIndex.state_usps,
            CBDemographics.total_population,
        )
        .distinct()
        .join(CBDemographics, CBDemographics.mid == CBGeomIndex.county_mid)
        .filter(CBGeomIndex.county_geoid.is_not(None))
    )

    state_mid_index = defaultdict(set)

    mid_display_labels = {}
    for row in zcta3_results:
        if row.zcta3_mid not in mid_display_labels:
            mid_display_labels[row.zcta3_mid] = ZCTA3PicklistLabel(row.zcta3_mid, row.total_population)

        state_mid_index[row.state_mid].add(row.zcta3_mid)
        mid_display_labels[row.zcta3_mid].add_county(row.county_namelsad, row.state_usps)

    for row in county_results:
        if row.county_mid not in mid_display_labels:
            mid_display_labels[row.county_mid] = CountyPicklistLabel(
                row.county_namelsad, row.state_usps, row.total_population
            )

        state_mid_index[row.state_mid].add(row.county_mid)

    response = {}
    for state_mid, nested_mids in state_mid_index.items():
        response[state_mid] = {}
        for mid in nested_mids:
            response[state_mid][mid] = mid_display_labels[mid].stringify()

    return response


@bp.route('/bins', methods=['GET'])
@cache.cached(query_string=True)
def get_bins() -> Dict[str, Any]:
    """Get NEMSIS Bin Statistics.

    Returns
    -------
    Dict[str, Any]

    """

    outcome = request.args.get('outcome', None)
    outcome = Outcome(outcome=outcome).outcome

    subquery_rnk = db_session.query(
        func.rank()
        .over(
            order_by=(Bins.end_date.desc(), Bins.start_date.asc()),
            partition_by=[Bins.outcome, Bins.rank, Bins.measure],
        )
        .label('rnk'),
        Bins,
    ).subquery()

    results = (
        db_session.query(subquery_rnk)
        .filter(subquery_rnk.c.outcome == outcome)
        .filter(subquery_rnk.c.rnk == 1)
        .distinct()
    )

    response = defaultdict(list)

    for row in results:
        response[row.measure].append(
            {
                'rank': row.rank,
                'min': round(row.min, 3),
                'max': round(row.max, 3),
                'representative': round(row.midpoint, 3),
                'start_date': row.start_date,
                'end_date': row.end_date,
                'label': row.rankValue,
            }
        )

    # Sort By Bin Rank
    response = {measure: sorted(bins, key=lambda x: x['rank']) for measure, bins in response.items()}
    return jsonify(response)


@bp.route('/download', methods=['POST'])
@cache.cached(make_cache_key=make_properties_key)
def get_states_properties() -> Dict[str, Any]:
    """Dummy Route for logging CSV Requests.

    Returns
    -------
    Dict[str, Any]
    """

    # Get MIDs and Validate
    # args = request.args.to_dict(flat=False)
    geography = request.json.get('geography', 'COUNTY')
    mids = request.json.get('mids', [])
    outcome = request.json.get('outcome', '')  # no defualt here, throw an error if no outcome

    logger.info(
        f"Request to Download for MIDS: ({','.join(mids)}), GEOGRAPHY: {geography}, OUTCOME: {outcome} <{g.request_id}>"
    )

    # results is a list of rows
    results = Area.query_by_mids(mids=mids, geography=geography)

    bins = db_session.query(Bins)

    # get headers from MAPPINGS
    demographic_pop_keys = []
    demographic_pop_headers = []
    for key in MAPPINGS['cb_demographics']:
        # TODO: should male and female follow the other demographics for data dictionary format?
        if key.startswith('pop_') or key == 'male_population' or key == 'female_population':
            demographic_pop_keys.append(key)
            demographic_pop_headers.append(MAPPINGS['cb_demographics'][key]['display_name'])

    header_row = [
        'MID',
        'LABEL',
        'POPULATION',
        str(outcome).title() + ' Rank',
        'Adjacent Areas',
    ] + demographic_pop_headers

    data_rows = []

    area_rank = []
    area_pop = []

    for index, row in enumerate(results):
        row_mid = results[index].mid
        row_label = results[index].demographics[0].to_dict()['name']
        demographics = results[index].demographics[0].to_dict()
        row_population = demographics['total_population']

        if outcome == 'alcohol':
            outcome_results = results[index].alcohol[0].to_dict()
            row_outcome_rate_rank = outcome_results['alcohol_rate_rank']
            row_outcome_rate_rank_value = outcome_results['alcohol_rate_rank_value']
        elif outcome == 'cardio':
            outcome_results = results[index].ascvd[0].to_dict()
            row_outcome_rate_rank = outcome_results['total_mean_rank']
            row_outcome_rate_rank_value = outcome_results['total_mean_rank_value']
        elif outcome == 'opioid':
            outcome_results = results[index].opioid[0].to_dict()
            row_outcome_rate_rank = outcome_results['opioid_rate_rank']
            row_outcome_rate_rank_value = outcome_results['opioid_rate_rank_value']
        elif outcome == 'soc':
            outcome_results = results[index].soc[0].to_dict()
            row_outcome_rate_rank = outcome_results['any_soc_rate_rank']
            row_outcome_rate_rank_value = outcome_results['any_soc_rate_rank_value']

        # TODO: add clause for future outcomes here

        # Handle null metrics for area
        if row_outcome_rate_rank is None:
            row_rank = 'No Data'
        else:
            row_rank = str(int(row_outcome_rate_rank)) + ' ' + row_outcome_rate_rank_value

        row_adjacencies = []
        for adj in results[index].adjacencies:
            row_adjacencies.append(adj.to_dict()['adjacent_mid'])

        demographics_pops = []
        for d in demographic_pop_keys:
            demographics_pops.append(demographics[d])

        csv_row = [
            row_mid,
            '"' + str(row_label) + '"',
            row_population,
            row_rank,
            ';'.join(row_adjacencies),
        ] + demographics_pops
        data_rows.append(csv_row)

        if row_outcome_rate_rank is not None:  # only counting regions with non null metric ranks
            # rank x population
            area_rank.append(int(row_population) * row_outcome_rate_rank)
            area_pop.append(row_population)

    # rows with None in population add 0 to totals
    total_population = sum([row[2] if row[2] else 0 for row in data_rows])

    # calculate totals of every demographic population group
    total_demographics_pops = []
    for i in range(len(demographic_pop_keys)):  # for every demographic header i.e. pop_0_5
        # affected by location of demographic populations, assumes they are in the same place
        total_demographics_pops.append(sum([row[i + 5] if row[i + 5] else 0 for row in data_rows]))

    # calculate weighted average of outcome metric rank, No Data regions are not counted in this!
    # TODO: if this is switched to actual metric, alc and opioid have no raw rates
    valid_metric_total = sum([r for r in area_rank])
    valid_pop_total = sum([r for r in area_pop])
    # division by 0 is a risk if called outside valid ui selection, avg rank -1 if no valid pop
    average_rank = floor(valid_metric_total / valid_pop_total) if valid_pop_total else -1
    average_rank_value = bins[average_rank].rankValue

    totals_row = [
        'TOTAL',
        'SUMMARY',
        total_population,
        str(average_rank) + ' ' + average_rank_value,
        'ADJACENCY',
    ] + total_demographics_pops

    return {'header_row': header_row, 'totals_row': totals_row, 'data_rows': data_rows}


@bp.route('/national/distributions')
@cache.cached(query_string=True)
def get_national_distributions() -> Dict[str, Any]:
    """Route that returns the national distribtuions of demographic data.
    Response is in the same format as the /api/<geography>/properties route except it is
    keyed by geography rather than MID.

    """

    demographics = {row.type: row._asdict() for row in CBDemographics.get_sums_over_geography()}
    acs_estimates = {row.type: row._asdict() for row in CBACSEstimates.get_sums_over_geography()}

    response = StandardV1Response()
    for type_, row in demographics.items():
        response.data[type_] = StandardV1DataKindBundle()

        # Demographics
        response.data[type_].demographics.add_row(row, MAPPINGS[row.__data_dictionary_key__])

    for type_, row in acs_estimates.items():
        # ACS Estimates
        response.data[type_].acs_estimates.add_row(row, MAPPINGS[row.__data_dictionary_key__])

    return response.to_response(compress=True)


@bp.route('/consts')
def get_consts() -> Dict[str, Any]:
    """Returns JSON version of the Constants for Frontend Usage."""

    return jsonify(constants)
