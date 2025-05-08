def print_row_key_value(row_dict, title="Row Data"):
    """
    Prints a dictionary (like a row of metadata) in a vertically aligned format.
    """
    print(f"\n--- {title} ---")
    max_len = max(len(str(key)) for key in row_dict.keys())
    for key, value in row_dict.items():
        print(f"{key:<{max_len}} | {value}")
