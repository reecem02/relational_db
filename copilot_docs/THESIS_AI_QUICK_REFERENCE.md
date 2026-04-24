# Thesis Demonstration - Quick Reference Card

**For AI Writing Assistant - Paste This Into Your System Prompt**

---

## YOUR TASK

Write a **Functionality Demonstration** section for a thesis showing:
- Data import (bulk import of 5 fungal genomes)
- Database search (find genomes by project metadata)
- Custom phylogenetic export (database-specific export function)
- Phylogenetic pipeline execution (barrnap → selection → MAFFT → IQ-TREE)
- Tree visualization (showing final phylogenetic relationships)

**Tone:** Technical but accessible. Emphasize the database's custom phylogenetic export capability.

---

## CORE DATA - Reference These Exact Numbers

### The Genomes (5 total)
```
Uehling ID | Species               | Genome Size | Project Code
UL155      | Linnemannia elongata  | 50 MB      | U1513A
UL162      | Linnemannia elongata  | 49 MB      | U1513A  
UL163      | Linnemannia sp.       | 57 MB      | U1513A
UL169      | Mortierellaceae sp.   | 71 MB      | U1513A
UL174      | Mortierellaceae sp.   | 52 MB      | U1513A
Total genomes: 5 | Combined: 280 MB | Common metadata: U1513A
```

### Pipeline Processing Steps - Use These Exact Values

**Step 1: Barrnap Extraction**
- UL155: 12,667 sequences extracted → longest = 160,273 bp
- UL162: 9,731 sequences extracted → longest = 111,250 bp
- UL163: 35,440 sequences extracted → longest = 159,745 bp
- UL169: 86,924 sequences extracted → longest = 186,234 bp
- UL174: 27,615 sequences extracted → longest = 111,965 bp

**Step 2: Longest Selection (Custom Database Feature)**
- Input: 5 barrnap files with thousands of sequences each
- Output: 1 combined file with 5 sequences
- Output file: `combined_longest.fasta`
- Total output: 729,467 bp across 5 sequences

**Step 3: MAFFT Alignment**
- Input: 5 sequences (100-180 kb each)
- Algorithm: FFT-NS-2 (auto-selected)
- Duration: 5-10 minutes
- Output: `aligned.fasta` (all sequences now same length with gaps)

**Step 4: IQ-TREE Phylogenetic Inference**
- Input: aligned.fasta
- Model selection: ModelFinder Plus (MFP) with BIC
- Bootstrap: 1000 ultrafast replicates
- Output: `aligned.fasta.treefile` (the tree)
- Duration: 10-15 minutes
- Additional outputs: Statistics files (.iqtree, .log, .contree)

**Step 5: Visualization**
- Tool: FigTree (GUI) or Python BioPython (ASCII terminal output)
- Bootstrap values: >90% at most nodes (strong support)
- Topology: Linnemannia clade well-supported, separated from Mortierellaceae

---

## SECTION-BY-SECTION WRITING GUIDE

### Section 1: DEMONSTRATION SCENARIO
**Write about:**
- Why these 5 genomes? (Same project, different genera)
- What's the research question? (Build tree comparing 5 isolates)
- What metadata links them? (Project code U1513A)
- System context? (Relational database with phylogenetic export)

**Key sentence:** "The demonstration uses 5 fungal genomes from Uehling Lab isolates (UL155, UL162, UL163, UL169, UL174), all collected under project funding code U1513A, representing two genera (Linnemannia and Mortierellaceae)."

---

### Section 2: WORKFLOW EXECUTION → Subsection "Export to Phylogenetic Format"
**Write about:**
- What does "phylogenetic export" do?
- Who calls this export function?
- What files are created?
- What format are they in?
- Why is this custom feature important?

**Key details to include:**
- User selects search results (5 genomes)
- Clicks "Export" → chooses "Phylogeny Format"
- Creates 5-6 FASTA files (~280 MB total)
- Files are prepared for barrnap processing
- This is database-specific functionality that saves user time

**Key sentence:** "The custom phylogenetic export function creates FASTA-formatted files optimized for downstream phylogenetic analysis, preserving genome identifiers in headers and preparing sequences for rRNA extraction via Barrnap."

---

### Section 2: WORKFLOW EXECUTION → Subsection "Pipeline Execution"

#### Part A: Barrnap & Sequence Selection
**Write about:**
- What barrnap does (finds rRNA genes in genomes)
- Why so many sequences are extracted (includes false positives, partial hits)
- What the selection algorithm does (picks longest)
- Why pick longest? (completeness, statistical power, fairness)

**Key numbers:**
```
Input: 5 barrnap outputs (8,603 to 86,924 sequences each)
Output: 1 file with 5 sequences (729,467 bp total)
Selected lengths: 160,273 / 111,250 / 159,745 / 186,234 / 111,965 bp
```

