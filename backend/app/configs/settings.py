import os
from dataclasses import dataclass
from app.db.data_dictionary import DataDictionary


DEPLOYMENT_ENV = os.getenv('DEPLOYMENT_ENV')

@dataclass
class FlaskConfig:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')


@dataclass
class PostgresSettings:
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DB = os.getenv('POSTGRES_DB')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT')

    DATABASE_URI = (
        f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    )


@dataclass
class GeometrySettings:
    # Geometry Settings (orig default 0.0005)
    GEOMETRY_TOLERANCE = 0.001
    ADJACENCY_TOLERANCE_METERS = 5632.7  # 3.5 Miles


# Cache Configs
@dataclass
class CacheSettings:
    CACHE_TYPE: str = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT: int = 7200
    CACHE_IGNORE_ERRORS: bool = False
    CACHE_THRESHOLD: int = 200

# (local|cicd|sandbox|dev|demo|prod)
USERS_AND_PROJECTS_DIRECTORY_MAPPINGS = {
    'local': 'fake-users-projects',
    'cicd': 'test-users-projects',
    'sandbox': 'fake-users-projects',
    'dev': 'fake-users-projects',
    'prod': 'real-users-projects',
}
@dataclass
class Directories:
    DOCS_DIRECTORY: str = './docs'
    CONF_DIRECTORY: str = 'app/configs'
    STATIC_DIRECTORY: str = 'app/static'
    USERS_AND_PROJECTS_DIRECTORY: str = USERS_AND_PROJECTS_DIRECTORY_MAPPINGS[DEPLOYMENT_ENV]


DATA_DICTIONARY = DataDictionary(os.path.join(Directories.DOCS_DIRECTORY, 'DATA-DICTIONARY.xlsx'))
MAPPINGS = DATA_DICTIONARY.mappings
