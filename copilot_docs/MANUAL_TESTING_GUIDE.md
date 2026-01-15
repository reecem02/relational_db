# Bulk Import Feature - Manual Testing Guide

## Prerequisites

Before starting, ensure:
- ✅ You're in the `r_db` directory
- ✅ The database file exists: `database/fungal_db.sqlite`
- ✅ Example files exist:
  - `example_files/bulk_import_example.xlsx`
  - `example_files/genomes/genome1.fasta`
  - `example_files/genomes/genome2.fasta`
  - `example_files/genomes/genome3.fasta`

---

## Quick Start (5 minutes)

### Test 0: Run the Automated Test Suite First (Recommended)

```bash
cd c:\Users\reece\OneDrive\Desktop\reece\coding\myco_research\r_db
python3 tools/test_bulk_import.py
```

This runs Tests 1-3 automatically and shows you exactly what to expect.

---

## Manual Testing Workflow

### TEST 1: Happy Path (All Works)

**Objective:** Verify bulk import works with valid files and no duplicates

**Steps:**

1. **Open terminal and navigate to project:**
   ```bash
   cd c:\Users\reece\OneDrive\Desktop\reece\coding\myco_research\r_db
   ```

2. **Start the program:**
   ```bash
   python3 main.py
   ```

3. **You should see the main menu:**
   ```
   Welcome to the Fungal Research Database
   1) Import Data
   2) Search Data
   3) Delete Data
   4) Help
   5) Database Information
   6) Exit
   
   Enter your choice:
   ```

4. **Select option 1 (Import Data):**
   ```
   Enter your choice: 1
   ```

5. **You should see the new import menu:**
   ```
   --Import Data--
   1) Standard Excel Import (metadata only)
   2) Standard FASTA Import (single genome)
   3) Bulk Import (Excel + FASTA file locations)
   4) Folder Import (all Excel or FASTA from directory)
   
   Select import type (1/2/3/4):
   ```

6. **Select option 3 (Bulk Import):**
   ```
   Select import type (1/2/3/4): 3
   ```

7. **You should see a prompt for the Excel file:**
   ```
   Enter Excel file name (including extension) or full path:
   ```

8. **Enter the example file:**
   ```
   bulk_import_example.xlsx
   ```

9. **The program will start the bulk import:**
   ```
   ============================================================
   BULK IMPORT: Excel with FASTA File Locations
   ============================================================
   
   Loading Excel file: example_files/bulk_import_example.xlsx
   Processing 3 rows...
   
   [Row 1/3] Lab ID: UL001
     ✓ Metadata imported
     ✓ FASTA imported
   
   [Row 2/3] Lab ID: UL002
     ✓ Metadata imported
     ✓ FASTA imported
   
   [Row 3/3] Lab ID: UL003
     ✓ Metadata imported
     ✓ FASTA imported
   
   ============================================================
   BULK IMPORT RESULTS
   ============================================================
   Total rows processed:     3
   ✓ Metadata imported:      3
   ✓ FASTA imported:         3
   ============================================================
   ```

10. **Verify success:**
    - All 3 rows show ✓ checkmarks
    - Results show 3 metadata imported, 3 FASTA imported
    - No warnings or errors

**Expected Result:** ✅ TEST 1 PASSED

---

### TEST 2: Missing FASTA File (Error Handling)

**Objective:** Verify the program gracefully handles missing FASTA files

**Steps:**

1. **Create a test Excel file** by editing `bulk_import_example.xlsx`:
   - Open it in Excel or a spreadsheet program
   - Change row 2's "Primary Assembly Filename" to: `./genomes/nonexistent.fasta`
   - Save as `test_missing_file.xlsx`

2. **Start the program:**
   ```bash
   python3 main.py
   ```

3. **Select:** 1 → 3

4. **Enter:** `test_missing_file.xlsx`

5. **Watch for the warning:**
   ```
   [Row 2/3] Lab ID: UL002
     ✓ Metadata imported
     ⚠ FASTA file not found: C:\...\genomes\nonexistent.fasta
     → Skipping genomic import for UL002
   ```

