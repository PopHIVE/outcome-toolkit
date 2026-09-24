import os
import yaml
import argparse
from db.datasets.core import Area
from app.db.database import (
    init_db,
    db_session,
    registry,
    registered_tables,
    init_registry,
)
from app.configs.settings import Directories
from app.configs.consts import ValidMorpheusIDs
from app.utilities.loggerfactory import LoggerFactory


logger = LoggerFactory.getLogger(__name__, log_level='DEBUG')

parser = argparse.ArgumentParser(description='Setup DB')
parser.add_argument('-d', '--data', type=str, default='data/build')
parser.add_argument('-r', '--rebuild', action=argparse.BooleanOptionalAction, default=False)
parser.add_argument('-b', '--bundle', type=str)


def setup_db(datasources_root: str = 'data/build', data_bundle: str = None, delete: bool = False) -> None:
    """Executing this function will setup the DB. If delete=True it will clear out the db prior to ETL."""

    # Initialize the DB and Tables
    init_db(delete)

    with open(os.path.join(Directories.CONF_DIRECTORY, 'datasources.yml')) as stream:
        datasources = yaml.safe_load(stream)['datasources']

    # Load Valid MIDs into the Central Areas Table
    records = []
    for mid, type_ in ValidMorpheusIDs.mids():
        records.append(Area(mid=mid, type=type_))

    db_session.bulk_save_objects(records)
    db_session.commit()

    # Initialize Loaders For ETL
    tables = registered_tables()
    _ = init_registry()

    for table in tables:
        if db_session.query(table).count() == 0:
            logger.info(f'Loading Data for Table: {table.__tablename__}')
            registry.load_sources(
                datasources.get(table.__loader_key__),
                datasources_root,
                data_bundle=data_bundle,
                fill_nulls=table.__fill_nulls__,
            )
        logger.info(f'Table {table.__tablename__} now has {db_session.query(table).count()} rows.')

    registry.load_sources(
        datasources.get('national'),
        datasources_root,
        data_bundle=data_bundle, fill_nulls=False
    )

    registry.load_sources(
        datasources.get('fill_nemsis_rates'),
        datasources_root,
        data_bundle=data_bundle, fill_nulls=False
    )

    # Generate 6 mo Moving Averages
    registry.load_sources(
        datasources.get('moving_averages'),
        datasources_root,
        data_bundle=data_bundle,
        fill_nulls=False
    )


if __name__ == '__main__':
    args = parser.parse_args()
    setup_db(args.data, args.bundle.split('/')[-1], args.rebuild)
