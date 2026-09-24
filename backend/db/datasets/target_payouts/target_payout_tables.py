from db.base import Base
from sqlalchemy import Column, Date, String, Float, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.models.common import PayoutPeriod, OutcomesEnum

class TargetPayoutRate(Base):
    __tablename__ = "target_payout_rate"
    __loader_key__ = "target_payouts"
    __fill_nulls__ = False

    outcome = Column(SQLAlchemyEnum(OutcomesEnum), primary_key=True, nullable=False)
    period = Column(SQLAlchemyEnum(PayoutPeriod), primary_key=True, nullable=False)
    minimum_payout = Column(Float, nullable=False, default=0.0)
    maximum_payout = Column(Float, nullable=False)
    target_rate = Column(Float, nullable=False)