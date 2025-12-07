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
from enum import Enum

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


# ============================================================================
# BULK IMPORT WITH FASTA FILE LOCATIONS
# ============================================================================

class DuplicateHandlingChoice(Enum):
    """User's choice when a duplicate lab_id is encountered"""
    SKIP = 1        # Keep existing data
    REPLACE = 2     # Delete old, insert new
    STOP = 3        # Cancel entire import


class BulkImportContext:
    """Track state during a bulk import session"""
    def __init__(self):
        self.duplicate_handling_cache = {}  # lab_id → user's choice
    
    def get_duplicate_handling(self, lab_id):
        """
        Returns cached user choice if available.
        Prompts user on first encounter with a duplicate.
        
        This way: If UL001 appears in rows 5, 15, 45
                  Only prompt once at row 5
                  Apply same choice to rows 15 and 45
        """
        if lab_id in self.duplicate_handling_cache:
            return self.duplicate_handling_cache[lab_id]
        
        choice = handle_duplicate_lab_id(lab_id)
        self.duplicate_handling_cache[lab_id] = choice
        return choice


class BulkImportResult:
    """Track and report import results"""
    def __init__(self):
        self.total_rows = 0
        self.metadata_imported = 0
        self.metadata_skipped = []      # (lab_id, reason)
        self.metadata_failed = []       # (lab_id, error_msg)
        self.fasta_imported = 0
        self.fasta_skipped = []         # (lab_id, reason)
        self.fasta_failed = []          # (lab_id, error_msg)
    
    def print_summary(self):
        """Display import results to user"""
        print("\n" + "="*60)
        print("BULK IMPORT RESULTS")
        print("="*60)
        print(f"Total rows processed:     {self.total_rows}")
        print(f"✓ Metadata imported:      {self.metadata_imported}")
        print(f"ⓘ Metadata skipped:       {len(self.metadata_skipped)}")
        if self.metadata_skipped:
            for lab_id, reason in self.metadata_skipped:
                print(f"    {lab_id}: {reason}")
        print(f"✗ Metadata failed:        {len(self.metadata_failed)}")
        if self.metadata_failed:
            for lab_id, error in self.metadata_failed:
                print(f"    {lab_id}: {error}")
        print()
        print(f"✓ FASTA imported:         {self.fasta_imported}")
        print(f"ⓘ FASTA skipped:          {len(self.fasta_skipped)}")
        if self.fasta_skipped:
            for lab_id, reason in self.fasta_skipped:
                print(f"    {lab_id}: {reason}")
        print(f"✗ FASTA failed:           {len(self.fasta_failed)}")
        if self.fasta_failed:
            for lab_id, error in self.fasta_failed:
                print(f"    {lab_id}: {error}")
        print("="*60 + "\n")


def resolve_fasta_path(fasta_path_from_excel, excel_dir):
    """
    Resolve FASTA file path to an absolute path.
    
    Args:
        fasta_path_from_excel: Path string from Excel cell
        excel_dir: Directory containing the Excel file
    
    Returns:
        (absolute_path: str, exists: bool)
    
    Supports:
        - Absolute paths: /nfs6/BPP/data/genome.fasta (used directly)
        - Relative paths: genomes/genome.fasta (resolved from excel_dir)
    """
    # Validate no URLs
    if fasta_path_from_excel.startswith('http://') or fasta_path_from_excel.startswith('https://'):
        raise ValueError("URLs not supported. Use local file paths only.")
    
    # Check for other protocols (but allow Windows C:\ paths)
    if '://' in fasta_path_from_excel:
        # If not Windows drive letter (C:), reject it
        if not (len(fasta_path_from_excel) > 1 and fasta_path_from_excel[1] == ':'):
            raise ValueError("Only local file paths supported.")
    
    # If absolute path, use as-is
    if os.path.isabs(fasta_path_from_excel):
        return fasta_path_from_excel, os.path.exists(fasta_path_from_excel)
    
    # If relative, resolve relative to Excel directory
    resolved = os.path.abspath(os.path.join(excel_dir, fasta_path_from_excel))
    return resolved, os.path.exists(resolved)


