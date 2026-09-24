import pandas as pd
import numpy as np
from typing import List
from sqlalchemy.engine import Row
from db.datasets.ascvd.ascvd_tables import ASCVDScore, ASCVDScore_v2
from db.datasets.opioid.opioid_tables import Bins
from app.db.database import registry
from app.configs.consts import ValidMorpheusIDs, Replacements, BinLabels
from app.utilities.serialize import parse_yearmon_to_start_end
from datetime import datetime


import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


@registry.register('load_sample_ascvd_sheet', version='3.0')
def load_sample_ascvd_sheet(input_file: str, start_date: str, end_date: str) -> List[Row]:
    """ETL Scripts to Load ASCVD Scores Data.

    Parameters
    ----------
    input_file: str

    Returns
    -------
    List[Rows]
        List of Rows to be inserted into the DB.

    """

    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)

    excel = pd.ExcelFile(input_file)
    dfs = {
        sheet_name: excel.parse(sheet_name, dtype=str).replace({'.': None}).replace(Replacements.JAVASCRIPT_SAFE)
        for sheet_name in excel.sheet_names
    }

    discovered_zip3s = set()
    for sheet_name, df in dfs.items():
        dfs[sheet_name]['ROW_NUM'] = dfs[sheet_name].index + 1
        dfs[sheet_name].index = dfs[sheet_name].zip3

        for col in dfs[sheet_name].columns:
            if col != 'zip3':
                dfs[sheet_name][col] = dfs[sheet_name][col].astype(float).replace(Replacements.JAVASCRIPT_SAFE)

        for zip3 in df.index.unique():
            if ValidMorpheusIDs.is_valid(f'ZCTA3 {zip3}', 'ZCTA3'):
                discovered_zip3s.add(zip3)

    dfs['TOTAL BY ZIP3']['total_mean_bin_rank'] = (
        pd.qcut(dfs['TOTAL BY ZIP3']['TOTAL_MEAN'], 10, labels=BinLabels.LABELS.keys())
        .astype(float)
        .replace(Replacements.JAVASCRIPT_SAFE)
    )

    records = []

    for zip3 in discovered_zip3s:
        record = ASCVDScore(
            start_date=start_date,
            end_date=end_date,
            zip3=zip3,
            mid=f'ZCTA3 {zip3}',
            # General
            total_obs=dfs['TOTAL BY ZIP3'].loc[zip3]['TOTAL_OBS'],
            total_mean=dfs['TOTAL BY ZIP3'].loc[zip3]['TOTAL_MEAN'],
            total_mean_rank=dfs['TOTAL BY ZIP3'].loc[zip3]['total_mean_bin_rank'],
            total_mean_rank_value=BinLabels.LABELS[dfs['TOTAL BY ZIP3'].loc[zip3]['total_mean_bin_rank']],
            # By Age
            age_40_to_49_obs=dfs['AGE BY ZIP3'].loc[zip3]['AGE_40_to_49_OBS'],
            age_40_to_49_mean=dfs['AGE BY ZIP3'].loc[zip3]['AGE_40_to_49_MEAN'],
            age_50_to_59_obs=dfs['AGE BY ZIP3'].loc[zip3]['AGE_50_to_59_OBS'],
            age_50_to_59_mean=dfs['AGE BY ZIP3'].loc[zip3]['AGE_50_to_59_MEAN'],
            age_60_to_69_obs=dfs['AGE BY ZIP3'].loc[zip3]['AGE_60_to_69_OBS'],
            age_60_to_69_mean=dfs['AGE BY ZIP3'].loc[zip3]['AGE_60_to_69_MEAN'],
            age_70_obs=dfs['AGE BY ZIP3'].loc[zip3]['AGE_70_OBS'],
            age_70_mean=dfs['AGE BY ZIP3'].loc[zip3]['AGE_70_MEAN'],
            # By Gender
            female_obs=dfs['GENDER BY ZIP3'].loc[zip3]['F_OBS'],
            female_mean=dfs['GENDER BY ZIP3'].loc[zip3]['F_MEAN'],
            male_obs=dfs['GENDER BY ZIP3'].loc[zip3]['M_OBS'],
            male_mean=dfs['GENDER BY ZIP3'].loc[zip3]['M_MEAN'],
            # By Race
            asian_obs=dfs['RACE BY ZIP3'].loc[zip3]['Asian_OBS'],
            asian_mean=dfs['RACE BY ZIP3'].loc[zip3]['Asian_MEAN'],
            black_obs=dfs['RACE BY ZIP3'].loc[zip3]['Black_OBS'],
            black_mean=dfs['RACE BY ZIP3'].loc[zip3]['Black_MEAN'],
            null_race_obs=dfs['RACE BY ZIP3'].loc[zip3]['NULL_OBS'],
            null_race_mean=dfs['RACE BY ZIP3'].loc[zip3]['NULL_MEAN'],
            other_obs=dfs['RACE BY ZIP3'].loc[zip3]['Other_OBS'],
            other_mean=dfs['RACE BY ZIP3'].loc[zip3]['Other_MEAN'],
            white_obs=dfs['RACE BY ZIP3'].loc[zip3]['White_OBS'],
            white_mean=dfs['RACE BY ZIP3'].loc[zip3]['White_MEAN'],
            # By Ethnicity
            hispanic_obs=dfs['ETHNICITY BY ZIP3'].loc[zip3]['Hispanic_OBS'],
            hispanic_mean=dfs['ETHNICITY BY ZIP3'].loc[zip3]['Hispanic_MEAN'],
            null_ethnicity_obs=dfs['ETHNICITY BY ZIP3'].loc[zip3]['NULL_OBS'],
            null_ethnicity_mean=dfs['ETHNICITY BY ZIP3'].loc[zip3]['NULL_MEAN'],
            non_hispanic_obs=dfs['ETHNICITY BY ZIP3'].loc[zip3]['Non_Hispanic_OBS'],
            non_hispanic_mean=dfs['ETHNICITY BY ZIP3'].loc[zip3]['Non_Hispanic_MEAN'],
            type='ZCTA3',
            source_file=input_file,
            row_num=dfs['TOTAL BY ZIP3'].loc[zip3]['ROW_NUM'],
        )
        records.append(record)

    return records

