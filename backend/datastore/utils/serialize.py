import zipfile
import dagster as dg
import pandas as pd
from typing import Optional, Tuple, Union, Dict, Any
from datetime import datetime
import calendar

MONTH_ABBREV = {month.lower(): index for index, month in enumerate(calendar.month_abbr) if month}

def first_day_month(year, month):
    return datetime(year, month, 1)

def last_day_month(year, month):
    return datetime(year, month, calendar.monthrange(year, month)[1])

def month_to_number(month: str) -> int:
    return MONTH_ABBREV[month.lower()]


def parse_yearmon_to_start_end(yearmon: str) -> Tuple[int, int]:
    month = month_to_number(yearmon[:3])
    year = int(f'20{yearmon[-2:]}')
    return first_day_month(year, month), last_day_month(year, month)

def extract_excel_file_from_zip(
    archive_path: str, file_name: str, sheet_name: Optional[Union[str, int]] = 0
) -> pd.DataFrame:
    """Extract an Excel Spreadsheet from a Zipfile.

    Parameters
    ----------
    archive_path : str
    file_name : str
    sheet_name : Optional[Union[str, int]], optional, by default 0

    Returns
    -------
    pd.DataFrame

    """
    archive = zipfile.ZipFile(archive_path, 'r')
    with archive.open(file_name, 'r') as file:
        df = pd.read_excel(file, sheet_name=sheet_name)

    return df

def extract_sas_file_from_zipfile(zip_file: str, file_name: str, encoding: str = 'utf-8') -> pd.DataFrame:
    """
    Extract a SAS file from a Zipfile and add a 'ROW_NUM' column.

    Parameters:
    zip_file (str): The path to the Zipfile.
    file_name (str): The name of the SAS file within the Zipfile.
    encoding (str, optional): The encoding of the SAS file. Default is 'utf-8'.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the data from the SAS file. The DataFrame will have an additional 'ROW_NUM' column.

    Raises:
    Exception: If there is an error reading the SAS file from the Zipfile.
    """
    archive = zipfile.ZipFile(zip_file, 'r')
    try:
        with archive.open(file_name) as f:
            df = pd.read_sas(f, format='sas7bdat', encoding=encoding)
            df['ROW_NUM'] = (df.index + 1).astype(str)
    except Exception as e:
        print(f"Files in ZipFile: {archive.namelist()}")
        raise e

    return df


def expand_first_day_of_month(yyyymm: pd.Series) -> pd.Series:
    return yyyymm.apply(lambda x: first_day_month(*x))


def expand_last_day_of_month(yyyymm: pd.Series) -> pd.Series:
    return yyyymm.apply(lambda x: last_day_month(*x))


def first_day_month(year, month):
    return datetime(year, month, 1)


def last_day_month(year, month):
    return datetime(year, month, calendar.monthrange(year, month)[1])


def dict_to_partition_key(d: Dict[str, str]) -> str:
    return "||".join([f"{k}|{v}" for k,v in d.items()])


def partition_key_to_dict(key: str) -> Dict[str, str]:
    return {pair.split('|')[0] : pair.split('|')[1] for pair in key.split("||")}


def df_to_metadata(df: pd.DataFrame, n: int = 10) -> Dict[str, Any]:
    """ Convert DF to Dagster Metadata. """
    metadata = {
        'num_records': len(df),
        'preview': dg.MetadataValue.md(df.head(n).to_markdown())
    }
    return metadata
    