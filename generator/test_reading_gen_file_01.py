import chdb

query = """
SELECT
    user_id,
    avg(latency_ms) AS avg_latency,
    count() AS requests
FROM file('../data/logs/*.parquet', Parquet)
GROUP BY user_id
ORDER BY avg_latency DESC
LIMIT 100
"""

result = chdb.query(query, "DataFrame")
print(result)

query = """
SELECT
    user_id, timestamp, endpoint, status
FROM file('../data/logs/*.parquet', Parquet)
LIMIT 10
"""

result = chdb.query(query, "DataFrame")
print(result)

query = """
SELECT
    count() as total_requests,
    endpoint, status
FROM file('../data/logs/*.parquet', Parquet)
GROUP BY endpoint, status
ORDER BY endpoint, total_requests DESC
"""

result = chdb.query(query, "DataFrame")
print(result)

# using other formats
result = chdb.query(query, "Pretty")
print(result)

result = chdb.query(query, "ArrowTable")
print(result)

result = chdb.query(query, "JsonEachRow")
print(result)

result = chdb.query(query, "csv")
print(result)
