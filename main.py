import os
from modules.data_import import import_metadata, import_fasta
from modules.data_output import display_data_by_lab_id, print_row_key_value
from modules.search import search_db
from modules.db_info import get_database_info  # Import the new function
from modules.delete import delete_lab_id, delete_metadata, delete_fasta
from modules.delete import display_lab_id_data
from modules.export_utils import select_rows, export_table, export_pretty


def import_data_ui():
    print("\n--Import Data--")
    file_type = input("Select file type: 1)Excel  2)Fasta\n")
    file_name = input("Enter file name (including file extention): ")
    file_path = "example_files/" + file_name
    print(f"File type: {file_type}")
    print(f"File path: {file_path}")

    if file_type.lower() == "excel" or file_type == "1":
        import_metadata(file_path)
    elif file_type.lower() == "fasta" or file_type == "2":
        import_fasta(file_path)
    else:  
        print("Unknown file type. Please select 1 or 2.")

def search_data_ui():
    print("\n-- Search Data --")
    search_term = input("Enter a keyword to search: ").strip()

    if not search_term:
        print("Search term cannot be empty.")
        return

    results = search_db(search_term)

    if results.empty:
        print("No results found.")
        return

    export_prompt(results)


def export_prompt(results):
    if results.empty:
        return
    choice = input("\nWould you like to export these results? (y/n): ").strip().lower()
    if choice != 'y':
        return

    # Select rows to export
    export_df = select_rows(results)

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
        export_table(export_df, file_path, file_type, append=append)
    else:
        export_pretty(export_df, file_path, append=append)

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
    print("3) Export Data: Save search results as CSV after running a query.")
    print("4) Exit: Quit the program.")
    return

def display_results(results):
    if results.empty:
        print("No results found.")
    else:
        print("\n-- Search Results --")
        for _, row in results.iterrows():
            print_row_key_value(row.to_dict())

        # Save results for export
        export_data_ui.last_results = results

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
    main()