@registry.register('load_ascvd_aggregate', version='3.0')
def load_ascvd_aggregate(input_file: str, gender_or_sex: str = 'sex') -> List[Row]:
    """ETL Scripts to Load ASCVD Scores Data.

    Parameters
    ----------
    input_file: str

    Returns
    -------
    List[Rows]
        List of Rows to be inserted into the DB.

    """

    excel = pd.ExcelFile(input_file)
    
    df = excel.parse('ASCVD BY ZIP3', dtype=str).replace({'.': None}).replace(Replacements.JAVASCRIPT_SAFE)

    df['mid'] = df['zip3'].apply(lambda x: f"ZCTA3 {x}")
    df['is_valid_zip3'] = df['mid'].apply(lambda mid: ValidMorpheusIDs.is_valid(mid, 'ZCTA3'))
    df['ROW_NUM'] = df.index + 1

    # .astype(float).replace(Replacements.JAVASCRIPT_SAFE)

    df['total_mean_bin_rank'] = (
        pd.qcut(df['MeanASCVD'].astype(float), 10, labels=BinLabels.LABELS.keys())
        .astype(float)
        .replace(Replacements.JAVASCRIPT_SAFE)
    )

    records = []

    for _, row in df.loc[df.is_valid_zip3].iterrows():
        record = ASCVDScore(
            start_date=datetime.fromisoformat(row['StartDate']),
            end_date=datetime.fromisoformat(row['EndDate']),
            zip3=row['zip3'],
            mid=row['mid'],
            # General
            total_obs=row['MeanASCVD_obs'],
            total_mean=row['MeanASCVD'],
            total_mean_rank=row['total_mean_bin_rank'],
            total_mean_rank_value=BinLabels.LABELS[row['total_mean_bin_rank']],
            # By Age
            age_40_to_49_obs=row['MeanASCVD_age_40_to_49_obs'],
            age_40_to_49_mean=row['MeanASCVD_age_40_to_49'],
            age_50_to_59_obs=row['MeanASCVD_age_50_to_59_obs'],
            age_50_to_59_mean=row['MeanASCVD_age_50_to_59'],
            age_60_to_69_obs=row['MeanASCVD_age_60_to_69_obs'],
            age_60_to_69_mean=row['MeanASCVD_age_60_to_69'],
            age_70_obs=row['MeanASCVD_age_70_obs'],
            age_70_mean=row['MeanASCVD_age_70'],
            # By Gender
            female_obs=row[f'MeanASCVD_{gender_or_sex}_female_obs'],
            female_mean=row[f'MeanASCVD_{gender_or_sex}_female'],
            male_obs=row[f'MeanASCVD_{gender_or_sex}_male_obs'],
            male_mean=row[f'MeanASCVD_{gender_or_sex}_male'],
            # By Race
            asian_obs=row['MeanASCVD_race_asian_obs'],
            asian_mean=row['MeanASCVD_race_asian'],
            black_obs=row['MeanASCVD_race_black_obs'],
            black_mean=row['MeanASCVD_race_black'],
            null_race_obs=row['MeanASCVD_race_null_obs'],
            null_race_mean=row['MeanASCVD_race_null'],
            other_obs=row['MeanASCVD_race_other_obs'],
            other_mean=row['MeanASCVD_race_other'],
            white_obs=row['MeanASCVD_race_white_obs'],
            white_mean=row['MeanASCVD_race_white'],
            # By Ethnicity (Deprecated in recent deliveries)
            # hispanic_obs=row['MeanASCVD_obs'],
            # hispanic_mean=row['MeanASCVD_obs'],
            # null_ethnicity_obs=row['MeanASCVD_obs'],
            # null_ethnicity_mean=row['MeanASCVD_obs'],
            # non_hispanic_obs=row['MeanASCVD_obs'],
            # non_hispanic_mean=row['MeanASCVD_obs'],
            type='ZCTA3',
            source_file=input_file,
            row_num=row['ROW_NUM'],
        )
        records.append(record)

    return records


