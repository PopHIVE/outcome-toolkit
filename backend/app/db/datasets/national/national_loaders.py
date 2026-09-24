import math
from typing import List
from sqlalchemy import func, and_
from sqlalchemy.engine import Row
from db.datasets.alcohol.alcohol_tables import NEMSISAlcohol, NEMSISAlcohol_v2
from db.datasets.ascvd.ascvd_tables import ASCVDScore, ASCVDScore_v2
from db.datasets.demographics.demographics_tables import CBDemographics
from db.datasets.opioid.opioid_tables import NEMSISOpioid, NEMSISOpioid_v2
from db.datasets.soc.soc_tables import AggregatedSOCV1, AggregatedSOCV2
from app.db.database import registry, db_session
from app.configs.consts import BinLabels, COUNTRY_MID, ValidGeographies
from app.utilities.serialize import (
    extract_sas_file_from_zipfile,
    last_day_month,
    first_day_month,
)
from datetime import datetime


def rankify(x: float) -> int:
    if x is None:
        return -1
    return math.floor(x)


@registry.register('load_national_ascvd_data', version='1.0')
def load_national_ascvd_data(aggregated: bool = False) -> List[Row]:
    """Generate National ASCVD Data via population weighted methodology.

    Parameters
    ----------
    aggregated : bool, optional
        Which table to run the c, by default False

    Returns
    -------
    List[Row]

    """

    if aggregated:
        TBL = ASCVDScore
    else:
        TBL = ASCVDScore_v2

    results = (
        db_session.query(
            TBL.start_date,
            TBL.end_date,
            (func.sum(TBL.total_obs)).label('total_obs'),
            (
                func.sum(CBDemographics.total_population * TBL.total_mean) / func.sum(CBDemographics.total_population)
            ).label('total_mean'),
            (
                func.sum(CBDemographics.total_population * TBL.total_mean_rank)
                / func.sum(CBDemographics.total_population)
            ).label('total_mean_rank'),
        )
        .join(CBDemographics, CBDemographics.mid == TBL.mid)
        .group_by(
            TBL.start_date,
            TBL.end_date,
        )
        .filter(and_(TBL.type == ValidGeographies.ZCTA3, TBL.start_date >= datetime(year=1975, month=1, day=1)))
    )

    records = []

    for row in results:
        record = TBL(
            mid=COUNTRY_MID,
            type=ValidGeographies.COUNTRY,
            start_date=row.start_date,
            end_date=row.end_date,
            total_obs=row.total_obs,
            total_mean=row.total_mean,
            total_mean_rank=rankify(row.total_mean_rank),
            total_mean_rank_value=BinLabels.LABELS.get(rankify(row.total_mean_rank), 'No Data'),
        )
        records.append(record)

    return records


