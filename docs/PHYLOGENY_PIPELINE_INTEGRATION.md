# Phylogeny Pipeline Integration Guide

This guide covers how to move from a database query to a whole-genome similarity tree using the built-in FASTA export and the Sourmash workflow.

Source repository for the Sourmash workflow: https://github.com/haydenjohnson94/WholeGenomeSimilarityTree

---

## Overview

The pipeline has two stages:

1. **Database → FASTA export** (handled by this program)
2. **FASTA → similarity tree** (handled by Sourmash, in `WholeGenomeSimilarityTree/`)

---

## One-Time Setup (First Use Only)

1. Clone the Sourmash workflow repo:
   ```bash
   git clone https://github.com/haydenjohnson94/WholeGenomeSimilarityTree
   ```

2. Open `SourmashTreeWorkflow_FromAssemblyDirectory.ipynb` and update the `BASE_DIR` variable to match where you cloned the repo on your system:
   ```python
   BASE_DIR = Path("/your/path/to/WholeGenomeSimilarityTree")
   ```
   All subdirectories (`Assemblies/`, `SourmashSignatures/`, `SourmashTrees/`) are derived from this path automatically.

---

## Stage 1: Export Genomes from the Database

Run the program and use the **Search** menu to query the genomes you want.

When prompted to export:
- Choose format **[4] FASTA**
- If your query returned multiple Uehling IDs, the program will automatically create one `.fasta` file per genome in a folder of your choice
- Export destination: `exported_files/<your_folder_name>/`

Each file will be named `{LAB_ID}.fasta` (e.g., `UL155.fasta`).

Copy or move the exported `.fasta` files into the `Assemblies/` directory inside the Sourmash repo.

---

## Stage 2: Build the Similarity Tree with Sourmash

From the `WholeGenomeSimilarityTree/` directory, submit the SLURM job:

```bash
cd /your/path/to/WholeGenomeSimilarityTree
sbatch Run_Jupyter_Sourmash.sh
```

The notebook will run automatically and:
1. Compute Sourmash signatures for each genome in `Assemblies/`
2. Compute pairwise similarity across all genomes
3. Plot and save a similarity tree as a `.png` file in `SourmashTrees/`

---

## Expected Output

| Path | Contents |
|---|---|
| `WholeGenomeSimilarityTree/SourmashSignatures/` | Per-genome Sourmash signature files |
| `WholeGenomeSimilarityTree/SourmashTrees/` | Similarity tree `.png` |

---

## Troubleshooting

| Issue | Fix |
|---|---|
| No FASTA files exported | Confirm your search returned results with genomic data attached |
| `BASE_DIR` error in notebook | Ensure `BASE_DIR` in the notebook matches your actual repo path |
| SLURM job fails | Check the log: `run_notebook_Sourmash.<job_id>.out` in the repo directory |
| Sourmash not found | Ensure Sourmash is installed and on your PATH (`sourmash --version`) |
| Empty `SourmashTrees/` | Verify `.fasta` files are present and non-empty in `Assemblies/` before running |
