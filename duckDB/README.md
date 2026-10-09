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
