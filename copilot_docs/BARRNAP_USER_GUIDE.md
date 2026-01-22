# Barrnap rRNA Annotation Pipeline - User Guide

## Overview

The Barrnap rRNA Annotation Pipeline is an integrated workflow that allows you to:
1. **Search** your fungal genome database using flexible filtering
2. **Export** selected genomes for processing
3. **Run Barrnap** to identify ribosomal RNA (rRNA) sequences
4. **Extract** rRNA sequences for downstream analysis
5. **Organize** results for phylogenetic tree-building

This integration provides a streamlined interface to Barrnap, a specialized tool for annotating RNA features in genomes.

---

## Prerequisites

### Required Software
- **Barrnap** - RNA annotation tool
  - Install via: `pip install barrnap`
  - GitHub: https://github.com/tseemann/barrnap
  - Or manual installation from the GitHub repository

### Python Dependencies
All dependencies are already included in `requirements.txt`:
- pandas (data manipulation)
- biopython (sequence handling)
- sqlalchemy (database access)
- pyyaml (configuration management)

---

## How to Use

### Starting the Workflow

1. **Run the database program:**
   ```bash
   python3 main.py
   ```

2. **From the main menu, select:**
   ```
   4) Analysis Workflows
   ```

3. **Then select:**
   ```
   1) Barrnap rRNA Annotation Pipeline
   ```

---

## Step-by-Step Workflow

### Step 1: Genome Selection

Choose how to select genomes from your database:

#### Option 1: By Lab ID
```
Select option: 1
Enter Lab ID (e.g., UL001): UL042
```
Selects a single genome by its Uehling Lab ID.

#### Option 2: By Metadata Keyword
```
Select option: 2
Enter metadata keyword (e.g., 'Rhizopus', '2025', 'soil'): Rhizopus
```
Finds all genomes where ANY metadata field contains your keyword. Case-insensitive.

#### Option 3: All Genomes
```
Select option: 3
```
Processes every genome currently in the database.

#### Option 4: Advanced Filter (AND Logic)
```
Select option: 4
Enter metadata key #1 (or leave blank to finish): Taxonomy comments
Enter value for 'Taxonomy comments': Rhizopus
✓ Added filter: Taxonomy comments = 'Rhizopus'

Enter metadata key #2 (or leave blank to finish): Extraction Date(YYYY-MM-DD)
Enter value for 'Extraction Date(YYYY-MM-DD)': 2025
✓ Added filter: Extraction Date(YYYY-MM-DD) = '2025'

Enter metadata key #3 (or leave blank to finish): 
```

**Advanced Filter Explanation:**
- Add multiple criteria by entering key-value pairs
- All criteria must be satisfied (AND logic, not OR)
- Leave the key blank when finished
- Useful for: "All Rhizopus genomes collected in 2025 from soil samples"

### Step 2: Review Selection

```
Found 12 genome(s) matching all criteria
Lab IDs: UL001, UL002, UL005, ...

Proceed with export and analysis? (y/n): y
```

Review the count and confirm before proceeding.

### Step 3: Export Genomes

```
--- STEP 2: EXPORTING GENOMES ---

✓ Exported UL001 to UL001.fasta
✓ Exported UL002 to UL002.fasta
✓ Exported UL005 to UL005.fasta
...
Exported 12/12 genomes
```

Genomes are temporarily staged in: `barrnap_input/genomes/`

### Step 4: Set Barrnap Parameters

```
--- STEP 3: BARRNAP PARAMETERS ---

Barrnap Default Settings (for fungi):
  Kingdom: fungi
  Coverage: 50
  Threads: auto (system default)

Use default settings? (y/n): y
```

#### Option A: Use Defaults (Recommended for most cases)
- Kingdom: fungi (optimized for fungal genomes)
- Coverage: 50 (sensitivity threshold)
- Threads: automatic (uses all available CPU cores)

#### Option B: Customize Parameters
```
Use default settings? (y/n): n

--- CUSTOM PARAMETERS ---
Kingdom (fungi/bacteria/archaea) [default: fungi]: fungi
Coverage threshold [default: 50]: 75
Number of threads (or 'auto') [default: auto]: 4
```

**Parameter Explanations:**
- **Kingdom:** Type of organism (fungi, bacteria, or archaea). Barrnap uses different models for each.
- **Coverage:** Minimum coverage threshold for sequence detection. Higher = stricter filtering.
- **Threads:** Number of CPU cores to use. More = faster, but requires available cores.

### Step 5: Barrnap Execution

```
--- STEP 4: RUNNING BARRNAP ---

Running Barrnap on 12 genome(s)...
Command parameters: kingdom=fungi, coverage=50
✓ Barrnap completed successfully
```

