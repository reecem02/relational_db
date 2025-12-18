# Bulk Import Testing - Quick Reference

## 🚀 Start Here

### Option A: Run Automated Tests (Recommended First)
```bash
cd c:\Users\reece\OneDrive\Desktop\reece\coding\myco_research\r_db
python3 tools/test_bulk_import.py
```
Takes ~2 minutes, tests 3 scenarios automatically.

### Option B: Manual Testing
Follow `MANUAL_TESTING_GUIDE.md` for step-by-step instructions.

---

## 📋 Test Matrix

| Test | File | FASTA Files | Duplicates | Expected Result |
|------|------|-------------|-----------|-----------------|
| 1: Happy Path | `bulk_import_example.xlsx` | All exist ✓ | None | 3 imported, 0 skipped |
| 2: Missing File | `test_missing_file.xlsx` | 1 missing ✗ | None | 3 metadata, 2 FASTA |
| 3: Invalid FASTA | `test_corrupted_fasta.xlsx` | 1 corrupted ✗ | None | 3 metadata, 2 FASTA |
| 4: Duplicates | `bulk_import_example.xlsx` | All exist ✓ | Yes ⚠️ | User choice applied |

---

## 🎯 Quick Manual Test (5 min)

```
1. python3 main.py
2. Select: 1 (Import Data)
3. Select: 3 (Bulk Import)
4. Enter: bulk_import_example.xlsx
5. Watch for: ✓ checkmarks and results
6. Exit and search to verify data
```

**Expected Output:**
```
Total rows processed:     3
✓ Metadata imported:      3
✓ FASTA imported:         3
```

---

## ⚡ Menu Navigation

```
Main Menu
├─ 1: Import Data
│  ├─ 1: Standard Excel
│  ├─ 2: Standard FASTA
│  ├─ 3: Bulk Import ⭐ NEW
│  └─ 4: Folder Import
├─ 2: Search Data
├─ 3: Delete Data
├─ 4: Help
├─ 5: Database Information
└─ 6: Exit
```

---

## 📁 Important Files

```
example_files/
├─ bulk_import_example.xlsx      ← Example Excel file
└─ genomes/
   ├─ genome1.fasta              ← Example FASTA 1
   ├─ genome2.fasta              ← Example FASTA 2
   └─ genome3.fasta              ← Example FASTA 3

config/
└─ schema.yaml                   ← NEW bulk_import_config

modules/
└─ data_import.py               ← NEW import_bulk_with_fasta()

tools/
├─ test_bulk_import.py          ← Automated tests ⭐
└─ create_bulk_import_example.py ← Create examples

MANUAL_TESTING_GUIDE.md          ← Detailed steps
BULK_IMPORT_IMPLEMENTATION_PLAN.md ← Technical details
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| "Excel file not found" | Use full path or place in `example_files/` |
| "FASTA file not found" | (Expected in Test 2) Program skips gracefully |
| "Invalid FASTA format" | (Expected in Test 3) Program skips gracefully |
| No duplicate prompt | Run bulk import twice with same file |
| Database empty | Use Search Data (option 2) to verify |
| Syntax errors | Run: `python3 -m py_compile modules/data_import.py main.py` |

---

## ✅ Success Criteria

- [x] All 3+ test scenarios pass
- [x] Metadata imports even if FASTA fails
- [x] Import continues after errors (doesn't crash)
- [x] Duplicate handling works (skip/replace/stop)
- [x] Data appears in database
- [x] Results report shows accurate counts

---

## 🔄 Before Deploying to Server

1. ✅ Run automated tests locally
2. ✅ Manually test all 4 scenarios
3. ✅ Verify database has correct data
4. ✅ Commit to git
5. ✅ Pull on server
6. ✅ Test with production data paths (/nfs6, /nfs4)

---

## 📞 Need Help?

1. Check: `MANUAL_TESTING_GUIDE.md` - Detailed step-by-step
2. Check: `BULK_IMPORT_IMPLEMENTATION_PLAN.md` - Technical details
3. Check: `README.md` - User documentation
4. Check: Error messages in console output

---

## 🚀 Quick Commands

```bash
# Test locally
cd c:\Users\reece\OneDrive\Desktop\reece\coding\myco_research\r_db
python3 tools/test_bulk_import.py

# Check syntax
python3 -m py_compile modules/data_import.py main.py

# Start program
python3 main.py

# Create example files
python3 tools/create_bulk_import_example.py
```

---

**Ready to test? Start with `python3 tools/test_bulk_import.py`** ✨
