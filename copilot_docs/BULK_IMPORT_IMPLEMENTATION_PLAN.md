# Bulk Import Feature - Final Implementation Plan

**Status:** Ready for Development  
**Date:** December 6, 2025  
**Based on User Feedback:** ✅ Approved

---

## Overview

This document details the implementation of the bulk import feature that allows users to upload an Excel file with genomes and their corresponding FASTA file locations, then bulk import both metadata and genomic data in a single workflow.

---

## Part 1: Network Path Resolution

### File Structure Context
```
Program Location:
  /nfs6/BPP/Uehling_Lab/morgaree/relational_db

Data Locations:
  /nfs6/BPP/Uehling_Lab/data                (Primary data storage)
  /nfs4/BPP/Uehling_Lab/                    (Secondary data storage)

Excel files will be: /nfs6/BPP/Uehling_Lab/data/genomes.xlsx
FASTA files may be: /nfs6/BPP/Uehling_Lab/data/genomes/genome1.fasta
                    OR
                    /nfs4/BPP/Uehling_Lab/genomes/genome1.fasta
```

### Path Resolution Strategy

**Updated:** Since data is on the same NFS servers, we'll support three path resolution modes:

#### Mode 1: Absolute Paths (Recommended for your setup)
```
Excel column: "Primary Assembly Filename"
Value: /nfs6/BPP/Uehling_Lab/data/genomes/genome1.fasta

Result: Used directly as-is
```

#### Mode 2: Relative to Excel Directory (Default)
```
Excel file location: /nfs6/BPP/Uehling_Lab/data/genomes_batch1.xlsx
Excel column value: ./genome_files/genome1.fasta

Result: Resolved to /nfs6/BPP/Uehling_Lab/data/genome_files/genome1.fasta
```

#### Mode 3: Relative Path Only (User provides relative portion)
```
Excel column value: genomes/genome1.fasta

With config setting path_resolution: "excel_dir"
Result: Resolved relative to Excel file's directory
```

### Configuration Implementation

**File: `config/schema.yaml`**

```yaml
metadata_columns:
  - Uehling Lab ID
  - Sample Location Plate
  - GC3F Submission Sample ID
  - Alternate ID 1
  - Alternate ID 2
  - Lab Unique ID 3
  - Extracted by
  - Top ITS Blast Hit
  - ITS Top Hit Similarity
  - ITS Taxonomy Comments
  - Top 16S Blast Hit
  - 16S Top Hit Similarity
  - 16S Taxonomy Comments
  - Project Funding
  - Latitude
  - Longitude
  - Location ID
  - DNA Extraction Method
  - Extraction Date

genomic_columns:
  - lab_id
  - key
  - value
  - seq_order

# NEW: Bulk import configuration
bulk_import_config:
  # Column name in Excel that contains FASTA file paths
  fasta_file_column: "Primary Assembly Filename"
  
  # Users can add alternative column names here if needed (optional)
  # This allows flexibility without code changes
  alternative_fasta_columns:
    # - "Assembly Filename"
    # - "Genome File"
    # - "FASTA Path"
  
  # How to resolve relative file paths
  # Options: "excel_dir" (relative to Excel file), "absolute" (only absolute paths)
  # Default: "excel_dir" 
  # For your NFS setup, absolute paths recommended
  path_resolution: "excel_dir"
  
  # What to do if a file is not found
  # Option: "skip" (warn and continue to next file)
  path_resolution: "excel_dir"
  
  # Missing file behavior
  # Option: "skip" - warns user and continues with next file
  missing_file_behavior: "skip"
```

---

## Part 2: Duplicate Handling Workflow

### User Requirements
When a duplicate `lab_id` is detected during bulk import:
1. **Option 1:** Skip this entry (keep old data)
2. **Option 2:** Replace the old duplicate with new information (replace old data)
3. **Option 3:** Stop the entire bulk import

### Implementation Flow

```
User starts bulk import
    ↓
Processing row with lab_id = UL001
    ↓
Check: Does UL001 already exist in Metadata table?
    ├─ NO → Continue to import
    │
    └─ YES → Duplicate found!
        ↓
        Display prompt to user:
        "lab_id 'UL001' already exists in database"
        "What would you like to do?"
        "1) Skip this entry (keep existing data)"
        "2) Replace existing data with new information"
        "3) Stop entire bulk import"
        ↓
        User choice:
        ├─ 1 → Skip UL001, continue to next row
        ├─ 2 → Delete old UL001 data, insert new data
        └─ 3 → Stop import, rollback changes
```

### Implementation Details