The system runs Barrnap on all exported genomes and produces GFF3 annotation files.

### Step 6: Extract rRNA Sequences

```
--- STEP 5: EXTRACTING rRNA SEQUENCES ---

✓ UL001: 3 sequences extracted (16S:1, 23S:1, 5S:1, tRNA:47)
✓ UL002: 3 sequences extracted (16S:1, 23S:1, 5S:1, tRNA:48)
✓ UL005: 3 sequences extracted (16S:1, 23S:1, 5S:1, tRNA:49)
```

Barrnap results are parsed and rRNA sequences are extracted.

### Step 7: Choose Output Options

```
--- EXTRACTION OUTPUT OPTIONS ---

What would you like to save?
1) rRNA sequences (FASTA files)
2) Summary CSV (counts per genome/type)
3) Raw GFF annotations (Barrnap output)

Default (all): Press ENTER or enter '1,2,3'

Select options (comma-separated): 1,2
```

**Output Options:**
- **Option 1 - FASTA Files** (Recommended): Extracted rRNA sequences ready for alignment and tree-building
- **Option 2 - Summary CSV**: Quick overview of counts per genome/rRNA type
- **Option 3 - GFF Files**: Raw Barrnap output with exact coordinates (useful for reference)

**Common Selections:**
- `1` - Just the sequences (quickest, minimal disk space)
- `1,2` - Sequences + summary (balanced)
- `1,2,3` - Everything (most complete)
- Press ENTER - All options (default)

### Step 8: Results Summary

```
============================================================
BARRNAP rRNA ANNOTATION PIPELINE - SUMMARY REPORT
============================================================
Generated: 2025-01-21 14:32:15

--- PROCESSING STATISTICS ---
Total genomes processed: 12
Successfully processed: 12
Failed genomes: 0

--- rRNA SEQUENCES FOUND ---
16S rRNA (small subunit): 12
23S rRNA (large subunit): 12
5S rRNA (small subunit): 12
tRNA (transfer RNA): 576
tmRNA (transfer-mRNA): 0
Other RNA features: 0
Total rRNA sequences: 612

--- OUTPUT FILES ---
✓ rRNA sequences: barrnap_output/rrna_sequences/
✓ Summary CSV: barrnap_output/rrna_summary.csv
✓ GFF annotations: barrnap_output/gff_annotations/

--- NEXT STEPS ---
The extracted rRNA sequences are ready for:
  - Sequence alignment (MAFFT, Clustal)
  - Phylogenetic tree building (RAxML, FastTree, IQTree)
  - Further analysis and visualization

For alignment and tree building, use the extracted FASTA files in:
  barrnap_output/rrna_sequences/

============================================================

✓ Summary report saved to: barrnap_output/summary.txt

✓ Barrnap workflow complete!

Results directory: barrnap_output/
```

---

## Output Files Explained

### Directory Structure

```
barrnap_output/
├── rrna_sequences/           (FASTA files of extracted rRNA)
│   ├── UL001_16S_rRNA_1.fasta
│   ├── UL001_23S_rRNA_1.fasta
│   ├── UL001_5S_rRNA_1.fasta
│   ├── UL001_tRNA_1.fasta
│   ├── ... (files for all genomes)
│
├── gff_annotations/          (Raw Barrnap GFF3 output)
│   ├── UL001.gff
│   ├── UL002.gff
│   ├── ... (one per genome)
│
├── rrna_summary.csv         (Summary table)
│
└── summary.txt              (Human-readable report)
```

### File Descriptions

#### rRNA FASTA Files (`rrna_sequences/`)
Individual FASTA files for each detected rRNA sequence.

**Filename pattern:** `{LAB_ID}_{RNA_TYPE}_{COUNT}.fasta`

Example:
- `UL001_16S_rRNA_1.fasta` - First 16S rRNA from genome UL001
- `UL001_23S_rRNA_1.fasta` - First 23S rRNA from genome UL001
- `UL001_tRNA_47.fasta` - 47th tRNA from genome UL001

**File content:**
```fasta
>UL001_16S_rRNA_1
ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT...
```

#### Summary CSV (`rrna_summary.csv`)
Spreadsheet showing counts of each rRNA type per genome.

**Example:**
```
genome_id,16S_count,23S_count,5S_count,tRNA_count,tmRNA_count,other_count,total_rRNA
UL001,1,1,1,47,0,0,50
UL002,1,1,1,48,0,0,51
UL005,1,1,1,49,0,0,52
```

**Use cases:**
- Quick quality check (are counts reasonable?)
- Export to Excel for reporting
- Identify genomes with unusual rRNA counts

#### GFF3 Annotations (`gff_annotations/`)
Raw output from Barrnap with exact genomic coordinates.

