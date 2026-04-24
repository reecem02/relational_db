# Phylogenetic Tree Generation Workflow: From Database Import to Phylogenetic Analysis

## Executive Summary

This document describes a comprehensive bioinformatics pipeline that integrates genomic data management with phylogenetic analysis. The system consists of two main components:

1. **Relational Database Module** (`relational_db/`): Accepts, organizes, and manages genomic metadata and sequence data
2. **Phylogenetic Analysis Module** (`WholeGenomeSimilarityTree/`): Generates phylogenetic trees using Sourmash-based whole-genome similarity analysis

---

## System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                     INPUT DATA SOURCES                            │
├──────────────────────────────────────────────────────────────────┤
│  • Excel metadata files (lab IDs, sample info, collection data) │
│  • FASTA genome assemblies (whole genomes or sequences)          │
│  • File paths or direct FASTA uploads                             │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│              RELATIONAL DATABASE IMPORT LAYER                     │
├──────────────────────────────────────────────────────────────────┤
│  SQLite Database with 3 Tables:                                  │
│  • Metadata: key-value pairs (lab_id, species, location, etc.)  │
│  • GenomicData: sequences (lab_id, sequence_header, sequence)   │
│  • Maintains 1:N relationships (1 lab_id → multiple sequences)   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                    SEARCH & EXPORT LAYER                          │
├──────────────────────────────────────────────────────────────────┤
│  • Query database for specific genomes or metadata criteria      │
│  • Export as: CSV, Excel, pure FASTA (per lab_id)               │
│  • Each genome → separate FASTA file (ready for Sourmash)       │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│            PHYLOGENETIC ANALYSIS (Sourmash) LAYER                │
├──────────────────────────────────────────────────────────────────┤
│  Step 1: Parse genome FASTA files                                │
│  Step 2: Create digital signatures (k-mer profiles)              │
│  Step 3: Compare all pairwise signatures                         │
│  Step 4: Generate phylogenetic tree from distance matrix         │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                    OUTPUT: PHYLOGENETIC TREE                      │
├──────────────────────────────────────────────────────────────────┤
│  • Newick format (.newick file) - standard for phylogenetics    │
│  • PNG visualization (UPGMA tree with bootstrap-like values)    │
│  • Can be imported into FigTree, Geneious, or other tools       │
└──────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Data Import & Organization (Relational Database)

### A. Import Methods

The relational database supports multiple flexible import pathways:

#### **Method 1: Bulk Import (Recommended)**
- User provides: Single Excel file with metadata columns + FASTA file paths
- Process:
  1. Read Excel; validate columns match schema (lab_id, species, location, etc.)
  2. For each row: extract lab_id and corresponding FASTA file path
  3. Validate FASTA file exists (supports absolute or relative paths)
  4. Import metadata as key-value pairs → Metadata table
  5. Parse FASTA file; import sequences → GenomicData table
- Advantage: Single operation for multiple genomes
- Duplicate handling: User can skip, replace, or stop on duplicates

#### **Method 2: Standard Excel + Individual FASTA Upload**
- User provides: Excel file (metadata only) in one step
- Then: User provides FASTA files individually, specifying lab_id for each
- Advantage: Flexible if genomes are acquired at different times
- Disadvantage: Multiple steps required

#### **Method 3: Directory Import**
- User provides: Directory path containing all Excel OR all FASTA files
- Process: Program automatically imports all matching files in directory
- Use case: Large batch import of pre-organized data

### B. Database Schema

The SQLite database consists of three tables:

**Metadata Table:**
```
lab_id          | key              | value
UL155           | species          | Linnemannia elongata
UL155           | collection_site  | Norway
UL155           | date_collected   | 2023-05-15
UL162           | species          | Linnemannia elongata
...
```
- `lab_id`: Unique identifier for each genome/organism
- `key`: Metadata field name (standardized via schema.yaml)
- `value`: Metadata field value

**GenomicData Table:**
```
lab_id | key                      | value (sequence)        | seq_order
UL155  | contig_1                 | ATGCATGCATGC...         | 0
UL155  | contig_2                 | GCTAGCTAGCTA...         | 1
UL162  | NODE_1_length_190000     | ATGCATGCATGC...         | 0
...
```
- `lab_id`: Links to Metadata table
- `key`: Sequence header from FASTA file
- `value`: The actual DNA sequence
- `seq_order`: Preserves sequence order from original file

### C. Data Validation & Error Handling

During import:
- **Column validation**: Excel columns checked against schema.yaml
- **Path resolution**: FASTA paths resolved (absolute or relative to Excel location)
- **File validation**: Checks that FASTA files exist and are valid format
- **Batch processing**: Sequences imported in batches (500 at a time) for performance
- **Transaction management**: If error occurs mid-import, rollback to previous state
- **User prompts**: Missing files skip with warning; user informed of results

---

