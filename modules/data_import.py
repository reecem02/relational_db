# Load configuration (from config/config.yaml)
import pandas as pd
from Bio import SeqIO
from sqlalchemy import inspect
import yaml
import os
from modules.data_output import print_row_key_value
from sqlalchemy import text
from datetime import datetime
from modules.utils import load_schema, engine, Session

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

        # We'll do a delete + bulk insert per lab_id to reduce DB roundtrips
        with Session() as session:
            insert_stmt = text("""
                INSERT INTO Metadata (lab_id, key, value)
                VALUES (:lab_id, :key, :value)
            """)

            for _, row in metadata.iterrows():
                lab_id = row["Uehling Lab ID"]
                # Delete existing metadata for the lab_id
                delete_query = text("DELETE FROM Metadata WHERE lab_id = :lab_id")
                session.execute(delete_query, {"lab_id": lab_id})

                # Build parameter list for executemany
                rows_to_insert = []
                for column, value in row.items():
                    if column in metadata_columns:
                        rows_to_insert.append({"lab_id": lab_id, "key": column, "value": str(value)})

                if rows_to_insert:
                    session.execute(insert_stmt, rows_to_insert)

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

        # We'll batch genomic inserts to reduce roundtrips and speed imports
        BATCH_SIZE = 500
        with Session() as session:
            # Validate that lab_id exists in Metadata
            query = text("SELECT * FROM Metadata WHERE lab_id = :lab_id")
            result = session.execute(query, {"lab_id": lab_id}).mappings().fetchone()
            if not result:
                print(f"Lab ID {lab_id} does not exist in Metadata. Creating {lab_id} entry...")
                # Insert a placeholder for each metadata column (empty string as value)
                insert_meta = text("""
                    INSERT INTO Metadata (lab_id, key, value)
                    VALUES (:lab_id, :key, :value)
                """)
                meta_rows = []
                for column in metadata_columns:
                    meta_rows.append({"lab_id": lab_id, "key": column, "value": ""})
                if meta_rows:
                    session.execute(insert_meta, meta_rows)

            # Prepare insert statement for genomic data (we only use a subset of columns)
            insert_stmt = text("""
                INSERT INTO GenomicData (lab_id, key, value, seq_order)
                VALUES (:lab_id, :key, :value, :seq_order)
            """)

            batch = []
            for idx, record in enumerate(SeqIO.parse(file_path, "fasta")):
                batch.append({
                    "lab_id": lab_id,
                    "key": record.id,
                    "value": str(record.seq),
                    "seq_order": idx
                })

                if len(batch) >= BATCH_SIZE:
                    session.execute(insert_stmt, batch)
                    batch = []

            if batch:
                session.execute(insert_stmt, batch)

            session.commit()
        print("FASTA data imported successfully.")

    except Exception as e:
        print(f"Error importing FASTA file: {e}")


def import_metadata_from_folder(folder_path, recursive=False):
    """
    Import all Excel files from a folder into the Metadata table.

    :param folder_path: Path to a folder containing .xlsx/.xls files
    :param recursive: If True, walk subdirectories recursively
    """
    folder = os.path.expanduser(folder_path)
    if not os.path.isdir(folder):
        print(f"Provided path is not a directory: {folder}")
        return

    exts = ('.xlsx', '.xls')
    files = []
    if recursive:
        for root, _, filenames in os.walk(folder):
            for fn in filenames:
                if fn.lower().endswith(exts):
                    files.append(os.path.join(root, fn))
    else:
        for fn in os.listdir(folder):
            if fn.lower().endswith(exts):
                files.append(os.path.join(folder, fn))

    if not files:
        print(f"No Excel files found in {folder}")
        return

    print(f"Found {len(files)} metadata file(s) in {folder}. Beginning import...")
    for f in files:
        try:
            print(f"Importing metadata from {f}...")
            import_metadata(f)
        except Exception as e:
            print(f"Error importing {f}: {e}")


def import_fasta_from_folder(folder_path, recursive=False):
    """
    Import all FASTA files from a folder into the GenomicData table.

    :param folder_path: Path to a folder containing .fasta/.fa/.fna files
    :param recursive: If True, walk subdirectories recursively
    """
    folder = os.path.expanduser(folder_path)
    if not os.path.isdir(folder):
        print(f"Provided path is not a directory: {folder}")
        return

    exts = ('.fasta', '.fa', '.fna')
    files = []
    if recursive:
        for root, _, filenames in os.walk(folder):
            for fn in filenames:
                if fn.lower().endswith(exts):
                    files.append(os.path.join(root, fn))
    else:
        for fn in os.listdir(folder):
            if fn.lower().endswith(exts):
                files.append(os.path.join(folder, fn))

    if not files:
        print(f"No FASTA files found in {folder}")
        return

    print(f"Found {len(files)} FASTA file(s) in {folder}. Beginning import...")
    for f in files:
        try:
            print(f"Importing FASTA from {f}...")
            import_fasta(f)
        except Exception as e:
            print(f"Error importing {f}: {e}")
