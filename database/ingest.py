from pathlib import Path
from typing import Dict

import duckdb
import pandas as pd

from data.schema import SCHEMAS, run_full_validation

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DATABASE_DIR = BASE_DIR / "database"

DUCKDB_PATH = DATABASE_DIR / "coffee_warehouse.duckdb"

TABLE_FILE_MAP: Dict[str, str] = {
    "products_bom": "products_bom.csv",
    "pricing_tiers": "pricing_tiers.csv",
    "customers": "customers.csv",
    "transactions": "transactions.csv",
    "shipping": "shipping.csv",
    "budget": "budget.csv",
}

class DataWarehouseIngestor:
    def __init__(self) -> None:
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

        self.conn = duckdb.connect(str(DUCKDB_PATH))
        self.conn.execute("PRAGMA threads=4;")
        self.conn.execute("PRAGMA enable_progress_bar=false;")

    #Delete all tables.
    def drop_tables(self):
        tables = self.conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main' AND table_type = 'BASE TABLE';").fetchall()
        for (table_name,) in tables:
            self.conn.execute(f"DROP TABLE IF EXISTS {table_name};")

    #Load csv file.
    def load_csv(self, table_name: str) -> pd.DataFrame:
        if table_name not in TABLE_FILE_MAP:
            raise ValueError(f"Table {table_name} not found in mapping.")

        file_path = RAW_DATA_DIR / TABLE_FILE_MAP[table_name]

        if not file_path.exists():
            raise FileNotFoundError(f"Missing file: {file_path}")

        print(f"Loading {table_name} from {file_path.name}")
        return pd.read_csv(file_path)

    #Validate schema and clean the data.
    def validate_and_clean(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        print(f"Validating {table_name}...")

        df = run_full_validation(df, table_name)

        before = len(df)
        df = df.drop_duplicates()
        after = len(df)

        if before != after:
            print(f"Removed {before - after} duplicate rows from {table_name}")

        return df

    #Save processed data as parquet.
    def save_parquet(self, df: pd.DataFrame, table_name: str) -> Path:
        parquet_path = PROCESSED_DIR / f"{table_name}.parquet"
        df.to_parquet(parquet_path, index=False)
        return parquet_path

    #Create table and indexes's.
    def create_table(self, parquet_path: Path, table_name: str) -> None:
        print(f"Creating table {table_name}...")

        self.conn.execute(f"DROP TABLE IF EXISTS {table_name};")

        self.conn.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM read_parquet('{parquet_path.as_posix()}');
        """)

        # Create index on primary keys
        pk_cols = SCHEMAS[table_name].get("primary_keys", [])
        if pk_cols:
            index_name = f"idx_{table_name}_pk"
            cols = ", ".join(pk_cols)
            try:
                self.conn.execute(
                    f"CREATE INDEX {index_name} ON {table_name} ({cols});"
                )
            except Exception as e:
                print(f"Index creation failed for {table_name}: {e}")

    #Runs full data ingestion pipeline, from csv files to duckdb(sql database).
    def run(self) -> None:
        print("Starting full ingestion pipeline...\n")

        self.drop_tables()
        
        for table_name in TABLE_FILE_MAP.keys():
            df = self.load_csv(table_name)
            df = self.validate_and_clean(df, table_name)
            parquet_path = self.save_parquet(df, table_name)
            self.create_table(parquet_path, table_name)

        print("\nIngestion completed successfully.")

    # Close duckdb connction.
    def close(self) -> None:
        self.conn.close()

if __name__ == "__main__":
    ingestor = DataWarehouseIngestor()
    try:
        ingestor.run()
    finally:
        ingestor.close()