6. **Check the results:**
   ```
   Total rows processed:     3
   ✓ Metadata imported:      3
   ⓘ FASTA skipped:          1
     UL002: File not found: ...
   ✓ FASTA imported:         2
   ```

**Expected Result:** ✅ TEST 2 PASSED
- All 3 metadata rows imported
- Row 2 FASTA skipped with warning
- Import didn't stop, continued to row 3

---

### TEST 3: Invalid FASTA Format (Error Handling)

**Objective:** Verify the program gracefully handles corrupted FASTA files

**Steps:**

1. **Create a corrupted FASTA file:**
   ```bash
   echo "This is not valid FASTA" > example_files/genomes/corrupted.fasta
   ```

2. **Create a test Excel file:**
   - Edit `bulk_import_example.xlsx`
   - Change row 3's "Primary Assembly Filename" to: `./genomes/corrupted.fasta`
   - Save as `test_corrupted_fasta.xlsx`

3. **Start the program:**
   ```bash
   python3 main.py
   ```

4. **Select:** 1 → 3

5. **Enter:** `test_corrupted_fasta.xlsx`

6. **Watch for the error:**
   ```
   [Row 3/3] Lab ID: UL003
     ✓ Metadata imported
     ✗ FASTA import failed: [error details]
     → Skipping genomic import for UL003
   ```

7. **Check the results:**
   ```
   Total rows processed:     3
   ✓ Metadata imported:      3
   ✓ FASTA imported:         2
   ✗ FASTA failed:           1
     UL003: Invalid FASTA format: ...
   ```

**Expected Result:** ✅ TEST 3 PASSED
- Metadata still imported even though FASTA failed
- Import didn't crash, showed error and continued
- Other rows imported successfully

---

### TEST 4: Duplicate Lab IDs (Interactive Handling)

**Objective:** Verify the program prompts for duplicate handling

**Steps:**

1. **Run bulk import once:**
   ```bash
   python3 main.py → 1 → 3 → bulk_import_example.xlsx
   ```
   
   Wait for it to complete successfully.

2. **Run bulk import AGAIN with the same file:**
   ```bash
   python3 main.py → 1 → 3 → bulk_import_example.xlsx
   ```

3. **Watch for the duplicate prompt at Row 1:**
   ```
   [Row 1/3] Lab ID: UL001
   ⚠ Duplicate Found: Lab ID 'UL001' already exists in database
      What would you like to do?
      1) Skip (keep existing data)
      2) Replace (delete old, import new)
      3) Stop bulk import
      Enter choice (1/2/3):
   ```

4. **Test choice 1 - SKIP:**
   ```
   Enter choice (1/2/3): 1
   ```
   
   Expected: Program skips this row and continues
   ```
   → Skipping (keeping existing data)
   [Row 2/3] Lab ID: UL002
   ⚠ Duplicate Found: Lab ID 'UL002' already exists in database
      What would you like to do?
      1) Skip (keep existing data)
      2) Replace (delete old, import new)
      3) Stop bulk import
      Enter choice (1/2/3): 1
   ```

5. **Press 1 again for row 2, and row 3**

6. **Verify results show all skipped:**
   ```
   Total rows processed:     3
   ✓ Metadata imported:      0
   ⓘ Metadata skipped:       3
     UL001: Duplicate - user chose SKIP
     UL002: Duplicate - user chose SKIP
     UL003: Duplicate - user chose SKIP
   ```

**Test choice 2 - REPLACE (requires running again):**

1. **Run bulk import a third time:**
   ```bash
   python3 main.py → 1 → 3 → bulk_import_example.xlsx
   ```

2. **This time, choose option 2 (REPLACE):**
   ```
   Enter choice (1/2/3): 2
   ```
   
   Expected: Program deletes old data and imports new
   ```
   → Replacing existing data
   ✓ Metadata imported
   ✓ FASTA imported
   ```