def handle_duplicate_lab_id(lab_id):
    """
    Prompt user for duplicate handling decision.
    
    Args:
        lab_id: The duplicate Uehling Lab ID
    
    Returns:
        DuplicateHandlingChoice enum value
    """
    print(f"\n⚠ Duplicate Found: Lab ID '{lab_id}' already exists in database")
    print("   What would you like to do?")
    print("   1) Skip (keep existing data)")
    print("   2) Replace (delete old, import new)")
    print("   3) Stop bulk import")
    
    choice = input("   Enter choice (1/2/3): ").strip()
    
    choice_map = {
        "1": DuplicateHandlingChoice.SKIP,
        "2": DuplicateHandlingChoice.REPLACE,
        "3": DuplicateHandlingChoice.STOP
    }
    return choice_map.get(choice, DuplicateHandlingChoice.SKIP)


def import_metadata_row(session, row, lab_id):
    """
    Import single metadata row.
    
    Args:
        session: SQLAlchemy session
        row: pandas Series from DataFrame row
        lab_id: The Uehling Lab ID for this row
    """
    schema = load_schema()
    metadata_columns = schema["metadata_columns"]
    
    insert_stmt = text("""
        INSERT INTO Metadata (lab_id, key, value)
        VALUES (:lab_id, :key, :value)
    """)
    
    rows_to_insert = []
    for column, value in row.items():
        if column in metadata_columns:
            rows_to_insert.append({
                "lab_id": lab_id,
                "key": column,
                "value": str(value)
            })
    
    if rows_to_insert:
        session.execute(insert_stmt, rows_to_insert)


def import_fasta_batch(session, fasta_file_path, lab_id):
    """
    Import FASTA file for a single lab_id with batching for performance.
    
    Args:
        session: SQLAlchemy session
        fasta_file_path: Absolute path to FASTA file
        lab_id: The Uehling Lab ID for this file
    """
    BATCH_SIZE = 500
    insert_stmt = text("""
        INSERT INTO GenomicData (lab_id, key, value, seq_order)
        VALUES (:lab_id, :key, :value, :seq_order)
    """)
    
    batch = []
    for idx, record in enumerate(SeqIO.parse(fasta_file_path, "fasta")):
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


