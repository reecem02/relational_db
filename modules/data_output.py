import pandas as pd
from sqlalchemy import create_engine
import yaml
import os

# Load configuration (from config/config.yaml)
with open("config/config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Load DB Path 
DB_PATH = os.path.expanduser(config["database"]["path"])  # or from config/config.yaml
DB_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DB_URL)

# Function to display data for a specific lab_id
def display_data_by_lab_id(lab_id):
    """Query and display data by Uehling Lab ID."""
    query_metadata = f"SELECT * FROM Metadata WHERE lab_id = '{lab_id}'"
    query_genomic_data = f"SELECT * FROM GenomicData WHERE lab_id = '{lab_id}'"

    try:
        metadata = pd.read_sql(query_metadata, con=engine)
        genomic_data = pd.read_sql(query_genomic_data, con=engine)
        
        print("\nMetadata:")
        print(metadata)
        
        print("\nGenomic Data:")
        print(genomic_data)
        
    except Exception as e:
        print(f"Error querying data: {e}")

# Function to print a dictionary in a vertically aligned format
def print_row_key_value(row_dict, title="Row Data"):
    """
    Prints a dictionary (like a row of metadata) in a vertically aligned format.
    """
    print(f"\n--- {title} ---")
    max_len = max(len(str(key)) for key in row_dict.keys())
    for key, value in row_dict.items():
        print(f"{key:<{max_len}} | {value}")
