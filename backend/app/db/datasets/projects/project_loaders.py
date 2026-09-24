import pandas as pd
from typing import List
from sqlalchemy.engine import Row
from db.datasets.projects.project_tables import Project
from app.db.database import registry


@registry.register('load_projects', version='1.0')
def load_projects(input_file_fr: str) -> List[Row]:
    """ETL Script to Load Project Data."""
    df = pd.read_csv(input_file_fr, dtype=str)
    records = []
    for index, row in df.iterrows():
        records.append(
            Project(
                id=row.id,
                project_name=row.project_name,
                performance_period_from=row.performance_period_from,
                performance_period_to=row.performance_period_to,
                outcome=row.outcome,
                performer_type=row.performer_type
            )
        )
    return records