```python
class DuplicateHandlingChoice(Enum):
    SKIP = 1          # Keep existing data
    REPLACE = 2       # Delete old, insert new
    STOP = 3          # Cancel entire import

def handle_duplicate_lab_id(lab_id, existing_count):
    """
    Prompt user for duplicate handling decision.
    
    Args:
        lab_id: The duplicate Uehling Lab ID
        existing_count: Number of sequences/metadata entries already in DB
    
    Returns:
        DuplicateHandlingChoice enum value
    """
    print(f"\n⚠ Duplicate Found: Lab ID '{lab_id}' already exists in database")
    print(f"   Existing entries: {existing_count}")
    print("\n   What would you like to do?")
    print("   1) Skip this entry (keep existing data)")
    print("   2) Replace existing data with new information")
    print("   3) Stop entire bulk import")
    
    choice = input("   Enter your choice (1/2/3): ").strip()
    
    if choice == "1":
        return DuplicateHandlingChoice.SKIP
    elif choice == "2":
        return DuplicateHandlingChoice.REPLACE
    elif choice == "3":
        return DuplicateHandlingChoice.STOP
    else:
        print("Invalid choice. Defaulting to SKIP.")
        return DuplicateHandlingChoice.SKIP
```

### Duplicate Check Optimization

To avoid prompting for duplicates multiple times in one import:

```python
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
        
        choice = handle_duplicate_lab_id(lab_id, ...)
        self.duplicate_handling_cache[lab_id] = choice
        return choice
```

---

## Part 3: Error Handling Implementation

### Q1: Missing FASTA Files → Option A (SKIP)
**Behavior:** User is informed a file is missing. That genome skips. Bulk import continues.

```python
def resolve_fasta_path(fasta_path_from_excel, excel_file_dir):
    """
    Attempt to resolve FASTA file path.
    
    Returns: (absolute_path, exists: bool)
    """
    # If path is absolute, use as-is
    if os.path.isabs(fasta_path_from_excel):
        return fasta_path_from_excel, os.path.exists(fasta_path_from_excel)
    
    # If relative, resolve relative to Excel directory
    resolved_path = os.path.join(excel_file_dir, fasta_path_from_excel)
    return os.path.abspath(resolved_path), os.path.exists(resolved_path)


# In import function:
fasta_path_from_excel = row["Primary Assembly Filename"]
resolved_path, exists = resolve_fasta_path(fasta_path_from_excel, excel_dir)

if not exists:
    print(f"⚠ Warning: FASTA file not found for {lab_id}")
    print(f"   Expected: {resolved_path}")
    print(f"   → Skipping genomic import for {lab_id}")
    results.fasta_skipped.append((lab_id, f"File not found: {resolved_path}"))
    continue  # Skip to next row
```

### Q2: Invalid FASTA Format → Option A (SKIP)
**Behavior:** If a FASTA file has parsing errors, that file is skipped and bulk import continues.

```python
try:
    batch = []
    for idx, record in enumerate(SeqIO.parse(resolved_fasta_path, "fasta")):
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
    
    results.fasta_imported.append(lab_id)

except Exception as e:
    print(f"⚠ Error: Invalid FASTA format for {lab_id}")
    print(f"   File: {resolved_fasta_path}")
    print(f"   Error: {e}")
    print(f"   → Skipping genomic import for {lab_id}")
    results.fasta_failed.append((lab_id, f"Invalid FASTA format: {str(e)}"))
    # Continue to next row
```

### Q3: Path Types → Local File Paths Only
**Implementation:** Only support local filesystem paths (no URLs, no special protocols)

```python
def validate_fasta_path(path):
    """
    Validate that path is a local file path (not URL, etc.)
    """
    # Reject URLs
    if path.startswith('http://') or path.startswith('https://'):
        raise ValueError("URLs are not supported. Use local file paths only.")
    
    # Reject other protocols
    if '://' in path:
        raise ValueError("Only local file paths are supported.")
    
    return True
```

---

## Part 4: Menu Structure Implementation

### Current Menu (Before)
```
--Import Data--
Select file type: 1)Excel  2)Fasta
```

### New Menu (After)
```
--Import Data--
1) Standard Excel Import (metadata only)
2) Standard FASTA Import (single genome)
3) Bulk Import (Excel + FASTA file locations)
4) Folder Import (all Excel or FASTA from directory)

Select import type: (1/2/3/4)
```

### Code Changes in `main.py`

