# Multi-Lab FASTA Export - Implementation Reference Guide

## Overview
This guide explains how the multi-lab Uehling ID barrnap export feature works. It's designed as a reference for implementing similar multi-record export patterns in future pipelines.

## Architecture

### 1. Search Module: Auto-Fetch for Multiple Matches
**File:** `modules/search.py`
**Purpose:** Detect when a keyword matches multiple lab_ids and automatically fetch all their FASTA sequences

**Flow:**
```
User Search Input (e.g., "U1513A")
    ↓
Check if it's a direct lab_id query (UL###)
    ├─ YES: Query metadata + genomic data for that one lab_id
    └─ NO: Search all tables for keyword
         ↓
         Find matching metadata rows
         ↓
         Extract unique lab_ids from matches (5 found)
         ↓
         Automatically fetch ALL FASTA sequences for those lab_ids
         ↓
         Combine metadata + FASTA sequences into single result
```

**Key Code Pattern (lines 115-137 in search.py):**
```python
# Detect multiple matched lab_ids
matched_lab_ids = metadata_results['lab_id'].unique()
if len(matched_lab_ids) > 0:
    # Fetch ALL genomic sequences for matched lab_ids
    or_conditions = " OR ".join([f"lab_id = :lab_id_{i}" for i in range(len(matched_lab_ids))])
    query_all_fasta = f"SELECT lab_id, key, value FROM GenomicData WHERE {or_conditions}"
    fasta_data = pd.read_sql(query_all_fasta, con=engine, params=params)
    
    # Combine results
    display_df = pd.concat([display_df, fasta_data], ignore_index=True, sort=False)
```

**Input to export_prompt():** DataFrame with ~178k rows (5 metadata + 178,363 FASTA sequences)

### 2. Export Prompt: Detect Multi-Lab Scenario
**File:** `main.py` - `export_prompt()` function
**Purpose:** Intelligently route to appropriate export function based on data structure

**Detection Logic (lines 115-135 in main.py):**
```python
# Check if we have FASTA data AND multiple lab_ids
has_fasta = False
unique_lab_ids = set()

if 'type' in results.columns and 'lab_id' in results.columns:
    fasta_data = results[results['type'] == 'fasta']
    has_fasta = not fasta_data.empty
    if has_fasta:
        unique_lab_ids = set(fasta_data['lab_id'].unique())

# Route based on conditions
if file_type == 'fasta' and has_fasta and len(unique_lab_ids) > 1:
    # → Use per-lab export function
    export_fasta_per_lab_id(results, folder_path)
else:
    # → Use standard single-file export
    export_fasta(results, file_path)
```

**Key Points:**
- Checks for 'type' column (indicates FASTA vs metadata distinction)
- Checks 'lab_id' column exists in FASTA subset
- Requires BOTH multiple lab_ids AND actual FASTA data
- Asks for folder name instead of file name in multi-lab mode

**CLI Output Differs by Scenario:**
```
Single Lab Query (UL155):
Export as [1] CSV, [2] Excel, [3] TXT, or [4] FASTA (for Barrnap)? (1/2/3/4):
Enter file name (.fasta will be added if not present):

Multi-Lab Query (U1513A → 5 labs):
[Multi-Lab Export Mode] Detected 5 genomes: UL155, UL162, UL163, UL169, UL174
Export as [1] CSV, [2] Excel, [3] TXT, or [4] FASTA per Lab ID (for Barrnap pipeline)? (1/2/3/4):
Enter folder name (will be created inside exported_files/):
```

### 3. Per-Lab Export Function: Separate Files Per Record
**File:** `modules/export_utils.py` - `export_fasta_per_lab_id()` function
**Purpose:** Create individual FASTA files, one per matched lab_id

**Function Signature:**
```python
def export_fasta_per_lab_id(df, folder_path):
    """
    Export FASTA sequences to separate files, one for each unique lab_id.
    - Creates folder structure
    - Names files: {LAB_ID}_barrnap.fasta
    - Prefixes headers: >{LAB_ID}_{SEQUENCE_KEY}
    """
```

**Logic:**
```python
for lab_id in unique_lab_ids:
    lab_data = fasta_data[fasta_data['lab_id'] == lab_id]
    
    file_name = f"{lab_id}_barrnap.fasta"
    file_path = os.path.join(folder_path, file_name)
    
    with open(file_path, 'w') as f:
        for _, row in lab_data.iterrows():
            # Prefix header with lab_id for tracking
            f.write(f">{lab_id}_{row['key']}\n")
            
            # Write sequence in 80-char lines (standard FASTA)
            for i in range(0, len(seq), 80):
                f.write(seq[i:i+80] + "\n")
```

**Output Structure:**
```
exported_files/
└── my_export_folder/
    ├── UL155_barrnap.fasta (12,667 sequences)
    ├── UL162_barrnap.fasta (9,731 sequences)
    ├── UL163_barrnap.fasta (35,440 sequences)
    ├── UL169_barrnap.fasta (86,924 sequences)
    └── UL174_barrnap.fasta (33,601 sequences)
```

## Complete User Workflow

### Step-by-Step

**1. Search Phase**
```
Welcome to the Fungal Research Database
2) Search Data
Enter a keyword to search: U1513A
```

**Output:**
```
Searching for keyword: U1513A
Results for keyword 'U1513A':
lab_id             key    value
 UL155 Project Funding [U1513A]
 UL162 Project Funding [U1513A]
 UL163 Project Funding [U1513A]
 UL169 Project Funding [U1513A]
 UL174 Project Funding [U1513A]

Matched 5 unique lab_ids. Fetching FASTA sequences for bulk export...
Fetched 178363 FASTA sequences from 5 lab_ids
```

