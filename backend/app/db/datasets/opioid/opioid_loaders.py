import pandas as pd
import zipfile
from typing import List
from sqlalchemy.engine import Row
from app.utilities.serialize import (
    extract_sas_file_from_zipfile,
    last_day_month,
    first_day_month,
)
from db.datasets.opioid.opioid_tables import NEMSISOpioid, Bins, NEMSISOpioid_v2
from app.db.database import registry
from app.configs.consts import Replacements, ValidMorpheusIDs
from datetime import datetime


@registry.register('load_nemsis_opioid_data', version='2.0')
def load_nemsis_opioid_data(
    zip_file: str, file_name: str, geography: str, start_date: str, end_date: str
) -> List[Row]:
    """ETL Scripts to Load NEMSIS Opioid Data.

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
        record = NEMSISOpioid(
            start_date=start_date,
            end_date=end_date,
            county_name=row['CountyName'],
            county_fips=row['CountyFIPS'],
            population_estimate=row['population'],
            opioid_rate_rank=row['Opioid Rate (Rank)'],
            opioid_rate_rank_value=row['Opioid Rate (RankValue)'],
            # Deprecated
            # avg_naloxone_administrations_rank=row['Average Naloxone Administrations (Rank)'],
            # avg_time_to_patient_rank=row['Average Time To Patient (Rank)'],
            # percent_not_transported_rank=row['Percent Not Transported (Rank)'],
            # avg_naloxone_administrations_rank_value=row['Average Naloxone Administrations (RankValue)'],
            # avg_time_to_patient_rank_value=row['Average Time To Patient (RankValue)'],
            # percent_not_transported_rank_value=row['Percent Not Transported (RankValue)'],
            mid=f"{geography} {row['CountyFIPS']}",
            type=geography,
            source_file=file_name,
            row_num=','.join(
                map(
                    str,
                    [
                        # row['Average Naloxone Administrations (ROW_NUM)'],
                        # row['Average Time To Patient (ROW_NUM)'],
                        row['Opioid Rate (ROW_NUM)'],
                        # row['Percent Not Transported (ROW_NUM)'],
                    ],
                )
            ),
        )
        records.append(record)

    return records


@registry.register('load_nemsis_opioid_data_monthly', version='1.0')
def load_nemsis_opioid_data_monthly(zip_file: str, file_name: str, geography: str) -> List[Row]:
    """ETL Scripts to Load NEMSIS Opioid Data.

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
        record = NEMSISOpioid_v2(
            start_date=first_day_month(int(row['Yearmonth'][:4]), int(row['Yearmonth'][4:])),
            end_date=last_day_month(int(row['Yearmonth'][:4]), int(row['Yearmonth'][4:])),
            county_name=row['CountyName'],
            county_fips=row['CountyFIPS'],
            population_estimate=row['population'],
            opioid_rate_rank=row['Opioid Rate (Rank)'],
            opioid_rate_rank_value=row['Opioid Rate (RankValue)'],
            mid=f"{geography} {row['CountyFIPS']}",
            type=geography,
            source_file=file_name,
            row_num=','.join(
                map(
                    str,
                    [
                        # row['Average Naloxone Administrations (ROW_NUM)'],
                        # row['Average Time To Patient (ROW_NUM)'],
                        row['Opioid Rate (ROW_NUM)'],
                        # row['Percent Not Transported (ROW_NUM)'],
                    ],
                )
            ),
        )
        records.append(record)

    return records


