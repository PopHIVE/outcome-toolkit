import pandas as pd
from typing import Union
from app.configs.consts import ValidGeographies


def mid_from_geoid(geoid: str, geography: str) -> Union[str, None]:
    if (geoid is None) or (pd.isna(geoid)):
        return None

    if geography == ValidGeographies.STATE:
        return f'{ValidGeographies.STATE} {geoid}'

    elif geography == ValidGeographies.COUNTY:
        return f'{ValidGeographies.COUNTY} {geoid}'

    elif geography == ValidGeographies.ZCTA3:
        return f'{ValidGeographies.ZCTA3} {geoid}'

    elif geography == ValidGeographies.ZCTA5:
        return f'{ValidGeographies.ZCTA5} {geoid}'

    return None