# Quick Start Guide - Complete Workflow

**For:** Lab members who have already installed the database  
**Goal:** Get data imported, searched, and exported in 10 minutes

---

## Overview

This guide covers:
1. Running the program
2. Importing data (samples or your own)
3. Searching by lab ID or metadata
4. Exporting for analysis (including phylogenetic pipelines)
5. Multi-lab export workflow

---

## 1. Start the Program

Navigate to your `relational_db` folder and run:

```bash
python main.py        # Windows
python3 main.py       # macOS/Linux
```

You'll see:
```
Welcome to the Fungal Research Database
1) Import Data
2) Search Data
3) Delete Data
4) Help
5) Database Information
6) Exit

Enter your choice:
```

---

## 2. Import Data (2-3 minutes)

### Quick Path: Use Built-in Examples

1. Select: `1` (Import Data)
2. Select: `3` (Bulk Import)
3. Enter: `example_files/bulk_import_example.xlsx`
4. Follow prompts for duplicate handling
5. You'll see: `✓ Metadata imported: 3` and `✓ FASTA imported: 3`

### Custom Path: Import Your Own Data

**For Excel/CSV metadata:**
- Select: `1` → `1` (Standard Excel Import)
- Enter file path
- Respond to column prompts

**For FASTA sequences:**
- Select: `1` → `2` (Standard FASTA Import)
- Enter file path and Uehling Lab ID when prompted

**For large datasets:**
- Select: `1` → `3` (Bulk Import)
- Requires coordination Excel file with both metadata and FASTA references

---

## 3. Search Options (1 minute each)

### Search by Lab ID

```
Select: 2 (Search Data)
Enter keyword: UL155
```

Returns all sequences and metadata for that specific genome.

### Search by Metadata

```
Select: 2 (Search Data)
Enter keyword: U1513A
```

Finds **all genomes** with "U1513A" in metadata (e.g., project codes, funding codes). System automatically fetches all matching FASTA sequences.

### Search Examples

| Search Term | Returns | Use Case |
|---|---|---|
| `UL155` | Single genome | Analyze one isolate |
| `U1513A` | All genomes with that project code | Compare multiple genomes from one project |
| `alpina` | All genomes matching species name | Single species analysis |
| `2023` | All recent samples | Time-based queries |

---

## 4. Export Results (1-2 minutes)

After searching, you'll see: `"Export results? (y/n)"`

### For Single-Genome Search (Search by Lab ID)

```
Type: y
Select format:
  1 = TXT (sequences only)
  2 = CSV (spreadsheet metadata)
  3 = XLSX (Excel metadata)
  4 = FASTA per Lab ID (for phylogenetic tools)
```

Choose your format and save location.

### For Multi-Genome Search (Search by Metadata)

#### **Export Option 1: Single Combined File**
```
Select: 1, 2, or 3
→ All matching genomes in one file (mixed together)
```

#### **Export Option 2: FASTA per Lab ID (Recommended for Phylogenetics)**
```
Select: 4
→ Creates separate FASTA file for each matched lab_id
→ Each file named: {UEHLING_ID}_phylo.fasta
→ Example output:
   ✓ UL155_phylo.fasta (12,667 sequences)
   ✓ UL162_phylo.fasta (9,731 sequences)
   ✓ UL163_phylo.fasta (35,440 sequences)
   ✓ UL169_phylo.fasta (86,924 sequences)
   ✓ UL174_phylo.fasta (33,601 sequences)
```

---

## 5. Complete Workflow Example: Phylogenetic Analysis

**Goal:** Prepare 5 genomes from project U1513A for phylogenetic tree analysis

### Step 1: Start Program
```bash
python3 main.py
```

### Step 2: Search by Project
```
Menu: Select "2) Search Data"
Enter keyword: U1513A
```

**What happens:**
- Program finds all lab_ids with "U1513A" in metadata
- Automatically fetches all FASTA sequences for those lab_ids
- Shows you results