@registry.register('load_national_soc_data', version='1.0')
def load_national_soc_data(aggregated: bool = False) -> List[Row]:
    """Generate National SOC Data via population weighted methodology.

    Parameters
    ----------
    aggregated : bool, optional
        Which table to run the c, by default False

    Returns
    -------
    List[Row]

    """

    if aggregated:
        TBL = AggregatedSOCV1
    else:
        TBL = AggregatedSOCV2

    results = (
        db_session.query(
            TBL.start_date,
            TBL.end_date,
            func.sum(TBL.dist_hvid_cnt).label('dist_hvid_cnt'),
            func.sum(TBL.acute_myocardial_infarction).label('acute_myocardial_infarction'),
            func.sum(TBL.aneurysm).label('aneurysm'),
            func.sum(TBL.acute_renal_failure).label('acute_renal_failure'),
            func.sum(TBL.ards).label('ards'),
            func.sum(TBL.amniotic_fluid_embolism).label('amniotic_fluid_embolism'),
            func.sum(TBL.cardiac_arrest_vfib).label('cardiac_arrest_vfib'),
            func.sum(TBL.convert_cardiac_rhythm).label('convert_cardiac_rhythm'),
            func.sum(TBL.dic).label('dic'),
            func.sum(TBL.transfusion).label('transfusion'),
            func.sum(TBL.eclampsia).label('eclampsia'),
            func.sum(TBL.hf_arrest_during_surgery).label('hf_arrest_during_surgery'),
            func.sum(TBL.puerperal_cvd).label('puerperal_cvd'),
            func.sum(TBL.pe_acute_hf).label('pe_acute_hf'),
            func.sum(TBL.anesthesia_comp).label('anesthesia_comp'),
            func.sum(TBL.sepsis).label('sepsis'),
            func.sum(TBL.shock).label('shock'),
            func.sum(TBL.sickle_cell_crisis).label('sickle_cell_crisis'),
            func.sum(TBL.air_thrombotic_embolism).label('air_thrombotic_embolism'),
            func.sum(TBL.hysterectomy).label('hysterectomy'),
            func.sum(TBL.tracheostomy).label('tracheostomy'),
            func.sum(TBL.ventilation).label('ventilation'),
            func.sum(TBL.exclude_transfusion).label('exclude_transfusion'),
            func.sum(TBL.any_soc).label('any_soc'),
            (
                func.sum(CBDemographics.total_population * TBL.any_soc_rate)
                / func.sum(CBDemographics.total_population)
            ).label('any_soc_rate'),
            (
                func.sum(CBDemographics.total_population * TBL.any_soc_rate_rank)
                / func.sum(CBDemographics.total_population)
            ).label('any_soc_rate_rank'),
            func.sum(TBL.mortality).label('mortality'),
            func.sum(TBL.mh_suicide_self_harm).label('mh_suicide_self_harm'),
            func.sum(TBL.mh_abuse).label('mh_abuse'),
            func.sum(TBL.mh_sud).label('mh_sud'),
            func.sum(TBL.mh_spmi).label('mh_spmi'),
            func.sum(TBL.any_soc_mortality).label('any_soc_mortality'),
        )
        .join(CBDemographics, CBDemographics.mid == TBL.mid)
        .group_by(
            TBL.start_date,
            TBL.end_date,
        )
        .filter(and_(TBL.type == ValidGeographies.ZCTA3, TBL.start_date >= datetime(year=1975, month=1, day=1)))
    )

    records = []

    for row in results:
        record = TBL(
            mid=COUNTRY_MID,
            type=ValidGeographies.COUNTRY,
            start_date=row.start_date,
            end_date=row.end_date,
            any_soc_rate=row.any_soc_rate,
            any_soc_rate_rank=rankify(row.any_soc_rate_rank),
            any_soc_rate_rank_value=BinLabels.LABELS.get(rankify(row.any_soc_rate_rank), 'No Data'),
            dist_hvid_cnt=row.dist_hvid_cnt,
            acute_myocardial_infarction=row.acute_myocardial_infarction,
            aneurysm=row.aneurysm,
            acute_renal_failure=row.acute_renal_failure,
            ards=row.ards,
            amniotic_fluid_embolism=row.amniotic_fluid_embolism,
            cardiac_arrest_vfib=row.cardiac_arrest_vfib,
            convert_cardiac_rhythm=row.convert_cardiac_rhythm,
            dic=row.dic,
            transfusion=row.transfusion,
            eclampsia=row.eclampsia,
            hf_arrest_during_surgery=row.hf_arrest_during_surgery,
            puerperal_cvd=row.puerperal_cvd,
            pe_acute_hf=row.pe_acute_hf,
            anesthesia_comp=row.anesthesia_comp,
            sepsis=row.sepsis,
            shock=row.shock,
            sickle_cell_crisis=row.sickle_cell_crisis,
            air_thrombotic_embolism=row.air_thrombotic_embolism,
            hysterectomy=row.hysterectomy,
            tracheostomy=row.tracheostomy,
            ventilation=row.ventilation,
            exclude_transfusion=row.exclude_transfusion,
            any_soc=row.any_soc,
            mortality=row.mortality,
            mh_suicide_self_harm=row.mh_suicide_self_harm,
            mh_abuse=row.mh_abuse,
            mh_sud=row.mh_sud,
            mh_spmi=row.mh_spmi,
            any_soc_mortality=row.any_soc_mortality,
        )
        records.append(record)

    return records


