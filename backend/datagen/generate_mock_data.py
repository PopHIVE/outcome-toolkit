import random
import argparse
import pandas as pd
from typing import Dict, Any

random.seed(1234)
RNG_CACHE = {}


def generate_mock_rng_norml(mu: float, std: float, key: str = None) -> float:
    """
    Generate a Random Normal value with Mu (mu) and STD (std). If the hash key exists then
    return the prior generated random number.

    Parameters
    ----------
    mu: float
    std: float
    key: str

    Returns
    -------
    float

    """
    hash_key = hash(key)
    if hash_key not in RNG_CACHE:
        RNG_CACHE[hash_key] = random.normalvariate(mu=mu, sigma=std)

    return RNG_CACHE[hash_key]


def generate_mock_data(
    srow: Dict[str, Any], prefix: str, rate: float = 1.0, error_std: float = 10.0
) -> Dict[str, Any]:
    """
    Generate Mock data using the formula N(value*rate, error_std).

    Parameters
    ----------
    srow: Dict[str, Any]
    prefix: str
    rate: float

    Returns
    -------
    Dict[str, Any]

    """

    mocked_srow = {}
    for key, value in srow.items():
        if isinstance(value, str):
            mocked_srow[key] = value
        if isinstance(value, int) or isinstance(value, float):
            mocked_value = generate_mock_rng_norml(value * rate, error_std, '-'.join({prefix, key}))
            mocked_srow[key] = int(max(mocked_value, 0))

    return mocked_srow


def generate_row_consistent_mock_data(srow: Dict[str, Any], sum_to: float, denominator: float) -> Dict[str, Any]:
    """
    Generates random data using the formula (value / denominator) * sum_to. This ensures characteristics sum to sum_to.

    Parameters
    ----------
    srow: Dict[str, Any]
    sum_to: float
    denominator: float
    error_std: float

    Returns
    -------
    Dict[str, Any]

    """

    mocked_srow = {}
    for key, value in srow.items():
        if isinstance(value, str):
            mocked_srow[key] = value
        if isinstance(value, int) or isinstance(value, float):
            if denominator > 0:
                mocked_srow[key] = int(max((value * 1.0 / denominator) * sum_to, 0))
            else:
                mocked_srow[key] = 0

    return mocked_srow


def generate_mock_soc_data(input_file: str, output_file: str, rate: float = 1.0, std: float = 1.0):
    """
    Generate a CSV data with Mock SOC Counts.

    Parameters
    ----------
    input_file: str
    geography: str
    output_file: str
    rate: float
    std: float

    Returns
    -------

    """

    demographics = pd.read_csv(input_file, dtype={'GEOID': str}, keep_default_na=False)

    mocked_df = demographics.copy()
    mocked_df['ROW_KEY'] = mocked_df.index.copy()
    mocked_df['DP1_0001C'] = mocked_df[['ROW_KEY', 'DP1_0001C']].apply(
        lambda row: max(generate_mock_rng_norml(row.DP1_0001C * rate, std=std, key=row.ROW_KEY), 0),
        axis=1,
    )
    for col in demographics.columns:
        if col.startswith('DP1') and col != 'DP1_0001C':
            mocked_df[col] = mocked_df['DP1_0001C'] * (mocked_df[col] * 1.0 / demographics['DP1_0001C'])

    mocked_df[demographics.columns].to_csv(output_file, index=None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str, help='Supported Commands are SOC|Opioid')
    parser.add_argument('-i', '--input_file', type=str, help='Input Demographic File')
    parser.add_argument('-o', '--output_file', type=str, help='Output CSV File')
    parser.add_argument(
        '-r',
        '--rate',
        type=float,
        default=25_000.0 / 330_000_000,
        help='Incidence Rate',
    )
    parser.add_argument('-s', '--std', type=float, default=100.0, help='Standard Deviation')
    args = parser.parse_args()

    if args.command == 'SOC':
        generate_mock_soc_data(
            input_file=args.input_file,
            output_file=args.output_file,
            rate=args.rate,
            std=args.std,
        )
    elif args.command == 'OPIOID':
        generate_mock_soc_data(
            input_file=args.input_file,
            output_file=args.output_file,
            rate=args.rate,
            std=args.std,
        )
