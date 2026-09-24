import pandas as pd
import numpy as np
from typing import List
from sqlalchemy.engine import Row
from app.configs.consts import ValidMorpheusIDs
from db.datasets.soc.soc_tables import RawSOCData, AggregatedSOCV1, AggregatedSOCV2
from app.db.database import registry
from app.configs.consts import Replacements, BinLabels, NormalizationRates
from db.datasets.opioid.opioid_tables import Bins
from app.utilities.serialize import first_day_month, last_day_month


@registry.register('load_hv_soc_data', version='1.0')
def load_hv_soc_data(input_file: str) -> List[Row]:
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
    results['MID'] = results['zip3'].apply(lambda x: f'ZCTA3 {x}')
    results['is_valid'] = results['MID'].apply(ValidMorpheusIDs.is_valid)

    records = []
    for index, row in results.replace(Replacements.JAVASCRIPT_SAFE).loc[results.is_valid].iterrows():
        record = RawSOCData(
            date_delivery=row['date_delivery'],
            race_ethnicity=row['race_ethnicity'],
            age_category=row['age_category'],
            state=row['state'],
            zip3=row['zip3'],
            mid=row['MID'],
            dist_hvid_cnt=row['dist_hvid_cnt'],
            acute_myocardial_infarction=row['acute_myocardial_infarction'],
            aneurysm=row['aneurysm'],
            acute_renal_failure=row['acute_renal_failure'],
            ards=row['ARDS'],
            amniotic_fluid_embolism=row['amniotic_fluid_embolism'],
            cardiac_arrest_vfib=row['cardiac_arrest_vfib'],
            convert_cardiac_rhythm=row['convert_cardiac_rhythm'],
            dic=row['DIC'],
            transfusion=row['transfusion'],
            eclampsia=row['eclampsia'],
            hf_arrest_during_surgery=row['HF_arrest_during_surgery'],
            puerperal_cvd=row['puerperal_CVD'],
            pe_acute_hf=row['PE_acute_HF'],
            anesthesia_comp=row['anesthesia_comp'],
            sepsis=row['sepsis'],
            shock=row['shock'],
            sickle_cell_crisis=row['sickle_cell_crisis'],
            air_thrombotic_embolism=row['air_thrombotic_embolism'],
            hysterectomy=row['hysterectomy'],
            tracheostomy=row['tracheostomy'],
            ventilation=row['ventilation'],
            exclude_transfusion=row['exclude_transfusion'],
            any_soc=row['any_SOC'],
            mortality=row['mortality'],
            mh_suicide_self_harm=row['mh_suicide_self_harm'],
            mh_abuse=row['mh_abuse'],
            mh_sud=row['mh_sud'],
            mh_spmi=row['mh_spmi'],
            any_soc_mortality=row['any_SOC_mortality'],
            row_num=index + 1,
        )

        records.append(record)

    return records


