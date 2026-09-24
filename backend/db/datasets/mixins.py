from typing import List, Dict, Any
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import ForeignKey, Column, Double, Integer, Text, String, DateTime
from collections import OrderedDict


class CoreAuditColumns(object):
    """These are the Core Columns a table needs to be 'Auditable'"""

    # Data Lineage Columns
    created = Column(DateTime(timezone=True), server_default=func.now())
    data_provider = Column(Text, nullable=True)
    data_release = Column(Text, nullable=True)
    data_bundle = Column(Text, nullable=True)
    source_file = Column(Text, nullable=True)
    row_num = Column(Text, nullable=True)
    etl_version = Column(Text, nullable=True)


class CoreDataTable(CoreAuditColumns):
    """These are the Core Attributes and Columns  a table needs to be auto joined
    to the 'area' table
    """

    type = Column(String(16), index=True)

    @declared_attr
    def mid(cls):
        """Every Table MUST have a MID Foreign Key Column"""
        return Column('mid', String(32), ForeignKey('area.mid'), primary_key=True)

    @classmethod
    def numeric_columns(cls) -> List[Column]:
        """List of all Numeric Columns in the Table

        Returns
        -------
        List[Column]
        """

        return filter(lambda c: isinstance(c, (Double, Integer)), cls.columns)

    def to_dict(self) -> Dict[str, Any]:
        """Helper function to convert a 'row' result to dictionaru

        Returns
        -------
        Dict[str, Any]
        """

        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result


######################################################################
