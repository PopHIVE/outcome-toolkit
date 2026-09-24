import pandas as pd
from typing import List, Dict
from datetime import datetime
from datastore.models.dataframes.common import RawBinStatisticsDataFrame

def format_nemsis_alcohol_df(
    df: pd.DataFrame,
    start_date: datetime,
    end_date: datetime,
    measure: str,
    outcome: str,
    source_file: str,
    label_converter: Dict[int, str],
) -> pd.DataFrame:
    """Convert a NEMSIS Raw Data DF to a Dataframe.

    Parameters
    ----------
    df : pd.DataFrame


    Returns
    -------
    pd.DataFrame
    """

    df_wide = pd.pivot(
        df,
        index=['CountyName', 'CountyFIPS', 'population'],
        columns=['MeasureName'],
        values=['Rank', 'RankValue', 'ROW_NUM'],
    )
    df_wide.columns = [f'{pair[1]} ({pair[0]})' for pair in df_wide.columns]
    df_wide.reset_index(inplace=True)
    
    df_wide.rename(
        columns={
            'CountyName': 'county_name',
            'CountyFIPS': 'county_fips',
            'population': 'population_estimate',
            'Alcohol Rate (Rank)': 'alcohol_rate_rank',
            'Alcohol Rate (RankValue)': 'alcohol_rate_rank_value',
            'Alcohol Rate (ROW_NUM)': 'row_num',
        },
        inplace=True,
    )
    df_wide['outcome'] = outcome
    df_wide['measure'] = measure
    df_wide['mid'] = 'COUNTY ' + df_wide['county_fips']
    df_wide['start_date'] = pd.Timestamp(start_date)
    df_wide['end_date'] = pd.Timestamp(end_date)
    df_wide['type'] = 'COUNTY'
    df_wide['source_file'] = source_file

    return df_wide


def format_nemsis_opioid_df(
    df: pd.DataFrame,
    start_date: datetime,
    end_date: datetime,
    measure: str,
    outcome: str,
    source_file: str,
    label_converter: Dict[int, str],
) -> pd.DataFrame:
    """Convert a NEMSIS Raw Data DF to a Dataframe.

    Parameters
    ----------
    df : pd.DataFrame


    Returns
    -------
    pd.DataFrame
    """

    df_wide = pd.pivot(
        df,
        index=['CountyName', 'CountyFIPS', 'population'],
        columns=['MeasureName'],
        values=['Rank', 'RankValue', 'ROW_NUM'],
    )
    df_wide.columns = [f'{pair[1]} ({pair[0]})' for pair in df_wide.columns]
    df_wide.reset_index(inplace=True)
    
    df_wide.rename(
        columns={
            'CountyName': 'county_name',
            'CountyFIPS': 'county_fips',
            'population': 'population_estimate',
            'Opioid Rate (Rank)': 'opioid_rate_rank',
            'Opioid Rate (RankValue)': 'opioid_rate_rank_value',
            'Opioid Rate (ROW_NUM)': 'row_num',
        },
        inplace=True,
    )
    df_wide['outcome'] = outcome
    df_wide['measure'] = measure
    df_wide['mid'] = 'COUNTY ' + df_wide['county_fips']
    df_wide['start_date'] = pd.Timestamp(start_date)
    df_wide['end_date'] = pd.Timestamp(end_date)
    df_wide['type'] = 'COUNTY'
    df_wide['source_file'] = source_file

    return df_wide

def format_nemsis_bin_statistics(
    df: RawBinStatisticsDataFrame,
    bin_stats: List[str],
    start_date: datetime,
    end_date: datetime,
    measure: str,
    outcome: str,
    source_file: str,
    label_converter: Dict[int, str],
) -> pd.DataFrame:
    """Convert a NEMSIS Raw Statistics DF to a Bin Statistics Dataframe.

    Parameters
    ----------
    df : RawBinStatisticsDataFrame


    Returns
    -------
    pd.DataFrame
    """

    df['ROW_NUM'] = (df.index + 1).astype(str)

    df_wide = pd.pivot(
        df.loc[df['_TYPE_'].isin(bin_stats)],
        index=['MeasureRank'],
        columns=['_TYPE_'],    
        values=['_VALUE_', 'ROW_NUM'],
    )
    df_wide.columns = [f'{pair[1]} ({pair[0]})' for pair in df_wide.columns]
    df_wide.reset_index(inplace=True)

    df_wide['measure'] = measure
    df_wide.rename(
        columns={
            'MeasureRank': 'rank',
            'N (_VALUE_)': 'n',
            'MIN (_VALUE_)': 'min',
            'MEDIAN (_VALUE_)': 'median',
            'MEAN (_VALUE_)': 'mean',
            'MAX (_VALUE_)': 'max',
        },
        inplace=True,
    )
    df_wide['outcome'] = outcome
    df_wide['start_date'] = pd.Timestamp(start_date)
    df_wide['end_date'] = pd.Timestamp(end_date)
    df_wide['source_file'] = source_file
    df_wide['midpoint'] = (df_wide['max'] + df_wide['max']) / 2.0
    df_wide['rankValue'] = df_wide['rank'].apply(lambda x: label_converter[x])

    row_num_cols = [col for col in df_wide.columns if ('ROW_NUM' in col)]
    df_wide['row_num'] = df_wide.apply(lambda row: ','.join(map(str, [row[col] for col in row_num_cols])), axis=1)
    df_wide.drop(columns=row_num_cols, inplace=True)

    return df_wide
