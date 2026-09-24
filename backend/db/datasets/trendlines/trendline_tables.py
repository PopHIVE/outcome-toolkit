from db.base import Base
from db.datasets.mixins import CoreAuditColumns


from sqlalchemy import Column, DateTime, Double, Text


from datetime import datetime


class Trendlines(CoreAuditColumns, Base):
    """
    The represents the table for Bin Data.

    See:
      from app.db.datasets.mixins import CoreDataTable

    for a full list of the Audit Columns and Joiners.

    """

    __tablename__ = 'trendlines'
    __loader_key__ = 'trendlines'
    __data_dictionary_key__ = 'trendlines'
    __fill_nulls__ = False

    start_date = Column(DateTime(timezone=True), default=datetime(1970, 1, 1), primary_key=True)
    end_date = Column(DateTime(timezone=True), default=datetime(1971, 1, 1), primary_key=True)

    outcome = Column(Text, primary_key=True)
    measure = Column(Text, primary_key=True)
    value = Column(Double)
