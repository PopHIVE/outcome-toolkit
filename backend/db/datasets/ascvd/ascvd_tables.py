from db.base import Base
from db.datasets.mixins import CoreDataTable
from sqlalchemy import Column, Double, Integer, Text, String, DateTime
from datetime import datetime


class ASCVDScore(CoreDataTable, Base):
    """
    The represents the table for ASCVD Scores Data.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'ascvd_scores'
    __loader_key__ = 'ascvd_scores'
    __data_dictionary_key__ = 'veradigm_ascvd_scores'
    __fill_nulls__ = True

    start_date = Column(DateTime(timezone=True), default=datetime(1970, 1, 1), primary_key=True)
    end_date = Column(DateTime(timezone=True), default=datetime(1971, 1, 1), primary_key=True)

    zip3 = Column(String(16))
    total_obs = Column(Integer)
    total_mean = Column(Double)
    total_mean_6mo = Column(Double)
    total_mean_rank = Column(Double)
    total_mean_6mo_rank = Column(Double)
    total_mean_rank_value = Column(Text)
    total_mean_6mo_rank_value = Column(Text)

    # By Age
    age_40_to_49_obs = Column(Integer)
    age_40_to_49_mean = Column(Double)
    age_50_to_59_obs = Column(Integer)
    age_50_to_59_mean = Column(Double)
    age_60_to_69_obs = Column(Integer)
    age_60_to_69_mean = Column(Double)
    age_70_obs = Column(Integer)
    age_70_mean = Column(Double)

    # By Gender
    female_obs = Column(Integer)
    female_mean = Column(Double)
    male_obs = Column(Integer)
    male_mean = Column(Double)

    # By Race
    asian_obs = Column(Integer)
    asian_mean = Column(Double)
    black_obs = Column(Integer)
    black_mean = Column(Double)
    null_race_obs = Column(Integer)
    null_race_mean = Column(Double)
    other_obs = Column(Integer)
    other_mean = Column(Double)
    white_obs = Column(Integer)
    white_mean = Column(Double)

    # By Ethnicity
    hispanic_obs = Column(Integer)
    hispanic_mean = Column(Double)
    null_ethnicity_obs = Column(Integer)
    null_ethnicity_mean = Column(Double)
    non_hispanic_obs = Column(Integer)
    non_hispanic_mean = Column(Double)


class ASCVDScore_v2(CoreDataTable, Base):
    """
    The represents the table for ASCVD Scores Data.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'ascvd_scores_v2'
    __loader_key__ = 'ascvd_scores_v2'
    __data_dictionary_key__ = 'veradigm_ascvd_scores'
    __fill_nulls__ = True

    start_date = Column(DateTime(timezone=True), default=datetime(1970, 1, 1), primary_key=True)
    end_date = Column(DateTime(timezone=True), default=datetime(1971, 1, 1), primary_key=True)
    zip3 = Column(String(16))

    total_obs = Column(Integer)
    total_mean = Column(Double)
    total_mean_6mo = Column(Double)
    total_mean_rank = Column(Double)
    total_mean_6mo_rank = Column(Double)
    total_mean_rank_value = Column(Text)
    total_mean_6mo_rank_value = Column(Text)
