# Barrnap Integration - Quick Start Reference

## Installation Check

```bash
# Verify Barrnap is installed
barrnap --version

# If not installed:
pip install barrnap
```

---

## Running the Workflow

```bash
cd c:\Users\reece\OneDrive\Desktop\reece\coding\myco_research\r_db
python3 main.py
```

**Menu:**
```
1) Import Data
2) Search Data
3) Delete Data
4) Analysis Workflows          ← SELECT THIS
5) Database Information
6) Help
7) Exit
```

**Then select:**
```
1) Barrnap rRNA Annotation Pipeline
```

---

## Workflow Overview

```
Step 1: Genome Selection
  → Lab ID / Metadata / All / Advanced Filter

Step 2: Export Genomes
  → Exported to: barrnap_input/genomes/

Step 3: Barrnap Parameters
  → Use Defaults (fungi, coverage=50)
  → Or Customize

Step 4: Run Barrnap
  → Processes all genomes

Step 5: Extract rRNA
  → Parses GFF, extracts sequences

Step 6: Choose Outputs
  → 1=FASTA, 2=CSV, 3=GFF
  → Enter: 1,2 (most common)

Step 7: Results
  → barrnap_output/
     ├── rrna_sequences/
     ├── rrna_summary.csv
     ├── gff_annotations/
     └── summary.txt
```

---

## Genome Selection Examples

### Example 1: Single Genome
```
Option: 1 (Lab ID)
Enter: UL001
Result: 1 genome selected
```

### Example 2: All Rhizopus Genomes
```
Option: 2 (Metadata keyword)
Enter: Rhizopus
Result: All genomes with "Rhizopus" in metadata
```

### Example 3: Rhizopus from 2025
```
Option: 4 (Advanced filter)
Key #1: Taxonomy comments
Value #1: Rhizopus
Key #2: Extraction Date(YYYY-MM-DD)
Value #2: 2025
Result: Only Rhizopus from 2025
```

---

## Output Examples

### rrna_summary.csv
```
genome_id,16S_count,23S_count,5S_count,tRNA_count,...,total_rRNA
UL001,1,1,1,47,...,50
UL002,1,1,1,48,...,51
```

### FASTA Files
```
barrnap_output/rrna_sequences/
├── UL001_16S_rRNA_1.fasta
├── UL001_23S_rRNA_1.fasta
├── UL001_5S_rRNA_1.fasta
├── UL001_tRNA_1.fasta
├── UL001_tRNA_2.fasta
└── ... (47 total tRNAs)
```

### summary.txt
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
16S rRNA: 12
23S rRNA: 12
5S rRNA: 12
tRNA: 576
Total rRNA: 612

[... more details ...]
```

---

## Common Parameters

### Barrnap Kingdom Options
- `fungi` - For fungal genomes (DEFAULT)
- `bacteria` - For bacterial genomes
- `archaea` - For archaeal genomes

### Coverage Threshold
- `50` - Default (balanced sensitivity)
- `75` - Stricter (fewer false positives)
- `25` - Looser (more sequences found)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Barrnap not found" | `pip install barrnap` |
| No genomes selected | Check metadata keywords match your data |
| Empty rRNA directory | Check organism kingdom is correct |
| GFF file missing | Barrnap failed - check genome file format |

---

## File Locations

```
c:\Users\reece\OneDrive\Desktop\reece\coding\myco_research\r_db\

├── modules/
│   └── workflow_barrnap.py          ← Main workflow code
│
├── main.py                          ← Updated menu
│
├── config/
│   └── schema.yaml                  ← Configuration
│
├── docs/
│   ├── BARRNAP_USER_GUIDE.md       ← Complete guide
│   ├── BARRNAP_DEVELOPER_GUIDE.md  ← For adding tools
│   └── IMPLEMENTATION_COMPLETE.md   ← Summary
│
├── barrnap_input/
│   └── genomes/                     ← Staging area
│
└── barrnap_output/
    ├── rrna_sequences/              ← FINAL RESULTS
    ├── gff_annotations/
    ├── rrna_summary.csv
    └── summary.txt
```

---

## Next Steps After Running

1. **Review summary.txt** for overview
2. **Check rrna_summary.csv** for counts
3. **Use sequences in rrna_sequences/** for tree building:
   ```bash
   # Align sequences
   mafft UL001_16S_rRNA_1.fasta > alignment.fasta
   
   # Build tree
   raxml -s alignment.fasta -n mytree
   ```

---

## For Lab Members Adding New Tools

See: **docs/BARRNAP_DEVELOPER_GUIDE.md**

Template covers:
- Architecture pattern
- 8-function module structure
- How to add menu option
- Configuration management
- Documentation requirements

---

**Quick Reference Version:** 1.0  
**Last Updated:** January 21, 2025
