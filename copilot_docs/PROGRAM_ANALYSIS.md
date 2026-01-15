# Relational Database Program Analysis

## Executive Summary
**Current State:** Your program **DOES have Excel file upload capabilities**, but it **LACKS a true bulk upload feature** that directly links genomes to their FASTA files based on file locations specified in Excel.

---

## Current Architecture

### Database Schema
The program uses **SQLite** with two main tables:

#### 1. **Metadata Table**
- Stores sample metadata with a key-value structure
- **Primary Key:** `lab_id` (Uehling Lab ID - unique identifier for each sample)
- **Columns:**
  - `id`: Auto-increment primary key
  - `lab_id`: Sample identifier (e.g., UL001)
  - `key`: Metadata field name (e.g., "Extracted by", "Location ID")
  - `value`: Metadata field value
  - `file_uploaded`: Timestamp of upload

#### 2. **GenomicData Table**
- Stores FASTA sequences in a key-value structure
- **Primary Key:** `lab_id` (linked to Metadata)
- **Columns:**
  - `id`: Auto-increment primary key
  - `lab_id`: Sample identifier
  - `key`: Sequence ID/header from FASTA
  - `value`: The actual DNA sequence
  - `seq_order`: Order of sequences in file
  - `file_uploaded`: Timestamp of upload

---

## Current Import/Upload Capabilities

### ✅ What EXISTS:

#### 1. **Excel Import** (`import_metadata()`)
- **Supported:** `.xlsx` and `.xls` files
- **Process:**
  - Reads Excel file using pandas
  - Expects specific columns (see below)
  - Each row = one genome's metadata
  - Maps Excel columns to key-value pairs in Metadata table
  - **For each upload:** Deletes old metadata for that lab_id, then inserts new data
- **Required Excel Columns:**
  ```
  - Uehling Lab ID (PRIMARY IDENTIFIER)
  - Sample Location Plate
  - GC3F Submission Sample ID
  - Alternate ID 1, ID 2, ID 3
  - Extracted by
  - Top ITS Blast Hit
  - ITS Top Hit Similarity
  - ITS Taxonomy Comments
  - Top 16S Blast Hit
  - 16S Top Hit Similarity
  - 16S Taxonomy Comments
  - Project Funding
  - Latitude
  - Longitude
  - Location ID
  - DNA Extraction Method
  - Extraction Date
  ```

#### 2. **FASTA Import** (`import_fasta()`)
- **Supported:** `.fasta`, `.fa`, `.fna` files
- **Process:**
  - User must **manually enter a single lab_id** for the entire file
  - Parses FASTA sequences
  - Stores each sequence as a row in GenomicData table
  - Batches inserts for performance (500 sequences per batch)
  - **Problem:** One lab_id per file upload; doesn't match multiple sequences to multiple lab_ids

#### 3. **Bulk Folder Import**
- `import_metadata_from_folder()`: Imports all Excel files from a folder
- `import_fasta_from_folder()`: Imports all FASTA files from a folder
- Both support recursive directory traversal

---

## ❌ What's MISSING: Bulk Upload with File Location Mapping

**Your Request:** Upload an Excel file with genomes and their corresponding FASTA file locations, then bulk import both metadata and genomic data.

**Current Gap:**
The program **cannot** currently:
1. Read a "Primary Assembly Filename" or file path column from Excel
2. Auto-locate and import FASTA files based on paths listed in Excel
3. Automatically map multiple genomes (multiple rows) to their individual FASTA files
4. Perform a true bulk upload workflow in one operation

**Example of what you want to do:**
```
Excel File Structure:
| Uehling Lab ID | Sample Location | Primary Assembly Filename      |
| UL001          | Sample Plate 1   | /path/to/genomes/genome1.fasta |
| UL002          | Sample Plate 1   | /path/to/genomes/genome2.fasta |
| UL003          | Sample Plate 2   | /path/to/genomes/genome3.fasta |
```

Then the program should:
1. Import metadata from Excel for UL001, UL002, UL003
2. Auto-import genome1.fasta for UL001, genome2.fasta for UL002, etc.
3. All in one workflow

**Currently, you must:**
1. Import Excel metadata separately
2. Import each FASTA file separately and manually enter the lab_id

---

## Current Import Workflow

