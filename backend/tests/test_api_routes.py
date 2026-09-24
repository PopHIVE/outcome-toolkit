import pytest
import geojson
from tests.conftest import PROPERTIES_API_URLS, MIDS, GEOMETRY_API_URLS
from app.utilities.serialize import decompress_response_data


@pytest.mark.parametrize('url', GEOMETRY_API_URLS)
def test_valid_geometries(url, client):
    """Verify All Geometries Returned are Valid."""

    response = client.get(url)
    response_data = decompress_response_data(response)
    assert response.status_code == 200, f'{url} return {response.status}'

    for feature in response_data['features']:
        assert geojson.Feature(feature).is_valid, f'Invalid Geometry: {feature}'


@pytest.mark.cicd
@pytest.mark.parametrize('url', GEOMETRY_API_URLS[1:])
def test_geometries_filters(url, client):
    """Verify Geometry Routes can be filtered by State."""

    states = {'MA', 'VT', 'VA'}
    response = client.get(url, query_string={'state': list(states)})
    response_data = decompress_response_data(response)

    states_returned = set()
    for feature in response_data['features']:
        states_returned.update(feature['properties']['state_usps'])

    assert (states.issubset(states_returned)) and (
        len(states_returned) < 15
    ), f'Missing State: {states - states_returned}'


@pytest.mark.parametrize('url', GEOMETRY_API_URLS)
def test_sub_second_response(url, client):
    """Verify Caching mechanism works and second attempts at hitting URL are sub-second."""
    _ = client.get(url)  # Call once to cache the result without storing the response
    response = client.get(url)  # Call a second time to get the cached response
    rtime = float(response.headers['X-Execution-Time'])
    status = response.status_code
    assert (rtime < 1) and (status == 200), f'{url} had Response Time {round(rtime, 2)} ({status})'


@pytest.mark.cicd
def test_adjacency_response(client):
    """Test ZCTA3 Adjacency"""

    response_012 = client.get('/api/v2/demographics')
    response_data = decompress_response_data(response_012)
    expected_adjacent_mids = set(
        [
            'ZCTA3 013',
            'ZCTA3 052',
            'ZCTA3 053',
            'ZCTA3 125',
            'ZCTA3 120',
            'ZCTA3 060',
            'ZCTA3 121',
            'ZCTA3 010',
        ]
    )

    assert set(response_data['data']['ZCTA3 012']['adjacency']) == expected_adjacent_mids, 'Unexpected Adjacency Results!'
