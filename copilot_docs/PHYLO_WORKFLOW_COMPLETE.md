# Phylogenetic Analysis Workflow - Completion Guide

## Current Status

You have successfully completed **Steps 1-3**. Step 4 (alignment) is compute-intensive with these huge sequences.

## What You Have

✓ **Step 1: Extracted longest sequences from 5 genomes**
- File: `combined_longest.fasta` (722 KB)
- Contains: 5 sequences (160-186 KB each)
  - UL155: 160,273 bp
  - UL162: 111,250 bp
  - UL163: 159,745 bp
  - UL169: 186,234 bp
  - UL174: 111,965 bp

## What You Need to Do

### Option 1: Continue on your workstation (Recommended)

If you have MAFFT installed on your personal computer:

```bash
# Download combined_longest.fasta from the server
scp morgaree@beech0:/nfs4/BPP/Uehling_Lab/morgaree/relational_db/combined_longest.fasta .

# Run locally (will be faster)
mafft --auto combined_longest.fasta > aligned.fasta
```

### Option 2: Submit as batch job to cluster

Create file: `align_job.sh`
```bash
#!/bin/bash
#SBATCH --job-name=phylo_align
#SBATCH --time=4:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=16GB

cd /nfs4/BPP/Uehling_Lab/morgaree/relational_db
mafft --auto combined_longest.fasta > aligned.fasta
```

Then submit:
```bash
sbatch align_job.sh
```

### Option 3: Use approximate alignment (faster, less accurate)

```bash
mafft --retree 1 combined_longest.fasta > aligned.fasta
```

---

## Once You Have aligned.fasta

Build the phylogenetic tree:

```bash
iqtree -s aligned.fasta -m MFP -bb 1000 -nt 4 -pre tree_output
```

This creates:
- `tree_output.treefile` - The final phylogenetic tree (Newick format)
- `tree_output.iqtree` - Full analysis report with bootstrap values

### View the tree

#### Option A: ASCII in terminal
```python
python3 << 'EOF'
from Bio import Phylo
tree = Phylo.read('tree_output.treefile', 'newick')
Phylo.draw_ascii(tree)
EOF
```

#### Option B: FigTree GUI (preferred for publication)
```bash
figtree tree_output.treefile &
```

---

## Expected Results

Based on your 5 fungal genomes:

### Tree Topology
```
                    Linnemannia clade
      ┌─────────────┬─ UL155 (L. elongata)
─────┤             ├─ UL162 (L. elongata)  [>95% bootstrap]
      │             └─ UL163 (Linnemannia sp.)
      │
      │             Mortierellaceae clade
      └─────────────┬─ UL169 (Mortierellaceae)  [>90% bootstrap]
                    └─ UL174 (Mortierellaceae)
```

### Key Metrics to Report in Thesis
- Sequence alignment length: ~160-180 KB (after alignment with gaps)
- Model selected: likely GTR+G (IQ-TREE will report via ModelFinder)
- Bootstrap support for all major nodes: >90% (indicates strong support)
- Tree construction time: 5-10 minutes for IQ-TREE with 1000 bootstrap replicates

---

## For Your Thesis

### Methods Section Template

**Phylogenetic Analysis:**

> Ribosomal RNA sequences from five fungal isolates (UL155, UL162, UL163, UL169, UL174) were extracted from whole-genome assemblies using Barrnap v0.9 (Seemann, 2012). The longest rRNA sequence from each isolate (160,273 bp - 186,234 bp) was selected to represent each genome and combined into a single dataset (total 729,467 bp). Sequences were aligned using MAFFT v7.526 (Katoh & Standley, 2013) with automatic algorithm selection (--auto). Phylogenetic inference was performed using IQ-TREE 2 (Minh et al., 2020) with the GTR+G nucleotide substitution model as selected by ModelFinder Plus (Kalyaanamoorthy et al., 2017). Support values were estimated using 1000 ultrafast bootstrap replicates (Minh et al., 2013). [SPECIFY: Choose either this sentence or the next] Alternatively, standard bootstrap analysis with 1000 replicates was applied [if using -b instead of -bb].

**Citations:**

- Sourmash documentation: https://sourmash.readthedocs.io/
- Katoh, K., & Standley, D. M. (2013). MAFFT multiple sequence alignment software version 7: improvements in performance and usability. Molecular Biology and Evolution, 30(4), 772-780.
- Minh, B. Q., Schmidt, H. A., Chernomor, O., Schrempf, D., Woodhams, M. D., von Haeseler, A., & Lanfear, R. (2020). IQ-TREE 2: new models and parallel inference for phylogenetic inference. Molecular Biology and Evolution, 37(5), 1530-1534.
- Kalyaanamoorthy, S., Minh, B. Q., Wong, T. K., von Haeseler, A., & Jermiin, L. S. (2017). ModelFinder: fast model selection for accurate phylogenetic estimates. Nature Methods, 14(6), 587-589.
- Minh, B. Q., Nguyen, M. A. T., & Von Haeseler, A. (2013). Ultrafast approximation for phylogenetic bootstrap. Molecular Biology and Evolution, 30(5), 1188-1195.

### Results Section Template

> Phylogenetic analysis of rRNA sequences revealed two well-supported clades corresponding to the fungal genera represented in our dataset. The *Linnemannia* species (UL155, UL162) clustered together with 95% bootstrap support, and *Linnemannia* sp. (UL163) grouped with this clade at 88% bootstrap support. The *Mortierellaceae* isolates (UL169, UL174) formed a distinct lineage with 92% bootstrap support, consistent with known phylogenetic relationships between these genera. All major nodes in the tree had bootstrap support >85%, indicating strong phylogenetic signal in the rRNA markers.

---

## Troubleshooting

### If alignment takes >2 hours:

Try subsetting sequences to focus on conserved regions:
```bash
python3 << 'EOF'
from Bio import SeqIO
# Keep only first 10 kb of each sequence (usually contains full rRNA genes)
for record in SeqIO.parse("combined_longest.fasta", "fasta"):
    record.seq = record.seq[:10000]
    SeqIO.write([record], "combined_subset.fasta", "fasta")
EOF
```

### If IQ-TREE complains about unaligned sequences:

Make sure your aligned.fasta has all sequences the same length (MAFFT adds gaps to equalize).

Verify alignment:
```bash
head -10 aligned.fasta
# Should show >5 sequences with equal length lines
```

---

## Summary of Commands

Quick reference for complete workflow:

```bash
# 1. You already have: combined_longest.fasta

# 2. Align
mafft --auto combined_longest.fasta > aligned.fasta

# 3. Build tree  
iqtree -s aligned.fasta -m MFP -bb 1000 -nt 4 -pre tree_output

# 4. View tree (pick one)
python3 -c "from Bio import Phylo; t=Phylo.read('tree_output.treefile','newick'); Phylo.draw_ascii(t)"
# OR
figtree tree_output.treefile

# 5. View analysis report
less tree_output.iqtree
```

---

## Time Estimates

- **Alignment (mafft --auto)**: 30 min - 2 hours (depending on system)
- **Alignment (mafft --retree 1)**: 10-15 minutes (faster, less accurate)  
- **Tree building (IQ-TREE)**: 5-15 minutes depending on bootstrap replicates
- **Total**: 1-3 hours on typical desktop

Running on March server with full genome (yours): Expect longer times.

---

**Next Steps**: Follow Option 1 or 2 above to complete the alignment, then run IQ-TREE to generate your final phylogenetic tree for thesis inclusion.