@registry.register('load_ascvd_bins', version='2.0')
def load_ascvd_bins(input_file: str, start_date: str, end_date: str) -> List[Row]:
    """ETL Scripts to Generate ASCVD Bins.

    Parameters
    ----------
    input_file : str

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    records = []

    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)

    excel = pd.ExcelFile(input_file)
    dfs = {
        sheet_name: excel.parse(sheet_name, dtype=str).replace({'.': None}).replace(Replacements.JAVASCRIPT_SAFE)
        for sheet_name in excel.sheet_names
    }

    discovered_zip3s = set()
    for sheet_name, df in dfs.items():
        dfs[sheet_name]['ROW_NUM'] = dfs[sheet_name].index + 1
        dfs[sheet_name].index = dfs[sheet_name].zip3

        for col in dfs[sheet_name].columns:
            if col != 'zip3':
                dfs[sheet_name][col] = dfs[sheet_name][col].astype(float).replace(Replacements.JAVASCRIPT_SAFE)

        for zip3 in df.index.unique():
            if ValidMorpheusIDs.is_valid(f'ZCTA3 {zip3}', 'ZCTA3'):
                discovered_zip3s.add(zip3)

    dfs['TOTAL BY ZIP3']['total_mean_bin_rank'] = (
        pd.qcut(dfs['TOTAL BY ZIP3']['TOTAL_MEAN'], 10, labels=BinLabels.LABELS.keys())
        .astype(float)
        .replace(Replacements.JAVASCRIPT_SAFE)
    )

    bin_stats = (
        dfs['TOTAL BY ZIP3']
        .groupby(['total_mean_bin_rank'])
        .agg(
            bin_mean=('TOTAL_MEAN', 'mean'),
            bin_median=('TOTAL_MEAN', 'median'),
            bin_min=('TOTAL_MEAN', 'min'),
            bin_max=('TOTAL_MEAN', 'max'),
            bin_count=('TOTAL_MEAN', lambda x: len(x)),
        )
        .reset_index()
    )

    bin_stats['bin_midpoint'] = (bin_stats['bin_max'] + bin_stats['bin_min']) / 2.0

    print(bin_stats, flush=True)

    bin_stats['start_date'] = start_date
    bin_stats['end_date'] = end_date

    bin_stats_sorted = bin_stats.sort_values(by=['start_date', 'end_date', 'total_mean_bin_rank'])

    bin_stats_sorted['next_min'] = bin_stats_sorted.groupby(['start_date', 'end_date'])['bin_min'].shift(-1)
    bin_stats_sorted['next_max'] = bin_stats_sorted.groupby(['start_date', 'end_date'])['bin_max'].shift(-1)

    for index, row in bin_stats_sorted.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        if not pd.isna(row['next_min']):
            max_=row['next_min']
        else:
            max_=row['bin_max']
        records.append(
            Bins(
                start_date=start_date,
                end_date=end_date,
                outcome='cardio',
                measure='total_mean',
                rank=row['total_mean_bin_rank'],
                rankValue=BinLabels.LABELS[row['total_mean_bin_rank']],
                n=row['bin_count'],
                min=row['bin_min'],
                median=row['bin_median'],
                mean=row['bin_mean'],
                midpoint=row['bin_midpoint'],
                max=max_,
                type='ZCTA3',
                source_file='Internal',
                row_num='NA',
            )
        )

    return records


@registry.register('load_ascvd_bins_v2', version='2.0')
def load_ascvd_bins_v2(input_file: str) -> List[Row]:
    """ETL Scripts to Generate ASCVD Bins.

    Parameters
    ----------
    input_file : str

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    records = []

    excel = pd.ExcelFile(input_file)
    
    df = excel.parse('ASCVD BY ZIP3', dtype=str).replace({'.': None}).replace(Replacements.JAVASCRIPT_SAFE)

    df['mid'] = df['zip3'].apply(lambda x: f"ZCTA3 {x}")
    df['is_valid_zip3'] = df['mid'].apply(lambda mid: ValidMorpheusIDs.is_valid(mid, 'ZCTA3'))
    df['ROW_NUM'] = df.index + 1
    df['MeanASCVD'] = df['MeanASCVD'].astype(float)

    # .astype(float).replace(Replacements.JAVASCRIPT_SAFE)

    df['total_mean_bin_rank'] = (
        pd.qcut(df['MeanASCVD'].astype(float), 10, labels=BinLabels.LABELS.keys())
        .astype(float)
        .replace(Replacements.JAVASCRIPT_SAFE)
    )

    bin_stats = (
        df.loc[df.is_valid_zip3]
        .groupby(['total_mean_bin_rank', 'StartDate', 'EndDate'])
        .agg(
            bin_mean=('MeanASCVD', 'mean'),
            bin_median=('MeanASCVD', 'median'),
            bin_min=('MeanASCVD', 'min'),
            bin_max=('MeanASCVD', 'max'),
            bin_count=('MeanASCVD', lambda x: len(x)),
        )
        .reset_index()
    )

    bin_stats['bin_midpoint'] = (bin_stats['bin_max'] + bin_stats['bin_min']) / 2.0

    print(bin_stats, flush=True)

    for index, row in bin_stats.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        records.append(
            Bins(
                start_date=row['StartDate'],
                end_date=row['EndDate'],
                outcome='cardio',
                measure='total_mean',
                rank=row['total_mean_bin_rank'],
                rankValue=BinLabels.LABELS[row['total_mean_bin_rank']],
                n=row['bin_count'],
                min=row['bin_min'],
                median=row['bin_median'],
                mean=row['bin_mean'],
                midpoint=row['bin_midpoint'],
                max=row['bin_max'],
                type='ZCTA3',
                source_file='Internal',
                row_num='NA',
            )
        )

    return records


