from app.models.common import OutcomesEnum, ProjectPerformerType
from db.base import Base
from sqlalchemy import Column, Date, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.datasets.common_imports import User, UserProjectAssociation, Area, ProjectAreaAssociation, ProjectMeasurement



class Project(Base):
    __tablename__ = "project"
    __loader_key__ = "projects"
    __fill_nulls__ = False


    id = Column(String, primary_key=True)
    project_name = Column(String, nullable=False)
    performance_period_from = Column(Date, nullable=False)
    performance_period_to = Column(Date, nullable=False)
    outcome = Column(SQLAlchemyEnum(OutcomesEnum), nullable=False)
    performer_type = Column(SQLAlchemyEnum(ProjectPerformerType), nullable=False)

    
    project_measurements = relationship(
        "ProjectMeasurement",
        back_populates="project"
    )

    users = relationship(
        "User",
        secondary="user_project_associations",
        back_populates="projects"
    )

    areas = relationship(
        "Area",
        secondary="project_area_associations",
        back_populates="projects"
    )