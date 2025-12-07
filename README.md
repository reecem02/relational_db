# Fungal Research Database

This project creates a MySQL-based database for storing and querying fungal research data, including metadata and genomic sequences.

## Prerequisites
- Python 3.8+
- MySQL
- Required Python libraries (see `requirements.txt`)

### Setup
To use the beta version of this database, you must follow these steps to ensure you have all required libraries and dependencies installed. Please report any errors or issues you encounter. Thanks!

1. Install Python
    1. Download and install Python 3.8 or newer from https://www.python.org/downloads/
2. Install Git
    1. Download and install Git from https://git-scm.com/downloads
3. Clone the Repository
    1. Open a terminal or command prompt.
    2. Run:
    git clone https://github.com/reecem02/relational_db.git
4. Change to the Project Directory
    1. Navigate to the project folder:
    cd relational_db
5. Install Python Dependencies
    1. Run:
    pip install -r requirements.txt
    2. If you get a permissions error, try:
    pip install --user -r requirements.txt
6. Create the SQL database file
    1. Inside the database folder, create a file called “fungal_db.sqlite”, this is to initialize the database file for your local machine 

---

## Troubleshooting

- If you see errors like "No module named 'pandas'", repeat step 5.
    - you can also try to install the exact missing module with “pip install module_name”
- If you see errors about missing files, make sure you are in the correct directory (r_db).
- If you see errors about the database, make sure the database/fungal_db.sqlite file exists (the setup script or first run should create it).

### Using the Database

Welcome to the database beta! To use this database you will need to provide your own files to import into the database (fasta files and/or excel metadata files), and familiarize yourselves with the basic features of the program.

Since this is a beta version, the program is still deep in development. Any issues or errors you encounter are greatly appreciated. All suggestions for ease of use, future feature ideas, or code changes are welcome as well. Please message Reece M on discord (you can find my profile in the Uehling Lab discord server).

## How to Use It:

**Using the most current versio**n: Please run “git pull” in the terminal while navigated in the main repository directory.

**Running the Program**: Navigate to the main repository folder (relational_db or fungal_db) and run “python3 main.py”

**Main Functions**:

- **Uploading your files** - Multiple import options:
    - **Standard Excel Import (Option 1):** Import metadata from a single Excel file
        - Run the program and select "Import Data" → "Standard Excel Import"
        - Enter the file path
        - The program will import all metadata columns into the database
    
    - **Standard FASTA Import (Option 2):** Import genomic data from a single FASTA file
        - Run the program and select "Import Data" → "Standard FASTA Import"
        - Enter the file path and the Uehling Lab ID
        - The program will import all sequences into the database
    
    - **Bulk Import with FASTA File Locations (Option 3):** ⭐ **NEW FEATURE**
        - Import metadata AND corresponding FASTA files in one operation
        - Prepare an Excel file with all required metadata columns PLUS a "Primary Assembly Filename" column
        - The "Primary Assembly Filename" column should contain paths to FASTA files (absolute or relative to Excel file)
        - Run the program and select "Import Data" → "Bulk Import"
        - Enter the Excel file path
        - The program will:
          - Import metadata for all rows
          - Automatically find and import FASTA files for each genome
          - Prompt you if duplicates are found (Skip/Replace/Stop)
          - Report success/failures with a summary
        - **Example Excel structure:**
          | Uehling Lab ID | Sample Location | ... metadata columns ... | Primary Assembly Filename |
          | UL001 | Plate A | ... | ./genomes/genome1.fasta |
          | UL002 | Plate A | ... | /nfs6/BPP/data/genome2.fasta |
    
    - **Folder Import (Option 4):** Import all Excel or FASTA files from a directory
        - Run the program and select "Import Data" → "Folder Import"
        - Choose to import all Excel files OR all FASTA files from a folder
        - The program will process all files of the selected type
    
- **Searching your files**:
    - Run the program
    - Search for the Lab ID, keyword, or specific information in the imported files
    - There will be a terminal output from your search, and you will be prompted if you want to export that information
- Exporting your files:
    - After a search, you will be prompted if you want to export that information
    - You can select what file format you want to export as
    - Select where you want it exported. If you select default, the exported file will go into the “exported_files” folder
    - If your search was a keyword match, select if you want both metadata and fasta info exported, or only one of the two
    - Name the export file (including the file extension), and then you should see the file in your destination folder
- Deleting your files:
    - Search for the Uehling Lab ID you want to delete, the terminal will output the data stored under that ID
    - Then select what Uehling Lab ID information (metadata and/or fasta data) you want to delete

---

## Bulk Import Feature Guide

