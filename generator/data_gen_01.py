from pathlib import Path
import pandas as pd
import numpy as np


OUTPUT = Path("../data/logs")
OUTPUT.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)

users = 100_000

for day in range(1, 31):
    rows = 100_000

    df = pd.DataFrame({
        "timestamp": pd.date_range(
            f"2026-09-{day:02d}",
            periods=rows,
            freq="s",
        ),
        "user_id": rng.integers(1, users + 1, rows),
        "endpoint": rng.choice(
            ["/api/search", "/api/login", "/api/orders", "/api/products"],
            rows,
        ),
        "latency_ms": rng.integers(5, 2000, rows),
        "status": rng.choice(
            [200, 200, 200, 201, 400, 404, 500],
            rows,
        ),
    })

    filename = OUTPUT / f"2026-09-{day:02d}.parquet"
    df.to_parquet(filename, index=False)

    print(f"created {filename}")