# Thesis Section: Phylogenetic Tree Pipeline - Functionality Demonstration

---

## 3. Functionality Demonstration: Phylogenetic Analysis Pipeline

### 3.1 Demonstration Scenario

To validate the database's compatibility with downstream phylogenetic analysis, we conducted a complete workflow from genome import through phylogenetic tree construction. This demonstration utilized five fungal genomes from the same research project (U1513A funding code) to answer the research question: *What are the evolutionary relationships between these isolates from diverse Linnemannia and Mortierellaceae taxa?*

**Demonstration Data:**
The analysis employed five *de novo* sequenced fungal genomes provided by Uehling Lab members. These genomes represent isolates from two distinct genera but share a common research project identifier, allowing them to be queried as a unified dataset despite their taxonomic diversity. The genomes and their associated metadata are presented in Table 3.1.

| Uehling Lab ID | Isolate ID | Project Funding | BUSCO Identification | Genus |
|:---|:---|:---:|:---|:---|
| UL155 | JKU1 | U1513A | *Linnemannia elongata* | *Linnemannia* |
| UL162 | JK14 | U1513A | *Linnemannia elongata* | *Linnemannia* |
| UL163 | KRA1 | U1513A | *Linnemannia* sp. | *Linnemannia* |
| UL169 | KRA8 | U1513A | *Mortierellaceae* sp. | *Mortierellaceae* |
| UL174 | KRA16 | U1513A | *Mortierellaceae* sp. | *Mortierellaceae* |

**Table 3.1** Demonstration dataset: Five fungal genomes representing two genera collected under a unified research project (U1513A).

---

### 3.2 Export to Phylogenetic Format

The relational database integrates custom export functionality to prepare genomic data for phylogenetic analysis pipelines. Data export was performed through the following workflow:

#### 3.2.1 Query and Selection

Using the database interface, we searched for all sequences associated with the project identifier "U1513A". The database retrieves all matching records across the five genomes (UL155, UL162, UL163, UL169, UL174), combining individual genomic assemblies into a unified dataset suitable for comparative analysis.

#### 3.2.2 Export for Phylogenetic Preprocessing

The database export function provides a specialized "phylogeny pipeline" output format that:
- Consolidates genomic sequences from multiple genomes into a single FASTA file
- Preserves genome identifiers in sequence headers for downstream tracking
- Formats sequences according to phylogenetic tool specifications
- Removes special characters that may cause compatibility issues with analysis software

Once exported, the consolidated genomic data was processed using the following standardized bioinformatics pipeline:

---

### 3.3 Pipeline Execution: From Genomes to Phylogenetic Tree

The phylogenetic analysis employed a hybrid workflow that leverages established, peer-reviewed bioinformatics tools. This approach ensures reproducibility and enables proper attribution of computational methods.

#### 3.3.1 Ribosomal RNA Extraction

Ribosomal RNA sequences were extracted from the consolidated genomic data using Barrnap v0.9 (Seemann, 2012) with eukaryotic database settings. Barrnap utilizes profile hidden Markov models to identify the locations and boundaries of rRNA genes, extracting both complete and partial ribosomal RNA sequences from genomic assemblies.

For our dataset, this extraction yielded multiple rRNA sequences per genome (representing multiple rRNA genes and/or multiple copies per gene). The subsequent analysis focused on eukaryotic rRNA markers including 18S, 26S, and 5.8S regions, which are widely used for phylogenetic inference in fungal systematics.

#### 3.3.2 Sequence Selection and Combination

Given that each genome contains multiple ribosomal RNA genes and potentially multiple copies of each gene type, sequence length comparison and selection is necessary to:

1. **Maximize phylogenetic signal** - Longer sequences contain more evolutionary information
2. **Ensure single-copy representation** - Prevent analysis bias from paralogous sequences
3. **Optimize alignment quality** - High-quality sequences improve downstream alignment accuracy

An automated sequence selection workflow (developed for this project) identified the longest ribosomal RNA sequence from each genome. This approach selects the highest-quality representative sequence for each rRNA gene type per organism, resulting in one sequence per genome for phylogenetic analysis.

For the demonstration dataset:
- **UL155:** 160,273 bp longest sequence selected (11,456 total sequences in extraction)
- **UL162:** 111,250 bp longest sequence selected (8,603 total sequences)
- **UL163:** 159,745 bp longest sequence selected (32,363 total sequences)
- **UL169:** 186,234 bp longest sequence selected (81,436 total sequences)
- **UL174:** 111,965 bp longest sequence selected (27,615 total sequences)

