# New Metadata Column Detection Feature

## Overview
Added automatic detection and prompting for new metadata columns during Excel imports. When importing metadata files with columns not present in `schema.yaml`, users are now prompted whether to add them to the schema.

## Changes Made

### 1. **modules/utils.py**
Added new function:
- `save_schema(schema)` - Saves schema dictionary to `config/schema.yaml` with proper YAML formatting

### 2. **modules/data_import.py**
Added new function:
- `check_and_add_new_metadata_columns(file_columns)` - Detects new columns and prompts user

**Behavior:**
1. Compares columns in import file against `metadata_columns` in schema
2. If new columns found, displays list to user
3. Prompts user: "Add these columns to metadata_columns? (yes/no)"
4. If yes: Updates schema.yaml with new columns
5. If no: New columns are ignored during import

### 3. **Updated Functions**
- `import_metadata(file_path)` - Now calls `check_and_add_new_metadata_columns()` before importing
- `import_bulk_with_fasta(excel_file_path)` - Now calls `check_and_add_new_metadata_columns()` before processing rows
- `import_metadata_row(session, row, lab_id, metadata_columns=None)` - Now accepts optional `metadata_columns` parameter to avoid reloading schema multiple times during bulk imports

## Import Workflow

### Standard Excel Import (Option 1)
```
1. Load Excel file
2. Detect new columns
3. Prompt user to add them
4. Import metadata (only columns in schema)
```

### Bulk Import with FASTA (Option 3)
```
1. Load Excel file
2. Detect new columns
3. Prompt user to add them (once, before processing)
4. Process each row with updated schema
5. Import metadata and FASTA files
```

## Example Output

```
Loading metadata...

⚠ Found 2 new column(s) not in metadata_columns schema:
  - Custom Field 1
  - Custom Field 2

Add these columns to metadata_columns? (yes/no): yes
✓ Added 2 new column(s) to schema.yaml
Metadata imported successfully.
```

## User Responses Supported

Users can respond to the prompt with:
- **yes** or **y** - Add new columns to schema
- **no** or **n** - Skip new columns, ignore them during import

## Benefits

1. **Flexible Schema** - No code changes needed to accommodate new columns
2. **User Control** - Users decide whether to adopt new columns
3. **Non-Destructive** - New columns are added without removing existing ones
4. **Persistent** - Schema updates are saved to `config/schema.yaml`
5. **Efficient** - Single prompt per import operation, even for bulk imports
