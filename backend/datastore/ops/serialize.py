import zipfile
import pandas as pd
from dagster import op, MetadataValue, OpExecutionContext
from datetime import datetime
import calendar


@op
def extract_excel_file_from_zip(context: OpExecutionContext, archive_path: str, file_name: str) -> pd.DataFrame:
    archive = zipfile.ZipFile(archive_path, 'r')
    with archive.open(file_name, 'r') as file:
        df = pd.read_excel(file, sheet_name=0)

    context.log.info(MetadataValue.md(df.head().to_markdown()))
    return df
