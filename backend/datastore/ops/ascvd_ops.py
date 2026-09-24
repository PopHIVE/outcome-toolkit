import pandas as pd
import numpy as np
from typing import Dict
from datetime import datetime
from app.configs.consts import BinLabels, ValidMorpheusIDs, Replacements
from datastore.utils.serialize import parse_yearmon_to_start_end

def extract_ascvd_data_from_excel_file(
    file_path: str,
) -> dict:
    """Extract ASCVD data from an excel file

    Parameters
    ----------
    file_path : str
        The path to the excel file containing the ASCVD data.

    Returns
    -------
    Output[dict] : dict[pd.DataFrame]
        A dictionary where the keys are the sheet names from the excel file,
        and the values are pandas DataFrames containing the data from each sheet.
    """
    excel = pd.ExcelFile(file_path)
    dfs = {
        sheet_name: excel.parse(sheet_name, dtype=str).replace(
            {'.': None}   
        ).replace(Replacements.JAVASCRIPT_SAFE)
    for sheet_name in excel.sheet_names}

    for sheet_name, df in dfs.items():
        dfs[sheet_name]['ROW_NUM'] = (dfs[sheet_name].index + 1)

        for col in dfs[sheet_name].columns:
            if col != 'zip3':
                dfs[sheet_name][col] = dfs[sheet_name][col].astype(float).replace(Replacements.JAVASCRIPT_SAFE)

    return dfs

def extract_ascvd_month_data_from_excel_file(
    file_path: str,
) -> pd.DataFrame:
    """
    Extract ASCVD month data from an excel file.

    Parameters
    ----------
    file_path : str
        The path to the excel file containing the ASCVD data.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the ASCVD month data. The DataFrame
        has columns for each year-month, with '_MEAN' and '_RANK' suffixes
        indicating the mean and rank values for each month.
    """
    excel = pd.ExcelFile(file_path)
    dfs = {
        sheet_name: excel.parse(sheet_name, dtype=str).replace(
            {'.': None}   
        ).replace(Replacements.JAVASCRIPT_SAFE)
    for sheet_name in excel.sheet_names}

    for sheet_name, df in dfs.items():
        for col in dfs[sheet_name].columns:
            if col != 'zip3':
                dfs[sheet_name][col] = dfs[sheet_name][col].astype(float).replace(Replacements.JAVASCRIPT_SAFE)

    yearmonths = set([col.split('_')[0] for col in dfs['MONTH BY ZIP3'].columns[1:]])
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

    df = dfs['MONTH BY ZIP3']
    return df

