from db.base import Base
from sqlalchemy import Column, String, Float, Date, ForeignKey, ForeignKeyConstraint, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.models.common import PayoutPeriod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.datasets.common_imports import Project

class ProjectMeasurement(Base):
    __tablename__ = "project_measurement"
    __loader_key__ = "project_measurements"
    __fill_nulls__ = False

    project_id = Column(String, ForeignKey("project.id"), primary_key=True)
    period = Column(SQLAlchemyEnum(PayoutPeriod), primary_key=True)

    date_of_payout = Column(Date, nullable=False)  
    actual_payout = Column(Float, nullable=False)

    project_metric = Column(Float, nullable=False)
    national_metric = Column(Float, nullable=False)
    
    project = relationship("Project", back_populates="project_measurements")
    
    mid_metrics = relationship(
        "MidMetric",
        back_populates="project_measurement",
        cascade="all, delete-orphan"
    )

class MidMetric(Base):
    __tablename__ = "mid_metric"
    __loader_key__ = "mid_metrics"
    __fill_nulls__ = False
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'period'],
            ['project_measurement.project_id', 'project_measurement.period']
        ),
        ForeignKeyConstraint(
            ['project_id', 'area_mid'],
            ['project_area_associations.project_id', 'project_area_associations.area_mid']
        ),
    )

    project_id = Column(String, primary_key=True)
    period = Column(SQLAlchemyEnum(PayoutPeriod), primary_key=True)
    area_mid = Column(String(32), primary_key=True)
    metric_value = Column(Float, nullable=False)
    
    project_measurement = relationship(
        "ProjectMeasurement",
        back_populates="mid_metrics"
    )
    
    project_area_association = relationship(
        "ProjectAreaAssociation",
        foreign_keys=[project_id, area_mid],
        back_populates="mid_metrics"
    )