@registry.register('load_aggregated_hv_soc_data', version='1.0')
def load_aggregated_hv_soc_data(input_file: str) -> List[Row]:
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

    excluded = ['date_delivery', 'race_ethnicity', 'age_category', 'state']
    keepers = [c for c in results.columns if c not in excluded]

    start_date = first_day_month(*map(int, results['date_delivery'].min().split('-')))
    end_date = last_day_month(*map(int, results['date_delivery'].max().split('-')))

    aggregated_results = results[keepers].groupby(['zip3']).sum().reset_index()
    aggregated_results['MID'] = aggregated_results['zip3'].apply(lambda x: f'ZCTA3 {x}')
    aggregated_results['is_valid'] = aggregated_results['MID'].apply(ValidMorpheusIDs.is_valid)

    # Calculate the SOC Rate (This Line Needs to change if we normalize to per 10k...)
    aggregated_results['any_soc_rate'] = (
        NormalizationRates.SOC * aggregated_results['any_SOC'] / aggregated_results['dist_hvid_cnt']
    )
    aggregated_results['any_soc_rate_rank'] = pd.qcut(
        aggregated_results['any_soc_rate'], 10, labels=BinLabels.LABELS.keys()
    )

    records = []
    for index, row in (
        aggregated_results.replace(Replacements.JAVASCRIPT_SAFE).loc[aggregated_results.is_valid].iterrows()
    ):
        record = AggregatedSOCV1(
            zip3=row['zip3'],
            start_date=start_date,
            end_date=end_date,
            mid=row['MID'],
            dist_hvid_cnt=row['dist_hvid_cnt'],
            acute_myocardial_infarction=row['acute_myocardial_infarction'],
            aneurysm=row['aneurysm'],
            acute_renal_failure=row['acute_renal_failure'],
            ards=row['ARDS'],
            amniotic_fluid_embolism=row['amniotic_fluid_embolism'],
            cardiac_arrest_vfib=row['cardiac_arrest_vfib'],
            convert_cardiac_rhythm=row['convert_cardiac_rhythm'],
            dic=row['DIC'],
            transfusion=row['transfusion'],
            eclampsia=row['eclampsia'],
            hf_arrest_during_surgery=row['HF_arrest_during_surgery'],
            puerperal_cvd=row['puerperal_CVD'],
            pe_acute_hf=row['PE_acute_HF'],
            anesthesia_comp=row['anesthesia_comp'],
            sepsis=row['sepsis'],
            shock=row['shock'],
            sickle_cell_crisis=row['sickle_cell_crisis'],
            air_thrombotic_embolism=row['air_thrombotic_embolism'],
            hysterectomy=row['hysterectomy'],
            tracheostomy=row['tracheostomy'],
            ventilation=row['ventilation'],
            exclude_transfusion=row['exclude_transfusion'],
            any_soc=row['any_SOC'],
            any_soc_rate=row['any_soc_rate'],
            any_soc_rate_rank=row['any_soc_rate_rank'],
            any_soc_rate_rank_value=BinLabels.LABELS[row['any_soc_rate_rank']],
            mortality=row['mortality'],
            mh_suicide_self_harm=row['mh_suicide_self_harm'],
            mh_abuse=row['mh_abuse'],
            mh_sud=row['mh_sud'],
            mh_spmi=row['mh_spmi'],
            any_soc_mortality=row['any_SOC_mortality'],
            type='ZCTA3',
            row_num=index + 1,
        )

        records.append(record)

    return records


