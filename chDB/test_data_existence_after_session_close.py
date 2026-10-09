from chdb import session as chs
from logger import get_logger
from benchmark import benchmark

@benchmark
def test_data_existence_after_session_close():
    
    # create a session
    db = chs.Session("../data/chDB-local-db")

    # create a table
    result = db.query("""
    select * from USERS_BY_LATENCY ORDER BY avg_latency DESC
    LIMIT 10
    """, "Pretty")

    # check if the table exists
    print(result)

    # close the session
    db.close()

def main():
    test_data_existence_after_session_close()

if __name__ == "__main__":
    main()