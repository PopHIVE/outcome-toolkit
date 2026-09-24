import shapely.wkt
from geojson import Feature
from typing import List
from app.db.database import db_session
from db.base import Base
from db.datasets.mixins import CoreDataTable, CoreAuditColumns
from sqlalchemy.engine import Row
from sqlalchemy import ForeignKey, Column, Double, Integer, Text, String, or_, tuple_, and_
from app.configs.settings import GeometrySettings
from app.configs.consts import ValidGeographies


class AdjacencyEdgeList(CoreDataTable, Base):
    """
    The represents the table for Adjacency Edge List Data for contiguousness.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'cb_geos_adjacency'
    __loader_key__ = 'adjacency_edge_list'
    __data_dictionary_key__ = 'cb_geos_adjacency'
    __fill_nulls__ = False

    adjacent_mid = Column(String(16), primary_key=True)
    distance = Column(Double)

    @classmethod
    def query(
        cls,
        geography: str,
        mids: List[str] = None,
        distance_m: float = GeometrySettings.ADJACENCY_TOLERANCE_METERS,
    ) -> List[Row]:
        """Filter adjacenct edges based on geography AND/OR MIDS and Distance.

        Parameters
        ----------
        geography : str
        mids: List[str]
        distance_m: float

        Returns
        -------
        List[Row]
        """

        mids = [] if mids is None else mids

        results = (
            db_session.query(AdjacencyEdgeList)
            .filter(AdjacencyEdgeList.type == geography)
            .filter(AdjacencyEdgeList.distance <= distance_m)
        )

        if len(mids) > 0:
            results = results.filter(AdjacencyEdgeList.mid.in_(mids))

        return results.all()


class CBGeomIndex(CoreAuditColumns, Base):
    """
    This Table represents spatial intersections between counties and ZCTA5s.

    It is generated based on the Census Relationships Files.

    https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.2020.htmlv
    """

    __tablename__ = 'cb_geom_index'
    __loader_key__ = 'cb_geom_index'
    __data_dictionary_key__ = 'cb_geoid_index'
    __fill_nulls__ = False

    id = Column(Integer, primary_key=True)
    zcta3_name = Column(Text)
    zcta3_geoid = Column(String(16))
    zcta3_mid = Column(String(32), ForeignKey('area.mid'), index=True)
    zcta5_name = Column(Text)
    zcta5_geoid = Column(String(16))
    zcta5_mid = Column(String(32), ForeignKey('area.mid'), index=True)
    county_namelsad = Column(Text)
    county_name = Column(Text)
    county_fips = Column(Text)
    county_geoid = Column(String(16))
    county_mid = Column(String(32), ForeignKey('area.mid'), index=True)
    state_fips = Column(Text)
    state_usps = Column(Text, index=True)
    state_name = Column(Text)
    state_geoid = Column(String(16))
    state_mid = Column(String(32), ForeignKey('area.mid'), index=True)

    @classmethod
    def query_intersections(
        cls,
        source_geography: str,
        target_geography: str,
        mids: List[str] = None
    ) -> List[Row]:
        """ Get intersections of different level.

        Parameters
        ----------
        source_geography : str
        target_geography : str
        mids: List[str]

        Returns
        -------
        List[Row]
        """

        mids = [] if mids is None else mids

        results = (
            db_session.query(
                CBGeomIndex.get_geography_mid_column(source_geography),
                CBGeomIndex.get_geography_mid_column(target_geography)
            ).filter(
                and_(
                    CBGeomIndex.get_geography_mid_column(source_geography).is_not(None),
                    CBGeomIndex.get_geography_mid_column(target_geography).is_not(None)
                )
                
            ).distinct()
        )

        if len(mids) > 0:
            results = results.filter(
                CBGeomIndex.get_geography_mid_column(source_geography).in_(mids)
            )

        return results.all()
    
    @classmethod
    def get_geography_mid_column(cls, geography: str) -> Column:
        if geography == ValidGeographies.STATE:
            return CBGeomIndex.state_mid
        elif geography == ValidGeographies.COUNTY:
            return CBGeomIndex.county_mid
        elif geography == ValidGeographies.ZCTA3:
            return CBGeomIndex.zcta3_mid
        elif geography == ValidGeographies.ZCTA5:
            return CBGeomIndex.zcta5_mid
        raise ValueError



class CBGeom(CoreDataTable, Base):
    """
    The represents the table for Census Geometries.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'cb_geos'
    __loader_key__ = 'cb_geos'
    __data_dictionary_key__ = 'cb_geos'
    __fill_nulls__ = False

    geoid = Column(String(16))
    affgeoid = Column(String(16))
    geometry = Column(Text)

    def to_feature(self) -> Feature:
        """
        Convert to GeoJSON Feature.

        Returns
        -------
        Feature

        """

        feature = Feature(
            id=self.id,
            geometry=shapely.wkt.loads(self.geometry),
            properties=self.serialize(include_geom=False),
        )
        return feature

    def __repr__(self) -> str:
        return f'<CBGeom {self.geoid!r} ({self.type!r})>'
