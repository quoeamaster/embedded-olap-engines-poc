## installation
```bash
brew install duckdb 

OR

# preferred
curl https://install.duckdb.org | bash
```

## testing on python library
```bash
pip install duckdb
```
run the following to check if duckDB works
```bash
python -c "import duckdb; print(duckdb.sql('SELECT 42 AS answer').fetchall())" 
```

## run with UI
```bash
duckdb -ui
```
the duckdb cli and a UI (webapp) would be deployed

## basics on python library usage
```python

# creates a in memory duckDB instance
con = duckdb.connect()
data = con.execute("""
select * from table_a order by some_columns desc
""").fetchall()

print(data)
```

OR with a persistent local db file
```python

# creates a in memory duckDB instance
con = duckdb.connect(DB_PATH)
con.execute("""
create table table_a().....
""")

con.execute("""
insert into table_a select ....""")

# query in dataframes format instead of raw (dedpend on your needs)
dataframes = con.execute("""
select * from table_a order by some_columns desc
""").fetchadf()

print(dataframes)
```