def format_ascvd_score_df(
    dfs_list: list,
    start_date: datetime,
    end_date: datetime,
    measure: str,
    outcome: str,
    source_file: str,
    label_converter: Dict[int, str]
) -> pd.DataFrame:
    """ Convert a ASCVD Raw Statistics DFs to a ASCVD Score Dataframe.

    This function takes a list of DataFrames (dfs_list) containing ASCVD data from different sheets.
    It then generates a new DataFrame (df_wide) that combines the ASCVD data from the different sheets into a single DataFrame,
    The function first identifies the unique ZIP3 codes present in the dfs_list.
    Then, for each unique ZIP3 code, it creates a new record in the df_wide DataFrame,
    populating it with the start and end dates, the measure and outcome, the ZIP3 code, the mid value,
    and the total number of observations, mean, rank, and rank value for the ZIP3 code.

    Parameters
    ----------
    dfs_list : list
        A list of DataFrames containing ASCVD data from different sheets.
    start_date : datetime
        The start date of the ASCVD data.
    end_date : datetime
        The end date of the ASCVD data.
    measure : str
        The measure for which the ASCVD data is being calculated.
    outcome : str
        The outcome for which the ASCVD data is being calculated.
    source_file : str
        The source file from which the ASCVD data is being derived.
    label_converter : Dict[int, str]
        A dictionary that maps rank values to their corresponding rank labels.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the ASCVD data from the different sheets, combined into a single DataFrame

    """
    df_wide = pd.DataFrame(
        columns = [
            'start_date', 'end_date', 'measure', 'outcome', 'zip3', 'mid',
            'total_obs', 'total_mean', 'total_mean_rank', 'total_mean_rank_value',
            'age_40_to_49_obs', 'age_40_to_49_mean', 'age_50_to_59_obs', 'age_50_to_59_mean',
            'age_60_to_69_obs', 'age_60_to_69_mean', 'age_70_obs', 'age_70_mean',
            'female_obs', 'female_mean', 'male_obs', 'male_mean',
            'asian_obs', 'asian_mean', 'black_obs', 'black_mean',
            'null_race_obs', 'null_race_mean', 'other_obs', 'other_mean',
            'white_obs', 'white_mean', 'hispanic_obs','hispanic_mean',
            'null_ethnicity_obs', 'null_ethnicity_mean', 'non_hispanic_obs', 'non_hispanic_mean',
            'type', 'source_file', 'row_num', 'etl_version'
            ])

    discovered_zip3s = set()
    for df in dfs_list:
        for zip3 in df.index:
            if zip3 not in discovered_zip3s:
                if ValidMorpheusIDs.is_valid(f'ZCTA3 {zip3}', 'ZCTA3'):
                    discovered_zip3s.add(zip3)

    for zip3 in discovered_zip3s:
        record = {
            'start_date': start_date,
            'end_date': end_date,
            'measure': measure,
            'outcome': outcome,
            'zip3': zip3,
            'mid': f'ZCTA3 {zip3}',
            'total_obs': dfs_list[0].loc[zip3, 'TOTAL_OBS'],
            'total_mean': dfs_list[0].loc[zip3, 'TOTAL_MEAN'],
            'total_mean_rank': dfs_list[0].loc[zip3, 'bin_rank'],
            'total_mean_rank_value': label_converter[dfs_list[0].loc[zip3, 'bin_rank']],
            'age_40_to_49_obs': dfs_list[1].loc[zip3, 'AGE_40_to_49_OBS'],
            'age_40_to_49_mean': dfs_list[1].loc[zip3, 'AGE_40_to_49_MEAN'],
            'age_50_to_59_obs': dfs_list[1].loc[zip3, 'AGE_50_to_59_OBS'],
            'age_50_to_59_mean': dfs_list[1].loc[zip3, 'AGE_50_to_59_MEAN'],
            'age_60_to_69_obs': dfs_list[1].loc[zip3, 'AGE_60_to_69_OBS'],
            'age_60_to_69_mean': dfs_list[1].loc[zip3, 'AGE_60_to_69_MEAN'],
            'age_70_obs': dfs_list[1].loc[zip3, 'AGE_70_OBS'],
            'age_70_mean': dfs_list[1].loc[zip3, 'AGE_70_MEAN'],
            'female_obs': dfs_list[2].loc[zip3, 'F_OBS'],
            'female_mean': dfs_list[2].loc[zip3, 'F_MEAN'],
            'male_obs': dfs_list[2].loc[zip3, 'M_OBS'],
            'male_mean': dfs_list[2].loc[zip3, 'M_MEAN'],
            'asian_obs': dfs_list[3].loc[zip3, 'Asian_OBS'],
            'asian_mean': dfs_list[3].loc[zip3, 'Asian_MEAN'],
            'black_obs': dfs_list[3].loc[zip3, 'Black_OBS'],
            'black_mean': dfs_list[3].loc[zip3, 'Black_MEAN'],
            'null_race_obs': dfs_list[3].loc[zip3, 'NULL_OBS'],
            'null_race_mean': dfs_list[3].loc[zip3, 'NULL_MEAN'],
            'other_obs': dfs_list[3].loc[zip3, 'Other_OBS'],
            'other_mean': dfs_list[3].loc[zip3, 'Other_MEAN'],
            'white_obs': dfs_list[3].loc[zip3, 'White_OBS'],
            'white_mean': dfs_list[3].loc[zip3, 'White_MEAN'],
            'hispanic_obs': dfs_list[4].loc[zip3, 'Hispanic_OBS'],
            'hispanic_mean': dfs_list[4].loc[zip3, 'Hispanic_MEAN'],
            'null_ethnicity_obs': dfs_list[4].loc[zip3, 'NULL_OBS'],
            'null_ethnicity_mean': dfs_list[4].loc[zip3, 'NULL_MEAN'],
            'non_hispanic_obs': dfs_list[4].loc[zip3, 'Non_Hispanic_OBS'],
            'non_hispanic_mean': dfs_list[4].loc[zip3, 'Non_Hispanic_MEAN'],
            'type': 'ZCTA3',
            'source_file': source_file,
        }
        df_wide.loc[len(df_wide.index)] = record
    
    return df_wide

def format_ascvd_bin_statistics(
    bin_stats: pd.DataFrame,
    start_date: datetime,
    end_date: datetime,
    measure: str,
    outcome: str,
    source_file: str,
    label_converter: Dict[int, str]
) -> pd.DataFrame:
    """ Convert a ASCVD Raw Statistics DF to a Bin Statistics Dataframe.

    Parameters
    ----------
    bin_stats : pd.DataFrame
        A pandas DataFrame containing the ASCVD raw statistics.
    start_date : datetime
        A datetime object representing the start date of the statistics.
    end_date : datetime
        A datetime object representing the end date of the statistics.
    measure : str
        A string representing the measure for which the statistics are calculated.
    outcome : str
        A string representing the outcome for which the statistics are calculated.
    source_file : str
        A string representing the source file from which the statistics are derived.
    label_converter : Dict[int, str]
        A dictionary that maps rank values to their corresponding rank labels.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the ASCVD bin statistics data.
    """

    df_wide = pd.DataFrame(bin_stats)

    df_wide.rename(
        columns={
            'bin_rank': 'rank',
            'bin_max': 'max',
            'bin_mean': 'mean',
            'bin_median': 'median',
            'bin_min': 'min',
            'bin_count': 'n'
        }, inplace=True
    )
    df_wide['measure'] = measure
    df_wide['outcome'] = outcome
    df_wide['start_date'] = pd.Timestamp(start_date)
    df_wide['end_date'] = pd.Timestamp(end_date)
    df_wide['source_file'] = source_file
    df_wide['midpoint'] = (df_wide['max'] + df_wide['max']) / 2.0
    df_wide['rankValue'] = df_wide['rank'].apply(lambda x: label_converter[x])

    return df_wide


