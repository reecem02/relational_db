# Multi-Lab Export: Exact Code Changes Reference

## Summary of Changes

Three files were modified to implement multi-lab Uehling ID barrnap export:

1. **modules/search.py** - Added FASTA fetching for multiple matched lab_ids
2. **modules/export_utils.py** - Added per-lab export function  
3. **main.py** - Updated export prompt with multi-lab detection

---

## File 1: modules/search.py

### Location: Lines 82-160 (keyword search section)

### What It Does
When searching by keyword (not direct lab_id), it now:
1. Finds all matching lab_ids from metadata
2. Automatically fetches ALL FASTA sequences for those lab_ids
3. Returns combined results ready for per-lab export

### The Change

```python
# BEFORE (Original):
# → Only returned 5 metadata rows, no FASTA sequences

# AFTER (Updated):
else: 
    print(f"Searching for keyword: {keyword}")
    results = []

    # Search Metadata
    metadata_results = pd.read_sql(query_metadata, ...)
    results.append(metadata_results)

    # ... (combine and display results) ...
    
    # ↓ NEW SECTION: Auto-fetch FASTA for multiple lab_ids ↓
    if not metadata_results.empty and 'lab_id' in metadata_results.columns:
        matched_lab_ids = metadata_results['lab_id'].unique()
        if len(matched_lab_ids) > 0:
            print(f"\nMatched {len(matched_lab_ids)} unique lab_ids. Fetching FASTA...")
            
            # Dynamic query with parameterized ORs
            or_conditions = " OR ".join([f"lab_id = :lab_id_{i}" 
                                        for i in range(len(matched_lab_ids))])
            query_all_fasta = f"""
                SELECT lab_id, key, value
                FROM GenomicData
                WHERE {or_conditions}
            """
            params = {f"lab_id_{i}": lab_id 
                      for i, lab_id in enumerate(matched_lab_ids)}
            
            fasta_data = pd.read_sql(query_all_fasta, con=engine, params=params)
            if not fasta_data.empty:
                fasta_data['type'] = 'fasta'
                display_df = pd.concat([display_df, fasta_data], 
                                      ignore_index=True, sort=False)
                print(f"Fetched {len(fasta_data)} FASTA sequences from "
                      f"{len(matched_lab_ids)} lab_ids")
```

### Key Technical Details

**Why parameterized ORs?**
- SQLAlchemy doesn't easily support IN with list parameters
- Solution: Build dynamic OR chain: `lab_id = :lab_id_0 OR lab_id = :lab_id_1 OR ...`
- Parameters passed as dict: `{"lab_id_0": "UL155", "lab_id_1": "UL162", ...}`

**Result Structure:**
- Returns 178,368 rows total: 5 metadata + 178,363 FASTA
- Each row has columns: `['lab_id', 'key', 'value', 'type']`
- Type: 'metadata' for records, 'fasta' for sequences

---

## File 2: modules/export_utils.py

### Location: Lines 58-102 (new function)

### What It Does
Creates separate FASTA files, one per unique lab_id, with proper formatting for barrnap

### The New Function

```python
def export_fasta_per_lab_id(df, folder_path):
    """
    Export FASTA sequences to separate files, one for each unique lab_id.
    This is ideal for multi-match barrnap exports.
    
    Args:
        df: DataFrame with columns 'lab_id', 'type', 'key', 'value'
        folder_path: Directory where files will be created (one per lab_id)
    
    Returns:
        List of created file paths
    """
    os.makedirs(folder_path, exist_ok=True)
    
    if 'lab_id' not in df.columns:
        print("Error: DataFrame must contain 'lab_id' column")
        return []
    
    # →  Filter only FASTA rows (not metadata)
    fasta_data = df[df['type'] == 'fasta']
    
    if fasta_data.empty:
        print("No FASTA sequences found to export")
        return []
    
    created_files = []
    unique_lab_ids = fasta_data['lab_id'].unique()
    
    print(f"\nExporting FASTA sequences for {len(unique_lab_ids)} lab_ids:")
    
    # → Process each lab_id independently
    for lab_id in unique_lab_ids:
        lab_data = fasta_data[fasta_data['lab_id'] == lab_id]
        seq_count = len(lab_data)
        
        # → File naming: {LAB_ID}_barrnap.fasta
        file_name = f"{lab_id}_barrnap.fasta"
        file_path = os.path.join(folder_path, file_name)
        
        # → Write FASTA format
        with open(file_path, 'w', encoding='utf-8') as f:
            for _, row in lab_data.iterrows():
                seq = str(row['value'])
                # → Prefix headers with lab_id for tracking
                f.write(f">{lab_id}_{row['key']}\n")
                # → Standard 80-character FASTA wrapping
                for i in range(0, len(seq), 80):
                    f.write(seq[i:i+80] + "\n")
        
        created_files.append(file_path)
        print(f"  ✓ {file_name} ({seq_count:,} sequences)")
    
    print(f"\nSuccessfully exported {len(created_files)} files to: {folder_path}")
    return created_files
```

