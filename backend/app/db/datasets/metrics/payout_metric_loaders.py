import pandas as pd
from typing import List
from sqlalchemy.engine import Row
from db.datasets.metrics.payout_metrics_tables import MidMetric, ProjectMeasurement
from app.db.database import registry

@registry.register('load_project_measurements', version='1.0')
def load_project_measurements(input_file_fr: str) -> List[Row]:
    """ETL Script to Load Project Measurement Data."""
    df = pd.read_csv(input_file_fr)
    records = []
    for index, row in df.iterrows():
        records.append(
            ProjectMeasurement(
                project_id=row.project_id,
                period=row.period,
                date_of_payout=row.date_of_payout,
                project_metric=row.project_metric,
                national_metric=row.national_metric,
                actual_payout=row.actual_payout
            )
        )
    return records


@registry.register('load_mid_metrics', version='1.0')
def load_mid_metrics(input_file_fr: str) -> List[Row]:
    """ETL Script to Load MID Metrics Data."""
    df = pd.read_csv(input_file_fr)
    records = []
    for index, row in df.iterrows():
        records.append(
            MidMetric(
                project_id=row.project_id,
                period=row.period,  
                area_mid=row.area_mid,
                metric_value=row.metric_value
            )
        )
    return records