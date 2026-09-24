from typing import List


class InvalidGeography(Exception):
    """Raise this Error if the user provides in Invalid Geography."""

    def __init__(self, geography: str, message: str = None):
        self.geography = geography
        self.message = message if message is not None else 'Invalid Geography Provided.'
        super().__init__(self.message)


class InvalidMID(Exception):
    """Raise this Error if the user provides in MID Geography."""

    def __init__(self, mid: str, message: str = None):
        self.mid = mid
        self.message = message if message is not None else 'Invalid MID Provided.'
        super().__init__(self.message)


class InvalidOutcome(Exception):
    """Raise this Error if the user provides in Outcome Geography."""

    def __init__(self, outcome: str, message: str = None):
        self.outcome = outcome
        self.message = message if message is not None else 'Invalid Outcome Provided.'
        super().__init__(self.message)


class InvalidMetric(Exception):
    """Raise this Error if the user provides in invalid Metric."""

    def __init__(self, metric: str, message: str = None):
        self.metric = metric
        self.message = message if message is not None else 'Invalid Metric Provided.'
        super().__init__(self.message)


class InvalidDatetime(Exception):
    """Raise this Error if the user provides in invalid Metric."""

    def __init__(self, datetime_str: str, message: str = None):
        self.datetime_str = datetime_str
        self.message = message if message is not None else 'Invalid Datetime Provided. Please provide ISO Format.'
        super().__init__(self.message)


class InvalidColumn(Exception):
    def __init__(self, value: str, acceptable: List[str]):
        self.provided_value = value
        self.message = f'Value Provided not in acceptable vals: {acceptable}'
        super().__init__(self.message)