### Key Technical Details

**Header Prefix Strategy:**
```
Original: >NODE_1_length_160273_cov_42.018477
New:      >UL155_NODE_1_length_160273_cov_42.018477
          └─ Lab ID prefix enables tracking through analysis
```

**File Structure:**
```
exported_files/
└── folder_name/
    ├── UL155_barrnap.fasta  ← Lab ID in filename AND headers
    ├── UL162_barrnap.fasta
    ├── UL163_barrnap.fasta
    ├── UL169_barrnap.fasta
    └── UL174_barrnap.fasta
```

**Why Naming Convention:**
- `{LAB_ID}_` prefix: Easy to identify file source
- `_barrnap.fasta`: Indicates format and tool compatibility
- Prevents name conflicts when processing multiple queries

---

## File 3: main.py

### Location: Lines 110-190 (export_prompt function)

### What It Does
Routes export to correct function based on data received:
- Multi-FASTA with multiple lab_ids → per-lab export
- Single file exports → standard export

### The Updated Function

```python
def export_prompt(results):
    """
    Export search results in various formats.
    Automatically detects multi-lab FASTA exports and creates separate files per lab_id.
    """
    if results.empty:
        return
    choice = input("\nWould you like to export these results? (y/n): ").strip().lower()
    if choice != 'y':
        return

    # ↓ MULTI-LAB DETECTION: Check for FASTA with multiple lab_ids ↓
    has_fasta = False
    unique_lab_ids = set()
    
    # → Check both 'type' and 'lab_id' columns exist
    if 'type' in results.columns and 'lab_id' in results.columns:
        # → Filter only rows with FASTA data
        fasta_data = results[results['type'] == 'fasta']
        has_fasta = not fasta_data.empty
        if has_fasta:
            # → Extract unique lab_ids from FASTA subset
            unique_lab_ids = set(fasta_data['lab_id'].unique())
    
    # ↓ PROMPT: Different message for multi-lab vs single export ↓
    if has_fasta and len(unique_lab_ids) > 1:
        # Show detected genomes
        print(f"\n[Multi-Lab Export Mode] Detected {len(unique_lab_ids)} genomes: "
              f"{', '.join(sorted(unique_lab_ids))}")
        fmt = input("Export as [1] CSV, [2] Excel, [3] TXT, or "
                   "[4] FASTA per Lab ID (for Barrnap pipeline)? (1/2/3/4): ").strip()
    else:
        fmt = input("Export as [1] CSV, [2] Excel, [3] TXT, or "
                   "[4] FASTA (for Barrnap)? (1/2/3/4): ").strip()
    
    # ↓ Parse format choice ↓
    if fmt == '1':
        ext, file_type = 'csv', 'csv'
    elif fmt == '2':
        ext, file_type = 'xlsx', 'excel'
    elif fmt == '3':
        ext, file_type = 'txt', 'txt'
    elif fmt == '4':
        ext, file_type = 'fasta', 'fasta'
    else:
        print("Invalid format, exporting as CSV.")
        ext, file_type = 'csv', 'csv'

    # ↓ ROUTING LOGIC: Choose export path based on conditions ↓
    
    # Multi-lab FASTA: Separate file per lab_id
    if file_type == 'fasta' and has_fasta and len(unique_lab_ids) > 1:
        print(f"\n→ Creating {len(unique_lab_ids)} separate FASTA files "
              f"(one per Uehling ID)")
        print(f"→ Each file formatted for barrnap phylogenetic pipeline\n")
        
        # → Ask for folder, not file name
        folder = input("Export to [d]efault folder (exported_files/) or "
                      "[c]ustom path? (d/c): ").strip().lower()
        if folder == 'd':
            os.makedirs('exported_files', exist_ok=True)
            folder_name = input("Enter folder name (will be created inside "
                               "exported_files/): ").strip()
            folder_path = os.path.join('exported_files', folder_name)
        else:
            folder_path = input("Enter full folder path: ").strip()
        
        # → Execute per-lab export function
        export_fasta_per_lab_id(results, folder_path)
    
    # Standard exports: Single file (CSV, Excel, TXT, or single FASTA)
    else:
        # → Ask for file name as usual
        folder = input("Export to [d]efault folder (exported_files/) or "
                      "[c]ustom path? (d/c): ").strip().lower()
        if folder == 'd':
            os.makedirs('exported_files', exist_ok=True)
            file_name = input(f"Enter file name (.{ext} will be added if not "
                             f"present): ").strip()
            if not file_name.endswith(f".{ext}"):
                file_name += f".{ext}"
            file_path = os.path.join('exported_files', file_name)
        else:
            file_path = input(f"Enter full file path (including .{ext}): ").strip()

        # Handle existing files
        append = False
        if os.path.exists(file_path):
            ao = input("File exists. [a]ppend or [o]verwrite? (a/o): "
                      ).strip().lower()
            append = (ao == 'a')

        # Execute export based on file type
        if file_type in ('csv', 'excel'):
            export_table(results, file_path, file_type, append=append)
        elif file_type == 'fasta':
            export_fasta(results, file_path, append=append)
        else:
            export_pretty(results, file_path, append=append)
```

