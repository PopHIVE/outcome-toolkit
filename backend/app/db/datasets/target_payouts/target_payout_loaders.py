import pandas as pd
from typing import List
from sqlalchemy.engine import Row
from db.datasets.target_payouts.target_payout_tables import TargetPayoutRate
from app.db.database import registry

@registry.register('load_target_payouts', version='1.0')
def load_target_payouts(input_file_fr: str) -> List[Row]:
    """ETL Script to Load Target Payout Rate Data."""
    df = pd.read_csv(input_file_fr)
    records = []
    for index, row in df.iterrows():
        records.append(
            TargetPayoutRate(
                outcome=row.outcome,
                period=row.period,
                minimum_payout=row.minimum_payout,
                maximum_payout=row.maximum_payout,
                target_rate=row.target_rate
            )
        )
    return records

