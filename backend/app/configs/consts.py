from enum import Enum
import os
import yaml
import pandas as pd
import numpy as np
from typing import Dict, Iterable, Tuple, Any, List
from dataclasses import dataclass
from app.configs.settings import Directories


with open(os.path.join(Directories.CONF_DIRECTORY, 'consts.yml')) as stream:
    constants = yaml.safe_load(stream)['constants']


class Replacements:
    JAVASCRIPT_SAFE: Dict[str, Any] = {'-': None, np.nan: None, -1: None}


class ValidMorpheusIDs:
    VALID_MIDS: Dict[str, str] = {
        row.mid: row.type
        for _, row in pd.read_csv(os.path.join(Directories.STATIC_DIRECTORY, 'valid_mids.csv')).iterrows()
    }

    @classmethod
    def is_valid(cls, mid: str, geography: str = None) -> bool:
        if mid not in cls.VALID_MIDS:
            return False

        if geography is not None:
            return cls.VALID_MIDS[mid] == geography

        return True

    @classmethod
    def mids(cls) -> Iterable[Tuple[str, str]]:
        return cls.VALID_MIDS.items()


@dataclass
class ValidGeographies:
    COUNTRY: str = constants['geographies'].get('country', 'COUNTRY')
    STATE: str = constants['geographies'].get('state', 'STATE')
    COUNTY: str = constants['geographies'].get('county', 'COUNTY')
    ZCTA3: str = constants['geographies'].get('zcta3', 'ZCTA3')
    ZCTA5: str = constants['geographies'].get('zcta5', 'ZCTA5')

    @classmethod
    def ALL(cls) -> List[str]:
        return [cls.STATE, cls.COUNTY, cls.ZCTA3, cls.ZCTA5]

    @classmethod
    def is_valid(cls, geography: str) -> bool:
        return geography in cls.ALL()


@dataclass
class ValidOutcomes ():
    ALCOHOL: str = constants['outcomes']['alcohol']['name']
    OPIOID: str = constants['outcomes']['opioid']['name']
    SOC: str = constants['outcomes']['soc']['name']
    CARDIO: str = constants['outcomes']['cardio']['name']

    @classmethod
    def ALL(cls) -> List[str]:
        return [cls.ALCOHOL, cls.OPIOID, cls.SOC, cls.CARDIO]

    @classmethod
    def is_valid(cls, outcome: str) -> bool:
        return outcome in cls.ALL()

    @classmethod
    def metrics(cls) -> Dict[str, List[Dict[str, str]]]:
        metrics_ = {
            cls.ALCOHOL: constants['outcomes']['alcohol']['metrics'],
            cls.OPIOID: constants['outcomes']['opioid']['metrics'],
            cls.SOC: constants['outcomes']['soc']['metrics'],
            cls.CARDIO: constants['outcomes']['cardio']['metrics'],
        }
        return metrics_
    
    @classmethod
    def to_enum(cls):
        return Enum('OutcomesEnum', {
            'ALCOHOL': cls.ALCOHOL,
            'OPIOID': cls.OPIOID,
            'SOC': cls.SOC,
            'CARDIO': cls.CARDIO
        })

@dataclass
class ValidCharacteristics:
    METADATA: str = constants['charactersitics'].get('metadata', 'metadata')
    GEOMETRY: str = constants['charactersitics'].get('geometry', 'geometry')
    AGE: str = constants['charactersitics'].get('age', 'age')
    SEX: str = constants['charactersitics'].get('sex', 'sex')
    RACE: str = constants['charactersitics'].get('race', 'race/ethnicity')
    RURALITY: str = constants['charactersitics'].get('rurality', 'rurality')
    GENERAL: str = constants['charactersitics'].get('general', 'general')
    INCOME: str = constants['charactersitics'].get('income', 'income')
    AGE_P_SEX: str = constants['charactersitics'].get('age_p_sex', 'age+sex')


@dataclass
class BinLabels:
    LABELS = {
        0: 'Low Outlier',
        1: 'Significantly Lower Than National Average',
        2: 'Much Lower than National Average',
        3: 'Lower than National Average',
        4: 'Slightly Lower than National Average',
        5: 'Slightly Higher than National Average',
        6: 'Higher than National Average',
        7: 'Much Higher than National Average',
        8: 'Significantly Higher than National Average',
        9: 'High Outlier',
    }


@dataclass
class NormalizationRates:
    SOC: float = 10_000


COUNTRY_MID = 'COUNTRY 840'
