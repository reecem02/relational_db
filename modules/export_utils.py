import os
import pandas as pd

def export_table(df, file_path, file_type, append=False):
    # Pivot the data: rows are lab_ids, columns are keys
    if 'lab_id' in df.columns and 'key' in df.columns and 'value' in df.columns:
        # Create pivot table with lab_id as rows and keys as columns
        pivoted_df = df.pivot_table(
            index='lab_id',
            columns='key',
            values='value',
            aggfunc='first'  # Use first value if there are duplicates
        )
        # Reset index to make lab_id a regular column
        pivoted_df = pivoted_df.reset_index()
        export_df = pivoted_df
    else:
        # If the structure is different, use the original dataframe
        export_df = df
    
    if file_type == 'csv':
        if append and os.path.exists(file_path):
            export_df.to_csv(file_path, mode='a', header=False, index=False)
        else:
            export_df.to_csv(file_path, index=False)
    elif file_type == 'excel':
        if append and os.path.exists(file_path):
            # Append to first sheet
            with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
                startrow = writer.sheets['Sheet1'].max_row
                export_df.to_excel(writer, index=False, header=False, startrow=startrow)
        else:
            export_df.to_excel(file_path, index=False)
    print(f"Exported table to {file_path}")

def export_fasta(df, file_path, append=False):
    """
    Export FASTA sequences only (pure FASTA format for phylogenetic tools).
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

def export_fasta_per_lab_id(df, folder_path):
    """
    Export pure FASTA sequences to separate files, one for each unique lab_id.
    Each file contains all sequences for that genome/lab_id in standard FASTA format.
    Compatible with tools like Sourmash for phylogenetic analysis.
    
    Args:
        df: DataFrame with columns 'lab_id', 'type', 'key', 'value'
        folder_path: Directory where files will be created (one per lab_id)
    
    Returns:
        List of created file paths
    """
    os.makedirs(folder_path, exist_ok=True)
    
    if 'lab_id' not in df.columns:
        print("Error: DataFrame must contain 'lab_id' column")
        return []
    
    fasta_data = df[df['type'] == 'fasta']
    
    if fasta_data.empty:
        print("No FASTA sequences found to export")
        return []
    
    created_files = []
    unique_lab_ids = fasta_data['lab_id'].unique()
    
    print(f"\nExporting FASTA sequences for {len(unique_lab_ids)} lab_ids:")
    
    for lab_id in unique_lab_ids:
        lab_data = fasta_data[fasta_data['lab_id'] == lab_id]
        seq_count = len(lab_data)
        
        # Create file name (pure FASTA format, no tool-specific suffix)
        file_name = f"{lab_id}.fasta"
        file_path = os.path.join(folder_path, file_name)
        
        # Write FASTA file in pure format
        with open(file_path, 'w', encoding='utf-8') as f:
            for _, row in lab_data.iterrows():
                seq = str(row['value'])
                # Write header (pure FASTA, no lab_id prefix)
                f.write(f">{row['key']}\n")
                # Write sequence in 80-character lines (standard FASTA)
                for i in range(0, len(seq), 80):
                    f.write(seq[i:i+80] + "\n")
        
        created_files.append(file_path)
        print(f"  ✓ {file_name} ({seq_count:,} sequences)")
    
    print(f"\nSuccessfully exported {len(created_files)} files to: {folder_path}")
    return created_files

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