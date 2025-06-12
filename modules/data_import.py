import pandas as pd
from Bio import SeqIO
from sqlalchemy import create_engine, inspect
import yaml
import os
from modules.data_output import print_row_key_value
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from modules.utils import load_schema


# Load configuration (from config/config.yaml)
with open("config/config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Load DB Path 
DB_PATH = os.path.expanduser(config["database"]["path"])  # or from config/config.yaml
DB_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)

def validate_columns(table_name, df):
    """
    Validate that the columns in the DataFrame match the columns in the database table.
    
    :param table_name: The name of the target table in the database.
    :param df: The DataFrame containing the data to be imported.
    :return: None if columns match, raises ValueError if they don’t.
    """
    # Use SQLAlchemy inspector to fetch table schema
    inspector = inspect(engine)
    try:
        db_columns = [col["name"] for col in inspector.get_columns(table_name)]
    except:
        raise ValueError(f"Table '{table_name}' does not exist in the database. "
                         f"Please create it or let pandas create it before validation.")    
    
    # Get DataFrame columns
    file_columns = list(df.columns)

    # Check for mismatches
    missing_columns = [col for col in db_columns if col not in file_columns]
    extra_columns = [col for col in file_columns if col not in db_columns]

    if missing_columns or extra_columns:
        raise ValueError(
            f"Column mismatch for table '{table_name}':\n"
            f"Missing columns in file: {missing_columns}\n"
            f"Unexpected columns in file: {extra_columns}"
        )

def import_metadata(file_path):
    """
    Import metadata from an Excel file into the Metadata table.
    """
    try:
        print("Loading metadata...")
        schema = load_schema()
        metadata_columns = schema["metadata_columns"]

        metadata = pd.read_excel(file_path)

        # Validate columns
        missing_columns = [col for col in metadata_columns if col not in metadata.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        with Session() as session:
            for _, row in metadata.iterrows():
                lab_id = row["Uehling Lab ID"]

                # Delete existing metadata for the lab_id
                delete_query = text("DELETE FROM Metadata WHERE lab_id = :lab_id")
                session.execute(delete_query, {"lab_id": lab_id})

                # Insert new metadata as key-value pairs
                for column, value in row.items():
                    if column in metadata_columns:
                        insert_query = text("""
                            INSERT INTO Metadata (lab_id, key, value)
                            VALUES (:lab_id, :key, :value)
                        """)
                        session.execute(insert_query, {"lab_id": lab_id, "key": column, "value": str(value)})

            session.commit()
        print("Metadata imported successfully.")

    except Exception as e:
        print(f"Error importing metadata: {e}")


from modules.utils import load_schema

def import_fasta(file_path):
    """
    Import genomic data from a FASTA file into the GenomicData table.
    """
    try:
        print("Loading genomic data from FASTA file...")
        schema = load_schema()
        metadata_columns = schema["metadata_columns"]
        genomic_columns = schema["genomic_columns"]

        lab_id = input(f"Enter the Uehling Lab ID for this FASTA file: ").strip()

        with Session() as session:
            # Validate that lab_id exists in Metadata
            query = text("SELECT * FROM Metadata WHERE lab_id = :lab_id")
            result = session.execute(query, {"lab_id": lab_id}).mappings().fetchone()
            if not result:
                print(f"Lab ID {lab_id} does not exist in Metadata. Creating {lab_id} entry...")
                # Insert a placeholder for each metadata column (empty string as value)
                for column in metadata_columns:
                    insert_query = text("""
                        INSERT INTO Metadata (lab_id, key, value)
                        VALUES (:lab_id, :key, :value)
                    """)
                    session.execute(insert_query, {"lab_id": lab_id, "key": column, "value": ""})
            # Insert each sequence for this lab_id, using the FASTA header as the key
            for idx, record in enumerate(SeqIO.parse(file_path, "fasta")):
                # Build the insert dynamically based on genomic_columns
                values = {
                    "lab_id": lab_id,
                    "key": record.id,
                    "value": str(record.seq),
                    "seq_order": idx
                }
                # Only use columns present in the schema
                insert_cols = [col for col in genomic_columns if col in values]
                insert_query = text(f"""
                    INSERT INTO GenomicData ({', '.join(insert_cols)})
                    VALUES ({', '.join(':' + col for col in insert_cols)})
                """)
                session.execute(insert_query, {col: values[col] for col in insert_cols})

            session.commit()
        print("FASTA data imported successfully.")

    except Exception as e:
        print(f"Error importing FASTA file: {e}")
