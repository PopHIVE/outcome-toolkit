import pandas as pd


def mid_from_geoid(geoid, geography) -> str:
    """ Generate MID from Census GEOID"""
    mid = f"{geography} {geoid}" if not ((geoid is None) or (pd.isna(geoid))) else None
    return mid
    
def zcta5_to_zcta3(name: str) -> str:
    """ Generate ZCTA3 MID from a ZCTA5 MID """
    zip3 = name.replace('ZCTA5', '').strip()[:3]
    return f'ZCTA3 {zip3}'