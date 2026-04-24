#!/usr/bin/env python3
"""
Interactive test to verify the export prompt works correctly
"""

import sys
from io import StringIO
from modules.search import search_db
from modules.export_utils import export_fasta, export_fasta_per_lab_id
import os
import shutil

def simulate_export_prompt(results, choice_format='4', choice_location='d', folder_name='test_interactive_export'):
    """
    Simulate user choices in the export_prompt function
    """
    if results.empty:
        return
    
    # Simulate the export prompt logic
    unique_lab_ids = []
    if 'lab_id' in results.columns:
        unique_lab_ids = results['lab_id'].unique()
    
    print(f"\nSimulating export prompt with {len(unique_lab_ids)} unique lab_ids...")
    print(f"User choices: format={choice_format}, location={choice_location}, folder={folder_name}\n")
    
    # Determine export type
    if len(unique_lab_ids) > 1 and choice_format == '4':
        print("→ Multi-lab FASTA detection: Activating per-lab export mode")
        
        # Simulate folder selection
        if choice_location == 'd':
            os.makedirs('exported_files', exist_ok=True)
            folder_path = os.path.join('exported_files', folder_name)
        else:
            folder_path = folder_name
        
        # Export with new per-lab function
        print(f"→ Exporting to folder: {folder_path}")
        created_files = export_fasta_per_lab_id(results, folder_path)
        
        return created_files
    else:
        print("→ Single-file FASTA export")
        return None

def test_interactive_flow():
    print("=" * 70)
    print("Interactive Test: Multi-Lab U1513A Export Flow")
    print("=" * 70)
    
    # Search
    print("\n[STEP 1] Searching for 'U1513A'...")
    results = search_db("U1513A")
    
    if results is None or results.empty:
        print("ERROR: No results!")
        return
    
    unique_lab_ids = results['lab_id'].unique()
    print(f"✓ Found {len(unique_lab_ids)} lab_ids: {', '.join(unique_lab_ids)}")
    
    # Test different export scenarios on the same results
    scenarios = [
        {
            'name': 'Default folder with sub-folder',
            'format': '4',  # FASTA
            'location': 'd',  # Default folder
            'folder_name': 'u1513a_phylo_export'
        },
        {
            'name': 'Custom folder path',
            'format': '4',
            'location': 'c',  # Custom
            'folder_name': '/tmp/test_phylo_export'
        }
    ]
    
    all_created_files = []
    
    for scenario in scenarios:
        print("\n" + "=" * 70)
        print(f"[SCENARIO] {scenario['name']}")
        print("=" * 70)
        
        created = simulate_export_prompt(
            results,
            choice_format=scenario['format'],
            choice_location=scenario['location'],
            folder_name=scenario['folder_name']
        )
        
        if created:
            all_created_files.extend(created)
            
            # Verify export
            print(f"\n✓ Export created {len(created)} files")
            for f in created:
                if os.path.exists(f):
                    size = os.path.getsize(f)
                    with open(f, 'r') as fp:
                        seq_count = len([line for line in fp if line.startswith('>')])
                    print(f"  - {os.path.basename(f)}: {seq_count:,} sequences ({size:,} bytes)")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✓ Total files created: {len(all_created_files)}")
    print(f"✓ All files exist: {all(os.path.exists(f) for f in all_created_files)}")
    
    # Check phylogenetic tool compatibility
    print("\n✓ PHYLOGENETIC EXPORT COMPATIBILITY CHECK:")
    sample_file = all_created_files[0] if all_created_files else None
    if sample_file:
        with open(sample_file, 'r') as f:
            lines = f.readlines()[:10]
        print(f"  Sample file: {os.path.basename(sample_file)}")
        print(f"  First 5 lines (valid FASTA format):")
        for line in lines[:5]:
            if line.startswith('>'):
                print(f"    HEADER: {line.strip()}")
            else:
                print(f"    SEQ:    {line.strip()[:60]}..." if len(line.strip()) > 60 else f"    SEQ:    {line.strip()}")

if __name__ == "__main__":
    test_interactive_flow()