**2. Export Prompt**
```
Would you like to export these results? (y/n): y
```

**Multi-Lab Detection Message:**
```
[Multi-Lab Export Mode] Detected 5 genomes: UL155, UL162, UL163, UL169, UL174
```

**3. Format Selection**
```
Export as [1] CSV, [2] Excel, [3] TXT, or [4] FASTA per Lab ID (for Barrnap pipeline)? (1/2/3/4): 4
```

**4. Output Location**
```
→ Creating 5 separate FASTA files (one per Uehling ID)
→ Each file formatted for barrnap phylogenetic pipeline

Export to [d]efault folder (exported_files/) or [c]ustom path? (d/c): d
Enter folder name (will be created inside exported_files/): my_sequences
```

**5. Execution & Confirmation**
```
Exporting FASTA sequences for 5 lab_ids:
  ✓ UL155_barrnap.fasta (12,667 sequences)
  ✓ UL162_barrnap.fasta (9,731 sequences)
  ✓ UL163_barrnap.fasta (35,440 sequences)
  ✓ UL169_barrnap.fasta (86,924 sequences)
  ✓ UL174_barrnap.fasta (33,601 sequences)

Successfully exported 5 files to: exported_files/my_sequences
```

## Implementation Checklist for New Pipelines

When implementing similar multi-record export functionality:

- [ ] **Search Module**: Auto-detect multiple matches and fetch related data
  - [ ] Extract matching record IDs/keys
  - [ ] Fetch ALL associated data for those records
  - [ ] Mark data with type/category (metadata vs sequences vs etc.)
  
- [ ] **Export Layer**: Detect multi-record scenarios
  - [ ] Check for 'type' column (distinguishes data categories)
  - [ ] Check for multiple unique record IDs
  - [ ] Route to appropriate export function
  
- [ ] **Per-Record Export Function**: Create individual files
  - [ ] Iterate through unique record IDs
  - [ ] Create named files: `{RECORD_ID}_{PURPOSE}.{FORMAT}`
  - [ ] Prefix content with record ID for tracking
  - [ ] Follow format standards for downstream tools
  
- [ ] **UI/UX Enhancements**
  - [ ] Show detected records to user
  - [ ] Ask for folder name (not file name) for multi-record exports
  - [ ] Clear messaging about what's being created
  - [ ] Progress reporting for large exports

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Search: "U1513A"                                           │
│     ↓                                                           │
│  2. System: "[Multi-Lab Mode] 5 genomes detected"             │
│     ↓                                                           │
│  3. Choose: Format (FASTA per Lab ID)                         │
│     ↓                                                           │
│  4. Choose: Folder location & name                            │
│     ↓                                                           │
├─────────────────────────────────────────────────────────────────┤
│                    INTERNAL PROCESSING                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  export_prompt(results):                                       │
│    ├─ Check: has_fasta = True                                 │
│    ├─ Check: len(unique_lab_ids) > 1 → True                  │
│    └─ Route: export_fasta_per_lab_id()                        │
│         │                                                      │
│         └─ For each lab_id:                                   │
│            ├─ Filter: results[results['lab_id'] == lab_id]  │
│            ├─ Create: {lab_id}_barrnap.fasta                │
│            └─ Write: Prefixed headers + sequences            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                          OUTPUT FILES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  exported_files/my_sequences/                                  │
│  ├── UL155_barrnap.fasta (12,667 sequences) → barrnap        │
│  ├── UL162_barrnap.fasta (9,731 sequences)  → barrnap        │
│  ├── UL163_barrnap.fasta (35,440 sequences) → barrnap        │
│  ├── UL169_barrnap.fasta (86,924 sequences) → barrnap        │
│  └── UL174_barrnap.fasta (33,601 sequences) → barrnap        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Code References

### Search Detection
- **File**: `modules/search.py`
- **Lines**: 82-160 (keyword search with multi-lab detection)
- **Key Pattern**: Extract lab_ids → fetch all related sequences → combine results

### Export Routing
- **File**: `main.py`
- **Function**: `export_prompt()`
- **Lines**: 115-190
- **Key Pattern**: Check conditions → choose export function → handle user I/O

### Per-Lab Export
- **File**: `modules/export_utils.py`
- **Function**: `export_fasta_per_lab_id()`
- **Lines**: 58-102
- **Key Pattern**: Group by record ID → create individual files → format for downstream

## Testing & Validation

Run tests to verify functionality:
```bash
# Complete workflow simulation
python3 test_cli_workflow.py

# Individual components
python3 test_multi_export_comprehensive.py
python3 test_end_to_end.py
```

## Performance Characteristics

| Operation | Time | Memory | Bottleneck |
|-----------|------|--------|-----------|
| Search 5 genomes | 2-3 sec | ~100MB | Database query |
| Fetch 178k sequences | 1-2 sec | ~500MB | SQL joins |
| Export to 5 files | 30-60 sec | ~500MB | Disk I/O |
| **Total workflow** | **1-2 min** | **~500MB** | Disk write speed |

## Future Enhancements

- Progress bar for large exports
- Streaming export for memory efficiency
- Batch processing for 100+ records
- Export format conversions
- Automatic downstream tool integration

---

**Status:** Production Ready | **Last Updated:** February 13, 2026
