from db.base import Base
from db.datasets.mixins import CoreDataTable, CoreAuditColumns
from sqlalchemy import Column, Double, Integer, Text, String, DateTime
from datetime import datetime


class NEMSISOpioid(CoreDataTable, Base):
    """
    The represents the table for NEMSIS Opioid Data.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'nemsis_opioid'
    __loader_key__ = 'nemsis_opioid_data'
    __data_dictionary_key__ = 'nemsis_opioid'
    __fill_nulls__ = True

    start_date = Column(DateTime(timezone=True), default=datetime(1970, 1, 1), primary_key=True)
    end_date = Column(DateTime(timezone=True), default=datetime(1971, 1, 1), primary_key=True)

    county_name = Column(Text)
    county_fips = Column(Text)
    population_estimate = Column(Double)
    opioid_rate = Column(Double)
    opioid_rate_6mo = Column(Double)
    opioid_rate_rank = Column(Integer)
    opioid_rate_6mo_rank = Column(Integer)
    opioid_rate_rank_value = Column(Text)
    opioid_rate_6mo_rank_value = Column(Text)

    # Deprecated
    # avg_naloxone_administrations_rank = Column(Integer)
    # avg_time_to_patient_rank = Column(Integer)
    # percent_not_transported_rank = Column(Integer)
    # avg_naloxone_administrations_rank_value = Column(Text)
    # avg_time_to_patient_rank_value = Column(Text)
    # percent_not_transported_rank_value = Column(Text)


class NEMSISOpioid_v2(CoreDataTable, Base):
    """
    The represents the table for NEMSIS Opioid Data.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'nemsis_opioid_v2'
    __loader_key__ = 'nemsis_opioid_data_v2'
    __data_dictionary_key__ = 'nemsis_opioid'
    __fill_nulls__ = True

    start_date = Column(DateTime(timezone=True), default=datetime(1970, 1, 1), primary_key=True)
    end_date = Column(DateTime(timezone=True), default=datetime(1971, 1, 1), primary_key=True)

    county_name = Column(Text)
    county_fips = Column(Text)
    population_estimate = Column(Double)
    opioid_rate = Column(Double)
    opioid_rate_6mo = Column(Double)
    opioid_rate_rank = Column(Integer)
    opioid_rate_6mo_rank = Column(Integer)
    opioid_rate_rank_value = Column(Text)
    opioid_rate_6mo_rank_value = Column(Text)


class Bins(CoreAuditColumns, Base):
    """
    The represents the table for Bin Data.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'bins'
    __loader_key__ = 'bins'
    __data_dictionary_key__ = 'bins'
    __fill_nulls__ = False

    start_date = Column(DateTime(timezone=True), default=datetime(1970, 1, 1), primary_key=True)
    end_date = Column(DateTime(timezone=True), default=datetime(1971, 1, 1), primary_key=True)

    outcome = Column(Text, primary_key=True)
    measure = Column(Text, primary_key=True)
    rank = Column(Integer, primary_key=True)
    rankValue = Column(Text)
    n = Column(Integer)
    min = Column(Double)
    median = Column(Double)
    mean = Column(Double)
    midpoint = Column(Double)
    max = Column(Double)
    type = Column(String(16))
