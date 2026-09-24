import pytest
from app.factory import create_app


@pytest.fixture
def app():
    app = create_app()
    yield app
    # teardown here


@pytest.fixture
def client(app):
    return app.test_client()


GEOMETRY_API_URLS = [
    '/api/state/geometries',
    '/api/county/geometries',
    '/api/zcta3/geometries',
    '/api/zcta5/geometries',
]

PROPERTIES_API_URLS = [
    '/api/state/properties',
    '/api/county/properties',
    '/api/zcta3/properties',
    '/api/zcta5/properties',
]

MIDS = [
    ['STATE 55', 'STATE 01'],
    ['COUNTY 25023', 'COUNTY 25003'],
    ['ZCTA3 012'],
    ['ZCTA5 01267'],
]
