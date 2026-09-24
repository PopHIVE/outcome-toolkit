import math
import numpy as np
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple, Any, List


COUNTRY_MID = 'COUNTRY 840'

class Replacements:
    JAVASCRIPT_SAFE: Dict[str, Any] = {'-': None, np.nan: None, -1: None}


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

def rankify(x: float) -> int:
    if x is None:
        return -1
    return math.floor(x)
