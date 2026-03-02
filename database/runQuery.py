# run_gross_margin_query.py

from database.db_manager import DatabaseManager
import pandas as pd

def main():
    # Initialize the database manager
    db_manager = DatabaseManager()

    # Define the query
    query = """
    SELECT DATE_TRUNC('month', date) AS month, 
       SUM(CASE WHEN service_type IN ('expedited', 'overnight') THEN shipping_cost ELSE 0 END) AS expedited_overnight_spend,
       SUM(shipping_cost) AS total_spend,
       ROUND(100.0 * SUM(CASE WHEN service_type IN ('expedited', 'overnight') THEN shipping_cost ELSE 0 END) / NULLIF(SUM(shipping_cost),0), 2) AS percent_expedited_overnight
FROM shipping
GROUP BY month
ORDER BY month;
    """

    try:
        # Execute the query
        result_df = db_manager.execute_query(query)

        # Display the result
        pd.set_option("display.max_columns", None)
        print(result_df)

    except Exception as e:
        print(f"Error executing query: {e}")

    finally:
        # Close the database connection
        db_manager.close()

if __name__ == "__main__":
    main()