**Example line:**
```
UL001.fasta    barrnap    rRNA    1000    1500    .    +    0    product=16S_ribosomal_RNA
```

**Columns:**
- Sequence ID, Tool, Feature Type, Start, End, Score, Strand, Phase, Attributes

**Use cases:**
- Verification of exact coordinates
- Integration with genome browsers
- Advanced analysis requiring precise location data

#### Summary Report (`summary.txt`)
Human-readable summary with all key statistics and file paths.

---

## Error Handling

### If Barrnap is Not Installed

```
ERROR: Barrnap is not installed or not in PATH.
Please install Barrnap: pip install barrnap
Or visit: https://github.com/tseemann/barrnap
```

**Solution:**
```bash
pip install barrnap
```

### If a Genome Fails to Process

```
⚠ No GFF output found for UL042
⚠ No rRNA features found in UL025

--- FAILED GENOMES ---
  UL042: No GFF output
  UL025: No rRNA features

Failed genomes: 2
```

**Possible reasons:**
- Genome file is corrupted or empty
- Barrnap detected no rRNA sequences (possible contamination or wrong organism type)
- File format issue

**Solutions:**
- Check the original genome file quality
- Verify you selected the correct organism kingdom
- Re-import the genome file if it's corrupted

---

## Common Workflows

### Workflow 1: Quick Analysis of All Fungi Genomes
```
1. Select option 3 (All genomes)
2. Use default Barrnap settings
3. Select output: 1,2 (FASTA + CSV)
```

### Workflow 2: Filter Specific Genus for Detailed Analysis
```
1. Select option 4 (Advanced filter)
   - Taxonomy comments = Rhizopus
   - Extraction Date(YYYY-MM-DD) = 2025
2. Customize Barrnap: coverage=75 for stricter filtering
3. Select output: 1,2,3 (All)
```

### Workflow 3: Single Genome Verification
```
1. Select option 1 (Lab ID)
   - Enter: UL001
2. Use defaults
3. Review GFF file manually for validation
```

### Workflow 4: Prepare for Tree Building
```
1. Select option 2 (Metadata keyword)
   - Keyword: Mortierellaceae
2. Use defaults
3. Select output: 1 (FASTA only)
4. Use extracted FASTA files with tree-building software
```

---

## Next Steps: Building Phylogenetic Trees

Once you have extracted rRNA sequences, you can build trees:

### Quick Method: Whole Genome Similarity
Use the Sourmash tool (separate workflow) for rapid tree visualization.

### Publication-Quality Method:
1. **Align sequences** (from `rrna_sequences/`)
   ```bash
   mafft UL001_16S_rRNA_1.fasta UL002_16S_rRNA_1.fasta > alignment.fasta
   ```

2. **Build tree** (requires alignment)
   ```bash
   raxml -s alignment.fasta -n mytree
   # or
   fasttree alignment.fasta > tree.nwk
   ```

3. **Visualize** (several tools available)
   - FigTree (desktop GUI)
   - ETE3 (Python library)
   - iTOL (online)

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| "Barrnap not found" | Not installed | `pip install barrnap` |
| No genomes selected | Wrong search criteria | Verify metadata keywords in database |
| "No GFF output" | Barrnap crash | Check genome file format (should be FASTA) |
| Empty rRNA directory | No rRNA found | Check organism kingdom setting |
| CSV file not created | Output option not selected | Re-run and select option 2 |

---

## FAQ

**Q: Can I run Barrnap on bacterial genomes?**
A: Yes! In step 4, select "bacteria" instead of "fungi" when prompted for kingdom.

**Q: How long does this take?**
A: Typically 30 seconds to 2 minutes for 10-20 fungal genomes, depending on genome size and CPU cores.

**Q: Can I use the extracted rRNA for other tools?**
A: Yes! The FASTA files are standard format and compatible with any sequence analysis tool.

**Q: What if I get tRNA sequences instead of rRNA?**
A: Both are valid RNA features. tRNA sequences can also be used for phylogenetics, though rRNA (especially 16S/23S) is more commonly used.

**Q: Can I re-run the workflow on the same genomes?**
A: Yes, but the previous results in `barrnap_output/` will be overwritten.

---

## For Lab Administrators & Developers

See `BARRNAP_DEVELOPER_GUIDE.md` for:
- Architecture and code structure
- How to integrate other tools using the same pattern
- Customizing the workflow for specific needs
- Understanding the module design

---

## Support & Issues

If you encounter errors or have questions:
1. Check the troubleshooting section above
2. Verify Barrnap installation: `barrnap --version`
3. Review the summary report in `barrnap_output/summary.txt`
4. Contact your database administrator (Reece M - Uehling Lab Discord)

---

**Last Updated:** January 21, 2025
**Version:** 1.0
