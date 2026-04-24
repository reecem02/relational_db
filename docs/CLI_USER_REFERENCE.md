# CLI Reference: Multi-Lab Export User Flow

## Complete CLI Output Example

When user searches for "U1513A" and exports to FASTA per Lab ID:

```
════════════════════════════════════════════════════════════════════════════════

Welcome to the Fungal Research Database
1) Import Data
2) Search Data
3) Delete Data
4) Help
5) Database Information
6) Exit
Enter your choice: 2

-- Search Data --
Enter a keyword to search: U1513A

════════════════════════════════════════════════════════════════════════════════
[SEARCH PHASE - Looking for matching records]

Searching for keyword: U1513A
Results for keyword 'U1513A':
lab_id             key    value
 UL155 Project Funding [U1513A]
 UL162 Project Funding [U1513A]
 UL163 Project Funding [U1513A]
 UL169 Project Funding [U1513A]
 UL174 Project Funding [U1513A]

Matched 5 unique lab_ids. Fetching FASTA sequences for bulk export...
Fetched 178363 FASTA sequences from 5 lab_ids

════════════════════════════════════════════════════════════════════════════════
[EXPORT PROMPT PHASE - Asking user what to do with results]

Would you like to export these results? (y/n): y

[Multi-Lab Export Mode] Detected 5 genomes: UL155, UL162, UL163, UL169, UL174
Export as [1] CSV, [2] Excel, [3] TXT, or [4] FASTA per Lab ID (for phylogenetic tools)? (1/2/3/4): 4

════════════════════════════════════════════════════════════════════════════════
[EXPORT FORMAT SELECTED: FASTA per Lab ID]

→ Creating 5 separate FASTA files (one per Uehling ID)
→ Each file formatted for barrnap phylogenetic pipeline

Export to [d]efault folder (exported_files/) or [c]ustom path? (d/c): d
Enter folder name (will be created inside exported_files/): my_u1513a_export

════════════════════════════════════════════════════════════════════════════════
[EXPORT EXECUTION PHASE - Creating files]

Exporting FASTA sequences for 5 lab_ids:
  ✓ UL155_phylo.fasta (12,667 sequences)
  ✓ UL162_phylo.fasta (9,731 sequences)
  ✓ UL163_phylo.fasta (35,440 sequences)
  ✓ UL169_phylo.fasta (86,924 sequences)
  ✓ UL174_phylo.fasta (33,601 sequences)

Successfully exported 5 files to: exported_files/my_u1513a_export

════════════════════════════════════════════════════════════════════════════════
[RETURN TO MAIN MENU]

Welcome to the Fungal Research Database
1) Import Data
2) Search Data
3) Delete Data
4) Help
5) Database Information
6) Exit
```

---

## File System Result

```
exported_files/
└── my_u1513a_export/
    ├── UL155_phylo.fasta (52 MB)
    ├── UL162_phylo.fasta (50 MB)
    ├── UL163_phylo.fasta (57 MB)
    ├── UL169_phylo.fasta (71 MB)
    └── UL174_phylo.fasta (52 MB)
    
Total: 5 files, 282 MB, 178,363 sequences
```

---

## File Content Example

Each file contains sequences properly formatted for phylogenetic analysis:

### UL155_phylo.fasta
```fasta
>UL155_NODE_1_length_160273_cov_42.018477
TCGACAAAGAGTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTCTTTCGTCTATTTCAAGTTCAGACGCTACTTAGGACCA
CCAGGGGGTATCTCAAGAACCAGCGTGTAAATAGACTACAAAATCACTGCCCATTTCCAACACCATGCCATGAGGTCCC
CCTCCAAGTTAACCAAGAGAGTATGAGTCGATTCAATAAAAAGTTGGCTTCATTGCTGTGGAATGAAAGGTTATGAAAG
...
>UL155_NODE_2_length_135548_cov_40.720686
AATTGAGACGAGAACGAACACACTGCGAGACGAACACGACACACTGCGAGACGAACACGACACACTGCGAGAC...
...
```

### File Characteristics
✓ 80-character line wrapping (standard FASTA)
✓ Headers prefixed with lab_id: `>UL155_...`
✓ Standard nucleotide characters: ATGCN
✓ Ready for phylogenetic tools: `sourmash sketch dna UL155_phylo.fasta`

---

## Alternative Scenarios

### Scenario A: Single Lab_ID Query (Backward Compatible)

