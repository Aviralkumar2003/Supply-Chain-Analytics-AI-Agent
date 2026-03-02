from pathlib import Path
import duckdb

class DuckDBConnection:
    def __init__(self, db_path: str, read_only: bool = True):
        self.db_path = db_path
        self.read_only = read_only
        self._conn = None
        self._validate_db_path()
        self._connect()

    def _validate_db_path(self):
        db_file = Path(self.db_path)
        if not db_file.exists():
            raise FileNotFoundError(f"DuckDB database not found at '{self.db_path}'. Run the ingestion pipeline before starting the agent.")

    def _connect(self):
        self._conn = duckdb.connect(database=self.db_path, read_only=self.read_only)
        self._conn.execute("PRAGMA threads=4;")
        self._conn.execute("PRAGMA enable_progress_bar=false;")

    def get_connection(self):
        if self._conn is None:
            self._connect()
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