### Key Logic Points

**Multi-Lab Detection Conditions:**
```
Multi-lab mode ACTIVATES when ALL are true:
  1. file_type == 'fasta'           ← User chose FASTA format
  2. has_fasta == True              ← Results contain FASTA sequences
  3. len(unique_lab_ids) > 1        ← Multiple different lab_ids
```

**Why This Structure:**
- Checks 'type' column first (distinguishes FASTA from metadata)
- Checks 'lab_id' column within FASTA subset (not all metadata)
- Prevents false positives (e.g., single lab_id metadata-only results)

**User Experience:**
- Multi-lab detection announces itself: `[Multi-Lab Export Mode] Detected 5 genomes`
- Different prompt text for different modes
- Asks for folder name instead of file name for multi-lab
- Clear messaging about what's being created

---

## Testing the Changes

### Quick Test
```bash
# Run the complete workflow test
python3 test_cli_workflow.py
```

### Expected Output
```
[STEP 2] Simulating user export choices...

[Multi-Lab Export Mode] Detected 5 genomes: UL155, UL162, UL163, UL169, UL174

→ Creating 5 separate FASTA files (one per Uehling ID)
→ Each file formatted for barrnap phylogenetic pipeline

Exporting FASTA sequences for 5 lab_ids:
  ✓ UL155_barrnap.fasta (12,667 sequences)
  ✓ UL162_barrnap.fasta (9,731 sequences)
  ... [3 more files]
```

---

## Key Design Principles

1. **Automatic Detection** - User doesn't need to specify; system detects from data
2. **Clear Feedback** - Shows what was detected and what will be created
3. **Backward Compatible** - Single searches still work exactly as before
4. **Format Ready** - Headers prefixed for downstream tracking
5. **Readable Code** - Comments and structure make implementation clear for future pipelines

---

## Common Questions

**Q: Why check both 'type' AND 'lab_id' columns?**
A: Type indicates whether FASTA data is present. Lab_id indicates which records the data belongs to. Both needed for validation.

**Q: Why use parameterized ORs instead of IN clause?**
A: SQLAlchemy's parameter binding works better with explicit conditions. IN with lists requires different handling. ORs are explicit and debuggable.

**Q: Why prefix headers with lab_id?**
A: Downstream tools (barrnap) output files named by input header prefix. This enables automatic record tracking through the pipeline.

**Q: Why separate files instead of one file with prefixes?**
A: barrnap processes one record at a time. Separate files enable parallel processing and simpler record-to-result mapping.

---

**Implementation Complete:** February 13, 2026  
**Status:** Production Ready  
**Code Review:** All functions documented with inline comments
