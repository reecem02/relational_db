# External Tool Integration Guide
## How to Add Export Formats for External Tools

**Purpose:** This guide shows how to add new export formats (like FASTA for phylogenetic tools such as Sourmash) to the relational database, making it easy to prepare data for any external tool or analysis pipeline.

**What You'll Learn:**
- How the FASTA export was designed for phylogenetic tools
- Pattern for adding any new export format
- How to update the user menu
- Template for your own tool integrations

---

## Quick Overview: What We Did

### The Problem
Phylogenetic tools like Sourmash need pure FASTA format:
```
>sequence_header
ACGTACGTACGT...
ACGTACGTACGT...
```

But the existing export options (CSV, Excel, TXT) mix metadata with sequences or truncate sequences.

### The Solution
Added a new `export_fasta()` function that exports **only sequences** in proper FASTA format.

---

## Step-by-Step: How to Add an Export Format

### Step 1: Identify Your Tool's Requirements

**For Sourmash (phylogenetic analysis):**
- Input: FASTA file with genomic sequences
- Format: Standard FASTA (header + sequence in 80-char lines)
- Metadata: Not needed (tool doesn't use it)

**For any new tool:**
- What file format does it need? (FASTA, GFF, JSON, CSV, etc.)
- What data should be included/excluded?
- Any special formatting requirements?

---

### Step 2: Create the Export Function

**File:** `modules/export_utils.py`

Add a new function following this template:

```python
def export_[TOOLNAME](df, file_path, append=False):
    """
    Export data in format required by [TOOLNAME].
    
    Args:
        df: DataFrame with columns ['type', 'key', 'value']
        file_path: Output file path
        append: Whether to append to existing file
    """
    mode = 'a' if append and os.path.exists(file_path) else 'w'
    with open(file_path, mode, encoding='utf-8') as f:
        # Filter to get only the data type you need
        data = df[df['type'] == 'fasta']  # or 'metadata' or whatever
        
        if not data.empty:
            for _, row in data.iterrows():
                # Format data according to tool requirements
                # Write to file
                f.write(f"formatted_output\n")
    
    print(f"Exported [TOOLNAME] format to {file_path}")
```

### Real Example: FASTA Export

```python
def export_fasta(df, file_path, append=False):
    """
    Export FASTA sequences only (pure FASTA format for phylogenetic tools).
    Strips out metadata and exports only sequences with headers.
    
    Args:
        df: DataFrame from search results
        file_path: Output file path
        append: Whether to append to existing file
    """
    mode = 'a' if append and os.path.exists(file_path) else 'w'
    with open(file_path, mode, encoding='utf-8') as f:
        fasta = df[df['type'] == 'fasta']
        if not fasta.empty:
            for _, row in fasta.iterrows():
                seq = str(row['value'])
                # Write header
                f.write(f">{row['key']}\n")
                # Write sequence in 80-character lines (standard FASTA)
                for i in range(0, len(seq), 80):
                    f.write(seq[i:i+80] + "\n")
    
    print(f"Exported FASTA sequences to {file_path}")
```

**Key points:**
- Filter the DataFrame to get only needed data types
- Format according to tool specifications
- Write to file with proper encoding
- Print confirmation message

---

### Step 3: Import the New Function

**File:** `main.py` (top of file)

Find the import line for export functions and add yours:

```python
# BEFORE:
from modules.export_utils import export_table, export_pretty

# AFTER:
from modules.export_utils import export_table, export_pretty, export_fasta
```

**Full example:**
```python
from modules.export_utils import export_table, export_pretty, export_fasta, export_gff, export_json
```

---

### Step 4: Update the Export Menu

**File:** `main.py` (in `export_prompt()` function)

Find this section:
```python
fmt = input("Export as [1] CSV, [2] Excel, or [3] TXT? (1/2/3): ").strip()
if fmt == '1':
    ext, file_type = 'csv', 'csv'
elif fmt == '2':
    ext, file_type = 'xlsx', 'excel'
elif fmt == '3':
    ext, file_type = 'txt', 'txt'
```

**Add your format:**
```python
    fmt = input("Export as [1] CSV, [2] Excel, [3] TXT, or [4] FASTA (for phylogenetic tools)? (1/2/3/4): ").strip()
if fmt == '1':
    ext, file_type = 'csv', 'csv'
elif fmt == '2':
    ext, file_type = 'xlsx', 'excel'
elif fmt == '3':
    ext, file_type = 'txt', 'txt'
elif fmt == '4':
    ext, file_type = 'fasta', 'fasta'
```

**Pattern for multiple tools:**
```python
    fmt = input("Export as [1] CSV, [2] Excel, [3] TXT, [4] FASTA (Phylogenetic tools), [5] Custom format? (1/2/3/4/5): ").strip()
if fmt == '1':
    ext, file_type = 'csv', 'csv'
elif fmt == '2':
    ext, file_type = 'xlsx', 'excel'
elif fmt == '3':
    ext, file_type = 'txt', 'txt'
elif fmt == '4':
    ext, file_type = 'fasta', 'fasta'
elif fmt == '5':
    ext, file_type = 'gff', 'gff'
```

---

### Step 5: Update the Export Execution

**File:** `main.py` (in `export_prompt()` function)

Find this section:
```python
if file_type in ('csv', 'excel'):
    export_table(results, file_path, file_type, append=append)
else:
    export_pretty(results, file_path, append=append)
```

**Update to handle your format:**
```python
if file_type in ('csv', 'excel'):
    export_table(results, file_path, file_type, append=append)
elif file_type == 'fasta':
    export_fasta(results, file_path, append=append)
else:
    export_pretty(results, file_path, append=append)
```

**For multiple tools:**
```python
if file_type in ('csv', 'excel'):
    export_table(results, file_path, file_type, append=append)
elif file_type == 'fasta':
    export_fasta(results, file_path, append=append)
elif file_type == 'gff':
    export_gff(results, file_path, append=append)
else:
    export_pretty(results, file_path, append=append)
```

---

## Complete Example: Adding Custom Export Format for Phylogenetic Analysis

Let's say after preparing sequences with Sourmash, you want to export additional metadata.

### Step 1: Create the function

**In `modules/export_utils.py`:**
```python
def export_gff(df, file_path, append=False):
    """
    Export metadata in GFF3-like format for genomic annotations.
    """
    mode = 'a' if append and os.path.exists(file_path) else 'w'
    with open(file_path, mode, encoding='utf-8') as f:
        f.write("##gff-version 3\n")
        metadata = df[df['type'] == 'metadata']
        
        if not metadata.empty:
            for _, row in metadata.iterrows():
                # Convert metadata to GFF format
                # Format: seqname source feature start end score strand frame attributes
                lab_id = row.get('lab_id', 'unknown')
                key = row['key']
                value = row['value']
                f.write(f"{lab_id}\tdatabase\tfeature\t1\t100\t.\t+\t.\tKey={key};Value={value}\n")
    
    print(f"Exported GFF annotations to {file_path}")
```

### Step 2: Import it

**In `main.py`:**
```python
from modules.export_utils import export_table, export_pretty, export_fasta, export_gff
```

### Step 3: Update menu

```python
fmt = input("Export as [1] CSV, [2] Excel, [3] TXT, [4] FASTA, or [5] GFF? (1/2/3/4/5): ").strip()
if fmt == '1':
    ext, file_type = 'csv', 'csv'
elif fmt == '2':
    ext, file_type = 'xlsx', 'excel'
elif fmt == '3':
    ext, file_type = 'txt', 'txt'
elif fmt == '4':
    ext, file_type = 'fasta', 'fasta'
elif fmt == '5':
    ext, file_type = 'gff', 'gff'
```

### Step 4: Update execution

```python
if file_type in ('csv', 'excel'):
    export_table(results, file_path, file_type, append=append)
elif file_type == 'fasta':
    export_fasta(results, file_path, append=append)
elif file_type == 'gff':
    export_gff(results, file_path, append=append)
else:
    export_pretty(results, file_path, append=append)
```

---

## Understanding the Data Structure

When users search and export, they get a DataFrame with this structure:

```
     lab_id      key           value                type
0    UL001    contig_001      ACGTACGT...          fasta
1    UL001    contig_002      ACGTACGT...          fasta
2    UL001    Taxonomy        Rhizopus             metadata
3    UL001    Location        Soil Sample          metadata
```

**Your export function receives this entire DataFrame** and filters it to what you need:

```python
# Get only FASTA sequences
fasta_only = df[df['type'] == 'fasta']

# Get only metadata
metadata_only = df[df['type'] == 'metadata']

# Get everything
all_data = df
```

---

## Checklist for Adding a New Export Format

- [ ] **Understand tool requirements**
  - What file format does it need?
  - What data should be included?
  - Any special formatting?

- [ ] **Create export function**
  - Add to `modules/export_utils.py`
  - Filter DataFrame to needed data type
  - Format according to tool specs
  - Add confirmation print statement

- [ ] **Import the function**
  - Add to imports in `main.py`

- [ ] **Update menu text**
  - Add option number to prompt
  - Add corresponding elif clause

- [ ] **Update execution logic**
  - Add elif clause to check file_type
  - Call your export function

- [ ] **Test**
  - Run program
  - Search for data
  - Export in new format
  - Verify file format is correct
  - Verify tool can read the file

---

## Common Patterns for Different Tools

### Pattern 1: Sequence-Only Export (Like FASTA)

```python
def export_sequences_only(df, file_path, append=False):
    mode = 'a' if append and os.path.exists(file_path) else 'w'
    with open(file_path, mode, encoding='utf-8') as f:
        data = df[df['type'] == 'fasta']
        for _, row in data.iterrows():
            f.write(f">{row['key']}\n")
            f.write(str(row['value']) + "\n")
    print(f"Exported sequences to {file_path}")
```

### Pattern 2: Metadata-Only Export (Like Tab-Delimited)

```python
def export_metadata_only(df, file_path, append=False):
    mode = 'a' if append and os.path.exists(file_path) else 'w'
    with open(file_path, mode, encoding='utf-8') as f:
        f.write("key\tvalue\n")  # Header
        data = df[df['type'] == 'metadata']
        for _, row in data.iterrows():
            f.write(f"{row['key']}\t{row['value']}\n")
    print(f"Exported metadata to {file_path}")
```

### Pattern 3: Combined Export (Like Paired Files)

```python
def export_paired(df, file_path, append=False):
    """Export both sequences and metadata to paired files"""
    base_path = file_path.replace('.paired', '')
    
    # Export sequences
    with open(f"{base_path}.fasta", 'w') as f:
        fasta = df[df['type'] == 'fasta']
        for _, row in fasta.iterrows():
            f.write(f">{row['key']}\n{str(row['value'])}\n")
    
    # Export metadata
    with open(f"{base_path}.metadata", 'w') as f:
        metadata = df[df['type'] == 'metadata']
        for _, row in metadata.iterrows():
            f.write(f"{row['key']}\t{row['value']}\n")
    
    print(f"Exported paired files to {base_path}.*")
```

---

## Real-World Examples: Other Tools

### For MAFFT (Sequence Alignment)
Same as FASTA - use `export_fasta()` directly

### For RAxML (Tree Building)
Same as FASTA - sequences need to be aligned first, then use FASTA export

### For Sourmash (Genome Sketching)
Needs individual genomes as separate FASTA files - would need modified export:
```python
def export_by_genome(df, output_dir):
    """Export each genome to separate FASTA file"""
    # Group by lab_id
    # Create subdirectory per genome
    # Export sequences for that genome to file
```

### For Galaxy Workflow
Might need JSON format:
```python
def export_galaxy_json(df, file_path, append=False):
    import json
    data = df[df['type'] == 'fasta']
    galaxy_format = [{"name": row['key'], "seq": str(row['value'])} 
                     for _, row in data.iterrows()]
    with open(file_path, 'w') as f:
        json.dump(galaxy_format, f, indent=2)
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ImportError: cannot import export_function | Check function name matches import statement |
| File is empty | Check DataFrame filter - make sure `df['type']` matches your data |
| File has wrong format | Review tool requirements - verify formatting in function |
| Tool can't read file | Check encoding (should be UTF-8) and line endings |
| Append doesn't work | Verify file exists and mode is set to 'a' |

---

## Summary: The 5-Step Process

1. **Understand** what format your tool needs
2. **Create** the export function in `export_utils.py`
3. **Import** the function in `main.py`
4. **Update** the menu prompt
5. **Update** the execution logic

**Result:** Users can now export data formatted for your tool with one command.

---

## Next Steps

After adding an export format:
- Document it in a tool-specific guide
- Test with actual tool
- Add to README
- Consider adding other formats for same tool if needed

---

**Last Updated:** January 28, 2026  
**Version:** 1.0
