# Updated Column Handling - Case-Insensitive & Individual Prompts

## What Changed

### 1. Individual Column Prompts (Yes/No for Each)
Previously: All new columns prompted together with a single yes/no

Now: Each new column gets its own prompt

**Example:**
```
⚠ Found 3 new column(s) not in metadata_columns schema:
  Add 'Custom Field 1' to metadata_columns? (yes/no): yes
    ✓ Will add 'Custom Field 1'
  Add 'Custom Field 2' to metadata_columns? (yes/no): no
    ⓘ Will ignore 'Custom Field 2'
  Add 'Custom Field 3' to metadata_columns? (yes/no): yes
    ✓ Will add 'Custom Field 3'

✓ Added 2 new column(s) to schema.yaml
```

### 2. Case-Insensitive Column Matching
Previously: Column names had to match exactly (case-sensitive)

Now: Column names are matched case-insensitively

**Example:**
- Excel has column: `uehling lab id`
- Schema has column: `Uehling Lab ID`
- Result: **MATCH** ✓ Data gets imported under `Uehling Lab ID`

**How It Works:**
1. File column `dna extraction method` matches schema column `DNA Extraction Method` (case-insensitive)
2. Data is imported under the schema column name (`DNA Extraction Method`)
3. Original case from schema is preserved in database

## Features

### New Helper Functions
- `create_column_mapping(metadata_columns)` - Creates lowercase → original mapping
- `get_schema_column_name(file_column, column_mapping)` - Gets schema column matching file column (case-insensitive)

### Updated Functions
- `check_and_add_new_metadata_columns()` - Now prompts for each column individually and returns column mapping
- `import_metadata()` - Uses case-insensitive matching for all columns
- `import_metadata_row()` - Now accepts optional `column_mapping` parameter
- `import_bulk_with_fasta()` - Gets column mapping early and reuses it for all rows

## Import Workflow

```
Excel Import:
1. Load Excel file
2. Check for new columns
3. For each new column:
   - Prompt user individually
   - If yes: Add to schema
   - If no: Ignore it
4. Create case-insensitive column mapping
5. Import metadata:
   - Match each Excel column to schema (case-insensitive)
   - Store data under schema column name
```

## Examples

### Example 1: All columns exist (different case)
```
Excel Columns:           Schema Columns:
- uehling lab id         - Uehling Lab ID
- sample location plate  - Sample Location Plate
- dna extraction method  - DNA Extraction Method

Result: All 3 columns match ✓
No new columns to add
Data imports successfully
```

### Example 2: Some existing, some new
```
Excel Columns:           Schema Columns:        Action:
- Uehling Lab ID ✓       - Uehling Lab ID      Match (exact)
- SAMPLE LOCATION PLATE   - Sample Location Plate  Match (case-insensitive)
- New Custom Field        (not in schema)       Prompt user to add

User says YES to "New Custom Field"
Result: Schema updated, data imported
```

### Example 3: Mix of exact and case-different matches
```
Excel has: "extracted by", "Top ITS Blast Hit", "NEW FIELD"
Schema has: "Extracted by", "Top ITS Blast Hit", "ITS Taxonomy Comments"

Matching:
- "extracted by" → "Extracted by" ✓ (case-insensitive match)
- "Top ITS Blast Hit" → "Top ITS Blast Hit" ✓ (exact match)
- "NEW FIELD" → No match, prompt user
```

## User Input Options
Users can respond to column prompts with:
- `yes` or `y` - Add column to schema
- `no` or `n` - Ignore column during import

## Benefits

1. **Flexibility**: Different case in Excel doesn't break imports
2. **User Control**: Each new column is explicitly approved
3. **Persistence**: Schema updates are saved to config/schema.yaml
4. **Efficiency**: Column mapping created once, reused for all rows
5. **Data Integrity**: Original schema column names preserved in database
