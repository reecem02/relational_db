# Multi-Lab ID Barrnap Export Implementation

## Summary
The system now supports exporting FASTA sequences for multiple matched lab_ids when searching by metadata criteria (like "U1513A"). Previously, exports would only work for single lab_id queries or combine all results into one file. Now each matched lab_id gets its own properly formatted barrnap FASTA file.

## What Was Changed

### 1. **Search Module** (`modules/search.py`)
**Change:** Modified keyword search to automatically fetch FASTA sequences for all matched lab_ids

**Details:**
- When searching for a non-lab_id keyword (e.g., "U1513A"), the search function now:
  1. Finds all metadata rows matching the keyword
  2. Extracts unique lab_ids from those matches
  3. Automatically fetches ALL genomic sequences for those lab_ids
  4. Returns results as type 'fasta' so they're available for export

**Code modification:**
- Added logic to detect matched lab_ids in metadata results
- Constructs dynamic SQL query with parameterized ORs to fetch all FASTA sequences
- Combines metadata and FASTA results into single DataFrame

### 2. **Export Utilities** (`modules/export_utils.py`)
**Addition:** New function `export_fasta_per_lab_id()`

**Purpose:** Exports FASTA sequences to separate files, one per unique lab_id

**Features:**
- Takes DataFrame with multi-lab results
- Creates folder structure with naming: `{LAB_ID}_barrnap.fasta`
- Each sequence header is prefixed with lab_id for clarity: `>{LAB_ID}_{SEQUENCE_KEY}`
- Returns list of created file paths
- Provides detailed progress output

### 3. **Main Menu** (`main.py`)
**Changes:**
- Added import of new `export_fasta_per_lab_id` function
- Modified `export_prompt()` to detect multi-lab scenarios
- When exporting FASTA with multiple lab_ids:
  - User is prompted to choose output folder (default or custom)
  - Automatically uses per-lab export mode
  - Creates separate files for each lab_id

## Test Results

### Scenario: Search for "U1513A"
- **Matched Lab IDs:** 5 (UL155, UL162, UL163, UL169, UL174)
- **Total FASTA Sequences:** 178,363
- **Distribution:**
  - UL155: 12,667 sequences (52MB)
  - UL162: 9,731 sequences (50MB)
  - UL163: 35,440 sequences (57MB)
  - UL169: 86,924 sequences (71MB)
  - UL174: 33,601 sequences (52MB)

### Exports Tested
✓ Single-file export: All 178,363 sequences in one file (compatible with existing workflows)
✓ Per-lab export: 5 separate files, one per lab_id
✓ Each file properly formatted for barrnap pipeline
✓ Headers properly prefixed with lab_id for identification

## How to Use

### Interactive Flow
1. **Search**: Enter keyword in search menu (e.g., "U1513A")
   ```
   -- Search Data --
   Enter a keyword to search: U1513A
   ```

2. **Review Results**: System shows matching lab_ids and fetches their sequences
   ```
   Results for keyword 'U1513A':
   lab_id             key    value
   UL155 Project Funding [U1513A]
   UL162 Project Funding [U1513A]
   ...
   
   Matched 5 unique lab_ids. Fetching FASTA sequences for bulk export...
   Fetched 178363 FASTA sequences from 5 lab_ids
   ```

3. **Export**: Choose export format
   ```
   Would you like to export these results? (y/n): y
   Export as [1] CSV, [2] Excel, [3] TXT, or [4] FASTA per Lab ID (for Barrnap)? (1/2/3/4): 4
   ```

4. **Choose Location**:
   ```
   Export to [d]efault folder (exported_files/) or [c]ustom path? (d/c): d
   Enter folder name (will be created inside exported_files/): u1513a_sequences
   ```

5. **Review Output**:
   ```
   Exporting FASTA sequences for 5 lab_ids:
     ✓ UL155_barrnap.fasta (12,667 sequences)
     ✓ UL162_barrnap.fasta (9,731 sequences)
     ✓ UL163_barrnap.fasta (35,440 sequences)
     ✓ UL169_barrnap.fasta (86,924 sequences)
     ✓ UL174_barrnap.fasta (33,601 sequences)
   
   Successfully exported 5 files to: exported_files/u1513a_sequences
   ```

## File Structure
```
exported_files/
└── u1513a_sequences/
    ├── UL155_barrnap.fasta (header: >UL155_NODE_1_length_...)
    ├── UL162_barrnap.fasta (header: >UL162_NODE_1_length_...)
    ├── UL163_barrnap.fasta (header: >UL163_NODE_1_length_...)
    ├── UL169_barrnap.fasta (header: >UL169_NODE_1_length_...)
    └── UL174_barrnap.fasta (header: >UL174_NODE_1_length_...)
```

## Barrnap Compatibility
- ✓ Standard FASTA format with 80-character line wrapping
- ✓ Proper sequence headers with lab_id prefix for tracking
- ✓ Valid DNA sequence characters (ATGCN with support for IUPAC codes)
- ✓ Each file can be independently run through barrnap pipeline

## Backward Compatibility
- ✓ Single lab_id queries (ULXXX format) work unchanged
- ✓ Existing CSV/Excel/TXT exports unaffected
- ✓ Single-file FASTA export still available for all results combined

## Testing
Three comprehensive test suites were created:

1. **test_multi_export.py** - Basic functionality test
2. **test_multi_export_comprehensive.py** - Full validation including:
   - Search functionality
   - FASTA fetching
   - Single-file export
   - Per-lab export
   - Data isolation verification
3. **test_interactive_export_flow.py** - User interaction simulation

All tests passed successfully! ✓

## Error Handling
- Gracefully handles cases with no results
- Validates folder/path permissions before export
- Provides clear error messages if FASTA data is unavailable
- Handles empty FASTA result sets

## Performance Notes
- First search may take a few seconds (fetching ~178k sequences)
- Exports complete in reasonable time (~30-60 seconds depending on disk speed)
- Memory usage scales with number of matched sequences (manageable for typical use)
