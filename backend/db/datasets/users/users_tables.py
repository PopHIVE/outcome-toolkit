from db.base import Base
from sqlalchemy import Column, String, Enum as SQLAlchemyEnum 
from sqlalchemy.orm import relationship
from app.models.common import UserRole
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from db.datasets.common_imports import Project, UserProjectAssociation


class User(Base):
    __tablename__ = "user"
    __loader_key__ = "users"
    __fill_nulls__ = False

    id = Column(String, primary_key=True) 
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.PROJECT_MEMBER)

    projects = relationship("Project", secondary="user_project_associations", back_populates="users")

