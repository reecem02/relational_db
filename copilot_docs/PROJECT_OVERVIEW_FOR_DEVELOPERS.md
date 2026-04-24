# Project Overview for Developers & Future Maintainers

**Date:** February 2026  
**Version:** 1.0  
**Audience:** Lab members who want to understand or extend the codebase  

---

## Mission Statement

Create a centralized, user-friendly database tool that allows the Uehling Lab to:
- Store and organize fungal genomic data (DNA sequences)
- Store and organize fungal metadata (collection info, taxonomy, etc.)
- Search across both data types with flexible, case-insensitive queries
- Export data for downstream analysis
- Integrate with external bioinformatics pipelines (e.g., phylogenetics)

---

## Architecture Overview

### Layered Architecture

```
┌─────────────────────────────────┐
│      User Interface Layer       │
│         (CLI Menu)              │
│       main.py, menu functions   │
└──────────────┬──────────────────┘
               │ imports
┌──────────────▼──────────────────┐
│    Business Logic Layer         │
│   Data Import/Search/Export     │
│ modules/data_import.py          │
│ modules/search.py               │
│ modules/data_output.py          │
│ modules/delete.py               │
└──────────────┬──────────────────┘
               │ uses
┌──────────────▼──────────────────┐
│     Configuration Layer         │
│    Schema & Settings            │
│ config/schema.yaml              │
│ config/config.yaml              │
└──────────────┬──────────────────┘
               │ reads
┌──────────────▼──────────────────┐
│      Database Access Layer      │
│    SQLAlchemy + SQLite          │
│  modules/utils.py (Session)     │
└──────────────┬──────────────────┘
               │ accesses
┌──────────────▼──────────────────┐
│     Persistent Storage Layer    │
│        SQLite Database          │
│  database/fungal_db.sqlite      │
│  • Metadata table               │
│  • GenomicData table            │
└─────────────────────────────────┘
```

### Key Principle: Separation of Concerns

Each layer has a specific responsibility:

