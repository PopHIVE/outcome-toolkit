from collections import defaultdict
from typing import Any, List


def readable_list(seq: List[Any]) -> str:
    """Return a grammatically correct human readable string (with an Oxford comma)."""
    # Ref: https://stackoverflow.com/a/53981846/
    seq = [str(s) for s in seq]
    if len(seq) < 3:
        return ' and '.join(seq)
    return ', '.join(seq[:-1]) + ', and ' + seq[-1]


def human_format(num: float) -> str:
    """Generate Human Readable Format for Number."""
    # https://stackoverflow.com/questions/579310/formatting-long-numbers-as-strings

    if num is None:
        return 'NA'

    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])


class CountyPicklistLabel:
    def __init__(self, county_namelsad: str, state_usps: str, population: float):
        self.county_namelsad = county_namelsad
        self.state_usps = state_usps
        self.population = population

    def stringify_pop(self) -> str:
        """Generate String version of Population."""

        return f'Pop: {human_format(self.population)}'

    def stringify(self) -> str:
        """Generate String version of County Label."""

        return f'{self.county_namelsad}, {self.state_usps} ({self.stringify_pop()})'


class ZCTA3PicklistLabel:
    def __init__(self, zcta3_mid: str, population: float):
        self.zcta3_mid = zcta3_mid
        self.population = population
        self.counties = defaultdict(set)

    def add_county(self, county_namelsad: str, state_usps: str) -> None:
        self.counties[state_usps].add(county_namelsad)

    def stringify_counties(self, max_num: int = 4) -> str:
        """Generate String version of County Label."""

        return '; '.join(
            [self._stringify_counties(counties, state_usps, max_num) for state_usps, counties in self.counties.items()]
        )

    def _stringify_counties(self, counties: List[str], state_usps: str, max_num: int = 4) -> str:
        """Takes in a list of counties and returns a strigified version of the list of counties."""

        if len(counties) > max_num:
            abbreviation = f'{len(counties) - max_num} more'
            list_to_convert = sorted(counties)[:max_num] + [abbreviation]
            return f'{readable_list(list_to_convert)} ({state_usps})'
        else:
            return f'{readable_list(sorted(counties))} ({state_usps})'

    def stringify_pop(self) -> str:
        """Generate String version of Population."""

        return f'Pop: {human_format(self.population)}'

    def stringify_mid(self) -> str:
        """Generate String version of MID ZCTA3."""

        return f'{self.zcta3_mid}xx'

    def stringify(self, max_num: int = 4) -> str:
        """Generate String version of MID ZCTA3 Intersections."""

        return f'{self.stringify_mid()}: {self.stringify_counties(max_num)} ({self.stringify_pop()})'