### Flow Diagram:
```
Main Menu
    ↓
[1] Import Data
    ↓
Select: [1] Excel or [2] Fasta
    ↓
Choose: File [f] or Directory [d]?
    ↓
IF Excel:
  → Load Excel file
  → Validate columns match schema.yaml
  → Convert to key-value pairs
  → Insert into Metadata table
    ↓
IF Fasta:
  → Manually enter lab_id (USER INPUT)
  → Parse FASTA sequences
  → Insert into GenomicData table for that lab_id
```

---

## Current Workflow Steps

### For Excel Upload:
```python
1. User selects "Import Data" → "Excel"
2. Provides file path
3. import_metadata(file_path) executes:
   - Reads Excel with pandas
   - Validates columns exist
   - For each row:
     a. Extract lab_id
     b. Delete existing metadata for that lab_id
     c. Insert all columns as key-value pairs
4. Success message displayed
```

### For FASTA Upload:
```python
1. User selects "Import Data" → "Fasta"
2. Provides file path
3. **USER MANUALLY ENTERS lab_id** ← KEY LIMITATION
4. import_fasta(file_path, lab_id) executes:
   - Verifies lab_id exists in Metadata
   - If not, creates placeholder entry
   - Batches parse FASTA sequences
   - Inserts sequences with seq_order
5. Success message displayed
```

---

## Code Location Reference

| Component | File | Key Function |
|-----------|------|--------------|
| Main menu | `main.py` | `main()`, `import_data_ui()` |
| Excel import logic | `modules/data_import.py` | `import_metadata()` |
| FASTA import logic | `modules/data_import.py` | `import_fasta()` |
| Folder scanning | `modules/data_import.py` | `import_metadata_from_folder()`, `import_fasta_from_folder()` |
| Database schema | `database/schema.sql` | Table definitions |
| Column definitions | `config/schema.yaml` | Expected metadata columns |
| Database config | `config/config.yaml` | SQLite path |

---

## Dependencies Available

Your `requirements.txt` includes:
- ✅ `pandas` - for reading Excel files
- ✅ `openpyxl` - for Excel support
- ✅ `biopython` - for FASTA parsing
- ✅ `sqlalchemy` - for database ORM

**All dependencies needed for bulk import feature already exist!**

---

## Recommendations for Adding Bulk Upload Feature

### Option 1: **Minimal Addition** (Recommended)
Add a new function `import_bulk_with_fasta_locations()` that:
1. Reads Excel file
2. **Expects a "Primary Assembly Filename" column** with file paths
3. For each row:
   - Import metadata as usual
   - Read the FASTA file path from that column
   - Auto-import FASTA file for that lab_id
4. Handle missing files gracefully

### Option 2: **Enhanced Version**
Same as Option 1, but with:
- Support for multiple FASTA columns (e.g., "RNA file", "Genome file")
- Configurable FASTA file path columns in `schema.yaml`
- Progress reporting (X of Y completed)
- Error logging for failed imports

### Implementation Considerations:
- **File Path Resolution:** Support relative paths (from Excel location or config), absolute paths, and UNC paths
- **Error Handling:** What if FASTA file doesn't exist? Skip? Fail? Log and continue?
- **Duplicate Prevention:** Current code deletes and re-inserts; ensure this behavior is desired
- **Performance:** Current batching (500 sequences) seems good; consider progress updates for large uploads

---

## Current Limitations Summary

| Limitation | Impact | Current Workaround |
|-----------|--------|-------------------|
| No file path mapping in Excel | Manual multi-step process | Import Excel, then manually import FASTA files |
| One lab_id per FASTA import | Can't bulk import per-genome FASTA files | Use folder import for many files with same ID |
| No progress reporting | No feedback during long uploads | Relies on print statements |
| No duplicate detection | Identical sequences inserted twice if run twice | Current behavior is replace (not append) |
| No validation of FASTA content | Bad sequences could be inserted | Only file extension validation |

---

## Summary Answer

**Does your database have bulk upload capabilities?**

**Partial:**
- ✅ Can bulk import Excel metadata files from a folder
- ✅ Can bulk import FASTA files from a folder
- ❌ **Cannot** link Excel rows to their individual FASTA files via file path mapping
- ❌ **Cannot** perform coordinated bulk import of metadata + corresponding FASTA in one operation

The feature you're looking for (Excel with "Primary Assembly Filename" column → auto-import matching FASTA files) **does not exist yet** but would be straightforward to implement given the existing architecture and dependencies.