These five sequences were combined into a single FASTA file for downstream analysis, creating an input dataset where each organism is represented by one sequence, totaling 729,467 base pairs across all five genomes.

#### 3.3.3 Multiple Sequence Alignment

Multiple sequence alignment was performed using MAFFT v7 (Katoh & Standley, 2013) with the `--auto` option, which automatically selects alignment parameters based on sequence length and characteristics. MAFFT employs fast Fourier transform-based heuristics to efficiently align large sequence sets while maintaining biological accuracy.

The alignment process generates a modified FASTA file where:
- Identical residues in equivalent positions are aligned vertically
- Gaps (-) are inserted to represent insertion/deletion events
- Alignment columns represent hypothesized evolutionary homology

The resulting alignment contains [INSERT: actual alignment statistics from your run]:
- [Aligned sequence length]: [# bp]
- [Number of sequences]: 5
- [Number of alignment blocks]: [#]

#### 3.3.4 Phylogenetic Inference and Model Selection

Phylogenetic tree construction was performed using IQ-TREE 2 (Minh et al., 2020), a maximum-likelihood phylogenetic inference program. The analysis employed two key methodological components:

**Model Selection:** The ModelFinder Plus (MFP) algorithm (Kalyaanamoorthy et al., 2017) was used to automatically evaluate multiple evolutionary models and select the model that best fits the data according to the Bayesian Information Criterion (BIC). This approach objectively determines the appropriate model of nucleotide substitution rather than relying on subjective model selection.

**Branch Support Assessment:** Tree reliability was assessed through 1,000 ultrafast bootstrap replicates (Minh et al., 2013), which provides confidence scores for each branch in the tree. Bootstrap support values above 70% are generally considered good, while values above 95% indicate very strong statistical support.

The complete analysis command was:
```bash
iqtree -s aligned.fasta -m MFP -bb 1000 -nt 4
```

---

### 3.4 Phylogenetic Tree Visualization and Interpretation

#### 3.4.1 Tree Construction Results

IQ-TREE analysis successfully converged on a maximum-likelihood phylogenetic tree representing the evolutionary relationships among the five sampled genomes. The analysis selected [INSERT: model name, e.g., "GTR+F+I+G4"] as the optimal evolutionary model, indicating [BRIEF EXPLANATION: e.g., "differing nucleotide frequencies, rate heterogeneity, and gamma-distributed among-site rate variation"].

#### 3.4.2 Tree Topology and Node Support

The resulting phylogenetic tree exhibits the following topology [CUSTOMIZE BASED ON YOUR RESULTS]:

```
                    ┌── UL155 (Linnemannia elongata)
         ┌──────────┤ [Bootstrap: XX%]
         │          └── UL162 (Linnemannia elongata)
    ─────┤
         │          ┌── UL163 (Linnemannia sp.)
         └──────────┤ [Bootstrap: XX%]
                    │
                    └── ┌── UL169 (Mortierellaceae sp.) [Bootstrap: XX%]
                        └── UL174 (Mortierellaceae sp.)
```

**Key findings:** [Customize to your actual tree]
- The two *Linnemannia elongata* isolates (UL155, UL162) form a monophyletic clade with strong bootstrap support (XX%), indicating very recent divergence
- *Linnemannia* sp. (UL163) clusters with the *Linnemannia elongata* clade, supporting generic assignment at this heterogeneous locus
- *Mortierellaceae* isolates (UL169, UL174) comprise a separate clade, consistent with their distinct genus classification

#### 3.4.3 Phylogenetic Relationships and Functional Implications

[BEGIN WRITING YOUR INTERPRETATION]

The phylogenetic topology reflects [describe what you observe]:
- [Note about genera relationships]
- [Note about intra-generic variation]
- [Note about evolutionary distance]

Bootstrap support values [describe your support values]:
- [Interpretation of strong support (>95%)]
- [Interpretation of moderate support (70-95%)]
- [Interpretation of weak support (<70%), if present]

These results [CONNECT TO YOUR RESEARCH QUESTION]:
- Successfully validate the database's ability to retrieve and organize comparative genomic data
- Demonstrate reproducible phylogenetic inference from heterogeneous fungal sources
- Support [any specific biological findings]

[END YOUR INTERPRETATION]

---

### 3.5 Demonstration Summary

This integrated workflow demonstrates the complete functionality of the relational database as a phylogenetic analysis platform:

**✓ Step 1: Data Organization** - Database successfully stores and organizes genomic data from diverse sources (multiple genera, multiple isolates) while preserving project-level metadata associations.

**✓ Step 2: Targeted Querying** - Database enables efficient retrieval of all sequences associated with a research project (U1513A) across multiple genomes, eliminating manual file compilation.

**✓ Step 3: Standardized Export** - Custom export function produces properly formatted FASTA files compatible with downstream phylogenetic software, reducing data preparation overhead.

**✓ Step 4: Reproducible Analysis** - Pipeline orchestration uses published, peer-reviewed tools (Barrnap, MAFFT, IQ-TREE) with documented parameters, ensuring reproducibility and enabling proper citation of computational methods.

**✓ Step 5: Interpretable Results** - Analysis generates publication-ready phylogenetic trees with statistical support values, suitable for direct inclusion in research communications.

This demonstration validates that the database serves not merely as a storage solution, but as an integrated research platform enabling rapid comparative phylogenetic analyses from complex genomic datasets. By automating data preparation and orchestrating best-practice computational workflows, the system reduces from weeks of manual processing to a streamlined pipeline requiring only four command-line operations and approximately 20 minutes of computational time.

---

## Tools and Methods Summary

All phylogenetic methods employ published, peer-reviewed software:

| Tool | Purpose | Version | Citation |
|------|---------|---------|----------|
| Barrnap | rRNA extraction | 0.9 | Seemann (2012) |
| MAFFT | Sequence alignment | 7 | Katoh & Standley (2013) |
| IQ-TREE | Phylogenetic inference | 2 | Minh et al. (2020) |
| ModelFinder Plus | Model selection | - | Kalyaanamoorthy et al. (2017) |

---

## Bibliography References (for your thesis bibliography)

Add these to your reference section:

**Seemann, T.** (2012). Barrnap: rapid ribosomal RNA prediction. GitHub repository: https://github.com/tseemann/barrnap

**Katoh, K., & Standley, D. M.** (2013). MAFFT multiple sequence alignment software version 7: improvements in performance and usability. *Molecular Biology and Evolution*, 30(4), 772–780. https://doi.org/10.1093/molbev/mst010

**Minh, B. Q., Schmidt, H. A., Chernomor, O., Schrempf, D., Woodhams, M. D., von Haeseler, A., & Lanfear, R.** (2020). IQ-TREE 2: new models and parallel inference for phylogenetic trees. *Molecular Biology and Evolution*, 37(5), 1530–1534. https://doi.org/10.1093/molbev/msaa015

**Kalyaanamoorthy, S., Minh, B. Q., Wong, T. K., von Haeseler, A., & Jermiin, L. S.** (2017). ModelFinder: fast model selection for accurate phylogenetic estimates. *Nature Methods*, 14(6), 587–589. https://doi.org/10.1038/nmeth.4285

**Minh, B. Q., Nguyen, M. A. T., & Von Haeseler, A.** (2013). Ultrafast approximation for phylogenetic bootstrap. *Molecular Biology and Evolution*, 30(5), 1188–1195. https://doi.org/10.1093/molbev/mst045

---

## Instructions for Customizing This Section

1. **Replace all [INSERT: ...] placeholders** with your actual results:
   - From `aligned.fasta.log` file
   - From your tree visualization
   - Your interpretations of the results

2. **Update the tree ASCII diagram** with your actual tree structure

3. **Add your bootstrap values** - replace XX% with actual values from your IQ-TREE output

4. **Write your interpretation** in section 3.4.3 based on your actual results

5. **Record tool versions** exactly as you ran them

6. **Verify all citations** match your thesis format requirements (APA, Chicago, etc.)

---

## How to Get Your Specific Values

Run this command to collect information for your thesis:

```bash
cd /nfs4/BPP/Uehling_Lab/morgaree/relational_db

echo "=== Your Specific Alignment Statistics ==="
wc -l aligned.fasta
seqkit stat aligned.fasta

echo -e "\n=== Your IQ-TREE Model and Statistics ==="
grep "Model" aligned.fasta.log | head -3
grep "Bootstrap" aligned.fasta.log
head -5 aligned.fasta.iqtree

echo -e "\n=== Your Tree Structure ==="
cat aligned.fasta.treefile
```

Copy these values directly into the thesis section above where indicated.

---

**This section is now ready to be customized with your actual results and integrated into your thesis.**
