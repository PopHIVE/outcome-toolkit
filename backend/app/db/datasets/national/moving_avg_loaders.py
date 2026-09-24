from typing import List, Dict
from sqlalchemy import create_engine, Column, Integer, ForeignKey, Numeric, DateTime, func, and_
from sqlalchemy.engine import Row
from sqlalchemy.sql import text
from sqlalchemy.inspection import inspect
from app.db.database import registry, db_session, engine
from db.datasets.opioid.opioid_tables import Bins
from datetime import datetime


@registry.register('load_moving_avgs', version='1.0')
def load_moving_avgs(target_table: str, metric_col: str, target_col: str, num_months: int) -> List[Row]:
    """ Generate num_months Moving Averages Data based on metric_col and inserts results into target_col.

    Parameters
    ----------
    target_table: str
    metric_col : str
    target_col: str
    num_months: str

    Returns
    -------
    List[Row]
    
    """

    # This is a RAW SQL so no results will be returned
    records = []

    sql_query = text(f"""
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
    """)

    with engine.connect() as conn:
        rs = conn.execute(sql_query)
        conn.commit()

    return records


@registry.register('load_moving_avgs_rank', version='1.0')
def load_moving_avgs_rank(bin_params: List[Dict[str, str]], bin_join_params: List[Dict[str, str]]) -> List[Row]:
    """ Generate the Bins

    Parameters
    ----------
    bin_params: List[Dict[str, str]]
    bin_join_params: List[Dict[str, str]]

    Returns
    -------
    List[Row]
    
    """

    # This is a RAW SQL so no results will be returned
    records = []

    bin_columns = [f'"{column.name}"' for column in inspect(Bins).c if column.name !='measure']

    for params in bin_params:
        create_new_bins_query = text(f"""
            INSERT INTO {Bins.__tablename__} ({', '.join(bin_columns)}, "measure")
            SELECT
            {', '.join(bin_columns)},
            '{params['target']}' measure
            FROM {Bins.__tablename__}
            WHERE ((outcome='{params['outcome']}') AND (measure='{params['measure']}'))
        """)

        with engine.connect() as conn:
            rs = conn.execute(create_new_bins_query)
            conn.commit()

    for params in bin_join_params:
        
        if params['rank_match']:
            intersection_criteria = f"""
                floor(a."{params['source_col']}") = b."rank"
            """
        else:
            intersection_criteria = f"""
                (a."{params['source_col']}" >= b."min") AND
                (a."{params['source_col']}" < b."max")
            """

        update_table_query = text(f"""
            UPDATE {params['target_table']}
            SET
              {params['target_rank_col']}=joined_sbq."rank",
              {params['target_rank_value_col']}=joined_sbq."rankValue"
            FROM (
                SELECT
                  a.mid,
                  a.start_date,
                  a.end_date,
                  b."rank",
                  b."rankValue"
                FROM {params['target_table']} a
                LEFT JOIN bins b ON (
                  (b.measure='{params['source_col']}') AND
                  (a.start_date=b.start_date) AND
                  (a.end_date=b.end_date) AND
                  ({intersection_criteria})
                )
            ) AS joined_sbq
            WHERE (joined_sbq.mid = {params['target_table']}.mid) AND (joined_sbq.start_date = {params['target_table']}.start_date) AND (joined_sbq.end_date = {params['target_table']}.end_date);
        """)

        with engine.connect() as conn:
            rs = conn.execute(update_table_query)
            conn.commit()

    return records


@registry.register('fill_nemsis_rates', version='1.0')
def fill_nemsis_rates(bin_join_params: List[Dict[str, str]]) -> List[Row]:
    """ Fill NEMSIS Rates with rep value joined from bins.

    Parameters
    ----------
    bin_join_params: List[Dict[str, str]]

    Returns
    -------
    List[Row]
    """

    for params in bin_join_params:

        update_table_sql_query = text(f"""
                UPDATE {params['target_table']}
                SET
                  {params['rate_col']}=COALESCE(joined_sbq."rate", joined_sbq."bin_rep_value"),
                  {params['rank_col']}=COALESCE(joined_sbq."rank", joined_sbq."bin_rank"),
                  {params['rank_value_col']}=COALESCE(joined_sbq."rank_value", joined_sbq."bin_rank_value")
                FROM (
                    SELECT
                      a.mid,
                      a.start_date,
                      a.end_date,
                      a.{params['rate_col']} "rate",
                      a.{params['rank_col']} "rank",
                      a.{params['rank_value_col']} "rank_value",
                      b.{params['rep_value']} "bin_rep_value",
                      b."rank" "bin_rank",
                      b."rankValue" "bin_rank_value"
                    FROM {params['target_table']} a
                    LEFT JOIN bins b ON (
                      (b.measure='{params['measure']}') AND
                      (a.start_date=b.start_date) AND
                      (a.end_date=b.end_date) AND
                      (
                        (
                          floor(a."{params['rank_col']}") = b."rank"
                        ) OR 
                        (                
                          (a."{params['rate_col']}" >= b."min") AND
                          (a."{params['rate_col']}" < b."max")
                        )
                      )
                    )
                ) AS joined_sbq
                WHERE (joined_sbq.mid = {params['target_table']}.mid) AND (joined_sbq.start_date = {params['target_table']}.start_date) AND (joined_sbq.end_date = {params['target_table']}.end_date);
        """)

        with engine.connect() as conn:
            rs = conn.execute(update_table_sql_query)
            conn.commit()

    records = []



    return records