@registry.register('load_aggregated_hv_soc_bins', version='1.0')
def load_aggregated_hv_soc_bins(input_file: str) -> List[Row]:
    """ETL Scripts to Generate HV SOC Bin Data.

    Parameters
    ----------
    input_file : str

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    records = []

    results = pd.read_parquet(input_file)
    results['row_num'] = (results.index + 1).astype(str)

    excluded = ['date_delivery', 'race_ethnicity', 'age_category', 'state']
    keepers = [c for c in results.columns if c not in excluded]

    start_date = first_day_month(*map(int, results['date_delivery'].min().split('-')))
    end_date = last_day_month(*map(int, results['date_delivery'].max().split('-')))

    aggregated_results = results[keepers].groupby(['zip3']).sum().reset_index()
    aggregated_results['MID'] = aggregated_results['zip3'].apply(lambda x: f'ZCTA3 {x}')
    aggregated_results['is_valid'] = aggregated_results['MID'].apply(ValidMorpheusIDs.is_valid)

    # Calculate the SOC Rate (This Line Needs to change if we normalize to per 10k...)
    aggregated_results['any_soc_rate'] = (
        NormalizationRates.SOC * aggregated_results['any_SOC'] / aggregated_results['dist_hvid_cnt']
    )
    aggregated_results['any_soc_rate_rank'] = pd.qcut(
        aggregated_results['any_soc_rate'], 10, labels=BinLabels.LABELS.keys()
    )

    bin_stats = (
        aggregated_results.replace(Replacements.JAVASCRIPT_SAFE)
        .loc[aggregated_results.is_valid]
        .groupby(['any_soc_rate_rank'])
        .agg(
            bin_mean=('any_soc_rate', 'mean'),
            bin_median=('any_soc_rate', 'median'),
            bin_min=('any_soc_rate', 'min'),
            bin_max=('any_soc_rate', 'max'),
            bin_count=('any_soc_rate', len),
        )
        .reset_index()
    )
    bin_stats['bin_midpoint'] = (bin_stats['bin_max'] + bin_stats['bin_min']) / 2.0

    print(bin_stats, flush=True)

    bin_stats['start_date'] = start_date
    bin_stats['end_date'] = end_date

    bin_stats_sorted = bin_stats.sort_values(by=['start_date', 'end_date', 'any_soc_rate_rank'])

    bin_stats_sorted['next_min'] = bin_stats_sorted.groupby(['start_date', 'end_date'])['bin_min'].shift(-1)
    bin_stats_sorted['next_max'] = bin_stats_sorted.groupby(['start_date', 'end_date'])['bin_max'].shift(-1)

    for index, row in bin_stats_sorted.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        if not pd.isna(row['next_min']):
            max_=row['next_min']
        else:
            max_=row['bin_max']
        records.append(
            Bins(
                outcome='soc',
                measure='any_soc_rate',
                start_date=start_date,
                end_date=end_date,
                rank=row['any_soc_rate_rank'],
                rankValue=BinLabels.LABELS[row['any_soc_rate_rank']],
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


#############################################################################


@registry.register('load_aggregated_hv_soc_data_v2', version='2.0')
def load_aggregated_hv_soc_data_v2(input_file: str) -> List[Row]:
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

    aggregated_results = results[keepers].groupby(['zip3', 'date_delivery']).sum().reset_index()
    aggregated_results['MID'] = aggregated_results['zip3'].apply(lambda x: f'ZCTA3 {x}')
    aggregated_results['is_valid'] = aggregated_results['MID'].apply(ValidMorpheusIDs.is_valid)
    aggregated_results['start_date'] = aggregated_results['date_delivery'].apply(
        lambda d: first_day_month(*map(int, d.split('-')))
    )
    aggregated_results['end_date'] = aggregated_results['date_delivery'].apply(
        lambda d: last_day_month(*map(int, d.split('-')))
    )

    aggregated_results['any_soc_rate'] = (
        NormalizationRates.SOC * aggregated_results['any_SOC'] / aggregated_results['dist_hvid_cnt']
    )
    aggregated_results['any_soc_rate_rank'] = 0

    non_zeroes = aggregated_results['any_soc_rate'] != 0
    aggregated_results.loc[non_zeroes, 'any_soc_rate_rank'] = (
        aggregated_results[non_zeroes]
        .groupby('date_delivery')['any_soc_rate']
        .transform(lambda x: pd.qcut(x, 9, labels=False) + 1)
    )
    # aggregated_results['any_soc_rate_rank'] = pd.qcut(aggregated_results['any_soc_rate'], 10, labels=BinLabels.LABELS.keys())

    records = []
    for index, row in (
        aggregated_results.replace(Replacements.JAVASCRIPT_SAFE).loc[aggregated_results.is_valid].iterrows()
    ):
        record = AggregatedSOCV2(
            zip3=row['zip3'],
            start_date=row['start_date'],
            end_date=row['end_date'],
            mid=row['MID'],
            dist_hvid_cnt=row['dist_hvid_cnt'],
            acute_myocardial_infarction=row['acute_myocardial_infarction'],
            aneurysm=row['aneurysm'],
            acute_renal_failure=row['acute_renal_failure'],
            ards=row['ARDS'],
            amniotic_fluid_embolism=row['amniotic_fluid_embolism'],
            cardiac_arrest_vfib=row['cardiac_arrest_vfib'],
            convert_cardiac_rhythm=row['convert_cardiac_rhythm'],
            dic=row['DIC'],
            transfusion=row['transfusion'],
            eclampsia=row['eclampsia'],
            hf_arrest_during_surgery=row['HF_arrest_during_surgery'],
            puerperal_cvd=row['puerperal_CVD'],
            pe_acute_hf=row['PE_acute_HF'],
            anesthesia_comp=row['anesthesia_comp'],
            sepsis=row['sepsis'],
            shock=row['shock'],
            sickle_cell_crisis=row['sickle_cell_crisis'],
            air_thrombotic_embolism=row['air_thrombotic_embolism'],
            hysterectomy=row['hysterectomy'],
            tracheostomy=row['tracheostomy'],
            ventilation=row['ventilation'],
            exclude_transfusion=row['exclude_transfusion'],
            any_soc=row['any_SOC'],
            any_soc_rate=row['any_soc_rate'],
            any_soc_rate_rank=row['any_soc_rate_rank'],
            any_soc_rate_rank_value=BinLabels.LABELS[row['any_soc_rate_rank']],
            mortality=row['mortality'],
            mh_suicide_self_harm=row['mh_suicide_self_harm'],
            mh_abuse=row['mh_abuse'],
            mh_sud=row['mh_sud'],
            mh_spmi=row['mh_spmi'],
            any_soc_mortality=row['any_SOC_mortality'],
            type='ZCTA3',
            row_num=index + 1,
        )

        records.append(record)

    return records


@registry.register('load_aggregated_hv_soc_bins_v2', version='2.0')
def load_aggregated_hv_soc_bins_v2(input_file: str) -> List[Row]:
    """ETL Scripts to Generate HV SOC Bin Data.

    Parameters
    ----------
    input_file : str

    Returns
    -------
    List[Row]
        List of Rows to be inserted into the DB.
    """

    records = []

    results = pd.read_parquet(input_file)
    results['row_num'] = (results.index + 1).astype(str)

    excluded = ['race_ethnicity', 'age_category', 'state']
    keepers = [c for c in results.columns if c not in excluded]

    aggregated_results = results[keepers].groupby(['zip3', 'date_delivery']).sum().reset_index()
    aggregated_results['MID'] = aggregated_results['zip3'].apply(lambda x: f'ZCTA3 {x}')
    aggregated_results['is_valid'] = aggregated_results['MID'].apply(ValidMorpheusIDs.is_valid)
    aggregated_results['start_date'] = aggregated_results['date_delivery'].apply(
        lambda d: first_day_month(*map(int, d.split('-')))
    )
    aggregated_results['end_date'] = aggregated_results['date_delivery'].apply(
        lambda d: last_day_month(*map(int, d.split('-')))
    )

    # Calculate the SOC Rate (This Line Needs to change if we normalize to per 10k...)
    aggregated_results['any_soc_rate'] = (
        NormalizationRates.SOC * aggregated_results['any_SOC'] / aggregated_results['dist_hvid_cnt']
    )
    aggregated_results['any_soc_rate_rank'] = 0

    non_zeroes = aggregated_results['any_soc_rate'] != 0
    aggregated_results.loc[non_zeroes, 'any_soc_rate_rank'] = (
        aggregated_results[non_zeroes]
        .groupby('date_delivery')['any_soc_rate']
        .transform(lambda x: pd.qcut(x, 9, labels=False) + 1)
    )
    # aggregated_results['any_soc_rate_rank'] = pd.qcut(aggregated_results['any_soc_rate'], 10, labels=BinLabels.LABELS.keys())

    bin_stats = (
        aggregated_results.replace(Replacements.JAVASCRIPT_SAFE)
        .loc[aggregated_results.is_valid]
        .groupby(['start_date', 'end_date', 'any_soc_rate_rank'])
        .agg(
            bin_mean=('any_soc_rate', 'mean'),
            bin_median=('any_soc_rate', 'median'),
            bin_min=('any_soc_rate', 'min'),
            bin_max=('any_soc_rate', 'max'),
            bin_count=('any_soc_rate', len),
        )
        .reset_index()
    )
    bin_stats['bin_midpoint'] = (bin_stats['bin_max'] + bin_stats['bin_min']) / 2.0

    print(bin_stats, flush=True)

    bin_stats_sorted = bin_stats.sort_values(by=['start_date', 'end_date', 'any_soc_rate_rank'])

    bin_stats_sorted['next_min'] = bin_stats_sorted.groupby(['start_date', 'end_date'])['bin_min'].shift(-1)
    bin_stats_sorted['next_max'] = bin_stats_sorted.groupby(['start_date', 'end_date'])['bin_max'].shift(-1)

    for index, row in bin_stats_sorted.replace(Replacements.JAVASCRIPT_SAFE).iterrows():
        # check for fillNA function
        if not pd.isna(row['next_min']):
            max_=row['next_min']
        else:
            max_=row['bin_max']
        records.append(
            Bins(
                outcome='soc',
                measure='any_soc_rate',
                start_date=row['start_date'],
                end_date=row['end_date'],
                rank=row['any_soc_rate_rank'],
                rankValue=BinLabels.LABELS[row['any_soc_rate_rank']],
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