def format_ascvd_month_score_df(
    df: pd.DataFrame,
    measure: str,
    outcome: str,
    source_file: str,
    label_converter: Dict[int, str]
) -> pd.DataFrame:
    """ Convert a ASCVD Raw month Statistics DF to a ASCVD month Score Dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the ASCVD raw month statistics.
    measure : str
        The measure for which the statistics are calculated.
    outcome : str
        The outcome for which the statistics are calculated.
    source_file : str
        The source file from which the statistics are derived.
    label_converter : Dict[int, str]
        A dictionary that maps rank values to their corresponding rank labels.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the ASCVD month score data.
    """

    yearmonths = set([col.split('_')[0] for col in df.columns[1:]])

    valid_mids = df['zip3'].apply(lambda x: ValidMorpheusIDs.is_valid(f'ZCTA3 {x}', 'ZCTA3'))

    df_wide = pd.DataFrame(
        columns=[
            'start_date', 'end_date', 'measure', 'outcome', 'zip3', 'mid',
            'total_obs', 'total_mean', 'total_mean_rank', 'total_mean_rank_value',
            'type', 'source_file', 'row_num'
        ]
    )

    for index, row in df.loc[valid_mids].iterrows():
        for yearmonth in yearmonths:
            start_date, end_date = parse_yearmon_to_start_end(yearmonth)
            zip3 = row['zip3']
            total_mean = row[f'{yearmonth}_MEAN'] if row[f'{yearmonth}_MEAN'] >= 0 else '0'
            total_mean_rank = row[f'{yearmonth}_RANK'] if row[f'{yearmonth}_RANK'] in range(1, 10) else '10'
            total_mean_rank_value = label_converter[row[f'{yearmonth}_RANK']] if row[f'{yearmonth}_RANK'] in range(1, 10) else 'No Data'
            record = {
                'start_date': start_date,
                'end_date': end_date,
                'measure': measure,
                'outcome': outcome,
                'zip3': zip3,
                'mid': f'ZCTA3 {zip3}',
                'total_obs': row[f'{yearmonth}_OBS'],
                'total_mean': total_mean,
                'total_mean_rank': total_mean_rank, 
                'total_mean_rank_value': total_mean_rank_value, 
                'type': 'ZCTA3',
                'source_file': source_file,
                'row_num': index + 1,
            }

            df_wide.loc[len(df_wide.index)] = record

    return df_wide

def format_ascvd_month_bin_statistics(
    df: pd.DataFrame,
    outcome: str,
    measure: str,
    source_file: str,
    label_converter: Dict[int, str]
) -> pd.DataFrame:
    """ Convert a ASCVD Raw Month Statistics DF to a Bin Statistics Dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the ASCVD raw month statistics.
    outcome : str
        The outcome for which the statistics are calculated.
    measure : str
        The measure for which the statistics are calculated.
    source_file : str
        The source file from which the statistics are derived.
    label_converter : Dict[int, str]
        A dictionary that maps rank values to their corresponding rank labels.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the bin statistics for the ASCVD raw month statistics.
    """
    df_wide = pd.DataFrame()

    yearmonths = set([col.split('_')[0] for col in df.columns[1:]])

    month_bin_stats_records = []
    for yearmonth in yearmonths:
        month_bin_stats = pd.DataFrame()
        month_bin_stats = (
            df.groupby([f'{yearmonth}_RANK']).agg(
                bin_mean=(f'{yearmonth}_MEAN', np.mean),
                bin_median=(f'{yearmonth}_MEAN', np.median),
                bin_min=(f'{yearmonth}_MEAN', np.min),
                bin_max=(f'{yearmonth}_MEAN', np.max),
                bin_count=(f'{yearmonth}_MEAN', lambda x: len(x)),
            )
        .reset_index()
        )
        for index, row in month_bin_stats.replace(Replacements.JAVASCRIPT_SAFE).iterrows(): 
            start_date, end_date = parse_yearmon_to_start_end(yearmonth)   
            record = {
                'start_date': start_date,
                'end_date': end_date,
                'outcome': outcome,
                'measure': measure,
                'rank': row[f'{yearmonth}_RANK'],
                'rankValue': label_converter[row[f'{yearmonth}_RANK']],
                'min': row['bin_min'],
                'mean': row['bin_mean'],
                'median': row['bin_median'],
                'midpoint': (row['bin_max'] + row['bin_max']) / 2.0,
                'max': row['bin_max'],
                'n': row['bin_count'],
                'type': 'ZCTA3',
                'source_file': source_file,
            }
            month_bin_stats_records.append(record)

    df_wide = pd.DataFrame(month_bin_stats_records)
    return df_wide
