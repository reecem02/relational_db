# Tools Directory

This folder contains helper scripts for database testing and development.

---

## Import Tools

### benchmark_import.py

**Purpose:** Measure import performance for FASTA files.

**Usage (from project root):**

```bash
python3 tools/benchmark_import.py
```

Copies `example_files/example_gen.fasta` into a temporary folder multiple times (controlled by `NUM_FILES`) and imports them using the current import code. Runs non-interactively using a fixed lab ID `BENCH1`. Adjust `NUM_FILES` in the script as needed.

---

### create_bulk_import_example.py

**Purpose:** Generate a sample `bulk_import_example.xlsx` file for testing the bulk import feature.

**Usage (from project root):**

```bash
python3 tools/create_bulk_import_example.py
```

Outputs the example Excel file to `example_files/bulk_import_example.xlsx` with three sample genomes and realistic field values.

---

### test_bulk_import.py

**Purpose:** Automated tests for the bulk import feature covering multiple scenarios.

**Tests:**
- Happy path (all files exist, no duplicates)
- Missing FASTA file (graceful skip)
- Invalid FASTA format (graceful skip)
- Duplicate handling (replace existing data)

**Usage (from project root):**

```bash
python3 tools/test_bulk_import.py
```
