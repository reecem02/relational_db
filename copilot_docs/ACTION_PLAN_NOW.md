# What To Do Now - Your Thesis Pipeline Action Plan

**Status:** Your alignment is running on the server  
**Date:** February 15, 2026  
**Your Project:** U1513A (5 genomes for phylogenetic tree)

---

## 🎯 What Just Happened

You've successfully completed **Step 1: Sequence Selection**

✅ **Done:**
- 5 genomes queried from database (UL155, UL162, UL163, UL169, UL174)
- 161,677 rRNA sequences analyzed
- 5 longest sequences selected (729,467 bp total)
- Combined into `combined_longest.fasta`

⏳ **Currently Running:**
- MAFFT aligning those 5 sequences (takes 10-20 minutes for large files)

---

## 📋 What To Do RIGHT NOW (5 minutes)

### 1. Review Your Thesis Section

Open and read: **[THESIS_SECTION_PHYLO_ANALYSIS.md](THESIS_SECTION_PHYLO_ANALYSIS.md)**

This is your complete thesis section with:
- All your specific data values already filled in
- Section 3.1-3.4 ready for customization
- Placeholder sections marked with [PENDINGINSERT instructions

**Key sections for your thesis:**
- 3.1: Demonstration scenario (✓ already done with your data)
- 3.2.1: Export to phylogenetic format (✓ already done)
- 3.3.1-3.3.2: rRNA extraction & selection (✓ already done - values filled in)
- 3.3.3: Alignment (⏳ waiting for MAFFT - you'll fill in actual stats)
- 3.3.4: Tree inference (⏳ waiting for IQ-TREE)
- 3.4: Results & interpretation (you'll write after seeing tree)

### 2. Gather Your Citations

Open: **[CITATIONS_AND_REFERENCES.md](CITATIONS_AND_REFERENCES.md)**

Copy the BibTeX entries into your thesis bibliography file now:
```bibtex
@article{Seemann2012,
  ...
}
@article{Katoh2013,
  ...
}
@article{Minh2020,
  ...
}
```

### 3. Keep This Summary Handy

Open: **[YOUR_RESULTS_SUMMARY.md](YOUR_RESULTS_SUMMARY.md)**

This has:
- All your specific values (729,467 bp, sequence counts, etc.)
- Templates with values pre-filled
- Commands to run next
- Troubleshooting guide

---

## ⏳ What To Do WHILE ALIGNMENT RUNS (Now, but doesn't require active work)

### Option A: Prepare Your Thesis Document

In your thesis editor (Word/LaTeX/etc):

1. Create section starting with:
   ```
   ### 3. Functionality Demonstration: Phylogenetic Analysis Pipeline
   ```

2. Copy from [THESIS_SECTION_PHYLO_ANALYSIS.md](THESIS_SECTION_PHYLO_ANALYSIS.md):
   - Section 3.1 (your demonstration scenario)
   - Section 3.2 (export to phylo format)
   - Section 3.3.1-3.3.2 (extraction & selection) - ALREADY HAS YOUR VALUES

3. Leave blank sections for:
   - 3.3.3 (alignment stats) - waiting for `aligned.fasta`
   - 3.3.4 (tree model) - waiting for IQ-TREE output
   - 3.4 (results) - waiting for tree visualization

### Option B: Set Up Bibliography

In your thesis, create bibliography entries:
```bibtex
@article{Seemann2012,
  author = {Seemann, Torsten},
  title = {Barrnap: rapid ribosomal RNA prediction},
  url = {https://github.com/tseemann/barrnap},
  year = {2012}
}

@article{Katoh2013,
  author = {Katoh, Kazutaka and Standley, David M},
  journal = {Molecular Biology and Evolution},
  volume = {30},
  number = {4},
  pages = {772--780},
  title = {MAFFT multiple sequence alignment software version 7},
  year = {2013}
}

@article{Minh2020,
  author = {Minh, Bui Quang and others},
  journal = {Molecular Biology and Evolution},
  volume = {37},
  number = {5},
  pages = {1530--1534},
  title = {IQ-TREE 2: new models and parallel inference for phylogenetic trees},
  year = {2020}
}
```

---

## ✅ What To Do WHEN ALIGNMENT COMPLETES (30 mins from now)

Check your terminal. You'll see alignment statistics. Then run:

```bash
cd /nfs4/BPP/Uehling_Lab/morgaree/relational_db

# Get exact alignment statistics
echo "=== Your Alignment ==="
seqkit stat aligned.fasta
wc -l aligned.fasta

# Copy alignment length (number of bp)
# Update YOUR_RESULTS_SUMMARY.md with this value
```

**Then fill in section 3.3.3 of your thesis:**

> Multiple sequence alignment was performed using MAFFT v7 (Katoh & Standley, 2013) with the `--auto` option. The alignment process generated an aligned FASTA file with:
> 
> - Aligned sequence length: **[YOUR VALUE FROM SEQKIT] bp**
> - Number of sequences: 5
> - Gaps introduced: [automatic, will see in alignment]

---

## ✅ What To Do WHEN IQ-TREE COMPLETES (20 mins after alignment finishes)

Total runtime: ~35-40 minutes from now

Run:
```bash
cd /nfs4/BPP/Uehling_Lab/morgaree/relational_db

# Check your tree model
echo "=== Your Selected Model ==="
grep "Model" aligned.fasta.log | head -1

# Check your tree structure
echo -e "\n=== Your Tree ==="
cat aligned.fasta.treefile

# Get bootstrap support info
echo -e "\n=== Bootstrap Assessment ==="
grep -i "bootstrap" aligned.fasta.log | head -3
```

**Then fill in section 3.3.4 of your thesis:**

The command output will tell you:
- Selected model (e.g., "GTR+F+G4")
- Your tree structure (copy exactly)
- Bootstrap values (e.g., "1000 ultrafast bootstrap replicates")

---

## 🎨 What To Do WITH YOUR TREE (After TQ-TREE)

### View as ASCII Art:
```bash
python3 -c "
from Bio import Phylo
tree = Phylo.read('aligned.fasta.treefile', 'newick')
Phylo.draw_ascii(tree)
"
```

Copy this output into your thesis section 3.4.2 as your tree topology diagram.

### Create Professional Figure (FigTree):

1. Download FigTree: http://tree.bio.ed.ac.uk/software/figtree/
2. Open: `aligned.fasta.treefile`
3. Customize:
   - Enable bootstrap values (right-click nodes)
   - Set branch scaling
   - Color by genus
   - Export as PDF/PNG

4. Insert into thesis as **Figure X. Phylogenetic tree...**

### Online Viewer (No Download):
- Copy content of `aligned.fasta.treefile`
- Paste at: http://iqtree.cibiv.univie.ac.at/treeviewer/
- Screenshot for thesis if needed

---

## 📝 Complete Your Thesis (Final Step)

After you have tree, fill in section **3.4.2 Tree Topology and Node Support**:

Example writing (customize for your results):

> The phylogenetic tree reveals [YOUR OBSERVATIONS]:
> 
> - **Linnemannia clade**: The three *Linnemannia* isolates (UL155, UL162, UL163) form a monophyletic clade with bootstrap support of [YOUR VALUE]%, indicating [close/moderate/distant] evolutionary relationships within this genus.
>
> - **Mortierellaceae separation**: *Mortierellaceae* isolates (UL169, UL174) cluster separately from *Linnemannia*, with bootstrap support of [YOUR VALUE]%, consistent with their distinct genus classification.
>
> - **Overall tree structure**: The phylogeny demonstrates clear primary divergence between the two genera, with [additional observations based on your tree].

---

## 🚀 Timeline Summary

| Time | Task | Command | Output |
|------|------|---------|--------|
| Now | Read thesis template | - | Read [THESIS_SECTION_PHYLO_ANALYSIS.md](THESIS_SECTION_PHYLO_ANALYSIS.md) |
| Now | Gather citations | - | Copy from [CITATIONS_AND_REFERENCES.md](CITATIONS_AND_REFERENCES.md) |
| ~15 min | ⏳ MAFFT running | (automatic) | `aligned.fasta` |
| ~20 min | Get alignment stats | `seqkit stat aligned.fasta` | Fill section 3.3.3 |
| ~35 min | ⏳ IQ-TREE running | (automatic) | Tree files |
| ~40 min | Get tree results | `grep "Model" aligned.fasta.log` | Fill section 3.3.4 |
| ~45 min | Visualize tree | FigTree or Python | ASCII diagram for thesis |
| ~60 min | Write results | Manual | Complete section 3.4 |
| **~90 min** | **✓ DONE** | Submit | **Complete thesis section** |

---

## Files You Should Understand

| File | Purpose |
|------|---------|
| [THESIS_SECTION_PHYLO_ANALYSIS.md](THESIS_SECTION_PHYLO_ANALYSIS.md) | Your complete thesis section (READ THIS FIRST) |
| [YOUR_RESULTS_SUMMARY.md](YOUR_RESULTS_SUMMARY.md) | Your specific values & templates |
| [WORKFLOW_TUTORIAL_EXECUTABLE.md](WORKFLOW_TUTORIAL_EXECUTABLE.md) | Step-by-step commands |
| [CITATIONS_AND_REFERENCES.md](CITATIONS_AND_REFERENCES.md) | Bibliography entries |

---

## Checklist: You Should Have

✅ Step 1 complete: 5 longest sequences selected (**229,467 bp**)  
✅ Combined file ready: `combined_longest.fasta`  
⏳ Step 2 running: MAFFT alignment  
⏳ Step 3 pending: IQ-TREE tree building  
✅ Thesis section template ready: [THESIS_SECTION_PHYLO_ANALYSIS.md](THESIS_SECTION_PHYLO_ANALYSIS.md)  
✅ Your data values documented: [YOUR_RESULTS_SUMMARY.md](YOUR_RESULTS_SUMMARY.md)  
✅ Bibliography sources: [CITATIONS_AND_REFERENCES.md](CITATIONS_AND_REFERENCES.md)  

---

## Pro Tips for Your Thesis

### Tip 1: Data Table
Include a table of your 5 genomes with metadata (already in [THESIS_SECTION_PHYLO_ANALYSIS.md](THESIS_SECTION_PHYLO_ANALYSIS.md))

### Tip 2: Sequence Statistics
Report exact numbers from your analysis:
- Total sequences extracted: 161,677
- Longest sequences selected: 5
- Total bp for alignment: 729,467
- Alignment length: [PENDING]

### Tip 3: Methods Section
Copy the reproducible methods template from [CITATIONS_AND_REFERENCES.md](CITATIONS_AND_REFERENCES.md)

### Tip 4: Figure Caption
Use this template for your tree figure:

> **Figure X. Phylogenetic tree of five fungal genomes.** Maximum-likelihood tree inferred from rRNA sequences using IQ-TREE 2 with [MODEL] model. Values above branches indicate bootstrap support from 1,000 ultrafast bootstrap replicates. Scale bar represents 0.01 substitutions per site. Genomes are colored by genus: *Linnemannia* (orange), *Mortierellaceae* (blue).

---

## Questions?

- **How do I know if alignment completed?** Check: `ls -lh aligned.fasta` if >100MB, it's done
- **Is tree still running?** Check: `ps aux | grep iqtree`
- **Can I stop and restart?** Yes, just re-run the command
- **Do I need FigTree?** No, ASCII tree works for thesis, but FigTree makes nicer figures

---

## You're Ready!

```
✓ Pipeline is executing
✓ Thesis section template is prepared  
✓ Your data is documented
✓ Bibliography is ready
✓ Instructions are clear

```

### Next Action:
1. Open [THESIS_SECTION_PHYLO_ANALYSIS.md](THESIS_SECTION_PHYLO_ANALYSIS.md) ← **READ NOW**
2. Check back in ~30 minutes for alignment results
3. Check back in ~45 minutes for tree results
4. Use templates to fill in your values

**Estimated completion: 90 minutes total** 🎯

---

Generated February 15, 2026  
Ready for integration into your thesis
