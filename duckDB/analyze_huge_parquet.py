from pathlib import Path
import typer
from benchmark import benchmark
from logger import get_logger
import pandas as pd
import duckdb

app = typer.Typer(
    name="nyc-taxi",
    help="Benchmark chDB against NYC Taxi Parquet data.",
    no_args_is_help=True,
)


@app.command(name="memory")
def mem_query(
    parquet_path: Path = typer.Option(
        Path("../data/yellow_tripdata_2025-12.parquet"),
        "--parquet",
        "-p",
        help="Path or glob pattern for NYC Taxi Parquet files.",
    ),
    stress_mode: bool = typer.Option(
        False,
        "--stress-mode",
        "-s",
        help="Run in stress mode (10 times looping), which will run the query multiple times.",
    ),
):
    """
    Run queries using a in-mem duckDB instance.
    """
    return run_memory(parquet_path, stress_mode)

@app.command(name="local")
def local_query(
    parquet_path: Path = typer.Option(
        Path("../data/yellow_tripdata_2025-12.parquet"),
        "--parquet",
        "-p",
        help="Path or glob pattern for NYC Taxi Parquet files.",
    ),
    db_path: Path = typer.Option(
        Path("../data/nyc-taxi-duckdb"),
        "--db-path",
        help="Directory for persistent session data.",
    ),
    stress_mode: bool = typer.Option(
        False,
        "--stress-mode",
        "-s",
        help="Run in stress mode (10 times looping), which will run the query multiple times.",
    ),
):
    """
    Run queries using a local persistent duckDB instance.
    """
    return run_local(parquet_path, db_path, stress_mode)

@benchmark
def run_memory(parquet_path: Path, stress_mode: bool):
    get_logger("analyze_huge_parquet").debug('parquet_path: %s', parquet_path)
    get_logger("analyze_huge_parquet").debug('stress_mode: %s', stress_mode)

    num_loops = 10 if stress_mode else 1
    con = duckdb.connect()

    for i in range(num_loops):
        get_logger("analyze_huge_parquet").debug(f'Running loop {i+1} of {num_loops}')

        query = f"""
        SELECT
            VendorID,
            RatecodeID,
            payment_type,
            max(fare_amount) as max_fare_amount,
            min(fare_amount) as min_fare_amount,
            avg(fare_amount) as avg_fare_amount,
            max(trip_distance) as max_trip_distance,
            min(trip_distance) as min_trip_distance,
            avg(trip_distance) as avg_trip_distance,
            count() as num_trips
        FROM '{parquet_path}'
        GROUP BY VendorID, RatecodeID, payment_type
        ORDER BY max_fare_amount DESC
        """

        dframe = con.execute(query).fetch_df()
        get_logger("analyze_huge_parquet").debug(dframe.head(10))

    con.close()


@benchmark
def run_local(parquet_path: Path, db_path: Path, stress_mode: bool):
    get_logger("analyze_huge_parquet").debug('parquet_path: %s', parquet_path)
    get_logger("analyze_huge_parquet").debug('db_path: %s', db_path)
    get_logger("analyze_huge_parquet").debug('stress_mode: %s', stress_mode)

    # create the db
    Path(db_path.as_posix()).mkdir(exist_ok=True)
    final_db_path = f"{db_path.as_posix()}/local.duckdb"

    num_loops = 10 if stress_mode else 1
    con = duckdb.connect(final_db_path)

    # prepare the local table; create and populate in one go...
    con.execute(f"CREATE or replace TABLE local_nyc_taxi_stats AS SELECT * FROM '{parquet_path}'")

    for i in range(num_loops):
        get_logger("analyze_huge_parquet").debug(f'Running loop {i+1} of {num_loops}')

        query = """
        SELECT
            VendorID,
            RatecodeID,
            payment_type,
            max(fare_amount) as max_fare_amount,
            min(fare_amount) as min_fare_amount,
            avg(fare_amount) as avg_fare_amount,
            max(trip_distance) as max_trip_distance,
            min(trip_distance) as min_trip_distance,
            avg(trip_distance) as avg_trip_distance,
            count() as num_trips
        FROM local_nyc_taxi_stats
        GROUP BY VendorID, RatecodeID, payment_type
        ORDER BY max_fare_amount DESC
        """

        dframe = con.execute(query).fetch_df()
        get_logger("analyze_huge_parquet").debug(dframe.head(10))

    con.close()

    
if __name__ == "__main__":
    app()    