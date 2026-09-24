from sqlalchemy.inspection import inspect
from typing import List, Dict
from db.datasets.opioid.opioid_tables import Bins


def generate_moving_avgs_sql(target_table: str, metric_col: str, target_col: str, num_months: int) -> str:
    """ Generate num_months Moving Averages Data based on metric_col and inserts results into target_col.

    Parameters
    ----------
    target_table: str
    metric_col : str
    target_col: str
    num_months: str

    Returns
    -------
    str
    
    """

    sql_query = f"""
        UPDATE {target_table} 
        SET {target_col} = moving_avg_sbq.moving_average
        FROM (
            SELECT a.mid, a.start_date, a.end_date, a.{metric_col},
                (
                    SELECT avg(b.{metric_col}) AS avg_1
                    FROM {target_table} b
                    WHERE (
                        (a.mid=b.mid) AND 
                        (b.start_date BETWEEN a.start_date - INTERVAL '{num_months} months' AND a.start_date) AND 
                        (b.end_date BETWEEN a.end_date - INTERVAL '{num_months} months' AND a.end_date) AND 
                        (b.{metric_col} IS NOT NULL)
                    )
                ) AS moving_average
            FROM {target_table} a
            WHERE (a.{metric_col} IS NOT NULL)
            ORDER BY (a.mid, a.start_date)
        ) AS moving_avg_sbq
        WHERE (moving_avg_sbq.mid = {target_table}.mid) AND (moving_avg_sbq.start_date = {target_table}.start_date) AND (moving_avg_sbq.end_date = {target_table}.end_date);
    """

    return sql_query

def generate_moving_avgs_columns_sql(outcome: str, measure: str, target: str) -> str:
    """ Generate the Bins
    
    Parameters
    ----------
    outcome: str
    measure : str
    target: str

    Returns
    -------
    str
    """
    
    bins_columns_excluding_measure = [f'"{column.name}"' for column in inspect(Bins).c if column.name !='measure']
    # bins_columns_excluding_measure = [column for column in bins_columns if column != 'measure']

    create_new_bins_query = f"""
        INSERT INTO {Bins.__tablename__} ({', '.join(bins_columns_excluding_measure)}, "measure")
        SELECT
        {', '.join(bins_columns_excluding_measure)},
        '{target}' measure
        FROM {Bins.__tablename__}
        WHERE ((outcome='{outcome}') AND (measure='{measure}'))
    """

    return create_new_bins_query


def generate_moving_avgs_rank_sql(target_table: str, source_col: str, target_rank_col: str, target_rank_value_col: str, rank_match: bool = False) -> str:
    """ Generate the Bins
    
    Parameters
    ----------
    target_table: str
    source_col : str
    target_rank_col: str
    target_rank_value_col: str
    rank_match: bool (False)

    Returns
    -------
    str
    """
    
    if rank_match:
        intersection_criteria = f"""
            floor(a."{source_col}") = b."rank"
        """
    else:
        intersection_criteria = f"""
            (a."{source_col}" >= b."min") AND
            (a."{source_col}" < b."max")
        """

    update_table_query = f"""
        UPDATE {target_table}
        SET
            {target_rank_col}=joined_sbq."rank",
            {target_rank_value_col}=joined_sbq."rankValue"
        FROM (
            SELECT
                a.mid,
                a.start_date,
                a.end_date,
                b."rank",
                b."rankValue"
            FROM {target_table} a
            LEFT JOIN {Bins.__tablename__} b ON (
                (b.measure='{source_col}') AND
                (a.start_date=b.start_date) AND
                (a.end_date=b.end_date) AND
                ({intersection_criteria})
            )
        ) AS joined_sbq
        WHERE (joined_sbq.mid = {target_table}.mid) AND (joined_sbq.start_date = {target_table}.start_date) AND (joined_sbq.end_date = {target_table}.end_date);
    """

    return update_table_query


def generate_fill_nemsis_rates_sql(target_table: str, rate_col: str, rep_value: str, rank_col: str, rank_value_col: str, measure: str) -> str:
    """ Fill NEMSIS Rates with rep value joined from bins.

    Parameters
    ----------
    target_table : str
    rate_col : str
    rep_value : str
    rank_col : str
    rank_value_col : str
    measure: str

    Returns
    -------
    str
    """

    update_table_sql_query = f"""
            UPDATE {target_table}
            SET
                {rate_col}=COALESCE(joined_sbq."rate", joined_sbq."bin_rep_value"),
                {rank_col}=COALESCE(joined_sbq."rank", joined_sbq."bin_rank"),
                {rank_value_col}=COALESCE(joined_sbq."rank_value", joined_sbq."bin_rank_value")
            FROM (
                SELECT
                    a.mid,
                    a.start_date,
                    a.end_date,
                    a.{rate_col} "rate",
                    a.{rank_col} "rank",
                    a.{rank_value_col} "rank_value",
                    b.{rep_value} "bin_rep_value",
                    b."rank" "bin_rank",
                    b."rankValue" "bin_rank_value"
                FROM {target_table} a
                LEFT JOIN {Bins.__tablename__} b ON (
                    (b.measure='{measure}') AND
                    (a.start_date=b.start_date) AND
                    (a.end_date=b.end_date) AND
                    (
                    (
                        floor(a."{rank_col}") = b."rank"
                    ) OR 
                    (                
                        (a."{rate_col}" >= b."min") AND
                        (a."{rate_col}" < b."max")
                    )
                    )
                )
            ) AS joined_sbq
            WHERE (joined_sbq.mid = {target_table}.mid) AND (joined_sbq.start_date = {target_table}.start_date) AND (joined_sbq.end_date = {target_table}.end_date);
    """

    return update_table_sql_query