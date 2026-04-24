# Hybrid Phylogenetic Pipeline - Implementation Summary

**Date:** February 14, 2026  
**Approach:** Hybrid (Python Orchestration + Existing Tools + Citations)

---

## What is the Hybrid Approach?

The hybrid approach balances three key goals:

1. **Reproducibility** - Uses peer-reviewed, published tools
2. **Usability** - Simple Python orchestration layer
3. **Scalability** - Leverages existing functionality rather than reinventing

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│ User Command                                        │
│ python3 phylo_pipeline.py --mode select-longest    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Python Orchestration (phylo_pipeline.py)           │
│ - File discovery                                    │
│ - Progress reporting                               │
│ - Error handling                                    │
│ - Statistics generation                            │
└──────┬──────────────────────────────────────────────┘
       │
       ├─────────────────────┬──────────────────────┬────────────────────┐
       ▼                     ▼                      ▼                    ▼
┌────────────────┐    ┌───────────────┐    ┌─────────────────┐    ┌──────────────┐
│ BARRNAP        │    │ SeqKit        │    │ MAFFT           │    │ IQ-TREE      │
│ (Extract rRNA) │    │ (Optional,    │    │ (Align)         │    │ (Tree build) │
│ Seemann 2012   │    │ Filter)       │    │ Katoh et al.    │    │ Minh et al.  │
│                │    │ Wei et al.    │    │ 2002/2013       │    │ 2020         │
└────────────────┘    └───────────────┘    └─────────────────┘    └──────────────┘
```

---

## Components

### 1. Python Scripts (Orchestration)

**Files:**
- `tools/phylo_pipeline.py` - Main orchestration
- `tools/extract_longest_rrna.py` - Standalone sequence extractor

**Responsibilities:**
- Parse FASTA files
- Detect rRNA types (18S, 26S, 5.8S, etc.)
- Group sequences by type
- Select longest of each type
- Combine outputs
- Generate statistics
- Report progress

**Design:** Modular, testable, well-documented

### 2. External Tools (Processing)

| Tool | Purpose | Citation | Version |
|------|---------|----------|---------|
| Barrnap | rRNA extraction | Seemann 2012 | 0.9 |
| MAFFT | Sequence alignment | Katoh et al. 2002/2013 | 7.x |
| IQ-TREE | Phylogenetic inference | Minh et al. 2020 | 2.x |
| SeqKit | Sequence filtering | Wei et al. 2016 | 2.8.2 |

**Why these tools?**
- **Peer-reviewed** - Published in major journals
- **Widely used** - Standard in phylogenetics community
- **Well-maintained** - Active development and support
- **Efficient** - Optimized for large datasets
- **Interoperable** - Work well together

---

## Files Created/Modified

### New Files

1. **`docs/CITATIONS_AND_REFERENCES.md`** ⭐ START HERE
   - Complete citations in APA and BibTeX format
   - Methods section template
   - Version recording template
   - Publication checklist

2. **`docs/MULTI_GENOME_PHYLOGENY_QUICK_START.md`**
   - User-friendly quick start guide
   - 4-command workflow
   - Troubleshooting

3. **`tools/README_PHYLO.md`**
   - Tool documentation
   - Quick reference

### Modified Files

1. **`tools/phylo_pipeline.py`**
   - Added comprehensive citation header
   - Updated docstrings with tool attribution
   - No functional changes (still works the same way)

2. **`tools/extract_longest_rrna.py`**
   - Added tool citations and references
   - Improved documentation

3. **`docs/PHYLOGENY_PIPELINE_INTEGRATION.md`**
   - Added multi-genome section
   - Added troubleshooting for multi-genome workflows
   - Added citation references

---

## How to Use for Publication

### Step 1: Review Citations
```bash
# Before submitting your paper:
cat docs/CITATIONS_AND_REFERENCES.md
```

### Step 2: Copy Methods Template
Use the template from `CITATIONS_AND_REFERENCES.md` → "Complete Example Methods Section"

### Step 3: Record Tool Versions
```bash
# Run once before your analysis:
barrnap --version
mafft --version
iqtree -version
seqkit version
python3 --version

