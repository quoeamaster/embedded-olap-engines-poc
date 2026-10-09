from pathlib import Path
import typer
from benchmark import benchmark
from logger import get_logger
import chdb
from chdb import session as chs
import pandas as pd


app = typer.Typer(
    name="nyc-taxi",
    help="Benchmark chDB against NYC Taxi Parquet data.",
    no_args_is_help=True,
)


@app.command(name="direct")
def direct_query(
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
    Run queries directly against Parquet files without a persistent session.
    """
    return run_direct(parquet_path, stress_mode)

@benchmark
def run_direct(parquet_path: Path, stress_mode: bool):
    parquet_path = parquet_path.as_posix()
    get_logger("analyze_huge_parquet").debug('parquet_path: %s', parquet_path)

    num_loops = 10 if stress_mode else 1

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
        FROM file('{parquet_path}', Parquet)
        GROUP BY VendorID, RatecodeID, payment_type
        ORDER BY max_fare_amount DESC
        """

        result = chdb.query(query, "DataFrame")
        get_logger("analyze_huge_parquet").debug(result.head(10))



# [lesson] if not provided name... the func name is the sub-command name
@app.command(name="session")
def session_query(
    parquet_path: Path = typer.Option(
        Path("../data/yellow_tripdata_2025-12.parquet"),
        "--parquet",
        "-p",
        help="Path or glob pattern for NYC Taxi Parquet files.",
    ),
    db_path: Path = typer.Option(
        Path("../data/nyc-taxi-ch-db"),
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
    Run queries using a persistent chDB session.
    """
    # session.run(
    #     parquet_path=parquet_path,
    #     db_path=db_path,
    # )
    return run_session(parquet_path, db_path, stress_mode)

@benchmark
def run_session(parquet_path: Path, db_path: Path, stress_mode: bool):
    get_logger("analyze_huge_parquet").debug('parquet_path: %s', parquet_path)
    get_logger("analyze_huge_parquet").debug('db_path: %s', db_path)

    # create the db
    Path(db_path.as_posix()).mkdir(exist_ok=True)
    # create the session and db
    db = chs.Session(db_path.as_posix())
    # create the table
    db.query("""
    CREATE OR REPLACE TABLE NYC_TAXI_STATS
    (
        VendorID UInt8,
        RatecodeID UInt8,
        payment_type UInt8,
        fare_amount Float64,
        trip_distance Float64
    )
    ENGINE = MergeTree
    ORDER BY (VendorID, RatecodeID, payment_type)
    """)
    # populate the table once (but can run mulitple analytics queries on it later)
    # no pre-aggs done here, just raw data (transformed from parquet to table)
    db.query(f"""
    INSERT INTO NYC_TAXI_STATS
    SELECT
        VendorID,
        RatecodeID,
        payment_type,
        fare_amount,
        trip_distance
    FROM file('{parquet_path}', Parquet)
    """)

    num_loops = 10 if stress_mode else 1

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
        FROM NYC_TAXI_STATS
        GROUP BY VendorID, RatecodeID, payment_type
        ORDER BY max_fare_amount DESC
        """

        result = db.query(query, "DataFrame")
        get_logger("analyze_huge_parquet").debug(result.head(10))

    db.close()

@app.command(name="pandas")
def pandas_query(
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
    Run queries using a runtime pandas dataframe.
    """
    # session.run(
    #     parquet_path=parquet_path,
    #     db_path=db_path,
    # )
    return run_pandas(parquet_path, stress_mode)

@benchmark
def run_pandas(parquet_path: Path, stress_mode: bool):
    get_logger("analyze_huge_parquet").debug('parquet_path: %s', parquet_path)

    num_loops = 10 if stress_mode else 1

    for i in range(num_loops):
        get_logger("analyze_huge_parquet").debug(f'Running loop {i+1} of {num_loops}')

        df = pd.read_parquet(parquet_path.as_posix())
        result = (
            df.groupby(["VendorID", "RatecodeID", "payment_type"], as_index=False)
            .agg(
                max_fare_amount=("fare_amount", "max"),
                min_fare_amount=("fare_amount", "min"),
                avg_fare_amount=("fare_amount", "mean"),
                max_trip_distance=("trip_distance", "max"),
                min_trip_distance=("trip_distance", "min"),
                avg_trip_distance=("trip_distance", "mean"),
                num_trips=("trip_distance", "count"),
            )
            .sort_values(by="max_fare_amount", ascending=False)
        )

        get_logger("analyze_huge_parquet").debug(result.head(100))

if __name__ == "__main__":
    app()