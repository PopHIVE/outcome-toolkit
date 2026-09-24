from enum import Enum
from typing import Any
from app.configs.consts import ValidGeographies, ValidMorpheusIDs, ValidOutcomes
from app.ext.exceptions.errors import (
    InvalidGeography,
    InvalidMID,
    InvalidOutcome,
    InvalidMetric,
)
from pydantic import BaseModel, validator


import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

class UserRole(Enum):
    PROGRAM_ADMIN = "PROGRAM_ADMIN"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    PROJECT_MEMBER = "PROJECT_MEMBER"

class ProjectRole(Enum):
    HEALTH_ACCELERATOR = "Health Accelerator"
    OUTCOME_BUYER = "Outcome Buyer"

class PayoutPeriod(Enum):
    BASELINE = "baseline"
    SIX_MONTHS = "6"
    TWELVE_MONTHS = "12"
    EIGHTEEN_MONTHS = "18"
    TWENTY_FOUR_MONTHS = "24"
    THIRTY_MONTHS = "30"
    THIRTY_SIX_MONTHS = "36"
    TOTAL = "total"

# Separate class for use with DB and pydantic
class OutcomesEnum(Enum):
    ALCOHOL = 'alcohol'
    OPIOID = 'opioid'
    SOC =  'soc'
    CARDIO = 'cardio'

class ProjectPerformerType(Enum):
    AHA = 'AHA'
    PHA = 'PHA'

class Geography(BaseModel):
    """A quick Wrapper to Validate Geographies.
    Will raise error if provided value is invalid.
    """

    type_: str

    @validator('type_', pre=True, always=True)
    def validate_geography(cls, v: Any) -> Any:
        if ValidGeographies.is_valid(v.upper()):
            return v.upper()

        raise InvalidGeography(v, f'Invalid Geograpy Provided. Valid Types are: {ValidGeographies.ALL()}')


class MorpheusID(BaseModel):
    """A quick Wrapper to Validate Morpheus IDs."""

    type_: str = None
    mid: str

    @validator('mid', pre=True, always=True)
    def validate_mid(cls, v: str, values) -> str:
        if ValidMorpheusIDs.is_valid(v, values['type_']):
            return v

        raise InvalidMID(v, 'Invalid MID Provided.')


class Outcome(BaseModel):
    """A quick Wrapper to Validate Outcomes."""

    outcome: str

    @validator('outcome', pre=True, always=True)
    def validate_outcome(cls, v: Any) -> Any:
        if ValidOutcomes.is_valid(v):
            return v

        raise InvalidOutcome(v, f'Invalid Outcomes Provided. Valid Types are: {ValidOutcomes.ALL()}')

    def get_metric_mappings(self, metric: str) -> bool:
        for metric_bundle in ValidOutcomes.metrics()[self.outcome]:
            if metric_bundle['metric'] == metric:
                return metric_bundle

        raise InvalidMetric(
            metric,
            f"Invalid Metric Provided. Valid Metrics are: {[m['metric'] for m in ValidOutcomes.metrics()[self.outcome]]}",
        )