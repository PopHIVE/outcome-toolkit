from db.base import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.datasets.common_imports import MidMetric

class UserProjectAssociation(Base):
    __tablename__ = 'user_project_associations'
    __loader_key__ = 'user_project_associations'
    __fill_nulls__ = False

    user_id = Column(String, ForeignKey("user.id"), primary_key=True)
    project_id = Column(String, ForeignKey("project.id"), primary_key=True)


class ProjectAreaAssociation(Base):
    __tablename__ = 'project_area_associations'
    __loader_key__ = 'project_area_associations'
    __fill_nulls__ = False

    project_id = Column(String, ForeignKey("project.id"), primary_key=True)
    area_mid = Column(String(32), ForeignKey("area.mid"), primary_key=True)
    
    # Relationship to metrics that use this project-area combination
    mid_metrics = relationship(
        "MidMetric",
        foreign_keys="[MidMetric.project_id, MidMetric.area_mid]",
        back_populates="project_area_association"
    )
