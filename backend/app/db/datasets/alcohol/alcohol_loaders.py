import pandas as pd
from typing import List
from sqlalchemy.engine import Row
from app.utilities.serialize import (
    extract_sas_file_from_zipfile,
    last_day_month,
    first_day_month,
)
from db.datasets.alcohol.alcohol_tables import NEMSISAlcohol, NEMSISAlcohol_v2
from app.db.database import registry
from app.configs.consts import Replacements, ValidMorpheusIDs
from datetime import datetime


@registry.register('load_nemsis_alcohol_data', version='2.0')
def load_nemsis_alcohol_data(
    zip_file: str, file_name: str, geography: str, start_date: str, end_date: str
) -> List[Row]:
    """ETL Scripts to Load NEMSIS Alcohol Data.

    Parameters
    ----------
    zip_file : str
        Filepath to the ZIP Archive within the Data Bundle.
    file_name : str
        Filename of the NEMSIS Alcohol Data within the ZIP Archive.
    geography : str
        The geography

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)

    # TO DO: THIS FUNCTION NEEDS MODIFICATION TO SUPPORT STATE geographies
    df = extract_sas_file_from_zipfile(zip_file, file_name)
    df_wide = pd.pivot(
        df,
        index=['CountyName', 'CountyFIPS', 'population'],
        columns=['MeasureName'],
        values=['Rank', 'RankValue', 'ROW_NUM'],
    )
    df_wide.columns = [f'{pair[1]} ({pair[0]})' for pair in df_wide.columns]
    df_wide.reset_index(inplace=True)

    records = []
    for index, row in df_wide.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        record = NEMSISAlcohol(
            start_date=start_date,
            end_date=end_date,
            county_name=row['CountyName'],
            county_fips=row['CountyFIPS'],
            population_estimate=row['population'],
            alcohol_rate_rank=row['Alcohol Rate (Rank)'],
            alcohol_rate_rank_value=row['Alcohol Rate (RankValue)'],
            # Deprecated
            # avg_time_to_patient_rank=row['Average Time To Patient (Rank)'],
            # percent_not_transported_rank=row['Percent Not Transported (Rank)'],
            # avg_time_to_patient_rank_value=row['Average Time To Patient (RankValue)'],
            # percent_not_transported_rank_value=row['Percent Not Transported (RankValue)'],
            mid=f"{geography} {row['CountyFIPS']}",
            type=geography,
            source_file=file_name,
            row_num=','.join(
                map(
                    str,
                    [
                        # row['Average Time To Patient (ROW_NUM)'],
                        row['Alcohol Rate (ROW_NUM)'],
                        # row['Percent Not Transported (ROW_NUM)'],
                    ],
                )
            ),
        )
        records.append(record)

    return records


@registry.register('load_nemsis_alcohol_data_monthly', version='1.0')
def load_nemsis_alcohol_data_monthly(zip_file: str, file_name: str, geography: str) -> List[Row]:
    """ETL Scripts to Load NEMSIS Alcohol Data.

    Parameters
    ----------
    zip_file : str
        Filepath to the ZIP Archive within the Data Bundle.
    file_name : str
        Filename of the NEMSIS Opioid Data within the ZIP Archive.
    geography : str
        The geography

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    # TO DO: THIS FUNCTION NEEDS MODIFICATION TO SUPPORT STATE geographies
    df = extract_sas_file_from_zipfile(zip_file, file_name, encoding='latin1')
    df_wide = pd.pivot(
        df,
        index=['CountyName', 'CountyFIPS', 'population', 'Yearmonth'],
        columns=['MeasureName'],
        values=['Rank', 'RankValue', 'ROW_NUM'],
    )
    df_wide.columns = [f'{pair[1]} ({pair[0]})' for pair in df_wide.columns]
    df_wide.reset_index(inplace=True)

    records = []

    for index, row in df_wide.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        record = NEMSISAlcohol_v2(
            start_date=first_day_month(int(row['Yearmonth'][:4]), int(row['Yearmonth'][4:])),
            end_date=last_day_month(int(row['Yearmonth'][:4]), int(row['Yearmonth'][4:])),
            county_name=row['CountyName'],
            county_fips=row['CountyFIPS'],
            population_estimate=row['population'],
            alcohol_rate_rank=row['Alcohol Rate (Rank)'],
            alcohol_rate_rank_value=row['Alcohol Rate (RankValue)'],
            mid=f"{geography} {row['CountyFIPS']}",
            type=geography,
            source_file=file_name,
            row_num=','.join(
                map(
                    str,
                    [
                        # row['Average Time To Patient (ROW_NUM)'],
                        row['Alcohol Rate (ROW_NUM)'],
                        # row['Percent Not Transported (ROW_NUM)'],
                    ],
                )
            ),
        )
        records.append(record)

    return records


@registry.register('load_nemsis_alcohol_monthly_v2', version='1.0')
def load_nemsis_alcohol_monthly_v2(zip_file: str, file_name: str, rank_col: str, rank_val_col: str, geography: str) -> List[Row]:
    """ETL Scripts to Load NEMSIS Opioid Data.

    Parameters
    ----------
    zip_file : str
        Filepath to the ZIP Archive within the Data Bundle.
    file_name : str
        Filename of the NEMSIS Opioid Data within the ZIP Archive.
    rank_col: str
    rank_val_col: str
    geography : str
        The geography

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    df = extract_sas_file_from_zipfile(zip_file, file_name, encoding='latin1')

    # Since there is variation in this column
    if 'CountyFIPS' in df.columns:
        df.rename(columns={'CountyFIPS': 'Countyfips'}, inplace=True)

    records = []

    for index, row in df.replace(Replacements.JAVASCRIPT_SAFE).iterrows():

        if not ValidMorpheusIDs.is_valid(f"{geography} {row['Countyfips']}"):
            continue

        record = NEMSISAlcohol_v2(
            start_date=first_day_month(int(row['Yearmonth'][:4]), int(row['Yearmonth'][4:])),
            end_date=last_day_month(int(row['Yearmonth'][:4]), int(row['Yearmonth'][4:])),
            county_name=row['Countyfips'],
            county_fips=row['Countyfips'],
            population_estimate=None,
            alcohol_rate_rank=row[rank_col],
            alcohol_rate_rank_value=row[rank_val_col],
            mid=f"{geography} {row['Countyfips']}",
            type=geography,
            source_file=file_name,
            row_num=index
        )
        records.append(record)

    return records