3. **Then choose SKIP for remaining duplicates:**
   ```
   Enter choice (1/2/3): 1
   Enter choice (1/2/3): 1
   ```

4. **Verify results:**
   ```
   Total rows processed:     3
   ✓ Metadata imported:      1
   ✓ FASTA imported:         1
   ⓘ Metadata skipped:       2
   ```

**Test choice 3 - STOP (requires running again):**

1. **Run bulk import a fourth time:**
   ```bash
   python3 main.py → 1 → 3 → bulk_import_example.xlsx
   ```

2. **Choose option 3 (STOP):**
   ```
   Enter choice (1/2/3): 3
   ```
   
   Expected: Program stops immediately
   ```
   ⚠ Bulk import stopped by user
   ```

3. **Verify results show only 0 imported:**
   ```
   Total rows processed:     3
   ✓ Metadata imported:      0
   ✓ FASTA imported:         0
   ```

**Expected Result:** ✅ TEST 4 PASSED
- Duplicate detection working
- All three choices (Skip, Replace, Stop) work as expected

---

### TEST 5: Verify Database Contents

**Objective:** Confirm data was actually saved to the database

**Steps:**

1. **From the main menu, select option 2 (Search Data):**
   ```
   Enter your choice: 2
   ```

2. **Search for one of the lab IDs we imported:**
   ```
   Enter a keyword to search: UL001
   ```

3. **You should see the metadata:**
   ```
   Lab ID: UL001
   Sample Location Plate: Plate A
   GC3F Submission Sample ID: GC3F-001
   ... (other metadata fields)
   ```

4. **Press Y to export and verify FASTA was also saved**

**Expected Result:** ✅ TEST 5 PASSED
- Lab ID found in database
- All metadata fields present
- Can see FASTA sequences when exporting

---

## Summary Checklist

After completing all tests, verify:

```
☐ Test 1: Happy path - all files imported successfully
☐ Test 2: Missing file - skipped with warning, import continued
☐ Test 3: Invalid FASTA - failed gracefully, import continued
☐ Test 4a: Duplicate SKIP - kept existing data
☐ Test 4b: Duplicate REPLACE - replaced with new data
☐ Test 4c: Duplicate STOP - stopped the import
☐ Test 5: Verify data in database via search
```

---

## Troubleshooting

**Issue:** "Excel file not found"
- Solution: Make sure you're entering the correct filename or path
- The program looks in `example_files/` if you don't provide a full path

**Issue:** "FASTA file not found"
- Solution: This is expected in Test 2 and Test 3
- The program should skip gracefully with a warning

**Issue:** "Duplicate prompt not appearing"
- Solution: You need to run bulk import twice with the same file
- Or manually modify files to have duplicate lab_ids

**Issue:** Database seems empty after importing
- Solution: The example database is persistent
- Run "Search Data" to verify records exist
- Or check "Database Information" (option 5) to see counts

**Issue:** Program crashes with an error
- Solution: Check the error message for details
- Make sure all required metadata columns are in Excel file
- Verify FASTA files are in correct format

---

## Next Steps After Testing

If all tests pass:

1. **Commit to git:**
   ```bash
   git add -A
   git commit -m "Implement bulk import feature with FASTA file location mapping"
   git push origin main
   ```

2. **Deploy to server:**
   ```bash
   cd /nfs6/BPP/Uehling_Lab/morgaree/relational_db
   git pull origin main
   ```

3. **Test on server with production data:**
   - Create Excel with real lab_id data
   - Use actual FASTA file paths from /nfs6 or /nfs4
   - Run bulk import to verify with production paths

---

## Questions?

If you have questions or run into issues:

1. Check the detailed implementation plan: `BULK_IMPORT_IMPLEMENTATION_PLAN.md`
2. Review the program analysis: `PROGRAM_ANALYSIS.md`
3. Check configuration: `config/schema.yaml`
4. Review bulk import code: `modules/data_import.py` (search for `import_bulk_with_fasta`)

Good luck! 🚀
