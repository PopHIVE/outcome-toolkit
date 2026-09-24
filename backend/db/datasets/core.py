from app.db.database import db_session
from db.base import Base
from typing import List
from sqlalchemy.engine import Row
from sqlalchemy import (
    Column,
    String,
    or_,
    and_,
    func,
    text,
    literal,
)
from sqlalchemy.orm import relationship

from db.datasets.alcohol.alcohol_tables import NEMSISAlcohol, NEMSISAlcohol_v2
from db.datasets.ascvd.ascvd_tables import ASCVDScore, ASCVDScore_v2
from db.datasets.demographics.demographics_tables import (
    CBDemographics,
    CBACSEstimates,
)
from db.datasets.geoms.geoms_tables import CBGeom, CBGeomIndex, AdjacencyEdgeList
from db.datasets.opioid.opioid_tables import NEMSISOpioid, NEMSISOpioid_v2
from db.datasets.soc.soc_tables import AggregatedSOCV1, AggregatedSOCV2

from app.configs.settings import GeometrySettings
from app.configs.consts import ValidOutcomes
from app.ext.exceptions.errors import InvalidOutcome
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.datasets.common_imports import Project, ProjectAreaAssociation


class Area(Base):
    """
    This is the Main touchpoint into the datasets. A row in this table represents a single area
    either STATE, COUNTY, ZCTA3, ZCTA5.

    Examples:

      >>> area = db_session.query(Area).filter(Area.mid=='ZCTA5 01267')
      >>> area.demographics -> List[Demographic] Data
      >>> area.geoms -> Geometry Data
      ...

      Any Table with a mixin CoreDataTable can be joined via 'relationship'.

    """

    __tablename__ = 'area'
    mid = Column(String(32), primary_key=True)
    type = Column(String(16))

    projects = relationship("Project", secondary="project_area_associations", back_populates="areas")


    alcohol = relationship(
        NEMSISAlcohol,
        order_by=(NEMSISAlcohol.end_date.desc(), NEMSISAlcohol.start_date.asc()),
        uselist=True,
    )

    alcohol_v2 = relationship(
        NEMSISAlcohol_v2,
        order_by=(NEMSISAlcohol_v2.end_date.desc(), NEMSISAlcohol_v2.start_date.asc()),
        uselist=True,
    )

    ascvd = relationship(
        ASCVDScore,
        order_by=(ASCVDScore.end_date.desc(), ASCVDScore.start_date.asc()),
        uselist=True,
    )

    ascvd_v2 = relationship(
        ASCVDScore_v2,
        order_by=(ASCVDScore_v2.end_date.desc(), ASCVDScore_v2.start_date.asc()),
        uselist=True,
    )

    opioid = relationship(
        NEMSISOpioid,
        order_by=(NEMSISOpioid.end_date.desc(), NEMSISOpioid.start_date.asc()),
        uselist=True,
    )

    opioid_v2 = relationship(
        NEMSISOpioid_v2,
        order_by=(NEMSISOpioid_v2.end_date.desc(), NEMSISOpioid_v2.start_date.asc()),
        uselist=True,
    )

    soc = relationship(
        AggregatedSOCV1,
        order_by=(AggregatedSOCV1.end_date.desc(), AggregatedSOCV1.start_date.asc()),
        uselist=True,
    )

    soc_v2 = relationship(
        AggregatedSOCV2,
        order_by=(AggregatedSOCV2.end_date.desc(), AggregatedSOCV2.start_date.asc()),
        uselist=True,
    )

    adjacencies = relationship(
        AdjacencyEdgeList,
        primaryjoin=and_(
            mid == AdjacencyEdgeList.mid,
            AdjacencyEdgeList.distance <= GeometrySettings.ADJACENCY_TOLERANCE_METERS,
        ),
        uselist=True,
    )

    intersections = relationship(
        CBGeomIndex,
        primaryjoin=or_(
            mid == CBGeomIndex.zcta3_mid,
            mid == CBGeomIndex.zcta5_mid,
            mid == CBGeomIndex.county_mid,
            mid == CBGeomIndex.state_mid,
        ),
        uselist=True,
    )

    demographics = relationship(
        CBDemographics,
        order_by=(CBDemographics.end_date.desc(), CBDemographics.start_date.desc()),
        uselist=True,
    )

    income = relationship(
        CBACSEstimates,
        order_by=(CBACSEstimates.end_date.desc(), CBACSEstimates.start_date.desc()),
        uselist=True,
    )

    geoms = relationship(CBGeom, uselist=False)

    @classmethod
    def query_by_mids(cls, mids: List[str], geography: str = None) -> List[Row]:
        """Query by MIDS and Geography

        Parameters
        ----------
        mids : List[str]
        geography : str

        Returns
        -------
        List[Row]
            List of Rows that meet the criteria.
        """

        results = db_session.query(Area).filter(Area.mid.in_(mids))

        if geography is not None:
            results = results.filter(Area.type == geography)

        return results.all()

    @classmethod
    def query_by_state_usps(cls, state_usps: List[str], geography: str) -> List[Row]:
        """Query by State Two Letter Abbreviation and Geography

        Parameters
        ----------
        state_usps : List[str]
        geography : str

        Returns
        -------
        List[Row]
            List of Rows that meet the criteria.
        """

        results = (
            db_session.query(Area)
            .filter(Area.type == geography)
            .filter(Area.intersections.any(CBGeomIndex.state_usps.in_(state_usps)))
            .all()
        )
        return results

    @classmethod
    def query_by_geography(cls, geography: str) -> List[Row]:
        """Query by Geography

        Parameters
        ----------
        geography : str

        Returns
        -------
        List[Row]
            List of Rows that meet have that geography type.
        """

        results = db_session.query(Area).filter(Area.type == geography).all()
        return results
    
    @classmethod
    def query_data_details(cls, outcome:str) -> Row:
        """Query an outcome for data details.
         
        Parameters
        ----------
        outcome : str
        
        Returns
        -------
        Row
            Row containing criteria for data details.
        """

        if outcome == ValidOutcomes.ALCOHOL:
            results = db_session.query(
                literal(ValidOutcomes.ALCOHOL).label('outcome'),
                func.min(NEMSISAlcohol_v2.start_date).label('earliest_date'),
                func.max(NEMSISAlcohol_v2.end_date).label('latest_date'),
                func.max(func.to_date(NEMSISAlcohol_v2.data_release, text("'mon YYYY'"))).label('data_release')
            ).filter(NEMSISAlcohol_v2.alcohol_rate.isnot(None)).one()
        elif outcome == ValidOutcomes.CARDIO:
            results = db_session.query(
                literal(ValidOutcomes.CARDIO).label('outcome'),
                func.min(ASCVDScore_v2.start_date).label('earliest_date'),
                func.max(ASCVDScore_v2.end_date).label('latest_date'),
                func.max(func.to_date(ASCVDScore_v2.data_release, text("'mon YYYY'"))).label('data_release')
            ).filter(ASCVDScore_v2.total_mean.isnot(None)).one()
        elif outcome == ValidOutcomes.OPIOID:
            results = db_session.query(
                literal(ValidOutcomes.OPIOID).label('outcome'),
                func.min(NEMSISOpioid_v2.start_date).label('earliest_date'),
                func.max(NEMSISOpioid_v2.end_date).label('latest_date'),
                func.max(func.to_date(NEMSISOpioid_v2.data_release, text("'mon YYYY'"))).label('data_release')
            ).filter(NEMSISOpioid_v2.opioid_rate.isnot(None)).one()
        elif outcome == ValidOutcomes.SOC:
            results = db_session.query(
                literal(ValidOutcomes.SOC).label('outcome'),
                func.min(AggregatedSOCV2.start_date).label('earliest_date'),
                func.max(AggregatedSOCV2.end_date).label('latest_date'),
                func.max(func.to_date(AggregatedSOCV2.data_release, text("'mon YYYY'"))).label('data_release')
            ).filter(AggregatedSOCV2.any_soc_rate.isnot(None)).one()

        return results

    @classmethod
    def query(
        cls,
        geography: str,
        mids: List[str] = None,
        state_usps: List[str] = None,
    ) -> List[Row]:
        """Query by geography (required), MIDS (optional), and State Two-Letter
        Abbrevation (optional). If no MIDS or State USPS are provided then it will not filter
        on those attributes and return all.

        Parameters
        ----------
        geography : str
        mids : List[str], optional
        state_usps : List[str], optional

        Returns
        -------
        List[Row]
            List of Rows that meet the criteria.
        """

        mids = [] if mids is None else mids
        state_usps = [] if mids is None else state_usps

        results = db_session.query(Area).filter(Area.type == geography)

        if len(state_usps) > 0:
            results = results.filter(Area.intersections.any(CBGeomIndex.state_usps.in_(state_usps)))
        if len(mids) > 0:
            results = results.filter(Area.mid.in_(mids))

        return results.all()

    @classmethod
    def query_outcome(cls, outcome: str, mids: List[str] = None, include_aggregate: bool = True):
        mids = [] if mids is None else mids

        areas = Area.query_by_mids(mids)

        for area in areas:
            if outcome == ValidOutcomes.ALCOHOL:
                if include_aggregate:
                    for outcome_row in area.alcohol:
                        yield outcome_row

                else:
                    for outcome_row in area.alcohol_v2:
                        yield outcome_row

            elif outcome == ValidOutcomes.CARDIO:
                if include_aggregate:
                    for outcome_row in area.ascvd:
                        yield outcome_row
                else:
                    for outcome_row in area.ascvd_v2:
                        yield outcome_row

            elif outcome == ValidOutcomes.OPIOID:
                if include_aggregate:
                    for outcome_row in area.opioid:
                        yield outcome_row

                else:
                    for outcome_row in area.opioid_v2:
                        yield outcome_row

            elif outcome == ValidOutcomes.SOC:
                if include_aggregate:
                    for outcome_row in area.soc:
                        yield outcome_row
                else:
                    for outcome_row in area.soc_v2:
                        yield outcome_row

            elif outcome == 'demographics':
                for outcome_row in area.demographics:
                    yield outcome_row

            elif outcome == 'income':
                for outcome_row in area.income:
                    yield outcome_row

            else:
                raise InvalidOutcome(outcome)

    @classmethod
    def outcome_relationships(cls, outcome: str):
        if outcome == ValidOutcomes.ALCOHOL:
            return Area.alcohol, NEMSISAlcohol

        elif outcome == ValidOutcomes.CARDIO:
            return Area.ascvd_v2, ASCVDScore_v2

        elif outcome == ValidOutcomes.OPIOID:
            return Area.opioid, NEMSISOpioid

        elif outcome == ValidOutcomes.SOC:
            return Area.soc_v2, AggregatedSOCV2

        else:
            raise InvalidOutcome(outcome)