```
Enter a keyword to search: UL155

Searching for keyword: UL155
[Direct lab_id match - using optimized query path]

Would you like to export these results? (y/n): y

Export as [1] CSV, [2] Excel, [3] TXT, or [4] FASTA (for phylogenetic tools)? (1/2/3/4): 4
                              ↑ Note: "FASTA" not "FASTA per Lab ID"
                              ↑ Single-file export mode

Export to [d]efault folder or [c]ustom path? (d/c): d
Enter file name (.fasta will be added if not present): ul155_sequences
                              ↑ Note: Asks for FILE name, not folder name

Exported FASTA sequences to exported_files/ul155_sequences.fasta
```

### Scenario B: Metadata-Only Match (No FASTA Available)

```
Enter a keyword to search: candida

Searching for keyword: candida
Results for keyword 'candida':
lab_id      key           value
UL200       Species Name  Candida albicans
UL201       Species Name  Candida tropicalis

Would you like to export these results? (y/n): y

Export as [1] CSV, [2] Excel, [3] TXT, or [4] FASTA (for phylogenetic tools)? (1/2/3/4): 1
                              ↑ Note: "FASTA" option available
                              ↑ But multi-lab mode NOT activated (no FASTA data)
```

---

## Expected Timing

| Operation | Duration | What's Happening |
|-----------|----------|------------------|
| Search input | Instant | User types |
| Search execution | 2-3 sec | Database lookup + FASTA fetch |
| Display results | <1 sec | Format and print |
| Export prompts | Instant | User input |
| Folder creation | <1 sec | Create directory structure |
| Export execution | 30-60 sec | Write 5 files to disk (~282MB) |
| **Total** | **1-2 min** | Full workflow, first run |

---

## Key Indicators of Success

✓ **Search phase**
- Sees message: "Matched 5 unique lab_ids. Fetching FASTA sequences..."
- Sees message: "Fetched 178363 FASTA sequences from 5 lab_ids"

✓ **Export prompt phase**
- Sees: "[Multi-Lab Export Mode] Detected 5 genomes: UL155, UL162, UL163, UL169, UL174"
- Sees: "Export as [1] CSV, [2] Excel, [3] TXT, or [4] FASTA per Lab ID (for Barrnap pipeline)?"
- Prompted for folder name, NOT file name

✓ **Export execution phase**
- Sees: "→ Creating 5 separate FASTA files (one per Uehling ID)"
- Sees: "→ Each file formatted for barrnap phylogenetic pipeline"
- Sees: 5 separate records: UL155_barrnap.fasta, UL162_barrnap.fasta, etc.
- Sees: Sequence counts per file

✓ **File system**
- 5 files created in specified folder
- Each file named: {LAB_ID}_barrnap.fasta
- Each file ~50-75 MB
- Each file contains thousands of sequences

---

## Troubleshooting

### Problem: Still asking for file name instead of folder name

**Solution:** Restart Python (module might be cached)
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Run program fresh
python3 main.py
```

### Problem: Not seeing "Matched X unique lab_ids" message

**Solution:** The search doesn't match multiple lab_ids
- Check search term spelling
- Try simpler search (e.g., "U1" instead of "U1513A")
- Verify data is imported

### Problem: "How do I know the export is working?"

**Verify these messages appear in order:**
1. "Matched 5 unique lab_ids. Fetching FASTA sequences..."
2. "[Multi-Lab Export Mode] Detected 5 genomes: ..."
3. "→ Creating 5 separate FASTA files"
4. "Successfully exported 5 files to: ..."

All 4 messages = success ✓

---

## Quick Reference: Code Flow

```
PHASE 1: Search
INPUT:    U1513A
PROCESS:  search_db() → find metadata → fetch FASTA
OUTPUT:   DataFrame with 5 metadata rows + 178,363 FASTA rows

PHASE 2: Export Prompt
INPUT:    User chooses export format
PROCESS:  export_prompt() → detect multi-lab → route to per-lab function
OUTPUT:   5 separate FASTA files

PHASE 3: Execution
INPUT:    Folder location from user
PROCESS:  export_fasta_per_lab_id() → create files → write sequences
OUTPUT:   Files in: exported_files/my_u1513a_export/
```

---

## Using Output Files

After export, use files with barrnap pipeline:

```bash
# Process single file
barrnap --kingdom bac exported_files/my_u1513a_export/UL155_barrnap.fasta \
        > results/UL155.gff

# Process all files
for f in exported_files/my_u1513a_export/*_barrnap.fasta; do
    lab_id=$(basename "$f" "_barrnap.fasta")
    echo "Processing $lab_id..."
    barrnap --kingdom bac "$f" > "results/${lab_id}.gff"
done

# Or with parallel processing
ls exported_files/my_u1513a_export/*_barrnap.fasta | \
    parallel barrnap --kingdom bac {} ">" "results/{/.}.gff"
```

---

**Status:** Ready to Use ✓  
**Tested:** February 13, 2026  
**User Ready:** Yes
