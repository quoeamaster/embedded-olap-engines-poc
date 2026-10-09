import glob
import pandas as pd

from benchmark import benchmark
from logger import get_logger

@benchmark
def query_pandas():
    files = glob.glob("../data/logs/*.parquet")
    get_logger("pandas_analyse").debug(f"Found {len(files)} files")

    if not files:
        raise FileNotFoundError("No Parquet files found")

    df = pd.concat(
        [pd.read_parquet(f) for f in files],
        ignore_index=True,
    )

    return (
        df.groupby("user_id", as_index=False)
        .agg(
            avg_latency=("latency_ms", "mean"),
            requests=("latency_ms", "count"),
        )
        .sort_values(by="avg_latency", ascending=False)
    )


def main():
    result = query_pandas()
    get_logger("pandas_analyse").debug(result.head(10))


if __name__ == "__main__":
    main()