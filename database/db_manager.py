
import pandas as pd
from database.db_connection import DuckDBConnection

class DatabaseManager:
    def __init__(self, db_path: str = "database/coffee_warehouse.duckdb", read_only: bool = True, max_rows: int = 100_000, connection=None):
        self.db_path = db_path
        self.read_only = read_only
        self.max_rows = max_rows
        self.connection = connection if connection is not None else DuckDBConnection(db_path, read_only)

    def get_connection(self):
        return self.connection.get_connection()

    def close(self):
        self.connection.close()

    def execute_query(self, query: str) -> pd.DataFrame:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        conn = self.get_connection()
        try:
            df = conn.execute(query).fetchdf()
            if len(df) > self.max_rows:
                df = df.head(self.max_rows)
            return df
        except Exception as e:
            raise RuntimeError(f"Database query failed: {str(e)}") from e

    def test_connection(self) -> bool:
        try:
            self.get_connection().execute("SELECT 1;")
            return True
        except Exception as e:
            return False

    def explain_query(self, query: str) -> pd.DataFrame:
        explain_sql = f"EXPLAIN {query}"
        return self.execute_query(explain_sql)