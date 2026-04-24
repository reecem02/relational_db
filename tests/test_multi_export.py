#!/usr/bin/env python3
"""
Test script to verify phylogenetic FASTA export for multiple matched lab_ids
"""

from modules.search import search_db
from modules.export_utils import export_fasta
import os
import pandas as pd

def test_multi_lab_export():
    print("=" * 60)
    print("Testing Multi-Lab ID Export for U1513A")
    print("=" * 60)
    
    # Search for U1513A
    print("\n[1] Searching for 'U1513A'...")
    results = search_db("U1513A")
    
    print(f"\nSearch returned {len(results)} rows")
    print(f"Columns: {results.columns.tolist()}")
    
    # Show unique lab_ids in results
    if 'lab_id' in results.columns:
        unique_lab_ids = results['lab_id'].unique()
        print(f"\nUnique lab_ids in results: {unique_lab_ids}")
        print(f"Total unique lab_ids: {len(unique_lab_ids)}")
        
        # Show count of fasta vs metadata rows per lab_id
        if 'type' in results.columns:
            print("\nBreakdown by type:")
            for lab_id in unique_lab_ids:
                lab_data = results[results['lab_id'] == lab_id]
                metadata_count = len(lab_data[lab_data['type'] == 'metadata'])
                fasta_count = len(lab_data[lab_data['type'] == 'fasta'])
                print(f"  {lab_id}: {metadata_count} metadata rows, {fasta_count} FASTA rows")
    
    # Test current export behavior
    print("\n[2] Testing current export_fasta() with all results...")
    os.makedirs('exported_files', exist_ok=True)
    test_file = 'exported_files/test_u1513a_current.fasta'
    if os.path.exists(test_file):
        os.remove(test_file)
    
    export_fasta(results, test_file)
    
    # Check what was exported
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Count headers and sequences
        headers = [line for line in content.split('\n') if line.startswith('>')]
        print(f"\nExported file contains {len(headers)} sequences")
        print(f"File size: {os.path.getsize(test_file)} bytes")
        
        print("\nHeaders in exported file:")
        for header in headers[:10]:  # Show first 10
            print(f"  {header}")
        if len(headers) > 10:
            print(f"  ... and {len(headers) - 10} more")
    
    print("\n" + "=" * 60)
    print("ANALYSIS: Current implementation exports all results to single file")
    print("NEEDED: Export one file per lab_id with only that lab_id's sequences")
    print("=" * 60)

if __name__ == "__main__":
    test_multi_lab_export()