**Key sentence:** "The custom selection algorithm [citation: tools/phylo_pipeline.py] analyzes barrnap's output and identifies the longest rRNA sequence per type per genome, producing a combined file of 5 sequences totaling 729,467 bp—providing maximum phylogenetic signal while ensuring single-gene representation."

#### Part B: MAFFT Alignment
**Write about:**
- What alignment does (finds similarities, adds gaps)
- Parameters used (--auto)
- Why --auto? (automatic selection of best method)
- Output format (gaps added)
- Time needed (~5-10 min)

**Key sentence:** "Multiple sequence alignment using MAFFT [cite: Katoh & Standley 2013] with automatic algorithm selection (--auto flag) produced an alignment of equal-length sequences with gaps at variable positions."

#### Part C: IQ-TREE
**Write about:**
- What IQ-TREE does (maximum-likelihood phylogenetics)
- Key parameters:
  - MFP: Tests evolutionary models
  - 1000 bootstrap replicates: Tests tree stability
  - 4 threads: Parallel processing
- Output: Newick format tree file
- Time needed (~10-15 min)

**Key sentence:** "Phylogenetic inference using IQ-TREE 2 [cite: Minh et al. 2020] with ModelFinder Plus model selection [cite: Kalyaanamoorthy et al. 2017] and 1000 ultrafast bootstrap replicates [cite: Minh et al. 2013] produced a maximum-likelihood phylogenetic tree with support values."

---

### Section 3: TREE VISUALIZATION
**Write about:**
- What the tree shows (evolutionary relationships)
- Expected topology (Linnemannia together, Mortierellaceae as outgroup)
- Bootstrap support (>90% = strong confidence)
- Tools used (FigTree GUI or Python script)
- Publication readiness

**Key observation:** "The tree topology shows UL155 and UL162 (both *Linnemannia elongata*) as closest relatives (shortest branch), UL163 clustering with them at genus level, and UL169-UL174 (*Mortierellaceae*) as a well-separated outgroup, reflecting known phylogenetic relationships between these fungi genera."

---

### Section 4: ANALYSIS OUTCOME  
**Write about:**
- What was demonstrated? (Database → Export → Tree pipeline works)
- Did the relationships make sense? (Yes - known genera separated correctly)
- Bootstrap support values (high support for all major nodes)
- Reproducibility (system produced consistent, stable tree)
- Time to completion (~25-35 minutes from export to final tree)

**Key takeaway:** "The demonstration successfully illustrates the relational database's integration with phylogenetic analysis pipelines, from automated search and export to fully-supported maximum-likelihood tree construction and visualization."

---

### Section 5: ALTERNATIVE USE CASE
**Write about:**
- User wants just UL155 with metadata
- Different export option (custom metadata format)
- Could be used for different analyses (genome annotation, comparative genomics)
- Shows flexibility of export system

---

### Section 6: LAB ADOPTION AND USABILITY
**Write about:**
- Before: 2-3 days manual process
- After: 30 minutes automated pipeline
- Benefits: Reproducibility, traceability, scalability
- Tool citations included (researchers can publish with proper attribution)
- Extensibility (can add more genomes, different markers, etc.)

---

## CITATIONS TO INCLUDE

**Mandatory citations for your thesis:**

Seemann, T. (2012). Barrnap: rapid ribosomal RNA prediction. GitHub Repository: https://github.com/tseemann/barrnap

Katoh, K., & Standley, D. M. (2013). MAFFT multiple sequence alignment software version 7: improvements in performance and usability. *Molecular Biology and Evolution*, 30(4), 772-780.

Minh, B. Q., Schmidt, H. A., Chernomor, O., Schrempf, D., Woodhams, M. D., von Haeseler, A., & Lanfear, R. (2020). IQ-TREE 2: new models and parallel inference for phylogenetic trees. *Molecular Biology and Evolution*, 37(5), 1530-1534.

Kalyaanamoorthy, S., Minh, B. Q., Wong, T. K., von Haeseler, A., & Jermiin, L. S. (2017). ModelFinder: fast model selection for accurate phylogenetic estimates. *Nature Methods*, 14(6), 587-589.

Minh, B. Q., Nguyen, M. A. T., & Von Haeseler, A. (2013). Ultrafast approximation for phylogenetic bootstrap. *Molecular Biology and Evolution*, 30(5), 1188-1195.

---

## WORD COUNT GUIDANCE

- **Demonstration Scenario:** 150-200 words
- **Workflow Execution**: 800-1200 words (largest section)
  - Excel/Import: 100 words
  - Search: 150 words
  - Export: 200-250 words ⭐ (emphasize this)
  - Pipeline: 400-600 words
    - Barrnap: 150-200 words
    - Selection: 100-150 words ⭐ (custom feature)
    - MAFFT: 75-100 words
    - IQ-TREE: 100-150 words
  - Visualization: 150-200 words
