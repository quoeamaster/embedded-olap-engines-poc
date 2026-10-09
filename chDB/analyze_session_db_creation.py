from chdb import session as chs
from directory_tree import DisplayTree
from pathlib import Path
from logger import get_logger
from benchmark import benchmark


Path("../data/chDB-local-db").mkdir(exist_ok=True)

@benchmark
def generate_session():
    # generate a local db file
    return chs.Session("../data/chDB-local-db")

@benchmark
def prepare_db(db: chs.Session):

    # create a table
    db.query("""
    CREATE OR REPLACE TABLE USERS_BY_LATENCY
    (
        user_id UInt64,
        avg_latency Float64,
        requests UInt64
    )
    ENGINE = MergeTree
    ORDER BY user_id
    """)


    # popluate the local table with data from parquet file(s)
    db.query("""
    INSERT INTO USERS_BY_LATENCY
    SELECT
        user_id,
        avg(latency_ms) AS avg_latency,
        count() AS requests
    FROM file('../data/logs/*.parquet', Parquet)
    GROUP BY user_id
    """)

@benchmark
def query_db(db: chs.Session):

    # query the local table 
    # note that there is no `file()` function call here; but a direct table reference is used
    result = db.query("""
    SELECT *
    FROM USERS_BY_LATENCY
    ORDER BY avg_latency DESC
    LIMIT 10
    """, "Pretty")

    return result

@benchmark
def close_db(db: chs.Session):
    db.close()
    return None



def main():
    logger = "analyze_session_db_creation"

    get_logger(logger).info("genearte session...")
    db = generate_session()

    get_logger(logger).info("prepare db...")
    prepare_db(db)

    get_logger(logger).info("query db...")
    query_result = query_db(db)
    get_logger(logger).debug(query_result)

    get_logger(logger).info("close db...")
    close_db(db)

    # list out the local db folder structure
    DisplayTree(
        dirPath='../data/chDB-local-db',
        stringRep=False,
        header=True,
        maxDepth=3,
        showHidden=False,
    )

if __name__ == "__main__":
    main()