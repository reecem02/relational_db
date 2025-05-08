import pandas as pd
from sqlalchemy import create_engine, inspect
import os
import yaml

# Load DB path
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

DB_PATH = os.path.expanduser(config["database"]["path"])
engine = create_engine(f"sqlite:///{DB_PATH}")

def search_db(keyword):
    try:
        # Get all table names
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        results = []

        # Search each table
        for table in table_names:
            # Get column names for the table
            columns = [col["name"] for col in inspector.get_columns(table)]

            # Build the WHERE clause to search all columns
            where_clause = " OR ".join([f'"{col}" LIKE :keyword' for col in columns])

            # Query the table
            query = f"""
                SELECT *, '{table}' AS source_table
                FROM {table}
                WHERE {where_clause}
                ORDER BY
                    CASE
                        WHEN "{columns[0]}" LIKE :exact_keyword THEN 1
                        ELSE 2
                    END
                LIMIT 5
            """
            print(f"Executing query on table '{table}': {query}")  # Debugging log
            table_results = pd.read_sql(query, con=engine, params={"keyword": f"%{keyword}%", "exact_keyword": keyword})

            if not table_results.empty:
                results.append(table_results)

        # Combine results from all tables
        if not results:
            print(f"No matches found for keyword: {keyword}")
            return pd.DataFrame()  # Return an empty DataFrame if no results are found

        combined_results = pd.concat(results, ignore_index=True)

        # Sort by relevance and extraction_date
        if "extraction_date" in combined_results.columns:
            combined_results.sort_values(by=["source_table", "extraction_date"], inplace=True)

        return combined_results

    except Exception as e:
        print(f"Error querying data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if an error occurs

def print_table_schemas():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    for table in table_names:
        columns = [col["name"] for col in inspector.get_columns(table)]
        print(f"Table '{table}' columns: {columns}")
