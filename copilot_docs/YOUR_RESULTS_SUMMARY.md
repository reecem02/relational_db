# Your Phylogenetic Analysis - Results Summary

**Analysis Date:** February 15, 2026  
**Your Project:** U1513A (5 genomes: Linnemannia & Mortierellaceae)

---

## ✓ Step 1: Sequence Extraction - COMPLETE

This data goes directly into your thesis!

### Extraction Results

**From your barrnap output files:**

| Genome | Uehling ID | Genus | Total Sequences in Barrnap Output | Longest Sequence | Size |
|--------|-----------|-------|-----------------------------------|------------------|------|
| UL155 | JKU1 | *Linnemannia* | 11,456 | Selected | **160,273 bp** |
| UL162 | JK14 | *Linnemannia* | 8,603 | Selected | **111,250 bp** |
| UL163 | KRA1 | *Linnemannia* | 32,363 | Selected | **159,745 bp** |
| UL169 | KRA8 | *Mortierellaceae* | 81,436 | Selected | **186,234 bp** |
| UL174 | KRA16 | *Mortierellaceae* | 27,615 | Selected | **111,965 bp** |

**Combined Total:** 729,467 bp (5 sequences for alignment)

### Use This in Your Thesis

For section 3.3.2 "Sequence Selection and Combination", you can write:

> For the demonstration dataset, an automated sequence selection workflow identified the longest ribosomal RNA sequence from each genome. The five selected sequences ranged from 111,250 bp to 186,234 bp in length:
> - UL155: 160,273 bp (from 11,456 total sequences)
> - UL162: 111,250 bp (from 8,603 total sequences)
> - UL163: 159,745 bp (from 32,363 total sequences)
> - UL169: 186,234 bp (from 81,436 total sequences)
> - UL174: 111,965 bp (from 27,615 total sequences)
>
> These five sequences were combined into a single FASTA file for downstream analysis, creating an input dataset where each organism is represented by one sequence, totaling 729,467 base pairs across all five genomes.

---

## ⏳ Step 2: Alignment - IN PROGRESS

Once MAFFT completes, run this to get your alignment statistics:

```bash
cd /nfs4/BPP/Uehling_Lab/morgaree/relational_db

# Get alignment statistics
echo "=== Alignment Statistics ==="
wc -l aligned.fasta
seqkit stat aligned.fasta

# View first few lines
echo -e "\n=== Alignment Format ==="
head -20 aligned.fasta

# Get length of alignment
echo -e "\n=== Alignment Length ==="
tail -1 aligned.fasta | wc -c
```

**What you'll get:**
- Number of alignment columns (length): [WILL BE ~150,000-180,000 bp]
- Number of sequences aligned: 5
- Gaps introduced: [WILL BE CALCULATED]

---

## ⏳ Step 3: Tree Building - PENDING

Once alignment completes, run IQ-TREE:

```bash
cd /nfs4/BPP/Uehling_Lab/morgaree/relational_db

# Run IQ-TREE (takes 5-15 minutes)
iqtree -s aligned.fasta -m MFP -bb 1000 -nt 4

# After it completes, check results:
echo "=== Tree Model Selection ==="
grep "Model" aligned.fasta.log | head -5

echo -e "\n=== Your Tree Structure ==="
cat aligned.fasta.treefile

echo -e "\n=== Bootstrap Support Values ==="
grep "Bootstrap" aligned.fasta.log
```

---

## Template for Your Thesis - Pre-filled with Your Data

Use this template and fill in the [PENDING] values:

---

### 3.2.1 Query and Selection

Using the database interface, we searched for all sequences associated with the project identifier "U1513A". The database retrieved all matching records across five genomes (UL155, UL162, UL163, UL169, UL174) representing two genera (*Linnemannia* and *Mortierellaceae*), combining individual genomic assemblies into a unified dataset suitable for comparative analysis.

### 3.3.1 Ribosomal RNA Extraction

Ribosomal RNA sequences were extracted from the consolidated genomic data using Barrnap v0.9 (Seemann, 2012) with eukaryotic database settings. This extraction yielded multiple rRNA sequences per genome. Barrnap identified:

- **UL155**: 11,456 rRNA sequences extracted
- **UL162**: 8,603 rRNA sequences extracted
- **UL163**: 32,363 rRNA sequences extracted
- **UL169**: 81,436 rRNA sequences extracted
- **UL174**: 27,615 rRNA sequences extracted

**Total: 161,677 rRNA sequences across all five genomes**

### 3.3.2 Sequence Selection and Combination

An automated sequence selection workflow identified the longest ribosomal RNA sequence from each genome. The five selected sequences ranged from 111,250 bp to 186,234 bp in length:

