import pandas as pd
from typing import List
from sqlalchemy.engine import Row
from db.datasets.users.users_tables import User
from app.db.database import registry

@registry.register('load_users', version='2.0')
def load_users(input_file_fr: str) -> List[Row]:
    """ETL Script to Load User Data.

    Parameters
    ----------
    input_file_fr : str

    Returns
    -------
    List[Row]
        List of User rows to be inserted into the DB.
    """
    df = pd.read_csv(input_file_fr, dtype=str)
    records = []
    for index, row in df.iterrows():
        records.append(
            User(
                id=row.id,
                email=row.email,
                first_name=row.first_name,
                last_name=row.last_name,
                organization=row.organization,
                role=row.role
            )
        )
    return records