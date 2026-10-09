"""
Test: Perform analytics on Parquet files directly, without creating or attaching a ClickHouse database.

This script demonstrates querying .parquet log files with analytics on the fly,
using ClickHouse's ability to read from files directly, without requiring DB/table creation.
"""

import chdb
from benchmark import benchmark
from logger import get_logger

@benchmark
def query_chdb():
    query = """
    SELECT
        user_id,
        avg(latency_ms) AS avg_latency,
        count() AS requests
    FROM file('../data/logs/*.parquet', Parquet)
    GROUP BY user_id
    ORDER BY avg_latency DESC
    """

    return query

def main():
    query = query_chdb()

    result = chdb.query(query, "DataFrame")
    get_logger("analyze_without_db_creation").debug(result)

if __name__ == "__main__":

    main()