## Phase 2: Search & Export (Data Retrieval)

### A. Query Methods

Users can search database by:
- **Lab ID**: `UL155` → retrieves all metadata + sequences for that genome
- **General keyword**: `Linnemannia` → finds all lab_ids matching that species
- **Range query**: Export all genomes with collection date > 2023

### B. Export Options

Once data is retrieved, users can export in multiple formats:

**Export Format: CSV/Excel**
- Standard tabular format (lab_id as rows, metadata as columns)
- Use case: Data analysis, spreadsheet review

**Export Format: Pure FASTA per Lab ID** ← *This is critical for Sourmash*
- Creates separate FASTA file for each unique lab_id
- Filename format: `{lab_id}.fasta` (e.g., `UL155.fasta`, `UL162.fasta`)
- Contents: Pure FASTA format (headers + sequences, no metadata)
- Example output structure:
  ```
  Assemblies_FromSQL/
  ├── UL155.fasta
  ├── UL162.fasta
  ├── UL163.fasta
  ├── UL169.fasta
  └── UL174.fasta
  ```

---

## Phase 3: Phylogenetic Tree Generation (Sourmash Workflow)

Once FASTA files are exported, the Sourmash pipeline generates the tree through four steps:

### Step 1: Signature Generation

**What happens:**
- Sourmash reads each FASTA file (e.g., `UL155.fasta`)
- Creates a "digital signature" (k-mer sketching) of that genome
- K-value (default: k=31): Counts all 31-nucleotide subsequences in genome
- Scales down to ~1000 k-mers via probabilistic sampling (scaled=1000)
- Signature = compact representation of genome sequence composition

**Why it works:**
- Similar genomes have similar k-mer compositions → similar signatures
- Not dependent on sequence alignment or order
- Computationally fast for large genomes

**Output:**
- `.sig` files: Compressed signature files (one per FASTA file)
- Located in: `SourmashSignatures/k31/`
- Examples: `UL155_k31.sig`, `UL162_k31.sig`, etc.

### Step 2: Comprehensive Pairwise Comparison

**What happens:**
- All signatures are compared pairwise using two methods:
  - **Jaccard ANI**: Intersection-based similarity (conservative)
  - **Max-Containment ANI**: One-directional similarity (sensitive to containment)

**Output:**
- Two ANI matrices (numpy format): 
  - `comprehensive_jaccard.npy`
  - `comprehensive_maxcontainment.npy`
- Both are N×N matrices where N = number of genomes
- Values range 0–1 (1 = identical, 0 = completely different)
- For 5 genomes (UL155, UL162, UL163, UL169, UL174):
  ```
  ANI matrix example (max-containment):
       UL155  UL162  UL163  UL169  UL174
  U155  1.0   0.98   0.91   0.90   0.98
  U162  0.98  1.0    0.91   0.91   0.98
  ...
  ```

### Step 3: Distance Conversion & Tree Construction

**What happens:**
- ANI values converted to distances: `distance = 1 - ANI`
- UPGMA (Unweighted Pair Group Method with Arithmetic Mean) algorithm applied:
  1. Start with each genome as separate cluster
  2. Iteratively merge closest clusters
  3. Update distances after each merge
  4. Continue until single tree remains

**Output:**
- Phylogenetic tree in **Newick format** (standard for phylogenetics)
- File: `upgma_tree_k31_maxcontainment.newick`
- Example:
  ```
  (((UL155:0.00, UL162:0.01):0.02, UL163:0.03):0.05, 
   ((UL169:0.00, UL174:0.01):0.02):0.04)root;
  ```
  Where branch lengths = evolutionary distances

### Step 4: Visualization

**What happens:**
- Tree rendered as PDF/PNG image
- Shows branching relationships and branch lengths
- Labels show genome identifiers

**Output:**
- PNG file: `upgma_tree_k31_maxcontainment.png`
- Can be imported into:
  - FigTree (phylogenetic tree viewer)
  - Geneious (sequence analysis software)
  - Publications/presentations

---

## Key Data Transformations

### Transformation 1: Metadata → Key-Value Pairs
```
Excel Raw:
Lab ID | Species | Location | Collection Date
UL155  | L. elongata | Norway | 2023-05-15

→ Database:
lab_id=UL155, key=species, value=L. elongata
lab_id=UL155, key=location, value=Norway
lab_id=UL155, key=collection_date, value=2023-05-15
```

### Transformation 2: Database → Per-Lab FASTA Files
```
GenomicData rows:
(UL155, contig_1, ATGC...)
(UL155, contig_2, GCTA...)
(UL162, contig_1, ATCG...)

→ Files:
UL155.fasta:
>contig_1
ATGC...
>contig_2
GCTA...

UL162.fasta:
>contig_1
ATCG...
```