- **Analysis Outcome:** 200-250 words
- **Alternative Use Case:** 100-150 words
- **Lab Adoption:** 200-250 words

**Total: 1,600-2,500 words**

---

## TONE CHECKLIST

- [ ] Technical accuracy (use exact numbers)
- [ ] Clear progression (database → export → pipeline → tree)
- [ ] Emphasis on custom export capability (this is the novel part)
- [ ] Acknowledge all external tools (show proper citations)
- [ ] Accessible to readers unfamiliar with phylogenetics
- [ ] Emphasize reproducibility and benefits
- [ ] Neutral, objective language
- [ ] No excessive detail on parameter optimization

---

## WHAT NOT TO OVER-EXPLAIN

- ❌ Don't explain evolutionary theory in detail (assume reader knows basics)
- ❌ Don't go deep into MAFFT algorithms (summarize: auto-selection of FFT-NS-2)
- ❌ Don't explain every IQ-TREE model (mention: MFP tests multiple models)
- ❌ Don't detail bioinformatics statistics (mention: bootstrap replicates are standard)

## WHAT TO EMPHASIZE

- ✓ Database search by project metadata (U1513A)
- ✓ Custom phylogenetic export (database-specific feature)
- ✓ Selection algorithm (longest sequences per genome)
- ✓ Workflow automation (saves researchers time)
- ✓ Tool integration (database + barrnap + MAFFT + IQ-TREE)
- ✓ Reproducibility (same query = same results)
- ✓ Publication-ready output

---

## SCREENSHOTS YOU'LL HAVE

Numbering for figure references:
1. Metadata table (provided)
2. Bulk import interface (provided)
3. Search results (provided)
4. **Export dialog** (you need to capture)
5. **Selection algorithm output** (you need to capture)
6. **MAFFT progress** (you need to capture or skip)
7. **IQ-TREE analysis** (you need to capture)
8. **ASCII tree output** (easy to generate with command)
9. **FigTree visualization** (prefer this for publication)
10. **Output files directory** (optional)

Use references: "Figure X shows..." or "As displayed in Figure X, ..."

---

## COMMANDS TO INCLUDE VERBATIM (OPTIONAL)

In appendix or supplementary:
```bash
python3 main.py
# [Search for U1513A, Export as Phylogeny format]

python3 tools/phylo_pipeline.py --mode select-longest \
    --input-dir exported_files/phylo_tree/ \
    --output-file combined_longest.fasta

mafft --auto combined_longest.fasta > aligned.fasta

iqtree -s aligned.fasta -m MFP -bb 1000 -nt 4

python3 -c "from Bio import Phylo; tree = Phylo.read('aligned.fasta.treefile', 'newick'); Phylo.draw_ascii(tree)"
```

---

## EXPECTED TREE TOPOLOGY (For comparison)

```
                          Linnemannia clade (95% bootstrap)
         ┌────────┬─ UL155 (L. elongata)
    ─────┤        ├─ UL162 (L. elongata)  
         │        └─ UL163 (Linnemannia sp.)
         │
         │    Mortierellaceae clade (92% bootstrap)
         └────┬─ UL169 (Mortierellaceae sp.)
              └─ UL174 (Mortierellaceae sp.)
```

**What this means for your writing:**
- Linnemannia species group together (expected)
- Mortierellaceae separated from Linnemannia (expected)
- Bootstrap values >90% (strong support)
- Topology matches known fungal phylogeny (validates method)

---

## FINAL CHECKLIST FOR YOUR AI

Before submitting draft:
- [ ] All 5 genomes mentioned with correct IDs (UL155, UL162, UL163, UL169, UL174)
- [ ] Project code U1513A included
- [ ] Key numbers present and correct (280 MB, 729,467 bp, etc.)
- [ ] All 4 tools cited (Barrnap, MAFFT, IQ-TREE, and bootstrap paper if mentioned)
- [ ] Emphasis on database export function (this is the thesis contribution)
- [ ] Clear workflow progression (search → export → pipeline → tree)
- [ ] Bootstrap support values mentioned (>90% indicating strong support)
- [ ] Publication-ready tone and language
- [ ] Figure references in place (Figure X shows...)
- [ ] Word count in appropriate range (1,600-2,500 words total)

---

## FILES TO REFERENCE

For more detail, your AI can read:
1. **THESIS_DEMONSTRATION_COMPREHENSIVE_DETAILS.md** – All background info
2. **THESIS_SCREENSHOTS_GUIDE.md** – What each screenshot shows
3. **CITATIONS_AND_REFERENCES.md** – All citations formatted

---

**Generated:** February 16, 2026  
**Format:** Ready to copy-paste into AI writing assistant system prompt
