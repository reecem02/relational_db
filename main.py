from modules.data_import import import_metadata, import_fasta, import_bulk_with_fasta
from modules.data_output import display_data_by_lab_id, print_row_key_value
from modules.search import search_db
from modules.db_info import get_database_info  # Import the new function
from modules.delete import delete_lab_id, delete_metadata, delete_fasta
from modules.delete import display_lab_id_data
from modules.export_utils import export_table, export_pretty
import os
import sqlite3

def initialize_database():
    db_path = "database/fungal_db.sqlite"
    schema_path = "database/schema.sql"
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if Metadata table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Metadata';")
    exists = cursor.fetchone()
    # Check if GenomicData table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='GenomicData';")
    exists_genomic = cursor.fetchone()

    if not exists:
        print("Initializing database schema...")
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        print("Database initialized.")
    conn.close()

def import_data_ui():
    print("\n--Import Data--")
    print("1) Standard Excel Import (metadata only)")
    print("2) Standard FASTA Import (single genome)")
    print("3) Bulk Import (Excel + FASTA file locations)")
    print("4) Folder Import (all Excel or FASTA from directory)")
    
    choice = input("Select import type (1/2/3/4): ").strip()
    
    if choice == "1":
        # Standard Excel Import
        file_name = input("Enter file name (including file extention) or full path: ").strip()
        if os.path.isabs(file_name) or os.path.exists(file_name):
            file_path = file_name
        else:
            file_path = os.path.join('example_files', file_name)
        
        print(f"Importing Excel metadata from: {file_path}")
        import_metadata(file_path)
    
    elif choice == "2":
        # Standard FASTA Import
        file_name = input("Enter file name (including file extention) or full path: ").strip()
        if os.path.isabs(file_name) or os.path.exists(file_name):
            file_path = file_name
        else:
            file_path = os.path.join('example_files', file_name)
        
        print(f"Importing FASTA from: {file_path}")
        import_fasta(file_path)
    
    elif choice == "3":
        # Bulk Import with FASTA locations
        file_name = input("Enter Excel file name (including extension) or full path: ").strip()
        if os.path.isabs(file_name) or os.path.exists(file_name):
            file_path = file_name
        else:
            file_path = os.path.join('example_files', file_name)
        
        import_bulk_with_fasta(file_path)
    
    elif choice == "4":
        # Folder Import
        file_type = input("Import [e]xcel files or [f]asta files from folder? (e/f): ").strip().lower()
        folder = input("Enter folder path (absolute or relative): ").strip()
        file_path = os.path.expanduser(folder)
        
        if file_type == "e" or file_type == "excel":
            from modules.data_import import import_metadata_from_folder
            import_metadata_from_folder(file_path)
        elif file_type == "f" or file_type == "fasta":
            from modules.data_import import import_fasta_from_folder
            import_fasta_from_folder(file_path)
        else:
            print("Invalid choice. Please select 'e' or 'f'.")
    
    else:
        print("Invalid choice. Please select 1, 2, 3, or 4.")

def search_data_ui():
    print("\n-- Search Data --")
    search_term = input("Enter a keyword to search: ").strip()

    if not search_term:
        print("Search term cannot be empty.")
        return

    # Perform the search
    results = search_db(search_term)

    if results.empty:
        print("No results found.")
        return

    # Prompt user to export results
    export_prompt(results)


def export_prompt(results):
    if results.empty:
        return
    choice = input("\nWould you like to export these results? (y/n): ").strip().lower()
    if choice != 'y':
        return

    # Choose format
    fmt = input("Export as [1] CSV, [2] Excel, or [3] TXT? (1/2/3): ").strip()
    if fmt == '1':
        ext, file_type = 'csv', 'csv'
    elif fmt == '2':
        ext, file_type = 'xlsx', 'excel'
    elif fmt == '3':
        ext, file_type = 'txt', 'txt'
    else:
        print("Invalid format, exporting as CSV.")
        ext, file_type = 'csv', 'csv'

    # Choose location
    folder = input("Export to [d]efault folder (exported_files/) or [c]ustom path? (d/c): ").strip().lower()
    if folder == 'd':
        os.makedirs('exported_files', exist_ok=True)
        file_name = input(f"Enter file name (.{ext} will be added if not present): ").strip()
        if not file_name.endswith(f".{ext}"):
            file_name += f".{ext}"
        file_path = os.path.join('exported_files', file_name)
    else:
        file_path = input(f"Enter full file path (including .{ext}): ").strip()

    # Append or overwrite
    append = False
    if os.path.exists(file_path):
        ao = input("File exists. [a]ppend or [o]verwrite? (a/o): ").strip().lower()
        append = (ao == 'a')

    # Export
    if file_type in ('csv', 'excel'):
        export_table(results, file_path, file_type, append=append)
    else:
        export_pretty(results, file_path, append=append)

def delete_data_ui():
    print("\n-- Delete Data --")
    lab_id = input("Enter the Uehling Lab ID to delete (e.g., UL001): ").strip()
    if not lab_id:
        print("Lab ID cannot be empty.")
        return

    # Show current data for confirmation
    print("\nCurrent data for this Lab ID:")
    display_lab_id_data(lab_id)

    print("\nWhat would you like to delete?")
    print("1) Delete the ENTIRE Uehling Lab ID (all metadata and FASTA data)")
    print("2) Delete ONLY the METADATA for this Lab ID")
    print("3) Delete ONLY the FASTA data for this Lab ID")
    print("4) Return to main menu")
    choice = input("Enter your choice (1/2/3/4): ").strip()

    if choice == "1":
        confirm = input(f"Are you sure you want to permanently delete ALL data for Lab ID '{lab_id}'? (y/n): ").strip().lower()
        if confirm == "y":
            delete_lab_id(lab_id)
            print(f"All data for Lab ID '{lab_id}' has been deleted.")
    elif choice == "2":
        confirm = input(f"Are you sure you want to permanently delete ONLY the METADATA for Lab ID '{lab_id}'? (y/n): ").strip().lower()
        if confirm == "y":
            delete_metadata(lab_id)
            print(f"Metadata for Lab ID '{lab_id}' has been deleted.")
    elif choice == "3":
        confirm = input(f"Are you sure you want to permanently delete ONLY the FASTA data for Lab ID '{lab_id}'? (y/n): ").strip().lower()
        if confirm == "y":
            delete_fasta(lab_id)
            print(f"FASTA data for Lab ID '{lab_id}' has been deleted.")
    elif choice == "4":
        print("Returning to main menu.")
    else:
        print("Invalid choice. Returning to main menu.")


def help_ui():
    print("\n-- Help --")
    print("1) Import Data: Upload Excel or Fasta files from the example_files folder.")
    print("2) Search Data: Find entries by lab ID, extraction method, or date.")
    print("3) Delete Data: Search a lab ID you want to delete, then select what information you want to deelte.")
    print("5) Database Information: View amount of entries in metadata and genomic data tables, last uploaded date, and total database size.")
    print("6) Exit: Quit the program.")
    return

def main():
    while True:
        print("\nWelcome to the Fungal Research Database")
        print("1) Import Data")
        print("2) Search Data")
        print("3) Delete Data")
        print("4) Help")
        print("5) Database Information")
        print("6) Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            import_data_ui()
        elif choice == "2":
            search_data_ui()
        elif choice == "3":
            delete_data_ui()
        elif choice == "4":
            help_ui()
        elif choice == "5":
            get_database_info()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    initialize_database()
    main()