@registry.register('load_ascvd_monthly_data', version=2.0)
def load_ascvd_monthly_data(input_file: str) -> List[Row]:
    """Load Monthyl ASCVD Data.

    Parameters
    ----------
    input_file : str
    start_date : str
    end_date : str

    Returns
    -------
    List[Row]

    """
    excel = pd.ExcelFile(input_file)
    dfs = {
        sheet_name: excel.parse(sheet_name, dtype=str).replace({'.': None}).replace(Replacements.JAVASCRIPT_SAFE)
        for sheet_name in excel.sheet_names
    }

    # Since Veradigm has an error in their format for recent submissions
    dfs['MONTH BY ZIP3'].columns = [c.replace('24OBS', '24_OBS') for c in dfs['MONTH BY ZIP3'].columns]

    yearmonths = set([col.split('_')[0] for col in dfs['MONTH BY ZIP3'].columns[1:]])

    valid_mids = dfs['MONTH BY ZIP3'].zip3.apply(lambda x: ValidMorpheusIDs.is_valid(f'ZCTA3 {x}', 'ZCTA3'))

    for yearmonth in yearmonths:
        dfs['MONTH BY ZIP3'][f'{yearmonth}_RANK'] = (
            pd.qcut(
                dfs['MONTH BY ZIP3'][f'{yearmonth}_MEAN'].astype(float),
                10,
                labels=BinLabels.LABELS.keys(),
            )
            .astype(float)
            .replace(Replacements.JAVASCRIPT_SAFE)
        )

    records = []

    for index, row in dfs['MONTH BY ZIP3'].loc[valid_mids].iterrows():
        for yearmonth in yearmonths:
            start_date, end_date = parse_yearmon_to_start_end(yearmonth)

            record = ASCVDScore_v2(
                start_date=start_date,
                end_date=end_date,
                zip3=row.zip3,
                mid=f'ZCTA3 {row.zip3}',
                total_obs=row[f'{yearmonth}_OBS'],
                total_mean=row[f'{yearmonth}_MEAN'],
                total_mean_rank=row[f'{yearmonth}_RANK'],
                total_mean_rank_value=BinLabels.LABELS.get(row[f'{yearmonth}_RANK']),
                type='ZCTA3',
                source_file=input_file,
                row_num=index + 1,
            )
            records.append(record)

    return records


