from typing import List
from app.db.database import db_session
from db.base import Base
from db.datasets.mixins import CoreDataTable
from sqlalchemy.engine import Row
from sqlalchemy import Column, Double, Integer, Text, String, DateTime
from datetime import datetime


class CBACSEstimates(CoreDataTable, Base):
    """
    The represents the table for Census ACS Estimates Data.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'cb_acs_estimates'
    __loader_key__ = 'acs_estimates'
    __data_dictionary_key__ = 'cb_acs_estimates'
    __fill_nulls__ = True

    start_date = Column(DateTime(timezone=True), default=datetime(1970, 1, 1), primary_key=True)
    end_date = Column(DateTime(timezone=True), default=datetime(1971, 1, 1), primary_key=True)

    name = Column(Text)
    total_households = Column(Double)
    less_than_10k = Column(Double)
    between_10k_15k = Column(Double)
    between_15k_20k = Column(Double)
    between_20k_25k = Column(Double)
    between_25k_30k = Column(Double)
    between_30k_35k = Column(Double)
    between_35k_40k = Column(Double)
    between_40k_45k = Column(Double)
    between_45k_50k = Column(Double)
    between_50k_60k = Column(Double)
    between_60k_75k = Column(Double)
    between_75k_100k = Column(Double)
    between_100k_125k = Column(Double)
    between_125k_150k = Column(Double)
    between_150k_200k = Column(Double)
    over_200k = Column(Double)
    total_population_race = Column(Double)
    pop_white = Column(Double)
    pop_black = Column(Double)
    pop_american_indian = Column(Double)
    pop_asian = Column(Double)
    pop_pacific_isl = Column(Double)
    pop_other = Column(Double)
    pop_multi = Column(Double)
    pop_multi_including_other = Column(Double)
    pop_multi_excluding_other = Column(Double)
    total_population_age_sex = Column(Double)
    total_male = Column(Double)
    male_pop_0_5 = Column(Double)
    male_pop_5_9 = Column(Double)
    male_pop_10_14 = Column(Double)
    male_pop_15_17 = Column(Double)
    male_pop_18_19 = Column(Double)
    male_pop_20 = Column(Double)
    male_pop_21 = Column(Double)
    male_pop_22_24 = Column(Double)
    male_pop_25_29 = Column(Double)
    male_pop_30_34 = Column(Double)
    male_pop_35_39 = Column(Double)
    male_pop_40_44 = Column(Double)
    male_pop_45_49 = Column(Double)
    male_pop_50_54 = Column(Double)
    male_pop_55_59 = Column(Double)
    male_pop_60_61 = Column(Double)
    male_pop_62_64 = Column(Double)
    male_pop_65_66 = Column(Double)
    male_pop_67_69 = Column(Double)
    male_pop_70_74 = Column(Double)
    male_pop_75_79 = Column(Double)
    male_pop_80_84 = Column(Double)
    male_pop_85_over = Column(Double)
    total_female = Column(Double)
    female_pop_0_5 = Column(Double)
    female_pop_5_9 = Column(Double)
    female_pop_10_14 = Column(Double)
    female_pop_15_17 = Column(Double)
    female_pop_18_19 = Column(Double)
    female_pop_20 = Column(Double)
    female_pop_21 = Column(Double)
    female_pop_22_24 = Column(Double)
    female_pop_25_29 = Column(Double)
    female_pop_30_34 = Column(Double)
    female_pop_35_39 = Column(Double)
    female_pop_40_44 = Column(Double)
    female_pop_45_49 = Column(Double)
    female_pop_50_54 = Column(Double)
    female_pop_55_59 = Column(Double)
    female_pop_60_61 = Column(Double)
    female_pop_62_64 = Column(Double)
    female_pop_65_66 = Column(Double)
    female_pop_67_69 = Column(Double)
    female_pop_70_74 = Column(Double)
    female_pop_75_79 = Column(Double)
    female_pop_80_84 = Column(Double)
    female_pop_85_over = Column(Double)
    geoid = Column(String(16))

    @classmethod
    def get_sums_over_geography(cls) -> List[Row]:
        """Returns the sum of all numeric columns grouped by geography type.

        Returns
        -------
        List[Row]
        """

        results = db_session.query(cls.type, *cls.numeric_columns).group_by(cls.type).all()
        return results


class CBDemographics(CoreDataTable, Base):
    """
    The represents the table for Census Demographics Data.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'cb_demographics'
    __loader_key__ = 'cb_demographics'
    __data_dictionary_key__ = 'cb_demographics'
    __fill_nulls__ = True

    start_date = Column(DateTime(timezone=True), default=datetime(1970, 1, 1), primary_key=True)
    end_date = Column(DateTime(timezone=True), default=datetime(1971, 1, 1), primary_key=True)

    name = Column(Text)
    total_population = Column(Integer)
    pop_0_5 = Column(Integer)
    pop_5_9 = Column(Integer)
    pop_10_14 = Column(Integer)
    pop_15_19 = Column(Integer)
    pop_20_24 = Column(Integer)
    pop_25_29 = Column(Integer)
    pop_30_34 = Column(Integer)
    pop_35_39 = Column(Integer)
    pop_40_44 = Column(Integer)
    pop_45_49 = Column(Integer)
    pop_50_54 = Column(Integer)
    pop_55_59 = Column(Integer)
    pop_60_64 = Column(Integer)
    pop_65_69 = Column(Integer)
    pop_70_74 = Column(Integer)
    pop_75_79 = Column(Integer)
    pop_80_84 = Column(Integer)
    pop_85_over = Column(Integer)
    male_population = Column(Integer)
    female_population = Column(Integer)
    pop_white = Column(Integer)
    pop_black = Column(Integer)
    pop_american_indian = Column(Integer)
    pop_asian = Column(Integer)
    pop_pacific_isl = Column(Integer)
    pop_other = Column(Integer)
    pop_multi = Column(Integer)
    geoid = Column(String(16))

    @classmethod
    def get_sums_over_geography(cls) -> List[Row]:
        """Returns the sum of all numeric columns grouped by geography type.

        Returns
        -------
        List[Row]
        """

        results = db_session.query(cls.type, *cls.numeric_columns).group_by(cls.type).all()
        return results
