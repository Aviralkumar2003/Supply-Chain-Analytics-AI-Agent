from typing import Any, Dict
import pandas as pd

SCHEMAS: Dict[str, Dict[str, Any]] = {
    "budget": {
        "required_columns": [
            "month",
            "category",
            "budget_amount",
            "actual_amount",
        ],
        "dtypes": {
            "month": "string",
            "category": "string",
            "budget_amount": "float",
            "actual_amount": "float",
        },
        "primary_keys": ["month", "category"],
    },
    "customers": {
        "required_columns": [
            "customer_id",
            "customer_name",
            "tier",
            "channel",
            "region",
            "account_manager",
        ],
        "dtypes": {
            "customer_id": "string",
            "customer_name": "string",
            "tier": "string",
            "channel": "string",
            "region": "string",
            "account_manager": "string",
        },
        "primary_keys": ["customer_id"],
    },
    "pricing_tiers": {
        "required_columns": [
            "sku_id",
            "tier",
            "unit_price",
        ],
        "dtypes": {
            "sku_id": "string",
            "tier": "string",
            "unit_price": "float",
        },
        "primary_keys": ["sku_id", "tier"],
    },
    "products_bom": {
        "required_columns": [
            "sku_id",
            "sku_name",
            "category",
            "weight_oz",
            "coffee_cost",
            "packaging_cost",
            "labor_cost",
            "total_cogs",
            "msrp",
        ],
        "dtypes": {
            "sku_id": "string",
            "sku_name": "string",
            "category": "string",
            "weight_oz": "float",
            "coffee_cost": "float",
            "packaging_cost": "float",
            "labor_cost": "float",
            "total_cogs": "float",
            "msrp": "float",
        },
        "primary_keys": ["sku_id"],
    },
    "shipping": {
        "required_columns": [
            "shipment_id",
            "transaction_id",
            "date",
            "carrier",
            "service_type",
            "weight_lbs",
            "shipping_cost",
            "origin_zip",
            "destination_zip",
        ],
        "dtypes": {
            "shipment_id": "string",
            "transaction_id": "string",
            "date": "datetime64[ns]",
            "carrier": "string",
            "service_type": "string",
            "weight_lbs": "float",
            "shipping_cost": "float",
            "origin_zip": "string",
            "destination_zip": "string",
        },
        "primary_keys": ["shipment_id"],
    },
    "transactions": {
        "required_columns": [
            "transaction_id",
            "date",
            "customer_id",
            "sku_id",
            "quantity",
            "unit_price_actual",
            "discount_applied",
            "net_revenue",
        ],
        "dtypes": {
            "transaction_id": "string",
            "date": "datetime64[ns]",
            "customer_id": "string",
            "sku_id": "string",
            "quantity": "int",
            "unit_price_actual": "float",
            "discount_applied": "float",
            "net_revenue": "float",
        },
        "primary_keys": ["transaction_id"],
    },
}


def validate_columns(df: pd.DataFrame, table_name: str) -> None:
    expected_cols=SCHEMAS[table_name]["required_columns"]
    missing_cols=[col for col in expected_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing columns in {table_name}: {missing_cols}")

def coerce_dtypes(df: pd.DataFrame, table_name:str)-> pd.DataFrame:
    dtype_map=SCHEMAS[table_name]["dtypes"]
    for col,dtype in dtype_map.items():
        if col not in df.columns:
            continue

        try:
            if dtype == "datetime64[ns]":
                df[col] = pd.to_datetime(df[col], errors="coerce")
            elif dtype == "int":
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int")
            elif dtype == "float":
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            elif dtype == "string":
                df[col] = df[col].astype("string")
        except Exception as e:
            raise ValueError(
                f"[TYPE COERCION ERROR] Failed to convert column '{col}' "
                f"in table '{table_name}' to {dtype}: {str(e)}"
            )

    return df  


def validate_primary_keys(df: pd.DataFrame, table_name: str) -> None:
    pk_cols=SCHEMAS[table_name]["primary_keys"]
    
    for col in pk_cols:
        if df[col].isnull().any():
            raise ValueError(
                f"[DATA QUALITY ERROR] Null values found in primary key column "
                f"'{col}' in table '{table_name}'. This will break joins."
            )


def run_full_validation(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    if table_name not in SCHEMAS:
        raise ValueError(f"Unknown table name: {table_name}")
    validate_columns(df, table_name)
    df = coerce_dtypes(df, table_name)
    validate_primary_keys(df, table_name)
    return df