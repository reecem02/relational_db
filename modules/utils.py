import yaml
import os
from sqlalchemy import create_engine


def get_engine():
    """
    Load the database path from config.yaml and return a SQLAlchemy engine.
    """
    with open("config/config.yaml", "r") as file:
        config = yaml.safe_load(file)

    db_path = os.path.expanduser(config["database"]["path"])
    return create_engine(f"sqlite:///{db_path}")

def print_row_key_value(row_dict, title="Row Data"):
    """
    Prints a dictionary (like a row of metadata) in a vertically aligned format.
    """
    print(f"\n--- {title} ---")
    max_len = max(len(str(key)) for key in row_dict.keys())
    for key, value in row_dict.items():
        print(f"{key:<{max_len}} | {value}")

def load_schema():
    ## Load the schema definitions from schema.yaml
    with open("config/schema.yaml", "r") as file:
        schema = yaml.safe_load(file)
    return schema