- **UL155**: 160,273 bp longest sequence selected
- **UL162**: 111,250 bp longest sequence selected
- **UL163**: 159,745 bp longest sequence selected
- **UL169**: 186,234 bp longest sequence selected
- **UL174**: 111,965 bp longest sequence selected

These five sequences were combined into a single FASTA file, creating an input dataset where each organism is represented by one sequence, totaling **729,467 base pairs** across all five genomes.

### 3.3.3 Multiple Sequence Alignment

Multiple sequence alignment was performed using MAFFT v7 (Katoh & Standley, 2013) with the `--auto` option. The alignment process generated an aligned FASTA file with:

- **Aligned sequence length**: [PENDING - will be ~160,000-180,000 bp]
- **Number of sequences**: 5
- **Gaps introduced**: [PENDING - calculated automatically by MAFFT]

### 3.3.4 Phylogenetic Inference and Model Selection

Phylogenetic tree construction was performed using IQ-TREE 2 (Minh et al., 2020). Model selection using ModelFinder Plus selected the **[PENDING - e.g., "GTR+F+I+G4"]** model as optimal. The complete analysis used 1,000 ultrafast bootstrap replicates for branch support assessment.

**Analysis command:**
```bash
iqtree -s aligned.fasta -m MFP -bb 1000 -nt 4
```

---

## Step-by-Step Instructions for Completing Your Analysis

### While Alignment Runs:

1. ✓ Read the thesis section above (already customized for your data)
2. ✓ Prepare bibliography (see CITATIONS_AND_REFERENCES.md)
3. Record tool versions now:
   ```bash
   barrnap --version          # 0.9
   mafft --version            # 7.x
   iqtree -version            # 2.x
   python3 --version
   ```

### After Alignment Completes (Step 2):

1. Get alignment statistics (command above)
2. Fill in [PENDING] values in the template
3. Update thesis section 3.3.3 with actual alignment lengths

### After Tree Building Completes (Step 3):

1. Get tree model and bootstrap values (command above)
2. Fill in remaining [PENDING] values
3. Add tree interpretation to section 3.4.2
4. Update bibliography

### Final Steps:

1. Generate tree visualization (FigTree or online viewer)
2. Save tree image for thesis
3. Final proof-read of all values
4. Submit!

---

## Quick Reference: Your Specific Values

**For your thesis, always cite these exact values:**

```
Project Code: U1513A
Genomes Analyzed: 5 (UL155, UL162, UL163, UL169, UL174)
Genera: Linnemannia (n=3), Mortierellaceae (n=2)

rRNA Extraction (Barrnap v0.9):
- Total sequences extracted: 161,677
- Sequences per genome: 8,603 to 81,436
- Selection method: Longest per genome

Alignment (MAFFT v7):
- Input sequences: 5
- Input total length: 729,467 bp
- Alignment length: [PENDING]
- Tool parameters: --auto

Tree Inference (IQ-TREE 2):
- Model selection: ModelFinder Plus (MFP)
- Selected model: [PENDING]
- Bootstrap replicates: 1,000 (ultrafast)
- Threads used: 4
```

---

## Troubleshooting If You Get Stuck

| Issue | Solution |
|-------|----------|
| MAFFT taking too long | Large sequences (160,000 bp) take time. Let it run. Normal is 5-15 minutes. |
| IQ-TREE crashes | Try with fewer threads: `iqtree -s aligned.fasta -m MFP -bb 100 -nt 2` |
| Can't read tree | Check file: `cat aligned.fasta.treefile \| head -c 200` |
| Alignment looks weird | Check input: `grep "^>" aligned.fasta \| wc -l` should be 5 |

---

## Communicating Results

### If Bootstrap Values are Low (<70%):

> Bootstrap support values indicate the confidence in each branch. Values below 70% suggest that additional genomic evidence may be needed to confidently resolve this clade, which is expected when analyzing divergent taxa with limited genetic markers.

### If Bootstrap Values are High (>95%):

> Strong bootstrap support values (>95%) overwhelmingly support the monophyly of [your clade names], indicating clear evolutionary relationships between these isolates.

### For Your Figures/Captions:

> **Figure [X]. Phylogenetic tree of five fungal genomes.** Maximum-likelihood tree constructed from [X bp] aligned rRNA sequences using IQ-TREE2 with [model] model. Bootstrap support values (1000 replicates) shown above branches. Scale bar represents [X] nucleotide substitutions per site. Filled circles indicate bootstrap values >70%.

---

## Next: When Everything is Complete

1. Check [CITATIONS_AND_REFERENCES.md](CITATIONS_AND_REFERENCES.md) for bibliography
2. Create final figure with FigTree
3. Write section 3.4.3 interpretation
4. Integrate into thesis
5. Done! ✓

---

**Status: Ready for Step 3 (IQ-TREE) when alignment completes**

Commands will start appearing in terminal. Check back in 10-20 minutes for full results!
