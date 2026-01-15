# Bulk Import Fix: Separate Metadata and Genomic Data Handling

## Problem Fixed
Previously, when a lab_id had existing metadata, the entire row would be skipped using `continue`, which also prevented FASTA file import. Users could not import genomic data independently from metadata.

## Solution
Metadata and genomic data are now checked **separately**, and users can make **independent decisions** for each type of data.

## How It Works

### 1. Detection
For each lab_id in the Excel file:
- Checks if metadata exists in the Metadata table
- Checks if genomic data exists in the GenomicData table
- These checks are **completely independent**

### 2. Prompting
If either exists, user sees a targeted prompt showing what actually exists:

```
⚠ Lab ID 'UL001' already has data in database:
   • Metadata exists
   • Genomic data exists

Metadata handling:
   1) Skip (keep existing metadata)
   2) Replace (delete old, import new metadata)
   3) Stop bulk import
   Enter choice (1/2/3): 1

Genomic data handling:
   1) Skip (keep existing genomic data)
   2) Replace (delete old, import new genomic data)
   3) Stop bulk import
   Enter choice (1/2/3): 2
```

### 3. Importing
- **Metadata**: Only imported if:
  - No metadata exists for lab_id, OR
  - Metadata exists and user chose "Replace"
  
- **Genomic Data (FASTA)**: Only imported if:
  - No genomic data exists for lab_id, OR
  - Genomic data exists and user chose "Replace"

**These are completely independent** - you can skip metadata but import FASTA, or vice versa.

## New Classes/Functions

### `MetadataGenomicChoice`
Tracks separate handling decisions:
```python
choice = MetadataGenomicChoice(
    metadata_action=DuplicateHandlingChoice.SKIP,    # What to do with metadata
    genomic_action=DuplicateHandlingChoice.REPLACE   # What to do with genomic
)
```

### `handle_duplicate_lab_id_detailed(lab_id, has_metadata, has_genomic)`
Prompts user separately for metadata and genomic data handling.

### Updated `BulkImportContext.get_duplicate_handling_for_lab_id()`
Now:
- Takes session parameter to check database
- Returns `MetadataGenomicChoice` instead of single choice
- Checks metadata and genomic data separately

## Key Changes in Main Loop

```python
# OLD BEHAVIOR:
if existing > 0:
    choice = context.get_duplicate_handling(lab_id)
    if choice == DuplicateHandlingChoice.SKIP:
        continue  # ← SKIPS ENTIRE ROW INCLUDING FASTA

# NEW BEHAVIOR:
if has_metadata or has_genomic:
    choices = context.get_duplicate_handling_for_lab_id(lab_id, session)
    
    # Handle metadata separately
    if has_metadata and choices.metadata_action == DuplicateHandlingChoice.SKIP:
        # Skip metadata import but continue with FASTA
    
    # Handle genomic separately
    if has_genomic and choices.genomic_action == DuplicateHandlingChoice.SKIP:
        # Skip FASTA import but metadata can still be handled
```

## Example Scenarios

### Scenario 1: Only metadata exists
```
⚠ Lab ID 'UL001' already has data in database:
   • Metadata exists

Metadata handling:
   1) Skip
   2) Replace
   3) Stop
   Enter choice: 1
   
→ Metadata skipped, FASTA imported normally
✓ Result: Genomic data added, metadata unchanged
```

### Scenario 2: Only genomic data exists
```
⚠ Lab ID 'UL002' already has data in database:
   • Genomic data exists

Genomic data handling:
   1) Skip
   2) Replace
   3) Stop
   Enter choice: 1
   
→ Genomic data skipped, metadata imported normally
✓ Result: Metadata updated, genomic data unchanged
```

### Scenario 3: Both exist
```
⚠ Lab ID 'UL003' already has data in database:
   • Metadata exists
   • Genomic data exists

Metadata handling: 2) Replace
Genomic data handling: 1) Skip

✓ Result: Metadata replaced, genomic data kept
```

## Benefits

1. **Flexible**: Users can update metadata while keeping existing genomic data
2. **Efficient**: Don't re-upload large FASTA files if only metadata changed
3. **Clear**: Prompts specify exactly what exists
4. **Independent**: Separate decisions for each data type
5. **Selective**: Can skip one type but import the other
