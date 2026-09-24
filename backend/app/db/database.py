from typing import List, Any
from app.configs.settings import PostgresSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from db.base import Base

# SqlAlchemy Engine
engine = create_engine(PostgresSettings.DATABASE_URI)

# Flask recommends a scoped_session object to manage multiple
# connections using the sessionmaker factory.
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base.query = db_session.query_property()


# NOTE: Necessary to import here in order to avoid circular import error for 'db_session'
from app.db.datasets.registry import LoaderRegistry

# Common Registry
registry = LoaderRegistry()


def init_db(delete=False) -> None:
    """Initialize the Postgres Database"""

    # NOTE: Possibly necessary to define 'tables' here to avoid a sqlalchemy/psycopg2 error
    tables = registered_tables()

    if delete:
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)


def registered_tables() -> List[Any]:
    """Return a list of registered tables."""

    from db.datasets.alcohol.alcohol_tables import NEMSISAlcohol, NEMSISAlcohol_v2
    from db.datasets.ascvd.ascvd_tables import ASCVDScore, ASCVDScore_v2
    from db.datasets.demographics.demographics_tables import CBDemographics, CBACSEstimates
    from db.datasets.geoms.geoms_tables import CBGeom, CBGeomIndex, AdjacencyEdgeList
    from db.datasets.opioid.opioid_tables import NEMSISOpioid, Bins, NEMSISOpioid_v2
    from db.datasets.soc.soc_tables import RawSOCData, AggregatedSOCV1, AggregatedSOCV2
    from db.datasets.trendlines.trendline_tables import Trendlines
    from db.datasets.common_imports import Area, User, Project, ProjectAreaAssociation, UserProjectAssociation, TargetPayoutRate, MidMetric, ProjectMeasurement


    tables = [
        NEMSISAlcohol,
        ASCVDScore,
        ASCVDScore_v2,
        CBDemographics,
        CBACSEstimates,
        CBGeom,
        CBGeomIndex,
        AdjacencyEdgeList,
        NEMSISOpioid,
        Bins,
        RawSOCData,
        AggregatedSOCV1,
        AggregatedSOCV2,
        User,
        Project,
        ProjectAreaAssociation,
        UserProjectAssociation,
        TargetPayoutRate,
        ProjectMeasurement,
        MidMetric,
        Area,
        Trendlines,
        NEMSISOpioid_v2,
        NEMSISAlcohol_v2,
     
    ]

    return tables


def init_registry() -> None:
    """Imports all the registries."""

    from app.db.datasets.alcohol.alcohol_loaders import registry
    from app.db.datasets.ascvd.ascvd_loaders import registry
    from app.db.datasets.demographics.demographics_loaders import registry
    from app.db.datasets.geoms.geoms_loaders import registry
    from app.db.datasets.opioid.opioid_loaders import registry
    from app.db.datasets.soc.soc_loaders import registry
    from app.db.datasets.trendlines.trendline_loaders import registry
    from app.db.datasets.national.national_loaders import registry
    from app.db.datasets.national.moving_avg_loaders import registry
    from app.db.datasets.users.user_loaders import registry
    from app.db.datasets.projects.project_loaders import registry
    from app.db.datasets.target_payouts.target_payout_loaders import registry
    from app.db.datasets.associations.association_loaders import registry
    from app.db.datasets.metrics.payout_metric_loaders import registry
