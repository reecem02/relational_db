#!/usr/bin/env python3
"""
End-to-end test: Simulate complete workflow through the main menu
"""

import sys
from io import StringIO
from unittest.mock import patch
import os

def test_e2e_workflow():
    """
    Simulate: Search → Export → Verify
    """
    print("=" * 70)
    print("END-TO-END TEST: Complete Workflow Simulation")
    print("=" * 70)
    
    # Import after we've verified no import errors
    from modules.search import search_db
    from modules.export_utils import export_fasta_per_lab_id
    
    # Test Case 1: Search and export
    print("\n[TEST 1] Search for U1513A and verify multi-lab detection")
    print("-" * 70)
    
    results = search_db("U1513A")
    
    if results is None:
        print("✗ FAILED: search_db returned None")
        return False
    
    if results.empty:
        print("✗ FAILED: No results returned")
        return False
    
    unique_lab_ids = results['lab_id'].unique()
    fasta_data = results[results['type'] == 'fasta']
    
    print(f"✓ Search successful")
    print(f"  - Unique lab_ids: {len(unique_lab_ids)}")
    print(f"  - FASTA sequences: {len(fasta_data):,}")
    print(f"  - Lab IDs: {', '.join(sorted(unique_lab_ids))}")
    
    # Test Case 2: Verify multi-lab detection logic
    if len(unique_lab_ids) > 1:
        print("✓ Multi-lab scenario detected: EXPORT MODE = PER-LAB")
    else:
        print("✗ FAILED: Expected multiple lab_ids")
        return False
    
    # Test Case 3: Export to folder
    print("\n[TEST 2] Execute per-lab export")
    print("-" * 70)
    
    test_folder = 'exported_files/e2e_test_export'
    
    # Clean up if exists
    import shutil
    if os.path.exists(test_folder):
        shutil.rmtree(test_folder)
    
    try:
        created_files = export_fasta_per_lab_id(results, test_folder)
    except Exception as e:
        print(f"✗ FAILED: Export raised exception: {e}")
        return False
    
    if not created_files:
        print("✗ FAILED: No files created")
        return False
    
    print(f"✓ Export successful")
    print(f"  - Files created: {len(created_files)}")
    
    # Test Case 4: Verify file integrity
    print("\n[TEST 3] Verify exported file integrity")
    print("-" * 70)
    
    all_valid = True
    total_sequences = 0
    
    for file_path in sorted(created_files):
        if not os.path.exists(file_path):
            print(f"✗ File not found: {file_path}")
            all_valid = False
            continue
        
        filename = os.path.basename(file_path)
        lab_id = filename.split('_')[0]
        
        # Read and validate
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Count sequences
        seq_count = len([l for l in lines if l.startswith('>')])
        total_sequences += seq_count
        
        # Verify lab_id prefix
        headers = [l.strip() for l in lines if l.startswith('>')]
        correct_prefix = all(h.startswith(f'>{lab_id}_') for h in headers)
        
        if correct_prefix and seq_count > 0:
            print(f"✓ {filename}: {seq_count:,} sequences, proper prefixing")
        else:
            print(f"✗ {filename}: Invalid format or prefix")
            all_valid = False
    
    if all_valid and total_sequences > 0:
        print(f"\n✓ Total sequences across all files: {total_sequences:,}")
    else:
        print("✗ FAILED: File validation failed")
        return False
    
    # Test Case 5: Verify pipelines compatibility
    print("\n[TEST 4] Verify phylogenetic pipeline compatibility")
    print("-" * 70)
    
    sample_file = created_files[0] if created_files else None
    if sample_file:
        with open(sample_file, 'r') as f:
            content = f.read(500)
        
        # Check for FASTA markers
        has_headers = '>' in content
        has_sequences = any(c in content for c in 'ATGCN')
        
        if has_headers and has_sequences:
            print("✓ FASTA format valid: Contains headers and sequences")
            print("✓ Ready for phylogenetic pipeline")
        else:
            print("✗ FAILED: Invalid FASTA format")
            return False
    
    # Summary
    print("\n" + "=" * 70)
    print("✓ END-TO-END TEST PASSED")
    print("=" * 70)
    print(f"✓ Exported {len(created_files)} properly formatted files")
    print(f"✓ Total {total_sequences:,} sequences across all files") 
    print(f"✓ All files ready for phylogenetic pipeline")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = test_e2e_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
