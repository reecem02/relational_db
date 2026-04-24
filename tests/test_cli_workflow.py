#!/usr/bin/env python3
"""
Automated test of the complete multi-lab export workflow
"""

import os
import shutil
from unittest.mock import patch
from io import StringIO

def test_cli_workflow():
    print("=" * 80)
    print("TESTING: Complete Multi-Lab Export Workflow")
    print("=" * 80)
    
    # Import after path is set
    from modules.search import search_db
    from main import export_prompt
    
    # Step 1: Search
    print("\n[STEP 1] Searching for 'U1513A'...")
    results = search_db("U1513A")
    
    if results.empty:
        print("✗ FAILED: No results")
        return False
    
    print(f"✓ Found {len(results)} total rows")
    fasta_rows = results[results['type'] == 'fasta']
    print(f"✓ Contains {len(fasta_rows)} FASTA sequences from {len(results['lab_id'].unique())} lab_ids")
    
    # Step 2: Simulate export prompt with user choices
    print("\n[STEP 2] Simulating user export choices...")
    
    # Simulate user input: y, 4 (FASTA), d (default folder), u1513a_phylo, <EOF>
    user_inputs = [
        'y',                          # Export? yes
        '4',                          # Format: FASTA
        'd',                          # Default folder
        'automated_test_u1513a'       # Folder name
    ]
    
    print("User inputs simulated:")
    print(f"  1. Export results? {user_inputs[0]}")
    print(f"  2. Export format? {user_inputs[1]} (FASTA)")
    print(f"  3. Folder location? {user_inputs[2]} (default)")
    print(f"  4. Folder name? {user_inputs[3]}")
    
    with patch('builtins.input', side_effect=user_inputs):
        print("\n→ Executing export_prompt()...")
        export_prompt(results)
    
    # Step 3: Verify output
    print("\n[STEP 3] Verifying export output...")
    
    export_folder = 'exported_files/automated_test_u1513a'
    if not os.path.exists(export_folder):
        print(f"✗ FAILED: Folder not created at {export_folder}")
        return False
    
    files = sorted([f for f in os.listdir(export_folder) if f.endswith('.fasta')])
    if len(files) < 5:
        print(f"✗ FAILED: Only created {len(files)} files instead of 5")
        for f in files:
            print(f"  - {f}")
        return False
    
    print(f"✓ Created {len(files)} FASTA files:")
    for filename in files:
        filepath = os.path.join(export_folder, filename)
        filesize = os.path.getsize(filepath)
        with open(filepath, 'r') as f:
            seq_count = len([line for line in f if line.startswith('>')])
        print(f"  ✓ {filename}: {seq_count:,} sequences ({filesize:,} bytes)")
    
    # Step 4: Verify each file has correct data
    print("\n[STEP 4] Validating file integrity...")
    all_valid = True
    for filename in files:
        filepath = os.path.join(export_folder, filename)
        lab_id = filename.split('_')[0]
        
        with open(filepath, 'r') as f:
            headers = [line.strip() for line in f if line.startswith('>')]
        
        correct_prefix = all(h.startswith(f'>{lab_id}_') for h in headers)
        if correct_prefix:
            print(f"  ✓ {lab_id}: All headers correctly prefixed")
        else:
            print(f"  ✗ {lab_id}: Wrong header prefix detected")
            all_valid = False
    
    # Summary
    print("\n" + "=" * 80)
    if all_valid and len(files) == 5:
        print("✓ SUCCESS: Multi-lab export workflow complete!")
        print("=" * 80)
        print(f"Output folder: {export_folder}")
        print(f"✓ 5 separate files created")
        print(f"✓ Each file formatted for phylogenetic pipeline")
        print(f"✓ Ready for phylogenetic analysis")
        return True
    else:
        print("✗ FAILED: Workflow incomplete or validation failed")
        return False

if __name__ == "__main__":
    try:
        success = test_cli_workflow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
