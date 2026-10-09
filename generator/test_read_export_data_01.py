import chdb
from pathlib import Path


Path("../export_report").mkdir(exist_ok=True)

# remove the file if it exists
Path("../export_report/users_by_latency.parquet").unlink(missing_ok=True)

query = """
INSERT INTO FUNCTION file(
    '../export_report/users_by_latency.parquet',
    Parquet
)
SELECT
    user_id,
    avg(latency_ms) AS avg_latency,
    count() AS requests
FROM file('../data/logs/*.parquet', Parquet)
GROUP BY user_id
ORDER BY avg_latency DESC
LIMIT 100
"""


chdb.query(query)

print("Exported to exports/users_by_latency.parquet\nread it back now...")

query = """
SELECT * FROM file('../export_report/users_by_latency.parquet', Parquet)
"""

result = chdb.query(query, "Pretty")
print(result)