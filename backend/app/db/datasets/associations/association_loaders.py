import pandas as pd
from typing import List
from sqlalchemy.engine import Row
from db.datasets.associations.association_tables import ProjectAreaAssociation, UserProjectAssociation
from app.db.database import registry

@registry.register('load_project_areas', version='1.0')
def load_project_areas(input_file_fr: str) -> List[Row]:
    """ETL Script to Load Project-Area Associations."""
    df = pd.read_csv(input_file_fr, dtype=str)
    records = []
    for index, row in df.iterrows():
        records.append(
            ProjectAreaAssociation(
                project_id=row.project_id,
                area_mid=row.area_mid
            )
        )
    return records

@registry.register('load_user_projects', version='1.0')
def load_user_projects(input_file_fr: str) -> List[Row]:
    """ETL Script to Load User-Project Associations."""
    df = pd.read_csv(input_file_fr, dtype=str)
    records = []
    for index, row in df.iterrows():
        records.append(
            UserProjectAssociation(
                user_id=row.user_id,
                project_id=row.project_id
            )
        )
    return records