def import_bulk_with_fasta(excel_file_path):
    """
    Bulk import metadata from Excel AND corresponding FASTA files in one operation.
    
    Expected Excel structure:
    | Uehling Lab ID | ... metadata cols ... | Primary Assembly Filename |
    | UL001          | ...                   | /nfs6/BPP/.../genome1.fasta |
    | UL002          | ...                   | /nfs6/BPP/.../genome2.fasta |
    
    Process:
    1. Validate Excel file and FASTA column exists
    2. Load configuration for path resolution
    3. For each row:
       a. Check for duplicate lab_id
       b. Import metadata
       c. Resolve FASTA file path
       d. Import FASTA if file exists
    4. Report results with counts and any issues
    
    Error Handling:
    - Missing FASTA files: Skip (warn user) - continues with next file
    - Invalid FASTA format: Skip individual file (warn user) - continues import
    - Duplicate lab_ids: Prompt user (skip/replace/stop)
    """
    
    try:
        print("\n" + "="*60)
        print("BULK IMPORT: Excel with FASTA File Locations")
        print("="*60)
        
        # Load configuration
        config = load_schema()
        bulk_config = config.get("bulk_import_config", {})
        fasta_column = bulk_config.get("fasta_file_column", "Primary Assembly Filename")
        
        # Validate file exists
        if not os.path.exists(excel_file_path):
            raise FileNotFoundError(f"Excel file not found: {excel_file_path}")
        
        # Get directory for relative path resolution
        excel_dir = os.path.dirname(os.path.abspath(excel_file_path))
        
        # Load Excel file
        print(f"\nLoading Excel file: {excel_file_path}")
        metadata_df = pd.read_excel(excel_file_path)
        
        # Validate required columns exist
        required_cols = ["Uehling Lab ID", fasta_column]
        missing = [col for col in required_cols if col not in metadata_df.columns]
        if missing:
            raise ValueError(
                f"Missing required columns in Excel: {missing}\n"
                f"Expected 'Uehling Lab ID' and '{fasta_column}'"
            )
        
        # Initialize tracking
        results = BulkImportResult()
        results.total_rows = len(metadata_df)
        context = BulkImportContext()
        
        print(f"Processing {results.total_rows} rows...\n")
        
        # Process each row
        with Session() as session:
            for idx, row in metadata_df.iterrows():
                lab_id = row["Uehling Lab ID"]
                fasta_path_col = row[fasta_column]
                
                print(f"[Row {idx+1}/{results.total_rows}] Lab ID: {lab_id}")
                
                # Check for duplicate
                existing = session.execute(
                    text("SELECT COUNT(*) FROM Metadata WHERE lab_id = :lab_id"),
                    {"lab_id": lab_id}
                ).scalar()
                
                if existing > 0:
                    choice = context.get_duplicate_handling(lab_id)
                    
                    if choice == DuplicateHandlingChoice.SKIP:
                        print(f"  → Skipping (keeping existing data)")
                        results.metadata_skipped.append((lab_id, "Duplicate - user chose SKIP"))
                        continue
                    
                    elif choice == DuplicateHandlingChoice.STOP:
                        print(f"\n⚠ Bulk import stopped by user")
                        session.commit()
                        results.print_summary()
                        return
                    
                    elif choice == DuplicateHandlingChoice.REPLACE:
                        print(f"  → Replacing existing data")
                        session.execute(
                            text("DELETE FROM Metadata WHERE lab_id = :lab_id"),
                            {"lab_id": lab_id}
                        )
                        session.execute(
                            text("DELETE FROM GenomicData WHERE lab_id = :lab_id"),
                            {"lab_id": lab_id}
                        )
                
                # Import metadata
                try:
                    import_metadata_row(session, row, lab_id)
                    results.metadata_imported += 1
                    print(f"  ✓ Metadata imported")
                except Exception as e:
                    print(f"  ✗ Metadata import failed: {e}")
                    results.metadata_failed.append((lab_id, str(e)))
                    continue
                
                # Import FASTA if path is provided
                if pd.isna(fasta_path_col) or str(fasta_path_col).strip() == "":
                    print(f"  ⓘ No FASTA file specified")
                    results.fasta_skipped.append((lab_id, "No file path provided"))
                    continue
                
                # Resolve path
                try:
                    resolved_path, exists = resolve_fasta_path(
                        str(fasta_path_col), 
                        excel_dir
                    )
                except ValueError as e:
                    print(f"  ✗ Invalid path: {e}")
                    results.fasta_failed.append((lab_id, str(e)))
                    continue
                
                if not exists:
                    print(f"  ⚠ FASTA file not found: {resolved_path}")
                    results.fasta_skipped.append((lab_id, f"File not found: {resolved_path}"))
                    continue
                
                # Import FASTA
                try:
                    import_fasta_batch(session, resolved_path, lab_id)
                    results.fasta_imported += 1
                    print(f"  ✓ FASTA imported")
                except Exception as e:
                    print(f"  ✗ FASTA import failed: {e}")
                    results.fasta_failed.append((lab_id, str(e)))
            
            session.commit()
        
        # Print summary
        results.print_summary()
        
    except Exception as e:
        print(f"\n✗ Error during bulk import: {e}")
        import traceback
        traceback.print_exc()

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