| Layer | Responsibility | Files |
|-------|---|---|
| **UI** | Display menu, get user input, show results | main.py |
| **Business Logic** | Import data, search, export, delete | modules/* |
| **Configuration** | Define schema, customize behavior | config/*.yaml |
| **Database Access** | Manage connections, execute queries | modules/utils.py |
| **Storage** | Persist data | database/*.sqlite |

**Benefit:** Easy to modify one layer without breaking others

---

## Data Model

### Tables

#### Metadata Table
```sql
CREATE TABLE Metadata (
    id INTEGER PRIMARY KEY,
    lab_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    file_uploaded DATETIME,
    UNIQUE(lab_id, key)
);
```

**Purpose:** Store all metadata fields for each genome

**Example Data:**
```
id | lab_id | key                    | value              | file_uploaded
---|--------|------------------------|--------------------|─────────────
1  | UL001  | Uehling Lab ID        | UL001              | 2024-03-15
2  | UL001  | Sample Location Plate  | Plate A            | 2024-03-15
3  | UL001  | Extracted by          | John Smith         | 2024-03-15
4  | UL002  | Uehling Lab ID        | UL002              | 2024-04-22
```

**Key Design Decision:** Key-value structure allows flexible metadata without schema changes

#### GenomicData Table
```sql
CREATE TABLE GenomicData (
    id INTEGER PRIMARY KEY,
    lab_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    seq_order INTEGER,
    file_uploaded DATETIME,
    UNIQUE(lab_id, key)
);
```

**Purpose:** Store genomic sequences

**Example Data:**
```
id | lab_id | key             | value (first 30 chars) | seq_order
---|--------|-----------------|----------------------|----------
1  | UL001  | scaffold_1      | ATCGATCGATCGATCGAT... | 0
2  | UL001  | scaffold_2      | GCTAGCTAGCTAGCTAG... | 1
3  | UL002  | contig_1        | TTAATTAATTAATTAAAA... | 0
```

**Key Design Decision:** `seq_order` preserves original file order for export

---

## Module Reference

### main.py
**Purpose:** Entry point and user interface

**Key Functions:**
- `main()` - Main menu loop
- `import_data_ui()` - Import menu
- `search_data_ui()` - Search menu
- `delete_data_ui()` - Delete menu

**Flow:**
```
User runs: python3 main.py
    ↓
Displays main menu
    ↓
User selects option (1-6)
    ↓
Calls appropriate UI function
    ↓
Function calls modules/* to do work
    ↓
Display results
    ↓
Loop back to menu
```

---

### modules/data_import.py
**Purpose:** All import functionality

**Key Classes:**
- `BulkImportResult` - Track import results
- `DuplicateAction` - Handle duplicate lab_ids
- `UserChoiceCache` - Cache user decisions

**Key Functions:**
- `import_metadata()` - Excel/CSV metadata
- `import_fasta()` - Individual FASTA file
- `import_bulk_with_fasta()` - Bulk import (Excel + FASTA paths)
- `check_and_add_new_metadata_columns()` - Dynamic schema evolution
- `create_column_mapping()` - Case-insensitive matching
- `resolve_fasta_path()` - Handle path formats
- `import_fasta_batch()` - Batch insert sequences

**Design Patterns:**
- **Batch Processing:** 500 records per transaction (performance)
- **Case-Insensitive Matching:** Users don't need perfect capitalization
- **Dynamic Schema:** New columns added on-the-fly
- **Transaction Management:** All-or-nothing imports (no partial data)

---

### modules/search.py
**Purpose:** Query functionality

**Key Functions:**
- `keyword_search()` - Search across metadata and sequences
- `format_results()` - Display results nicely
- `generate_snippets()` - Show ±40 chars around matches

**Design Patterns:**
- **Case-Insensitive:** Matches regardless of case
- **Partial Matching:** "alpina" matches "Mortierella alpina"
- **Result Formatting:** Readable terminal output
- **Snippet Generation:** Prevents huge sequence display

---

### modules/data_output.py
**Purpose:** Export functionality

**Key Functions:**
- `export_to_text()` - FASTA format
- `export_to_csv()` - Spreadsheet format
- `export_to_xlsx()` - Excel format
- `export_to_phylogeny()` - Phylogenetics tools
- `export_search_results()` - Router function

**Design Pattern:**
- **Strategy Pattern:** Route to appropriate export function based on format

---

### modules/utils.py
**Purpose:** Shared utilities

**Key Functions:**
- `load_schema()` - Read schema.yaml
- `save_schema()` - Write schema.yaml
- Database session management

**Why Separate?**
- All modules depend on these functions
- Centralized database connection
- Single place to change schema loading logic

---

### modules/delete.py
**Purpose:** Data deletion

**Key Functions:**
- `delete_by_lab_id()` - Remove genome and its sequences
- `delete_metadata_only()` - Remove metadata only
- `delete_genomic_only()` - Remove sequences only

**Safety Features:**
- Confirmation prompts
- Cascading deletes (remove both metadata and genomic)
- Transaction-based (atomic deletion)

---

## Configuration System

### schema.yaml
**Purpose:** Define database structure and behavior

**Structure:**
```yaml
metadata_columns:     # List of all possible metadata fields
  - Uehling Lab ID
  - Sample Location
  - Species
  # ... etc ...

genomic_columns:      # Genomic table columns
  - lab_id
  - key
  - value
  - seq_order

bulk_import_config:   # Bulk import settings
  fasta_file_column: "Primary Assembly Filename"
  path_resolution: "excel_dir"
  missing_file_behavior: "skip"
```

**Why YAML?**
- Human-readable
- Easy to edit without coding
- Supports lists and nested structures
- Lab members can customize without touching code

**How It's Used:**
```python
schema = load_schema()
metadata_columns = schema["metadata_columns"]
# Use in validation, column mapping, etc.
```

---

## How to Extend the Project

### Example 1: Add a New Export Format (JSON)

**Step 1:** Add function to `modules/data_output.py`
```python
def export_to_json(search_results):
    # ... implementation ...
    return filepath
```

**Step 2:** Update router in same file
```python
def export_search_results(...):
    if export_format == "json":
        return export_to_json(search_results)
```

**Step 3:** Update menu in `main.py`
```python
# Add to export menu
print("5) JSON format")
```

**No other changes needed!** Layers are independent.

### Example 2: Add a New Metadata Field

**Step 1:** Edit `config/schema.yaml`
```yaml
metadata_columns:
  - Uehling Lab ID
  - Sample Location
  - New Field Name    # ← Add here
```

**Step 2:** That's it!

The system:
- Prompts users to add new columns on import
- Validates against the new schema
- No code changes required

### Example 3: Add a Delete Confirmation Step

**Step 1:** Edit `modules/delete.py`
```python
def delete_by_lab_id(lab_id):
    # Add double confirmation
    confirm = input(f"Delete {lab_id}? (type 'DELETE' to confirm): ")
    if confirm != "DELETE":
        print("Cancelled")
        return
    
    # ... existing deletion code ...
```

**Step 2:** That's it!

---

## Testing Strategy

### Unit Tests
- **Location:** `tests/test_db.py`
- **Purpose:** Test individual functions
- **Run:** `python3 -m pytest tests/`

### Manual Tests
- **Location:** `copilot_docs/MANUAL_TESTING_GUIDE.md`
- **Purpose:** Test complete workflows
- **Run:** Follow guide step-by-step

### Automated Tests
- **Location:** `tools/test_bulk_import.py`
- **Purpose:** Test bulk import scenarios
- **Run:** `python3 tools/test_bulk_import.py`

### Performance Testing
- **Location:** `tools/benchmark_import.py`
- **Purpose:** Measure import speed
- **Run:** `python3 tools/benchmark_import.py`

---

## Common Problems & Solutions

### Problem: New Column Not Appearing in Export
**Root:** Export function doesn't include new column selection  
**Fix:** Edit `export_to_csv()` in `modules/data_output.py`, add column name to the select list

### Problem: Import Fails with Unknown Error
**Root:** Case-sensitivity issue  
**Fix:** Check `check_and_add_new_metadata_columns()` logic in `modules/data_import.py`

### Problem: Search Results Empty
**Root:** Query syntax error  
**Fix:** Review search.py logic, ensure columns exist in schema.yaml

### Problem: Export File Corruption
**Root:** File already exists, overwrite error  
**Fix:** Change filename or delete existing file first

---

## Future Enhancement Ideas

1. **Web Interface**
   - Replace CLI with web dashboard
   - Use Flask or FastAPI framework
   - Place in `frontend/` directory

2. **User Authentication**
   - Track who made changes
   - Edit history/audit log
   - Prepare for multi-user MySQL

3. **Advanced Search**
   - Boolean operators (AND, OR, NOT)
   - Range queries (dates, coordinates)
   - Regular expressions

4. **Data Validation**
   - Validate geographic coordinates
   - Validate dates
   - Check species against taxonomy database

5. **Visualization**
   - Map of sample locations
   - Statistics dashboard
   - Phylogenetic tree viewer integration

6. **API/Integration**
   - REST API for programmatic access
   - Integration with Galaxy workflows
   - Webhooks for automation

---

## Development Workflow

### To Make Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes**
   - Edit files
   - Test locally
   - Review code

3. **Commit changes**
   ```bash
   git add .
   git commit -m "Add description of change"
   ```

4. **Push and create pull request**
   ```bash
   git push origin feature/my-feature
   ```

5. **Get reviewed**
   - Reece or Dr. Uehling reviews code
   - Discuss feedback

6. **Merge to main**
   - Changes go live
   - Other users get updates with `git pull`

---

## Resource Files

**Generated by the system:**
- `database/fungal_db.sqlite` - SQLite database (auto-created)
- `exported_files/*` - User exports
- `example_files/` - Test data

**Configuration (edit these):**
- `config/schema.yaml` - Schema customization
- `config/config.yaml` - Database location

**Documentation:**
- `README.md` - User guide
- `docs/` - Detailed guides
- `copilot_docs/` - Development notes

---

## Support & Questions

- **Code Questions:** Review `modules/` docstrings
- **Architecture Questions:** Review this document
- **Integration Questions:** See `EXTERNAL_TOOL_INTEGRATION_GUIDE.md`
- **Help:** Contact Reece M (Discord)

---