```python
def import_data_ui():
    print("\n--Import Data--")
    print("1) Standard Excel Import (metadata only)")
    print("2) Standard FASTA Import (single genome)")
    print("3) Bulk Import (Excel + FASTA file locations)")
    print("4) Folder Import (all Excel or FASTA from directory)")
    
    choice = input("Select import type (1/2/3/4): ").strip()
    
    if choice == "1":
        # Existing Excel import logic
        ...
    elif choice == "2":
        # Existing FASTA import logic
        ...
    elif choice == "3":
        # NEW: Bulk import with FASTA locations
        file_name = input("Enter Excel file name or full path: ").strip()
        if os.path.isabs(file_name) or os.path.exists(file_name):
            file_path = file_name
        else:
            file_path = os.path.join('example_files', file_name)
        
        from modules.data_import import import_bulk_with_fasta
        import_bulk_with_fasta(file_path)
    elif choice == "4":
        # Existing folder import logic
        ...
```

---

## Part 5: Core Function Implementation

### Function: `import_bulk_with_fasta(excel_file_path)`

**Location:** `modules/data_import.py`

```python
def import_bulk_with_fasta(excel_file_path):
    """
    Bulk import metadata from Excel AND corresponding FASTA files in one operation.
    
    Expected Excel structure:
    | Uehling Lab ID | ... metadata cols ... | Primary Assembly Filename |
    | UL001          | ...                   | /nfs6/BPP/.../genome1.fasta |
    | UL002          | ...                   | /nfs6/BPP/.../genome2.fasta |
    
    Process:
    1. Validate Excel file and FASTA column exists
    2. Load configuration for path resolution and duplicate handling
    3. For each row:
       a. Check for duplicate lab_id
       b. Import metadata
       c. Resolve FASTA file path
       d. Import FASTA if file exists
    4. Report results with counts and any issues
    
    Error Handling:
    - Missing FASTA files: Skip (warn user)
    - Invalid FASTA format: Skip (warn user)
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
        path_resolution = bulk_config.get("path_resolution", "excel_dir")
        
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
                if pd.isna(fasta_path_col) or fasta_path_col.strip() == "":
                    print(f"  ⓘ No FASTA file specified")
                    results.fasta_skipped.append((lab_id, "No file path provided"))
                    continue
                
                # Resolve path
                resolved_path, exists = resolve_fasta_path(
                    str(fasta_path_col), 
                    excel_dir
                )
                
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
```

### Supporting Classes and Functions

```python
from enum import Enum

class DuplicateHandlingChoice(Enum):
    SKIP = 1
    REPLACE = 2
    STOP = 3

class BulkImportContext:
    """Track state during bulk import"""
    def __init__(self):
        self.duplicate_handling_cache = {}
    
    def get_duplicate_handling(self, lab_id):
        if lab_id in self.duplicate_handling_cache:
            return self.duplicate_handling_cache[lab_id]
        
        choice = handle_duplicate_lab_id(lab_id)
        self.duplicate_handling_cache[lab_id] = choice
        return choice

class BulkImportResult:
    """Track import results"""
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
    Resolve FASTA file path.
    
    Returns: (absolute_path: str, exists: bool)
    """
    # Validate no URLs
    if fasta_path_from_excel.startswith('http://') or fasta_path_from_excel.startswith('https://'):
        raise ValueError("URLs not supported. Use local file paths only.")
    
    if '://' in fasta_path_from_excel and not (len(fasta_path_from_excel) > 1 and fasta_path_from_excel[1] == ':'):
        # Check for protocol (but allow Windows C:\ paths)
        raise ValueError("Only local file paths supported.")
    
    # If absolute path, use as-is
    if os.path.isabs(fasta_path_from_excel):
        return fasta_path_from_excel, os.path.exists(fasta_path_from_excel)
    
    # If relative, resolve relative to Excel directory
    resolved = os.path.abspath(os.path.join(excel_dir, fasta_path_from_excel))
    return resolved, os.path.exists(resolved)

def handle_duplicate_lab_id(lab_id):
    """Prompt user for duplicate handling decision"""
    print(f"\n⚠ Duplicate Found: Lab ID '{lab_id}' already exists in database")
    print("   What would you like to do?")
    print("   1) Skip (keep existing data)")
    print("   2) Replace (delete old, import new)")
    print("   3) Stop bulk import")
    
    choice = input("   Enter choice (1/2/3): ").strip()
    
    choice_map = {"1": DuplicateHandlingChoice.SKIP, "2": DuplicateHandlingChoice.REPLACE, "3": DuplicateHandlingChoice.STOP}
    return choice_map.get(choice, DuplicateHandlingChoice.SKIP)

def import_metadata_row(session, row, lab_id):
    """Import single metadata row (refactored from import_metadata)"""
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
    """Import FASTA file for a single lab_id with batching"""
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
```

