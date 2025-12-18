#!/usr/bin/env python3
"""
Script to generate bulk_import_example.xlsx for testing the bulk import feature.

This creates an Excel file with example genomes and their corresponding FASTA file paths.
Run this script from the r_db directory.
"""

import pandas as pd
import os

# Get the project root directory (parent of tools/)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Go up one level from tools/
example_files_dir = os.path.join(project_root, 'example_files')
genomes_dir = os.path.join(example_files_dir, 'genomes')

# Create output path
output_path = os.path.join(example_files_dir, 'bulk_import_example.xlsx')

# Relative path from example_files to genomes directory
relative_genome_path = './genomes'

# Create sample data
data = {
    'Uehling Lab ID': ['UL001', 'UL002', 'UL003'],
    'Sample Location Plate': ['Plate A', 'Plate A', 'Plate B'],
    'GC3F Submission Sample ID': ['GC3F-001', 'GC3F-002', 'GC3F-003'],
    'Alternate ID 1': ['Alt001', 'Alt002', 'Alt003'],
    'Alternate ID 2': ['', '', ''],
    'Lab Unique ID 3': ['LU001', 'LU002', 'LU003'],
    'Extracted by': ['Lab Tech 1', 'Lab Tech 1', 'Lab Tech 2'],
    'Top ITS Blast Hit': ['Fungal Species A', 'Fungal Species B', 'Fungal Species C'],
    'ITS Top Hit Similarity': ['98.5%', '97.2%', '99.1%'],
    'ITS Taxonomy Comments': ['Good match', 'Good match', 'Excellent match'],
    'Top 16S Blast Hit': ['Bacterial Species X', 'Bacterial Species Y', 'Bacterial Species Z'],
    '16S Top Hit Similarity': ['96.3%', '95.8%', '97.5%'],
    '16S Taxonomy Comments': ['Moderate match', 'Moderate match', 'Good match'],
    'Project Funding': ['NSF Grant 123', 'NSF Grant 123', 'DOE Grant 456'],
    'Latitude': ['45.123', '45.456', '45.789'],
    'Longitude': ['-120.123', '-120.456', '-120.789'],
    'Location ID': ['LOC-001', 'LOC-002', 'LOC-003'],
    'DNA Extraction Method': ['Phenol-Chloroform', 'Phenol-Chloroform', 'CTAB'],
    'Extraction Date': ['2024-01-15', '2024-01-16', '2024-01-17'],
    'Primary Assembly Filename': [
        f'{relative_genome_path}/genome1.fasta',
        f'{relative_genome_path}/genome2.fasta',
        f'{relative_genome_path}/genome3.fasta'
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Write to Excel
try:
    df.to_excel(output_path, index=False, engine='openpyxl')
    print(f"✓ Successfully created: {output_path}")
    print(f"  Contains {len(df)} example genomes")
    print(f"  FASTA files referenced in: {genomes_dir}")
except Exception as e:
    print(f"✗ Error creating Excel file: {e}")
    import traceback
    traceback.print_exc()
