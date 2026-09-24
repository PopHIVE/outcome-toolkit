from dagster import ConfigurableResource, InitResourceContext
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from pydantic import PrivateAttr


class PostgresConnectionResource(ConfigurableResource):
    username: str
    password: str
    database: str
    host: str
    port: str

    _engine: Engine = PrivateAttr()
    _session_maker: sessionmaker = PrivateAttr()

    def setup_for_execution(self, context: InitResourceContext) -> None:
        self._engine = create_engine(self.database_uri)
        self._session_maker = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self._engine))

    @property
    def session(self) -> Session:
        return self._session_maker

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def database_uri(self) -> str:
        return f'postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'
