import os
import pandas as pd

def export_table(df, file_path, file_type, append=False):
    if file_type == 'csv':
        if append and os.path.exists(file_path):
            df.to_csv(file_path, mode='a', header=False, index=False)
        else:
            df.to_csv(file_path, index=False)
    elif file_type == 'excel':
        if append and os.path.exists(file_path):
            # Append to first sheet
            with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
                startrow = writer.sheets['Sheet1'].max_row
                df.to_excel(writer, index=False, header=False, startrow=startrow)
        else:
            df.to_excel(file_path, index=False)
    print(f"Exported table to {file_path}")

def export_fasta(df, file_path, append=False):
    """
    Export FASTA sequences only (pure FASTA format for tools like Barrnap).
    Strips out metadata and exports only sequences with headers.
    """
    mode = 'a' if append and os.path.exists(file_path) else 'w'
    with open(file_path, mode, encoding='utf-8') as f:
        fasta = df[df['type'] == 'fasta']
        if not fasta.empty:
            for _, row in fasta.iterrows():
                seq = str(row['value'])
                # Write header
                f.write(f">{row['key']}\n")
                # Write sequence in 80-character lines (standard FASTA)
                for i in range(0, len(seq), 80):
                    f.write(seq[i:i+80] + "\n")
    print(f"Exported FASTA sequences to {file_path}")

def export_pretty(df, file_path, append=False):
    mode = 'a' if append and os.path.exists(file_path) else 'w'
    with open(file_path, mode, encoding='utf-8') as f:
        # Metadata section
        metadata = df[df['type'] == 'metadata']
        if not metadata.empty:
            f.write("\nMetadata:\n")
            # Format as a two-column table, no index
            col_width = max(metadata['key'].astype(str).map(len).max(), len('key')) + 2
            f.write(f"{'key'.ljust(col_width)}value\n")
            for _, row in metadata.iterrows():
                f.write(f"{str(row['key']).ljust(col_width)}{row['value']}\n")
            f.write("\n")
        # FASTA section
        fasta = df[df['type'] == 'fasta']
        if not fasta.empty:
            f.write("FASTA sequences (first 2 lines of each):\n")
            for _, row in fasta.iterrows():
                seq = str(row['value'])
                lines = [seq[i:i+60] for i in range(0, len(seq), 60)]
                f.write(f">{row['key']}\n")
                for l in lines:
                    f.write(l + "\n")
    print(f"Exported to {file_path}")