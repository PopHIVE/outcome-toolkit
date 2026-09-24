from db.base import Base
from db.datasets.mixins import CoreDataTable
from sqlalchemy import Column, Double, Integer, Text, DateTime
from datetime import datetime


class NEMSISAlcohol(CoreDataTable, Base):
    """
    The represents the table for NEMSIS Alcohol Data.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'nemsis_alcohol'
    __loader_key__ = 'nemsis_alcohol_data'
    __data_dictionary_key__ = 'nemsis_alcohol'
    __fill_nulls__ = True

    start_date = Column(DateTime(timezone=True), default=datetime(1970, 1, 1), primary_key=True)
    end_date = Column(DateTime(timezone=True), default=datetime(1970, 1, 1), primary_key=True)

    county_name = Column(Text)
    county_fips = Column(Text)
    population_estimate = Column(Double)
    alcohol_rate = Column(Double)
    alcohol_rate_6mo = Column(Double)
    alcohol_rate_rank = Column(Integer)
    alcohol_rate_6mo_rank = Column(Integer)
    alcohol_rate_rank_value = Column(Text)
    alcohol_rate_6mo_rank_value = Column(Text)

    # Deprecated
    # avg_time_to_patient_rank = Column(Integer)
    # percent_not_transported_rank = Column(Integer)
    # avg_time_to_patient_rank_value = Column(Text)
    # percent_not_transported_rank_value = Column(Text)


class NEMSISAlcohol_v2(CoreDataTable, Base):
    """
    The represents the table for NEMSIS Opioid Data.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'nemsis_alcohol_v2'
    __loader_key__ = 'nemsis_alcohol_data_v2'
    __data_dictionary_key__ = 'nemsis_alcohol'
    __fill_nulls__ = True

    start_date = Column(DateTime(timezone=True), default=datetime(1970, 1, 1), primary_key=True)
    end_date = Column(DateTime(timezone=True), default=datetime(1971, 1, 1), primary_key=True)

    county_name = Column(Text)
    county_fips = Column(Text)
    population_estimate = Column(Double)
    alcohol_rate = Column(Double)
    alcohol_rate_6mo = Column(Double)
    alcohol_rate_rank = Column(Integer)
    alcohol_rate_6mo_rank = Column(Integer)
    alcohol_rate_rank_value = Column(Text)
    alcohol_rate_6mo_rank_value = Column(Text)
