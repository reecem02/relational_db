#!/usr/bin/env python3
"""
Test script to verify phylogenetic FASTA export works for multiple matched lab_ids
"""

from modules.search import search_db
from modules.export_utils import export_fasta, export_fasta_per_lab_id
import os
import shutil

def test_multi_lab_export():
    print("=" * 70)
    print("Testing Multi-Lab ID Export for U1513A")
    print("=" * 70)
    
    # Search for U1513A
    print("\n[1] Searching for 'U1513A'...")
    results = search_db("U1513A")
    
    if results is None or results.empty:
        print("ERROR: No results returned!")
        return
    
    # Show summary
    unique_lab_ids = results['lab_id'].unique()
    fasta_rows = results[results['type'] == 'fasta']
    
    print(f"\n✓ Search returned {len(results)} total rows")
    print(f"✓ Unique lab_ids: {list(unique_lab_ids)}")
    print(f"✓ FASTA sequences: {len(fasta_rows):,}")
    
    # Test 1: Current single-file export
    print("\n" + "=" * 70)
    print("[TEST 1] Current export_fasta() - Single file for all results")
    print("=" * 70)
    
    os.makedirs('exported_files', exist_ok=True)
    test_file_single = 'exported_files/test_u1513a_single.fasta'
    if os.path.exists(test_file_single):
        os.remove(test_file_single)
    
    export_fasta(results, test_file_single)
    
    if os.path.exists(test_file_single):
        file_size = os.path.getsize(test_file_single)
        with open(test_file_single, 'r') as f:
            headers = len([line for line in f if line.startswith('>')])
        print(f"✓ Single export: {headers:,} sequences, {file_size:,} bytes")
    
    # Test 2: New per-lab export
    print("\n" + "=" * 70)
    print("[TEST 2] New export_fasta_per_lab_id() - One file per lab_id")
    print("=" * 70)
    
    test_folder = 'exported_files/test_u1513a_per_lab'
    if os.path.exists(test_folder):
        shutil.rmtree(test_folder)
    
    created_files = export_fasta_per_lab_id(results, test_folder)
    
    # Verify the exported files
    print("\nFile verification:")
    total_sequences = 0
    for file_path in sorted(created_files):
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            with open(file_path, 'r') as f:
                headers = len([line for line in f if line.startswith('>')])
            total_sequences += headers
            print(f"  ✓ {os.path.basename(file_path)}: {headers:,} sequences, {file_size:,} bytes")
            
            # Show first few headers
            with open(file_path, 'r') as f:
                first_headers = [line.strip() for line in f if line.startswith('>')][:2]
            print(f"     Sample headers: {first_headers}")
    
    print(f"\nTotal sequences across all files: {total_sequences:,}")
    
    # Test 3: Verify each file has only its lab_id's sequences
    print("\n" + "=" * 70)
    print("[TEST 3] Verifying data isolation per lab_id")
    print("=" * 70)
    
    all_correct = True
    for file_path in sorted(created_files):
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            lab_id = filename.split('_')[0]  # Extract lab_id from filename
            
            with open(file_path, 'r') as f:
                headers = [line.strip() for line in f if line.startswith('>')]
            
            # Check all headers start with the correct lab_id
            headers_with_correct_lab = [h for h in headers if h.startswith(f'>{lab_id}_')]
            if len(headers_with_correct_lab) == len(headers):
                print(f"  ✓ {lab_id}: All {len(headers):,} sequences properly prefixed")
            else:
                print(f"  ✗ {lab_id}: MISMATCH - {len(headers_with_correct_lab)}/{len(headers)} sequences have correct prefix")
                all_correct = False
    
    print("\n" + "=" * 70)
    if all_correct:
        print("✓ SUCCESS: All tests passed!")
    else:
        print("✗ FAILURE: Some verification checks failed")
    print("=" * 70)

if __name__ == "__main__":
    test_multi_lab_export()