### Step 3: Export per Lab ID
```
Export results? (y/n): y
Export as [1] CSV, [2] Excel, [3] TXT, or [4] FASTA per Lab ID? 
Select: 4

Export to [d]efault folder or [c]ustom path?
Select: d

Enter folder name (will be created inside exported_files/):
Enter: my_phylo_analysis
```

### Step 4: Files Are Ready
```
✓ Successfully exported 5 files to: exported_files/my_phylo_analysis/
  ✓ UL155_phylo.fasta
  ✓ UL162_phylo.fasta
  ✓ UL163_phylo.fasta
  ✓ UL169_phylo.fasta
  ✓ UL174_phylo.fasta
```

### Step 5: Use in Sourmash Pipeline
```bash
# Each file can be processed independently with sourmash
sourmash sketch dna exported_files/my_phylo_analysis/UL155_phylo.fasta

# Or process all at once
for f in exported_files/my_phylo_analysis/*.fasta; do
  sourmash sketch dna "$f"
done
```

---

## Quick Reference: Common Tasks

| Task | Steps |
|------|-------|
| Import metadata only | `1` → `1` (Standard Excel) → select file |
| Import sequences only | `1` → `2` (Standard FASTA) → select file + lab ID |
| Bulk import (all data) | `1` → `3` (Bulk Import) → select coordination file |
| Search one genome | `2` → enter lab ID (e.g., "UL155") |
| Search multiple genomes | `2` → enter metadata value (e.g., "U1513A") |
| Export single file | After search → `y` → `1`, `2`, or `3` |
| Export multiple per-ID files | After search → `y` → `4` |
| Delete a genome | `3` (Delete Data) → enter lab ID → confirm |

---

## Export Formats Explained

| Format | File Type | Best For | Notes |
|---|---|---|---|
| **TXT** | `.txt` | Viewing sequences | Plain FASTA format, 80-char lines |
| **CSV** | `.csv` | Spreadsheet analysis | Metadata only, not sequences |
| **XLSX** | `.xlsx` | Excel analysis | Metadata only, formatted nicely |
| **FASTA per Lab ID** | `.fasta` | Phylogenetic tools | One file per matched lab_id, tools-ready |

---

## Tips & Tricks

✓ **For phylogenetics:** Always use export format `4` (FASTA per Lab ID) with metadata searches  
✓ **Search results** show 40-character snippets for long sequences  
✓ **File paths** can be relative or absolute in bulk import  
✓ **Each import** creates a timestamp in the database for reproducibility  
✓ **Export location** defaults to `exported_files/` (you can choose custom paths)  
✓ **Search is case-insensitive** - "u1513a" and "U1513A" both work  

---

## Performance Expectations

| Operation | Time |
|---|---|
| Search single genome | 1-2 seconds |
| Search by metadata (5 genomes) | 2-3 seconds |
| Export 5 genomes to FASTA | 30-60 seconds |
| Export 20 genomes to FASTA | 2-5 minutes |

---

## What Next?

| Interest | Read This |
|---|---|
| Full program docs | `README.md` |
| Detailed testing guide | `MANUAL_TESTING_GUIDE.md` |
| Custom export formats | `CUSTOM_OUTPUT_FORMATS.md` |
| Phylogenetic pipeline details | `PHYLOGENY_PIPELINE_INTEGRATION.md` |
| All documentation | `DOCUMENTATION_TABLE.md` |

---

## Troubleshooting

**"No results found"**
- Check spelling of search term
- Try a simpler search (e.g., "U1" instead of "U1513A")

**"No FASTA sequences found"**
- The search matched metadata but genomic data isn't loaded
- Import genomic data first using option `1` → `2` or `3`

**"Permission denied" on export**
- Try exporting to `/tmp/` or use an absolute path to a writable directory
- Check disk space

---

## Stuck?

- Check `README.md` in the main folder
- Contact Reece M on Discord (Uehling Lab server)
- See troubleshooting section in `PHYLOGENY_PIPELINE_INTEGRATION.md`