@registry.register('load_ascvd_monthly_data_bins', version=2.0)
def load_ascvd_monthly_data_bins(input_file: str) -> List[Row]:
    """ETL Scripts to Generate ASCVD Bins.

    Parameters
    ----------
    input_file : str

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    excel = pd.ExcelFile(input_file)
    dfs = {
        sheet_name: excel.parse(sheet_name, dtype=str).replace({'.': None}).replace(Replacements.JAVASCRIPT_SAFE)
        for sheet_name in excel.sheet_names
    }

    # Since Veradigm has an error in their format for recent submissions
    dfs['MONTH BY ZIP3'].columns = [c.replace('24OBS', '24_OBS') for c in dfs['MONTH BY ZIP3'].columns]

    yearmonths = set([col.split('_')[0] for col in dfs['MONTH BY ZIP3'].columns[1:]])

    records = []

    for yearmonth in yearmonths:
        dfs['MONTH BY ZIP3'][f'{yearmonth}_MEAN'] = dfs['MONTH BY ZIP3'][f'{yearmonth}_MEAN'].astype(float)
        dfs['MONTH BY ZIP3'][f'{yearmonth}_RANK'] = (
            pd.qcut(
                dfs['MONTH BY ZIP3'][f'{yearmonth}_MEAN'],
                10,
                labels=BinLabels.LABELS.keys(),
            )
            .astype(float)
            .replace(Replacements.JAVASCRIPT_SAFE)
        )

        bin_stats = (
            dfs['MONTH BY ZIP3']
            .groupby([f'{yearmonth}_RANK'])
            .agg(
                bin_mean=(f'{yearmonth}_MEAN', 'mean'),
                bin_median=(f'{yearmonth}_MEAN', 'median'),
                bin_min=(f'{yearmonth}_MEAN', 'min'),
                bin_max=(f'{yearmonth}_MEAN', 'max'),
                bin_count=(f'{yearmonth}_MEAN', lambda x: len(x)),
            )
            .reset_index()
        )
        bin_stats['bin_midpoint'] = (bin_stats['bin_max'] + bin_stats['bin_min']) / 2.0

        start_date, end_date = parse_yearmon_to_start_end(yearmonth)

        bin_stats['next_min'] = bin_stats['bin_min'].shift(-1)
        bin_stats['next_max'] = bin_stats['bin_max'].shift(-1)

        for index, row in bin_stats.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
            if not pd.isna(row['next_min']):
                max=row['next_min']
            else:
                max=row['bin_max']
            records.append(
                Bins(
                    start_date=start_date,
                    end_date=end_date,
                    outcome='cardio',
                    measure='total_mean',
                    rank=row[f'{yearmonth}_RANK'],
                    rankValue=BinLabels.LABELS[row[f'{yearmonth}_RANK']],
                    n=row['bin_count'],
                    min=row['bin_min'],
                    median=row['bin_median'],
                    mean=row['bin_mean'],
                    midpoint=row['bin_midpoint'],
                    max=max,
                    type='ZCTA3',
                    source_file='Internal',
                    row_num='NA',
                )
            )

    return records