# Record in lab notebook
```

### Step 4: Include Bibliography
Use the BibTeX entries from `CITATIONS_AND_REFERENCES.md` in your paper

---

## Why This Approach is Better

### ✅ Scalable
- Can add more genomes without changing code
- Same scripts work for 5 genomes or 500
- Can swap tools if needed (e.g., use MUSCLE instead of MAFFT)

### ✅ Reproducible
- All tools are published and peer-reviewed
- Exact versions are documented
- Command lines are preserved in scripts

### ✅ Citable
- Every tool has a DOI
- Complete bibliography included
- Methods section template provided

### ✅ Maintainable
- Python layer handles orchestration
- External tools via subprocesses
- Easy to troubleshoot
- Well-documented code

### ✅ Honest
- Cites all sources properly
- Doesn't claim credit for others' work
- Shows exactly what each tool does

---

## Example: Running Your Analysis

```bash
cd /nfs4/BPP/Uehling_Lab/morgaree/relational_db

# Step 1: Select sequences
python3 tools/phylo_pipeline.py --mode select-longest \
    --input-dir exported_files/phylo_tree/ \
    --output-file combined.fasta

# Step 2: Align (can use standard MAFFT command)
mafft --auto combined.fasta > aligned.fasta

# Step 3: Build tree (can use standard IQ-TREE command)
iqtree -s aligned.fasta -m MFP -bb 1000 -nt 4

# Step 4: Write up your methods
# See: docs/CITATIONS_AND_REFERENCES.md → Methods section template
```

---

## Publishing Workflow

### In Your Paper

**Methods section:**
```
Ribosomal RNA sequences were extracted using Barrnap v0.9 (Seemann, 2012). 
The longest sequence of each rRNA type was selected for analysis. Multi-sequence 
alignment was performed with MAFFT v7 (Katoh & Standley, 2013) using the --auto 
setting. Phylogenetic inference was conducted with IQ-TREE 2 (Minh et al., 2020), 
with model selection via ModelFinder Plus and 1000 ultrafast bootstrap replicates.
```

**References section:**
Use the BibTeX entries from `docs/CITATIONS_AND_REFERENCES.md`

**Supplementary Information (optional):**
```
Analysis performed using custom Python scripts to orchestrate the following 
peer-reviewed tools: [cite each tool]. Scripts and documentation available at:
[your lab repository/GitHub/etc.]
```

---

## Tools at a Glance

### Barrnap
- **What:** Identifies ribosomal RNA in genomes
- **Input:** Genomic FASTA sequences
- **Output:** rRNA FASTA sequences
- **Citation:** Seemann, T. (2012) https://github.com/tseemann/barrnap

### MAFFT
- **What:** Aligns sequences to each other
- **Input:** rRNA FASTA sequences
- **Output:** Aligned FASTA (with gaps)
- **Citation:** Katoh & Standley (2013) doi:10.1093/molbev/mst010

### IQ-TREE
- **What:** Builds phylogenetic trees
- **Input:** Aligned FASTA
- **Output:** Tree files (Newick format), statistics, support values
- **Citation:** Minh et al. (2020) doi:10.1093/molbev/msaa015

### SeqKit (Optional)
- **What:** Fast sequence manipulation
- **Input/Output:** FASTA sequences
- **Citation:** Wei et al. (2016) doi:10.1371/journal.pone.0163962

---

## Version Control / Lab Documentation

**Save this information with your analysis:**

```yaml
Analysis Date: 2026-02-14
User: [Your Name]
Project: [Project Name]

Tools Used:
  - Barrnap v0.9 (Seemann 2012)
  - MAFFT v7 (Katoh & Standley 2013)
  - IQ-TREE 2.x (Minh et al. 2020)
  - Python 3.x

Pipeline Scripts:
  - tools/phylo_pipeline.py (hybrid orchestration)
  - tools/extract_longest_rrna.py (optional standalone)

Command Used:
  python3 tools/phylo_pipeline.py --mode select-longest \
    --input-dir exported_files/phylo_tree/ \
    --output-file combined.fasta

Parameters:
  - Minimum sequence length: 100 bp
  - MAFFT algorithm: auto
  - IQ-TREE model: MFP (ModelFinder Plus)
  - Bootstrap replicates: 1000 (ultrafast)

Output Files:
  - combined.fasta (longest sequences)
  - aligned.fasta (multiple sequence alignment)
  - aligned.fasta.treefile (phylogenetic tree)

Notes:
  [Your analysis notes, special parameters, etc.]
```

---

## References

See **`docs/CITATIONS_AND_REFERENCES.md`** for:
- Complete citations in multiple formats
- Methods section template
- BibTeX entries ready for your bibliography
- Version recording template
- Publication checklist

---

## Key Takeaways

✅ **Scalable** - Works with 5 genomes or 500  
✅ **Reproducible** - Uses published tools with specific versions  
✅ **Citable** - All tools properly referenced  
✅ **Maintainable** - Python + external tools separation  
✅ **Honest** - Full disclosure of what each tool does  

**Ready for publication!** 📄

---

Generated February 14, 2026
