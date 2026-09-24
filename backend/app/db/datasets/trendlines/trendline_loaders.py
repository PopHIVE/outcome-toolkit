import pandas as pd
from typing import List
from sqlalchemy.engine import Row
from app.utilities.serialize import (
    extract_sas_file_from_zipfile,
    last_day_month,
    first_day_month,
)
from app.db.database import registry
from db.datasets.trendlines.trendline_tables import Trendlines


@registry.register('load_nemsis_trendlines', version='2.0')
def load_nemsis_trendlines(
    trendline_zip_file: str,
    trendline_datafile: str,
    county_data_2022_zip_file: str,
    county_data_2022_datafile: str,
    county_data_2023_zip_file: str,
    county_data_2023_datafile: str,
    outcome: str,
    outcome_col: str,
) -> List[Row]:
    trendlines = extract_sas_file_from_zipfile(trendline_zip_file, trendline_datafile)
    county_2022 = extract_sas_file_from_zipfile(county_data_2022_zip_file, county_data_2022_datafile)
    county_2023 = extract_sas_file_from_zipfile(county_data_2023_zip_file, county_data_2023_datafile)

    population_2022 = county_2022.loc[county_2022.Rank >= 0].population.sum()
    population_2023 = county_2022.loc[county_2023.Rank >= 0].population.sum()

    denominators = {
        2022: population_2022,
        2023: population_2023,
    }

    records = []

    MEASURE_CONVERTER_RATES = {
        'MonthlyOpioidTotal': 'opioid_rate',
        'MonthlyAlcoholTotal': 'alcohol_rate',
    }

    for index, row in trendlines.iterrows():
        year = int(row['Year'])
        month = int(row['month'])

        records.append(
            Trendlines(
                start_date=first_day_month(year, month),
                end_date=last_day_month(year, month),
                value=(row[outcome_col] / denominators[year]) * 100_000,
                outcome=outcome,
                measure=MEASURE_CONVERTER_RATES[outcome_col],
                source_file=trendline_datafile,
                row_num=index + 1,
            )
        )

    return records


@registry.register('load_aggregated_hv_soc_trendline_data', version='1.0')
def load_aggregated_hv_soc_trendline_data(input_file: str) -> List[Row]:
    """ETL Scripts to Load HV SOC Data.

    Parameters
    ----------
    input_file : str

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    results = pd.read_parquet(input_file)
    results['row_num'] = (results.index + 1).astype(str)

    excluded = ['race_ethnicity', 'age_category', 'state']
    keepers = [c for c in results.columns if c not in excluded]

    aggregated_results = results[keepers].groupby(['date_delivery']).sum().reset_index()

    aggregated_results['start_date'] = aggregated_results['date_delivery'].apply(
        lambda d: first_day_month(*map(int, d.split('-')))
    )
    aggregated_results['end_date'] = aggregated_results['date_delivery'].apply(
        lambda d: last_day_month(*map(int, d.split('-')))
    )

    # Calculate the SOC Rate (This Line Needs to change if we normalize to per 10k...)
    aggregated_results['any_soc_rate'] = (aggregated_results['any_SOC'] / aggregated_results['dist_hvid_cnt']) * 10_000

    records = []

    for index, row in aggregated_results.iterrows():
        records.append(
            Trendlines(
                start_date=row.start_date,
                end_date=row.end_date,
                value=row.any_soc_rate,
                outcome='soc',
                measure='any_soc_rate',
                source_file=input_file,
                row_num=index + 1,
            )
        )

    return records