@registry.register('load_national_nemsis_data', version='1.0')
def load_national_nemsis_data(outcome: str, aggregated: bool = False) -> List[Row]:
    """Generate National NEMSIS Data via population weighted methodology.

    Parameters
    ----------
    outcome : str
        opioid or alcohol outcomes supported.
    aggregated : bool, optional
        which table to run the aggregation on, by default False

    Returns
    -------
    List[Row]

    """

    if outcome == 'opioid':
        if aggregated:
            TBL = NEMSISOpioid
        else:
            TBL = NEMSISOpioid_v2
        METRIC_COL = TBL.opioid_rate_rank
    elif outcome == 'alcohol':
        if aggregated:
            TBL = NEMSISAlcohol
        else:
            TBL = NEMSISAlcohol_v2
        METRIC_COL = TBL.alcohol_rate_rank
    else:
        raise ValueError('Unsuported Outcome')

    results = (
        db_session.query(
            TBL.start_date,
            TBL.end_date,
            (func.sum(TBL.population_estimate)).label('population_estimate'),
            (func.sum(CBDemographics.total_population * METRIC_COL) / func.sum(CBDemographics.total_population)).label(
                'weighted_metric_value'
            ),
        )
        .join(CBDemographics, CBDemographics.mid == TBL.mid)
        .group_by(
            TBL.start_date,
            TBL.end_date,
        )
        .filter(and_(TBL.type == ValidGeographies.COUNTY, TBL.start_date >= datetime(year=1975, month=1, day=1)))
    )

    records = []

    for row in results:
        if outcome == 'opioid':
            record = TBL(
                mid=COUNTRY_MID,
                type=ValidGeographies.COUNTRY,
                start_date=row.start_date,
                end_date=row.end_date,
                population_estimate=row.population_estimate,
                opioid_rate_rank=rankify(row.weighted_metric_value),
                opioid_rate_rank_value=BinLabels.LABELS.get(rankify(row.weighted_metric_value), 'No Data'),
            )
            records.append(record)
        else:
            record = TBL(
                mid=COUNTRY_MID,
                type=ValidGeographies.COUNTRY,
                start_date=row.start_date,
                end_date=row.end_date,
                population_estimate=row.population_estimate,
                alcohol_rate_rank=rankify(row.weighted_metric_value),
                alcohol_rate_rank_value=BinLabels.LABELS.get(rankify(row.weighted_metric_value), 'No Data'),
            )
            records.append(record)

    return records


@registry.register('load_national_nemsis_data_trendlines', version='1.0')
def load_national_nemsis_data_trendlines(zip_file: str, file_name_trendlines: str, outcome: str, conversion_factor: int = 1) -> List[Row]:
    """Generate National NEMSIS Data via population weighted methodology.

    Parameters
    ----------
    zip_file: str
    file_name_trendlines: str
    outcome : str
        opioid or alcohol outcomes supported.
    conversion_factor: int

    Returns
    -------
    List[Row]

    """

    if outcome == 'opioid':
        METRIC = 'Opioid'
    elif outcome == 'alcohol':
        METRIC = 'Alcohol'
    else:
        raise ValueError('Unsuported Outcome')


    df = extract_sas_file_from_zipfile(zip_file, file_name_trendlines)
    df['ROW_NUM'] = df.index + 1
    df['start_date'] = df.apply(lambda row: first_day_month(int(row['year']), int(row['month'])), axis=1)
    df['end_date'] = df.apply(lambda row: last_day_month(int(row['year']), int(row['month'])), axis=1)

    records = []

    for _, row in df.loc[df['Metric']==METRIC].iterrows():
        
        if outcome == 'opioid':
            record = NEMSISOpioid_v2(
                mid=COUNTRY_MID,
                type=ValidGeographies.COUNTRY,
                start_date=row.start_date,
                end_date=row.end_date,
                population_estimate=row.population,
                opioid_rate=row.monthlyRate * conversion_factor,
                row_num=row.ROW_NUM
            )
        else:
            record = NEMSISAlcohol_v2(
                mid=COUNTRY_MID,
                type=ValidGeographies.COUNTRY,
                start_date=row.start_date,
                end_date=row.end_date,
                population_estimate=row.population,
                alcohol_rate=row.monthlyRate * conversion_factor,
                row_num=row.ROW_NUM
            )
        
        records.append(record)

    return records