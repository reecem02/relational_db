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

- Uploading your files:
    - Before running the program, copy files you want to upload into the database into the example_files folder
    - Run the program
    - Select Import Data and the data type of the file you want to import into the database
    - Enter the file name of the file to import, and if it’s a fasta file enter the Uehling Lab ID
    - This should import your selected file into the database. If there are any issues please document and report it.
- Searching your files:
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