### Transformation 3: FASTA → Genome Distance Matrix → Phylogenetic Tree
```
FASTA Files → K-mer Signatures → ANI Comparisons → Distance Matrix → Tree
```

---

## Workflow Example with Real Data

**Example: Analyzing 5 fungal genomes**

### Step 1: Import Data into Database
```
User: "I'll import 5 genomes from Excel + FASTA paths"
↓
Imports: 5 rows of metadata + 5 FASTA files
Database now contains:
  • Metadata: 5 lab_ids × ~15 metadata fields = ~75 key-value pairs
  • Genomic Data: 5 lab_ids × multiple sequences = 50,000+ sequences total
```

### Step 2: Search & Export
```
User: "Export all these 5 genomes as FASTA per lab_id"
↓
Creates folder with 5 files:
  UL155.fasta (160 KB)
  UL162.fasta (111 KB)
  UL163.fasta (160 KB)
  UL169.fasta (186 KB)
  UL174.fasta (112 KB)
```

### Step 3: Run Sourmash Pipeline
```
INPUT: 5 FASTA files
  ↓
SOURMASH STEP 1: Generate signatures
  Output: 5 .sig files
  ↓
SOURMASH STEP 2: Compare all pairs (5 × 5 = 25 comparisons)
  Output: 5×5 ANI matrices (jaccard + max-containment)
  ↓
SOURMASH STEP 3: Build UPGMA tree
  Output: Newick file + PNG visualization
  ↓
OUTPUT: Phylogenetic tree showing evolutionary relationships
```

### Example Result:
```
Newick format tree:
(((UL155:0.0, UL162:0.002):0.008, (UL163:0.044, UL169:0.0, UL174:0.002):0.012))

Interpretation:
• UL155 & UL162 are nearly identical (distance 0.002)
• UL169 & UL174 are nearly identical (distance 0.002)
• These two pairs are more distantly related (distance ~0.06)
• UL163 branches separately
```

---

## Advantages of This Two-Module Design

| Aspect | Relational Database | Sourmash Phylogenetics |
|--------|-------------------|----------------------|
| **Input flexibility** | Multiple import methods, batch processing | Clean FASTA files only |
| **Scalability** | Handles thousands of genomes' metadata | Works with any number of genomes |
| **Data organization** | Centralized, queryable, standardized | Focused on specific analysis |
| **Validation** | Column checking, path verification | Sequence format checking |
| **Reproducibility** | Database maintains complete record | Trees can be regenerated identically |
| **Metadata retention** | Full sample info preserved in DB | Focus on sequence relationships |

---

## Computational Considerations

### Time Complexity
- **Import**: O(M × N) where M = metadata fields, N = genomes
- **Export**: O(G) where G = total genomic data
- **Signature generation**: O(G × k) where G = genome size, k = k-mer size
- **Comparisons**: O(n²) where n = number of genomes
- **Tree building**: O(n²) using UPGMA algorithm

### Memory Requirements
- **Database**: ~10 MB per 1000 genomes (metadata + index)
- **Signatures**: ~10 MB total for 10 genomes
- **Comparison matrices**: Small (< 1 MB for < 1000 genomes)
- **Genome files**: Depends on assembly size (typically 50-500 MB per genome)

### Parallel Processing
- Sourmash: Signature generation parallelized across CPU cores (default: 32 threads)
- Database imports: Batch processing with transaction commits

---

## Error Handling & Data Integrity

**Import Phase:**
- Missing files → logged warning, import continues
- Invalid FASTA → file skipped, user notified
- Duplicate lab_ids → user prompted for action (skip/replace/stop)

**Database Phase:**
- Transaction rollback on error (ACID compliance)
- Foreign key constraints maintained
- Batch commits every 500 sequences (balances performance + safety)

**Export Phase:**
- File existence checks before export
- Warnings for empty result sets
- Filepath validation

**Phylogenetic Phase:**
- Signature validation before comparison
- Error logging to standard output

---

## Integration with Downstream Tools

Generated Newick trees can be used with:

1. **FigTree** - Interactive phylogenetic tree viewer
2. **Geneious** - Bioinformatics workbench
3. **PAUP*** - Phylogenetic Analysis Using Parsimony
4. **R packages** - ape, phytools, phylogram
5. **EvolView** - Web-based tree visualization
6. **Dendroscope** - Phylogenetic tree viewer for large trees

---

## Summary

This integrated workflow provides:
1. **Flexible input** - Excel or FASTA; single or bulk import
2. **Organized storage** - Relational database for metadata + sequences
3. **Queryable access** - Search by lab_id, species, location, etc.
4. **Clean export** - Per-genome FASTA files
5. **Rapid phylogenetics** - Sourmash signatures for whole-genome comparison
6. **Publication-ready output** - Newick trees + PNG visualizations

The modular design allows researchers to leverage either component independently: use only the database for data management, or use only Sourmash for phylogenetic analysis with existing FASTA files.