@registry.register('load_nemsis_bins', version='1.0')
def load_nemsis_bins(
    zip_file: str,
    file_name: str,
    outcome: str,
    geography: str,
    start_date: str,
    end_date: str,
) -> List[Row]:
    """ETL Scripts for NEMSIS Bins Data.

    Parameters
    ----------
    zip_file : str
        Filepath to the ZIP Archive within the Data Bundle.
    file_name : str
        Filename of the NEMSIS Opioid Data within the ZIP Archive.
    outcome: str

    geography : str
        The geography

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)

    BIN_STATS = ['N', 'MIN', 'MEAN', 'MEDIAN', 'MAX']

    BIN_STATS_MEASURE_CONVERTER = {
        'alcohol': {
            'AllAlcoholSchematic': 'alcohol_rate',
            # Deprecated
            # 'AllNonTransportSchematic': 'percent_not_transported',
            # 'AllAvgTimeSchematic': 'avg_time_to_patient'
        },
        'opioid': {
            'AllOpioidSchematic': 'opioid_rate',
            # Deprecated
            # 'AllNonTransportSchematic': 'percent_not_transported',
            # 'AllAvgTimeSchematic': 'avg_time_to_patient',
            # 'AllAvgNaloxoneSchematic': 'avg_naloxone_administrations',
        },
    }

    RANK_CONVERTER = {
        0: 'Zero or No/Limited Data Available',
        1: 'Significantly Lower Than National Average',
        2: 'Much Lower than National Average',
        3: 'Lower than National Average',
        4: 'Slightly Lower than National Average',
        5: 'Slightly Higher than National Average',
        6: 'Higher than National Average',
        7: 'Much Higher than National Average',
        8: 'Significantly Higher than National Average',
        9: 'High Outlier',
    }

    records = []

    archive = zipfile.ZipFile(zip_file, 'r')
    with archive.open(file_name) as f:
        bin_stats_excel = pd.ExcelFile(f)
        for sheet_name in bin_stats_excel.sheet_names:
            df = bin_stats_excel.parse(sheet_name)
            df['ROW_NUM'] = (df.index + 1).astype(str)

            df_wide = pd.pivot(
                df.loc[df._TYPE_.isin(BIN_STATS)],
                index=['MeasureRank'],
                columns=['_TYPE_'],
                values=['_VALUE_', 'ROW_NUM'],
            )

            df_wide.columns = [f'{pair[1]} ({pair[0]})' for pair in df_wide.columns]
            df_wide.reset_index(inplace=True)

            df_wide['start_date'] = start_date
            df_wide['end_date'] = end_date

            # df_wide['next_min'] = df_wide['MIN (_VALUE_)'].shift(-1)
            # df_wide['next_max'] = df_wide['MAX (_VALUE_)'].shift(-1)

            df_wide_sorted = df_wide.sort_values(by=['start_date', 'end_date', 'MeasureRank'])

            df_wide_sorted['next_min'] = df_wide_sorted.groupby(['start_date', 'end_date'])['MIN (_VALUE_)'].shift(-1)
            df_wide_sorted['next_max'] = df_wide_sorted.groupby(['start_date', 'end_date'])['MAX (_VALUE_)'].shift(-1)

            for index, row in df_wide_sorted.iterrows():
                if not pd.isna(row['next_min']):
                    max_=row['next_min']
                else:
                    max_=row['MAX (_VALUE_)']
                records.append(
                    Bins(
                        start_date=start_date,
                        end_date=end_date,
                        outcome=outcome,
                        measure=BIN_STATS_MEASURE_CONVERTER[outcome][sheet_name],
                        rank=row['MeasureRank'],
                        rankValue=RANK_CONVERTER[row['MeasureRank']],
                        n=row['N (_VALUE_)'],
                        min=row['MIN (_VALUE_)'],
                        median=row['MEDIAN (_VALUE_)'],
                        mean=row['MEAN (_VALUE_)'],
                        midpoint=(row['MIN (_VALUE_)'] + row['MAX (_VALUE_)']) / 2.0,
                        max=max_,
                        type=geography,
                        source_file=file_name,
                        row_num=','.join(
                            map(
                                str,
                                [row[col] for col in df_wide.columns if ('ROW_NUM' in col)],
                            )
                        ),
                    )
                )

    return records


@registry.register('load_nemsis_bins_monthly', version='1.0')
def load_nemsis_bins_monthly(
    zip_file: str,
    file_name_monthly: str,
    file_name_bins: str,
    outcome: str,
    geography: str,
) -> List[Row]:
    """_summary_

    Parameters
    ----------
    zip_file : str
        Filepath to the ZIP Archive within the Data Bundle.
    file_name_monthly : str
        Filename of NEMSIS Opioid Monthly Data within the ZIP Archive
    file_name_bins : str
        Filename of the NEMSIS Opioid Bins Data within the ZIP Archive.
    outcome: str

    Returns
    -------
    List[Row]

    """

    df = extract_sas_file_from_zipfile(zip_file, file_name_monthly, encoding='latin1')

    records = []

    for yearmon in df.Yearmonth.unique():
        year, month = int(yearmon[:4]), int(yearmon[4:])
        start_date = first_day_month(year, month)
        end_date = last_day_month(year, month)

        records.extend(
            load_nemsis_bins(
                zip_file,
                file_name_bins,
                outcome,
                geography,
                start_date.isoformat(),
                end_date.isoformat(),
            )
        )

    return records


@registry.register('load_nemsis_opioid_monthly_v2', version='1.0')
def load_nemsis_opioid_monthly_v2(zip_file: str, file_name: str, rank_col: str, rank_val_col: str, geography: str) -> List[Row]:
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

        record = NEMSISOpioid_v2(
            start_date=first_day_month(int(row['Yearmonth'][:4]), int(row['Yearmonth'][4:])),
            end_date=last_day_month(int(row['Yearmonth'][:4]), int(row['Yearmonth'][4:])),
            county_name=row['Countyfips'],
            county_fips=row['Countyfips'],
            population_estimate=None,
            opioid_rate_rank=row[rank_col],
            opioid_rate_rank_value=row[rank_val_col],
            mid=f"{geography} {row['Countyfips']}",
            type=geography,
            source_file=file_name,
            row_num=index
        )
        records.append(record)

    return records


@registry.register('load_nemsis_bins_monthly_v2', version='1.0')
def load_nemsis_bins_monthly_v2(
    zip_file: str,
    file_name_bins: str,
    yearmon: str,
    metric: str,
    outcome: str,
    geography: str
) -> List[Row]:
    """_summary_

    Parameters
    ----------
    zip_file : str
        Filepath to the ZIP Archive within the Data Bundle.
    file_name_bins : str
        Filename of the NEMSIS Opioid Bins Data within the ZIP Archive.
    yearmon: str
    metric: str
    outcome: str

    Returns
    -------
    List[Row]

    """

    # TO DO: NEED TO EXTRACT YEARMON DYNAMICALLY ... REACH OUT TO VENDOR
    start_date = first_day_month(int(yearmon[:4]), int(yearmon[4:]))
    end_date = last_day_month(int(yearmon[:4]), int(yearmon[4:]))

    BIN_STATS_MEASURE_CONVERTER = {
        'opioid': 'opioid_rate',
        'alcohol': 'alcohol_rate'
    }

    RANK_CONVERTER = {
        0: 'Zero or No/Limited Data Available',
        1: 'Significantly Lower Than National Average',
        2: 'Much Lower than National Average',
        3: 'Lower than National Average',
        4: 'Slightly Lower than National Average',
        5: 'Slightly Higher than National Average',
        6: 'Higher than National Average',
        7: 'Much Higher than National Average',
        8: 'Significantly Higher than National Average',
        9: 'High Outlier',
    }

    df = extract_sas_file_from_zipfile(zip_file, file_name_bins, encoding='latin1')

    records = []

    for index, row in df.loc[df.Metric == metric].iterrows():
        records.append(
            Bins(
                start_date=start_date,
                end_date=end_date,
                outcome=outcome,
                measure=BIN_STATS_MEASURE_CONVERTER[outcome],
                rank=row['Rank'],
                rankValue=RANK_CONVERTER[row['Rank']],
                n=None, # TO DO: NEED VENDOR TO ADD THIS COLUMN
                min=row['MIN'],
                median=row['MEDIAN'],
                mean=row['MEAN'],
                midpoint=(row['MIN'] + row['MAX']) / 2.0,
                max=row['MAX'],
                type=geography,
                source_file=file_name_bins,
                row_num=index,
            )
        )


    return records