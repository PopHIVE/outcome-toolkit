import gzip
import zipfile
import pandas as pd
from flask import make_response, json, Response
import shapely.wkt
from geojson import Feature
from sqlalchemy import inspect
from sqlalchemy.engine import Row
from typing import Dict, Any, List, Tuple
from datetime import datetime
import calendar
from app.ext.exceptions.errors import InvalidDatetime

MONTH_ABBREV = {month.lower(): index for index, month in enumerate(calendar.month_abbr) if month}


def serialize_row(row: Row) -> Dict[str, Any]:
    """
    Convert an SQLAlchemy row to a Serializable Dictionary.

    Parameters
    ----------
    row: Row
        The row object to serialize.

    Returns
    -------
    Dict[str, Any]
        Dictionary Format of the Row

    """
    return {c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs}


def row_to_feature(row: Row) -> Feature:
    """
    Convert an SQLAlchemy row to a GeoJSON Feature.

    Parameters
    ----------
    row: Row
        The row object to convert to a Feature.

    Returns
    -------
    Feature
        GeoJSON Feature.

    """
    data = row._asdict()
    feature = Feature(
        id=data['geoid'],
        geometry=shapely.wkt.loads(data.pop('geometry')),
        properties=data,
    )
    return feature


def dict_to_feature(data: Dict[str, Any], props: List[str] = None, tolerance: float = None) -> Feature:
    """
    Convert a Dictionary to a GeoJSON Feature.

    Parameters
    ----------
    data: Dict[str, Any]
        The dictionary to convert to a GeoJSON Feature.

    tolerance: float
        If not None, it will simplify the geometry

    Returns
    -------
    Feature
        GeoJSON Feature.

    """

    geom = shapely.wkt.loads(data.get('geometry'))

    if tolerance is not None:
        geom = geom.simplify(tolerance=tolerance)

    if props is None:
        props = data.keys()

    feature = Feature(
        id=data['mid'],
        geometry=geom,
        properties={k: v for k, v in data.items() if ((k != 'geometry') and (k in props))},
    )
    return feature


def compress_content(content: str, compressionlevel: int = 9) -> Response:
    gzipped_content = gzip.compress(content.encode('utf8'), compressionlevel)
    response = make_response(gzipped_content)
    response.headers['Content-length'] = len(gzipped_content)
    response.headers['Content-Encoding'] = 'gzip'
    return response


def compress_json_response(json_data: Dict, compressionlevel: int = 9) -> Response:
    return compress_content(json.dumps(json_data), compressionlevel)


def decompress_response_data(response: Response) -> Dict:
    if response.headers['Content-Encoding'] == 'gzip':
        return json.loads(gzip.decompress(response.data))

    return response.json


def extract_sas_file_from_zipfile(zip_file: str, file_name: str, encoding: str = 'utf-8'):
    archive = zipfile.ZipFile(zip_file, 'r')
    try:
        with archive.open(file_name) as f:
            df = pd.read_sas(f, format='sas7bdat', encoding=encoding)
            df['ROW_NUM'] = (df.index + 1).astype(str)
    except Exception as e:
        print(f"Files in ZipFile: {archive.namelist()}")
        raise e
    
    return df


def first_day_month(year, month):
    return datetime(year, month, 1)


def last_day_month(year, month):
    return datetime(year, month, calendar.monthrange(year, month)[1])


def format_time_interval(start_date: datetime, end_date: datetime) -> str:
    return f'{start_date.isoformat()}|{end_date.isoformat()}'


def parse_time(time_str: str) -> datetime:
    try:
        parsed_datetime = datetime.fromisoformat(time_str)
    except Exception:
        raise InvalidDatetime(time_str)

    return parsed_datetime


def month_to_number(month: str) -> int:
    return MONTH_ABBREV[month.lower()]


def parse_yearmon_to_start_end(yearmon: str) -> Tuple[int, int]:
    month = month_to_number(yearmon[:3])
    year = int(f'20{yearmon[-2:]}')
    return first_day_month(year, month), last_day_month(year, month)
