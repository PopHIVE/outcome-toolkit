from db.base import Base
from db.datasets.mixins import CoreDataTable, CoreAuditColumns
from sqlalchemy import Column, Double, Integer, Text, String, DateTime
from datetime import datetime


class AggregatedSOCV1(CoreDataTable, Base):
    """
    The represents the table for Aggregated SOC Data.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'aggregated_soc_data'
    __loader_key__ = 'aggregated_soc_data'
    __data_dictionary_key__ = 'hv_soc_v1'
    __fill_nulls__ = True

    start_date = Column(DateTime(timezone=True), default=datetime(1970, 1, 1), primary_key=True)
    end_date = Column(DateTime(timezone=True), default=datetime(1971, 1, 1), primary_key=True)

    zip3 = Column(String(16))
    dist_hvid_cnt = Column(Integer)
    acute_myocardial_infarction = Column(Integer)
    aneurysm = Column(Integer)
    acute_renal_failure = Column(Integer)
    ards = Column(Integer)
    amniotic_fluid_embolism = Column(Integer)
    cardiac_arrest_vfib = Column(Integer)
    convert_cardiac_rhythm = Column(Integer)
    dic = Column(Integer)
    transfusion = Column(Integer)
    eclampsia = Column(Integer)
    hf_arrest_during_surgery = Column(Integer)
    puerperal_cvd = Column(Integer)
    pe_acute_hf = Column(Integer)
    anesthesia_comp = Column(Integer)
    sepsis = Column(Integer)
    shock = Column(Integer)
    sickle_cell_crisis = Column(Integer)
    air_thrombotic_embolism = Column(Integer)
    hysterectomy = Column(Integer)
    tracheostomy = Column(Integer)
    ventilation = Column(Integer)
    exclude_transfusion = Column(Integer)
    any_soc = Column(Integer)
    any_soc_rate = Column(Double)
    any_soc_rate_6mo = Column(Double)
    any_soc_rate_rank = Column(Double)
    any_soc_rate_6mo_rank = Column(Double)
    any_soc_rate_rank_value = Column(Text)
    any_soc_rate_6mo_rank_value = Column(Text)
    mortality = Column(Integer)
    mh_suicide_self_harm = Column(Integer)
    mh_abuse = Column(Integer)
    mh_sud = Column(Integer)
    mh_spmi = Column(Integer)
    any_soc_mortality = Column(Integer)


class RawSOCData(CoreAuditColumns, Base):
    """
    The represents the table for Raw SOC Data.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'raw_soc_data'
    __loader_key__ = 'soc_data'
    __data_dictionary_key__ = 'hv_soc_v1'
    __fill_nulls__ = False

    mid = Column(String(16), primary_key=True)
    date_delivery = Column(String(16), primary_key=True)
    race_ethnicity = Column(String(16), primary_key=True)
    age_category = Column(String(16), primary_key=True)
    state = Column(String(16), primary_key=True)
    zip3 = Column(String(16), primary_key=True)

    dist_hvid_cnt = Column(Integer)
    acute_myocardial_infarction = Column(Integer)
    aneurysm = Column(Integer)
    acute_renal_failure = Column(Integer)
    ards = Column(Integer)
    amniotic_fluid_embolism = Column(Integer)
    cardiac_arrest_vfib = Column(Integer)
    convert_cardiac_rhythm = Column(Integer)
    dic = Column(Integer)
    transfusion = Column(Integer)
    eclampsia = Column(Integer)
    hf_arrest_during_surgery = Column(Integer)
    puerperal_cvd = Column(Integer)
    pe_acute_hf = Column(Integer)
    anesthesia_comp = Column(Integer)
    sepsis = Column(Integer)
    shock = Column(Integer)
    sickle_cell_crisis = Column(Integer)
    air_thrombotic_embolism = Column(Integer)
    hysterectomy = Column(Integer)
    tracheostomy = Column(Integer)
    ventilation = Column(Integer)
    exclude_transfusion = Column(Integer)
    any_soc = Column(Integer)
    mortality = Column(Integer)
    mh_suicide_self_harm = Column(Integer)
    mh_abuse = Column(Integer)
    mh_sud = Column(Integer)
    mh_spmi = Column(Integer)
    any_soc_mortality = Column(Integer)


###################################################################


class AggregatedSOCV2(CoreDataTable, Base):
    """
    The represents the table for Aggregated SOC Data.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'aggregated_soc_data_v2'
    __loader_key__ = 'aggregated_soc_data_v2'
    __data_dictionary_key__ = 'hv_soc_v1'
    __fill_nulls__ = True

    start_date = Column(DateTime(timezone=True), default=datetime(1970, 1, 1), primary_key=True)
    end_date = Column(DateTime(timezone=True), default=datetime(1971, 1, 1), primary_key=True)

    zip3 = Column(String(16))
    dist_hvid_cnt = Column(Integer)
    acute_myocardial_infarction = Column(Integer)
    aneurysm = Column(Integer)
    acute_renal_failure = Column(Integer)
    ards = Column(Integer)
    amniotic_fluid_embolism = Column(Integer)
    cardiac_arrest_vfib = Column(Integer)
    convert_cardiac_rhythm = Column(Integer)
    dic = Column(Integer)
    transfusion = Column(Integer)
    eclampsia = Column(Integer)
    hf_arrest_during_surgery = Column(Integer)
    puerperal_cvd = Column(Integer)
    pe_acute_hf = Column(Integer)
    anesthesia_comp = Column(Integer)
    sepsis = Column(Integer)
    shock = Column(Integer)
    sickle_cell_crisis = Column(Integer)
    air_thrombotic_embolism = Column(Integer)
    hysterectomy = Column(Integer)
    tracheostomy = Column(Integer)
    ventilation = Column(Integer)
    exclude_transfusion = Column(Integer)
    any_soc = Column(Integer)
    any_soc_rate = Column(Double)
    any_soc_rate_6mo = Column(Double)
    any_soc_rate_rank = Column(Double)
    any_soc_rate_6mo_rank = Column(Double)
    any_soc_rate_rank_value = Column(Text)
    any_soc_rate_6mo_rank_value = Column(Text)
    mortality = Column(Integer)
    mh_suicide_self_harm = Column(Integer)
    mh_abuse = Column(Integer)
    mh_sud = Column(Integer)
    mh_spmi = Column(Integer)
    any_soc_mortality = Column(Integer)