---

## Part 6: Configuration Guide for Users

### How to Add Alternative Column Names

Users can easily add alternative FASTA filename column names by editing `config/schema.yaml`:

```yaml
bulk_import_config:
  fasta_file_column: "Primary Assembly Filename"
  
  # Uncomment/add alternative names if needed
  alternative_fasta_columns:
    - "Assembly Filename"
    - "Genome File"
    - "FASTA Path"
```

**Code behavior:** The system will search for columns in this order:
1. Primary column ("Primary Assembly Filename")
2. Alternative columns (if provided)

This allows users to customize without code changes.

---

## Part 7: Example Excel Template

**File:** `example_files/bulk_import_example.xlsx`

```
| Uehling Lab ID | Sample Location Plate | GC3F Submission Sample ID | Extracted by | Top ITS Blast Hit | Primary Assembly Filename                       |
| UL001          | Plate A               | GC3F-001                  | Lab Tech 1   | Fungal Species 1  | /nfs6/BPP/Uehling_Lab/data/genomes/genome1.fasta |
| UL002          | Plate A               | GC3F-002                  | Lab Tech 1   | Fungal Species 2  | /nfs6/BPP/Uehling_Lab/data/genomes/genome2.fasta |
| UL003          | Plate B               | GC3F-003                  | Lab Tech 2   | Fungal Species 3  | /nfs4/BPP/Uehling_Lab/genomes/genome3.fasta      |
```

---

## Part 8: Testing Scenarios

### Test 1: Basic Successful Import
- Excel with 3 rows
- All FASTA files exist and are valid
- No duplicates
- **Expected:** All metadata and FASTA imported successfully

### Test 2: Missing FASTA File
- Excel with 3 rows
- Row 2's FASTA file doesn't exist
- **Expected:** Rows 1 & 3 imported; Row 2 metadata imported, FASTA skipped with warning

### Test 3: Invalid FASTA Format
- Excel with 3 rows
- Row 3 has corrupted FASTA file
- **Expected:** Rows 1 & 2 successful; Row 3 metadata imported, FASTA failed with error message

### Test 4: Duplicate Lab IDs
- Excel with 2 rows
- UL001 already exists in database
- User chooses "REPLACE"
- **Expected:** UL001 replaced; UL002 imported normally

### Test 5: Duplicate - User Stops
- Excel with 3 rows
- Row 2 detects duplicate
- User chooses "STOP"
- **Expected:** Rows 1 imported; Row 2 stops; Rows 3+ not processed; Results show what completed

---

## Part 9: Implementation Checklist

```
CONFIGURATION:
☐ 1. Update config/schema.yaml with bulk_import_config section
☐ 2. Add comments documenting alternative column names usage

CODE - modules/data_import.py:
☐ 3. Add DuplicateHandlingChoice enum
☐ 4. Add BulkImportContext class
☐ 5. Add BulkImportResult class
☐ 6. Add resolve_fasta_path() function
☐ 7. Add handle_duplicate_lab_id() function
☐ 8. Add import_metadata_row() helper function
☐ 9. Add import_fasta_batch() helper function
☐ 10. Add import_bulk_with_fasta() main function

CODE - main.py:
☐ 11. Update import_data_ui() to add option 3
☐ 12. Add import statement for import_bulk_with_fasta

DOCUMENTATION:
☐ 13. Create bulk_import_example.xlsx in example_files/
☐ 14. Add example FASTA files in example_files/genomes/
☐ 15. Update README.md with bulk import instructions
☐ 16. Document how to add alternative column names

TESTING:
☐ 17. Test successful bulk import (all files exist)
☐ 18. Test missing FASTA file handling
☐ 19. Test invalid FASTA format handling
☐ 20. Test duplicate handling (skip, replace, stop)
☐ 21. Test with absolute paths
☐ 22. Test with relative paths
☐ 23. Test with mixed absolute/relative paths
☐ 24. Test with NFS paths (/nfs6/, /nfs4/)
```

---

## Summary

This implementation plan provides:

✅ **Path Resolution** for NFS server locations (/nfs6, /nfs4)
✅ **Duplicate Handling** with user prompts (skip/replace/stop)
✅ **Error Handling** for missing files and invalid FASTA
✅ **Batch Processing** for performance optimization
✅ **Separate Menu Option** for bulk import
✅ **Extensible Configuration** for alternative column names
✅ **Clear Result Reporting** with success/skip/fail counts
✅ **Local File Paths Only** (no URLs supported)

Ready to proceed with implementation! 🚀
