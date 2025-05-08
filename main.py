from modules.data_import import import_metadata, import_fasta
from modules.data_output import display_data_by_lab_id, print_row_key_value
from modules.search import search_db
from modules.db_info import get_database_info  # Import the new function


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

    # Perform the search
    results = search_db(search_term)

    if results.empty:
        print(f"No results found for: {search_term}")
        return

    # Display the first 5 results
    print("\n-- Search Results (First 5 Entries) --")
    for _, row in results.head(5).iterrows():
        print_row_key_value(row.to_dict())

    # Check if there are more results
    if len(results) > 5:
        print("\nMore than 5 results found.")
        choice = input("Would you like to [1] View all results or [2] Export to Excel? (1/2): ").strip()
        if choice == "1":
            print("\n-- All Search Results --")
            for _, row in results.iterrows():
                print_row_key_value(row.to_dict())
        elif choice == "2":
            file_name = input("Enter the file name to save the results (e.g., results.xlsx): ").strip()
            results.to_excel(file_name, index=False)
            print(f"Results exported to {file_name}.")

def export_data_ui():
    print("\n-- Export Data --")
    print("This feature allows exporting search results to CSV.")
    file_name = input("Enter a name for the export file (e.g., results.csv):\n> ").strip()
    if hasattr(export_data_ui, "last_results") and export_data_ui.last_results is not None:
        export_data_ui.last_results.to_csv(file_name, index=False)
        print(f"Results exported to {file_name}.")
    else:
        print("No data available to export. Please run a search first.")


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


def export_prompt(results):
    if not results.empty:
        choice = input("\nWould you like to export these results? (y/n): ").strip().lower()
        if choice == 'y':
            export_data_ui()

def main():
    while True:
        print("\nWelcome to the Fungal Research Database")
        print("1) Import Data")
        print("2) Search Data")
        print("3) Export Data")
        print("4) Help")
        print("5) Database Information")
        print("6) Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            import_data_ui()
        elif choice == "2":
            search_data_ui()
        elif choice == "3":
            export_data_ui()
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
