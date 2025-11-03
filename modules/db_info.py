import os
import yaml
from sqlalchemy import text, inspect
from modules.data_output import engine
from modules.utils import load_schema


def get_database_info():
    """
    Display general information about the database tables.
    """
    print("\n-- Database Information --")
    try:
        # Query Metadata table
        # Ensure indexes exist for faster queries on existing DBs
        ensure_indexes()
        metadata_query = text("SELECT COUNT(*) AS count, MAX(`file_uploaded`) AS last_uploaded FROM Metadata")
        with engine.connect() as connection:
            metadata_info = connection.execute(metadata_query).mappings().fetchone()
            metadata_count = metadata_info["count"]
            metadata_last_uploaded = metadata_info["last_uploaded"]

        # Query GenomicData table
        genomic_query = text("SELECT COUNT(*) AS count, MAX(`file_uploaded`) AS last_uploaded FROM GenomicData")
        with engine.connect() as connection:
            genomic_info = connection.execute(genomic_query).mappings().fetchone()
            genomic_count = genomic_info["count"]
            genomic_last_uploaded = genomic_info["last_uploaded"]

        with open("config/config.yaml", "r") as file:
            config = yaml.safe_load(file)
        # Calculate database size
        db_path = os.path.expanduser(config["database"]["path"])  # Update this if using MySQL
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / (1024 ** 3)  # Convert bytes to gigabytes
        else:
            db_size = None

        # Display information
        print("\nMetadata Table:")
        print(f"Number of entries: {metadata_count}")
        print(f"Last uploaded: {metadata_last_uploaded if metadata_last_uploaded else 'N/A'}")

        print("\nGenomicData Table:")
        print(f"Number of entries: {genomic_count}")
        print(f"Last uploaded: {genomic_last_uploaded if genomic_last_uploaded else 'N/A'}")

        if db_size is not None:
            print(f"\nTotal database size: {db_size:.2f} GB")
        else:
            print("\nDatabase size information is not available.")

    except Exception as e:
        print(f"Error retrieving database information: {e}")


def ensure_indexes():
    """
    Create indexes used by the application if they do not already exist.
    This is safe to call on an existing SQLite DB because we use IF NOT EXISTS.
    """
    try:
        idx_stmts = [
            "CREATE INDEX IF NOT EXISTS idx_metadata_lab_id ON Metadata(lab_id)",
            "CREATE INDEX IF NOT EXISTS idx_metadata_key ON Metadata(key)",
            "CREATE INDEX IF NOT EXISTS idx_genomic_lab_id ON GenomicData(lab_id)",
            "CREATE INDEX IF NOT EXISTS idx_genomic_key ON GenomicData(key)"
        ]
        with engine.connect() as connection:
            for s in idx_stmts:
                connection.execute(text(s))
        print("Indexes ensured (idx_metadata_lab_id, idx_metadata_key, idx_genomic_lab_id, idx_genomic_key).")
    except Exception as e:
        print(f"Error ensuring indexes: {e}")

def ensure_file_uploaded_field():
    """
    Ensure the 'file_uploaded' field exists in the Metadata and GenomicData tables.
    """
    schema = load_schema()
    metadata_columns = schema["metadata_columns"]

    print("Checking for 'file_uploaded' field in tables...")
    try:
        inspector = inspect(engine)

        # Check Metadata table
        if "file_uploaded" not in [col["name"] for col in inspector.get_columns("Metadata")]:
            print("Adding 'file_uploaded' field to Metadata table...")
            with engine.connect() as connection:
                connection.execute(text("ALTER TABLE Metadata ADD COLUMN file_uploaded DATETIME DEFAULT CURRENT_TIMESTAMP"))
            print("'file_uploaded' field added to Metadata table.")

        # Check GenomicData table
        if "file_uploaded" not in [col["name"] for col in inspector.get_columns("GenomicData")]:
            print("Adding 'file_uploaded' field to GenomicData table...")
            with engine.connect() as connection:
                connection.execute(text("ALTER TABLE GenomicData ADD COLUMN file_uploaded DATETIME DEFAULT CURRENT_TIMESTAMP"))
            print("'file_uploaded' field added to GenomicData table.")

    except Exception as e:
        print(f"Error ensuring 'file_uploaded' field: {e}")