### Overview
The Bulk Import feature allows you to upload an Excel file with metadata and FASTA file locations, and the program will automatically import both in a single operation. This is much faster than manually importing metadata and then FASTA files separately.

### Prerequisites for Bulk Import
- Excel file (.xlsx or .xls) with all required metadata columns
- A column named "Primary Assembly Filename" containing FASTA file paths
- FASTA files accessible from the paths specified in the Excel file

### Required Excel Columns
Your Excel file must include all of these columns (in any order):
```
Uehling Lab ID (REQUIRED - this is the unique identifier)
Sample Location Plate
GC3F Submission Sample ID
Alternate ID 1
Alternate ID 2
Lab Unique ID 3
Extracted by
Top ITS Blast Hit
ITS Top Hit Similarity
ITS Taxonomy Comments
Top 16S Blast Hit
16S Top Hit Similarity
16S Taxonomy Comments
Project Funding
Latitude
Longitude
Location ID
DNA Extraction Method
Extraction Date
Primary Assembly Filename (REQUIRED - contains FASTA file paths)
```

### Excel File Setup

#### Example 1: Relative Paths
If your Excel file is in `/data/` and FASTA files are in `/data/genomes/`:

```
Excel: /data/genomes_batch1.xlsx

| Uehling Lab ID | Sample Location | Primary Assembly Filename    |
| UL001          | Plate A         | ./genomes/genome1.fasta      |
| UL002          | Plate A         | ./genomes/genome2.fasta      |
```

The program will resolve `./genomes/genome1.fasta` to `/data/genomes/genome1.fasta`

#### Example 2: Absolute Paths
```
Excel: /data/genomes_batch1.xlsx

| Uehling Lab ID | Sample Location | Primary Assembly Filename               |
| UL001          | Plate A         | /nfs6/BPP/Uehling_Lab/data/genome1.fasta |
| UL002          | Plate A         | /nfs4/BPP/Uehling_Lab/data/genome2.fasta |
```

The program will use paths exactly as specified.

#### Example 3: Mixed Paths
You can mix relative and absolute paths in the same Excel file.

### How to Use Bulk Import

1. **Create your Excel file** with all required columns (see examples above)
2. **Prepare your FASTA files** and note their paths or organize them relative to your Excel file
3. **Run the program:**
   ```
   python3 main.py
   ```
4. **Select option 3** from the Import Data menu: "Bulk Import (Excel + FASTA file locations)"
5. **Enter the Excel file path** when prompted
6. **Handle duplicate lab_ids** when prompted:
   - **1 (Skip):** Keep existing data, skip this import
   - **2 (Replace):** Delete old data, import new data
   - **3 (Stop):** Cancel the entire bulk import
7. **Review the results** - the program will display:
   - Total rows processed
   - Successful metadata imports
   - Successful FASTA imports
   - Any skipped or failed entries with reasons

### Customizing the FASTA Column Name

By default, the program looks for a column named "Primary Assembly Filename". If you want to use a different column name, edit `config/schema.yaml`:

```yaml
bulk_import_config:
  fasta_file_column: "Your Column Name Here"
  
  # Optional: Add alternative column names
  alternative_fasta_columns:
    - "Assembly Filename"
    - "Genome File"
    - "FASTA Path"
```

The program will search for columns in this order: primary first, then alternatives.

### Error Handling

**Missing FASTA Files:**
- The program will warn you and skip that file
- Metadata for that genome will still be imported
- You can manually add the FASTA file later using Standard FASTA Import

**Invalid FASTA Format:**
- The program will warn you and skip that file
- Metadata for that genome will still be imported

**Duplicate Lab IDs:**
- The program will prompt you what to do (Skip/Replace/Stop)
- Your choice is remembered for all subsequent duplicates in that import

### Example Test Files

The repository includes example files for testing:
- **Excel file:** `example_files/bulk_import_example.xlsx`
- **FASTA files:** `example_files/genomes/genome1.fasta`, `genome2.fasta`, `genome3.fasta`

To test:
```
1. Run: python3 main.py
2. Select: Import Data → Bulk Import
3. Enter: bulk_import_example.xlsx
4. The example uses relative paths (./genomes/...) which should work automatically
```

### Creating Your Own Example Files

If you need to regenerate the example files, run:
```
python3 tools/create_bulk_import_example.py
```

---

## Configuration Files

### schema.yaml
Defines:
- Required metadata columns
- Genomic data column names
- **NEW:** Bulk import configuration (FASTA column name, path resolution strategy)

Edit this file to customize your import settings.

### config.yaml
Defines the database location and file paths.

---
