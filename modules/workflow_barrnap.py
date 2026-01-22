"""
Barrnap rRNA Annotation Workflow Module

This module provides a complete pipeline for:
1. Querying the database for genomes (by Lab ID, metadata, or all)
2. Exporting selected genomes for Barrnap processing
3. Running Barrnap to identify ribosomal RNA sequences
4. Extracting and organizing results (FASTA, CSV summary, GFF annotations)
5. Error handling with user prompts for failed genomes

This module serves as a reference implementation for integrating external tools
with the relational database. Other tools (tree-building, alignment, etc.) 
should follow the same structure.

Author: Reece M
Version: 1.0
"""

import os
import sys
import subprocess
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
from modules.utils import load_schema, engine
from modules.search import search_db
import re

# Constants
BARRNAP_INPUT_DIR = "barrnap_input/genomes"
BARRNAP_OUTPUT_DIR = "barrnap_output"
BARRNAP_ANNOTATIONS_DIR = f"{BARRNAP_OUTPUT_DIR}/annotations"
BARRNAP_RRNA_DIR = f"{BARRNAP_OUTPUT_DIR}/rrna_sequences"
BARRNAP_GFF_DIR = f"{BARRNAP_OUTPUT_DIR}/gff_annotations"


def initialize_barrnap_directories():
    """Create necessary directories for Barrnap workflow."""
    try:
        for directory in [BARRNAP_INPUT_DIR, BARRNAP_ANNOTATIONS_DIR, BARRNAP_RRNA_DIR, BARRNAP_GFF_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directories: {e}")
        return False


def display_barrnap_menu():
    """Display the main Barrnap workflow menu."""
    print("\n" + "="*50)
    print("BARRNAP rRNA ANNOTATION PIPELINE")
    print("="*50)
    print("\nThis workflow will:")
    print("  1. Search your database for genomes")
    print("  2. Export matching genomes to a staging directory")
    print("  3. Run Barrnap to identify rRNA sequences")
    print("  4. Extract rRNA sequences and annotations")
    print("  5. Generate a summary report")
    print("\nNote: Barrnap must be installed on your system.")
    print("Install with: pip install barrnap")
    print("="*50)


def get_genome_selection():
    """
    Allow user to select genomes through multiple filter options.
    Supports: Lab ID, metadata queries, all genomes, or combination (AND logic).
    Returns: List of (lab_id, fasta_data) tuples
    """
    print("\n--- STEP 1: GENOME SELECTION ---\n")
    print("How would you like to select genomes?")
    print("1) Single Lab ID (e.g., UL001)")
    print("2) Metadata keyword search (e.g., 'Rhizopus', '2025')")
    print("3) All genomes in database")
    print("4) Advanced filter (multiple criteria with AND logic)")
    
    choice = input("\nSelect option (1/2/3/4): ").strip()
    
    if choice == "1":
        return select_by_lab_id()
    elif choice == "2":
        return select_by_metadata_keyword()
    elif choice == "3":
        return select_all_genomes()
    elif choice == "4":
        return select_by_advanced_filter()
    else:
        print("Invalid option. Please try again.")
        return get_genome_selection()


def select_by_lab_id():
    """Select genomes by single Lab ID."""
    lab_id = input("\nEnter Lab ID (e.g., UL001): ").strip().upper()
    
    try:
        query = "SELECT lab_id, value FROM GenomicData WHERE lab_id = :lab_id ORDER BY seq_order"
        result = pd.read_sql(query, con=engine, params={"lab_id": lab_id})
        
        if result.empty:
            print(f"No genomes found for Lab ID: {lab_id}")
            return None
        
        # Group sequences by lab_id
        genomes = [(lab_id, result['value'].str.cat(sep='\n'))]
        print(f"\nFound 1 genome for {lab_id}")
        return genomes
    except Exception as e:
        print(f"Error querying database: {e}")
        return None


def select_by_metadata_keyword():
    """Select genomes by metadata keyword."""
    keyword = input("\nEnter metadata keyword (e.g., 'Rhizopus', '2025', 'soil'): ").strip()
    
    if not keyword:
        print("No keyword provided.")
        return None
    
    try:
        # Find all Lab IDs where any metadata value matches keyword
        query = """
        SELECT DISTINCT lab_id FROM Metadata 
        WHERE LOWER(value) LIKE LOWER(:keyword)
        """
        lab_ids = pd.read_sql(query, con=engine, params={"keyword": f"%{keyword}%"})
        
        if lab_ids.empty:
            print(f"No genomes found matching keyword: {keyword}")
            return None
        
        lab_id_list = lab_ids['lab_id'].tolist()
        print(f"\nFound {len(lab_id_list)} genome(s) matching '{keyword}'")
        print(f"Lab IDs: {', '.join(lab_id_list)}")
        
        return get_genomic_data_for_lab_ids(lab_id_list)
    except Exception as e:
        print(f"Error querying database: {e}")
        return None


def select_all_genomes():
    """Select all genomes in database."""
    try:
        query = "SELECT DISTINCT lab_id FROM GenomicData ORDER BY lab_id"
        lab_ids = pd.read_sql(query, con=engine)
        
        if lab_ids.empty:
            print("No genomes found in database.")
            return None
        
        lab_id_list = lab_ids['lab_id'].tolist()
        print(f"\nFound {len(lab_id_list)} genome(s) in database")
        
        return get_genomic_data_for_lab_ids(lab_id_list)
    except Exception as e:
        print(f"Error querying database: {e}")
        return None


def select_by_advanced_filter():
    """
    Advanced filtering with multiple criteria (AND logic).
    User builds a query by specifying multiple metadata key-value pairs.
    """
    print("\n--- ADVANCED FILTER (AND LOGIC) ---")
    print("Add filter criteria one at a time.")
    print("Press ENTER after each criterion to add another.")
    print("Leave the key blank when finished.\n")
    
    filters = []
    
    while True:
        key = input(f"Enter metadata key #{len(filters)+1} (or leave blank to finish): ").strip()
        
        if not key:
            break
        
        value = input(f"Enter value for '{key}': ").strip()
        
        if value:
            filters.append((key, value))
            print(f"✓ Added filter: {key} = '{value}'")
        else:
            print("Value cannot be empty. Try again.")
    
    if not filters:
        print("No filters provided.")
        return None
    
    try:
        # Start with all lab_ids
        query = "SELECT DISTINCT lab_id FROM Metadata"
        all_lab_ids = pd.read_sql(query, con=engine)['lab_id'].tolist()
        
        result_lab_ids = set(all_lab_ids)
        
        # Apply each filter with AND logic
        for key, value in filters:
            query = """
            SELECT DISTINCT lab_id FROM Metadata 
            WHERE LOWER(key) = LOWER(:key) AND LOWER(value) LIKE LOWER(:value)
            """
            matching_ids = pd.read_sql(query, con=engine, 
                                      params={"key": key, "value": f"%{value}%"})
            matching_set = set(matching_ids['lab_id'].tolist())
            result_lab_ids = result_lab_ids.intersection(matching_set)
        
        if not result_lab_ids:
            print("\nNo genomes match all criteria.")
            return None
        
        lab_id_list = sorted(list(result_lab_ids))
        print(f"\n✓ Found {len(lab_id_list)} genome(s) matching ALL criteria")
        print(f"Lab IDs: {', '.join(lab_id_list)}")
        
        return get_genomic_data_for_lab_ids(lab_id_list)
    except Exception as e:
        print(f"Error with advanced filter: {e}")
        return None


def get_genomic_data_for_lab_ids(lab_id_list):
    """Retrieve genomic data (FASTA sequences) for a list of Lab IDs."""
    genomes = []
    
    for lab_id in lab_id_list:
        try:
            query = "SELECT value FROM GenomicData WHERE lab_id = :lab_id ORDER BY seq_order"
            result = pd.read_sql(query, con=engine, params={"lab_id": lab_id})
            
            if not result.empty:
                fasta_data = result['value'].str.cat(sep='\n')
                genomes.append((lab_id, fasta_data))
        except Exception as e:
            print(f"Warning: Error retrieving data for {lab_id}: {e}")
    
    return genomes if genomes else None


def export_genomes_for_barrnap(genomes):
    """
    Export selected genomes to staging directory.
    
    Args:
        genomes: List of (lab_id, fasta_data) tuples
    
    Returns:
        List of exported file paths
    """
    print("\n--- STEP 2: EXPORTING GENOMES ---\n")
    
    exported_files = []
    failed_exports = []
    
    for lab_id, fasta_data in genomes:
        try:
            # Create filename from lab_id
            filename = f"{lab_id}.fasta"
            filepath = os.path.join(BARRNAP_INPUT_DIR, filename)
            
            # Write FASTA data
            with open(filepath, 'w') as f:
                f.write(fasta_data)
            
            exported_files.append(filepath)
            print(f"✓ Exported {lab_id} to {filename}")
        except Exception as e:
            failed_exports.append((lab_id, str(e)))
            print(f"✗ Failed to export {lab_id}: {e}")
    
    print(f"\nExported {len(exported_files)}/{len(genomes)} genomes")
    
    if failed_exports:
        print(f"\nFailed exports: {len(failed_exports)}")
        for lab_id, error in failed_exports:
            print(f"  - {lab_id}: {error}")
    
    return exported_files if exported_files else None


def validate_barrnap_installation():
    """Check if Barrnap is installed and accessible."""
    try:
        result = subprocess.run(['barrnap', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True
        return False
    except FileNotFoundError:
        return False
    except Exception:
        return False


def get_barrnap_parameters():
    """
    Get Barrnap execution parameters.
    Offers defaults with optional customization.
    """
    print("\n--- STEP 3: BARRNAP PARAMETERS ---\n")
    print("Barrnap Default Settings (for fungi):")
    print("  Kingdom: fungi")
    print("  Coverage: 50")
    print("  Threads: auto (system default)")
    
    use_defaults = input("\nUse default settings? (y/n): ").strip().lower()
    
    if use_defaults == 'y' or use_defaults == '':
        return {
            'kingdom': 'fungi',
            'coverage': 50,
            'threads': None
        }
    else:
        # Custom parameters
        print("\n--- CUSTOM PARAMETERS ---")
        
        kingdom = input("Kingdom (fungi/bacteria/archaea) [default: fungi]: ").strip().lower()
        if not kingdom:
            kingdom = 'fungi'
        
        coverage_input = input("Coverage threshold [default: 50]: ").strip()
        try:
            coverage = int(coverage_input) if coverage_input else 50
        except ValueError:
            coverage = 50
            print("Invalid coverage value, using default: 50")
        
        threads_input = input("Number of threads (or 'auto') [default: auto]: ").strip()
        threads = threads_input if threads_input else 'auto'
        
        return {
            'kingdom': kingdom,
            'coverage': coverage,
            'threads': threads
        }


def build_barrnap_command(genomes_dir, params):
    """Build Barrnap command string."""
    cmd = ['barrnap']
    
    if params['kingdom']:
        cmd.extend(['--kingdom', params['kingdom']])
    
    if params['coverage']:
        cmd.extend(['--coverage', str(params['coverage'])])
    
    if params['threads'] and params['threads'] != 'auto':
        cmd.extend(['--threads', str(params['threads'])])
    
    # Output to GFF directory
    cmd.extend(['--outdir', BARRNAP_GFF_DIR])
    
    # Add all FASTA files in genomes directory
    cmd.append(genomes_dir)
    
    return cmd


def run_barrnap_on_staging(exported_files, params):
    """
    Execute Barrnap on exported genomes.
    
    Args:
        exported_files: List of exported FASTA file paths
        params: Dictionary of Barrnap parameters
    
    Returns:
        Tuple of (success, results_summary)
    """
    print("\n--- STEP 4: RUNNING BARRNAP ---\n")
    
    if not validate_barrnap_installation():
        print("ERROR: Barrnap is not installed or not in PATH.")
        print("Please install Barrnap: pip install barrnap")
        print("Or visit: https://github.com/tseemann/barrnap")
        return False, None
    
    try:
        print(f"Running Barrnap on {len(exported_files)} genome(s)...")
        print(f"Command parameters: kingdom={params['kingdom']}, coverage={params['coverage']}")
        
        # Build command - barrnap processes all files in a directory
        cmd = ['barrnap']
        cmd.extend(['--kingdom', params['kingdom']])
        cmd.extend(['--coverage', str(params['coverage'])])
        cmd.extend(['--outdir', BARRNAP_GFF_DIR])
        cmd.append(BARRNAP_INPUT_DIR)
        
        # Run Barrnap
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        if result.returncode != 0:
            print(f"Barrnap returned error code {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False, None
        
        print("✓ Barrnap completed successfully")
        return True, result.stdout
    
    except subprocess.TimeoutExpired:
        print("ERROR: Barrnap execution timed out (>1 hour)")
        return False, None
    except FileNotFoundError:
        print("ERROR: Barrnap executable not found")
        return False, None
    except Exception as e:
        print(f"ERROR running Barrnap: {e}")
        return False, None


def parse_barrnap_gff(gff_file):
    """
    Parse Barrnap GFF3 output file.
    
    Returns:
        List of dictionaries with rRNA information
    """
    rna_features = []
    
    try:
        with open(gff_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split('\t')
                if len(parts) < 9:
                    continue
                
                seqid = parts[0]
                feature_type = parts[2]
                start = int(parts[3])
                end = int(parts[4])
                strand = parts[6]
                attributes = parts[8]
                
                # Extract product name from attributes
                product_match = re.search(r'product=([^;]+)', attributes)
                product = product_match.group(1) if product_match else 'unknown'
                
                rna_features.append({
                    'seqid': seqid,
                    'type': feature_type,
                    'product': product,
                    'start': start,
                    'end': end,
                    'strand': strand,
                    'length': end - start + 1
                })
        
        return rna_features
    except Exception as e:
        print(f"Error parsing GFF file {gff_file}: {e}")
        return []


def extract_rrna_sequences(lab_id, fasta_file, gff_file, rna_features):
    """
    Extract rRNA sequences based on GFF coordinates.
    
    Args:
        lab_id: Laboratory ID
        fasta_file: Original FASTA file path
        gff_file: Barrnap GFF output file
        rna_features: List of rRNA features from parse_barrnap_gff
    
    Returns:
        Tuple of (extracted_count, failed_count, summary_dict)
    """
    extracted_count = 0
    failed_count = 0
    summary = {'16S': 0, '23S': 0, '5S': 0, 'tRNA': 0, 'tmRNA': 0, 'other': 0}
    
    try:
        # Read original FASTA sequence
        fasta_sequence = {}
        current_seq_id = None
        current_seq = []
        
        with open(fasta_file, 'r') as f:
            for line in f:
                line = line.rstrip()
                if line.startswith('>'):
                    if current_seq_id:
                        fasta_sequence[current_seq_id] = ''.join(current_seq)
                    current_seq_id = line[1:].split()[0]  # Get ID without '>'
                    current_seq = []
                else:
                    current_seq.append(line)
            
            if current_seq_id:
                fasta_sequence[current_seq_id] = ''.join(current_seq)
        
        # Extract sequences for each rRNA feature
        for i, feature in enumerate(rna_features, 1):
            try:
                seqid = feature['seqid']
                start = feature['start'] - 1  # Convert to 0-based
                end = feature['end']
                product = feature['product']
                
                # Get the sequence
                if seqid in fasta_sequence:
                    extracted_seq = fasta_sequence[seqid][start:end]
                else:
                    # Try to find matching sequence
                    found = False
                    for seq_key in fasta_sequence.keys():
                        if seqid in seq_key or seq_key in seqid:
                            extracted_seq = fasta_sequence[seq_key][start:end]
                            found = True
                            break
                    
                    if not found:
                        failed_count += 1
                        continue
                
                # Categorize by product type
                if '16S' in product:
                    summary['16S'] += 1
                    product_name = f"16S_rRNA_{summary['16S']}"
                elif '23S' in product:
                    summary['23S'] += 1
                    product_name = f"23S_rRNA_{summary['23S']}"
                elif '5S' in product:
                    summary['5S'] += 1
                    product_name = f"5S_rRNA_{summary['5S']}"
                elif 'tRNA' in product:
                    summary['tRNA'] += 1
                    product_name = f"tRNA_{summary['tRNA']}"
                elif 'tmRNA' in product:
                    summary['tmRNA'] += 1
                    product_name = f"tmRNA_{summary['tmRNA']}"
                else:
                    summary['other'] += 1
                    product_name = f"other_rRNA_{summary['other']}"
                
                # Save sequence to FASTA file
                output_filename = f"{lab_id}_{product_name}.fasta"
                output_filepath = os.path.join(BARRNAP_RRNA_DIR, output_filename)
                
                with open(output_filepath, 'w') as f:
                    f.write(f">{lab_id}_{product_name}\n")
                    # Write sequence in 80-character lines (standard FASTA)
                    for j in range(0, len(extracted_seq), 80):
                        f.write(extracted_seq[j:j+80] + '\n')
                
                extracted_count += 1
            
            except Exception as e:
                failed_count += 1
                print(f"Warning: Could not extract feature {i} from {lab_id}: {e}")
        
        return extracted_count, failed_count, summary
    
    except Exception as e:
        print(f"Error in extract_rrna_sequences for {lab_id}: {e}")
        return 0, len(rna_features), summary


def organize_results(exported_files):
    """
    Process all Barrnap results and extract rRNA sequences.
    Handles error cases where individual genomes fail.
    
    Args:
        exported_files: List of exported FASTA file paths
    
    Returns:
        Dictionary with overall statistics
    """
    print("\n--- STEP 5: EXTRACTING rRNA SEQUENCES ---\n")
    
    overall_stats = {
        'total_genomes': len(exported_files),
        'processed': 0,
        'failed': [],
        'total_16S': 0,
        'total_23S': 0,
        'total_5S': 0,
        'total_tRNA': 0,
        'total_tmRNA': 0,
        'total_other': 0
    }
    
    for fasta_file in exported_files:
        try:
            # Extract lab_id from filename
            filename = os.path.basename(fasta_file)
            lab_id = filename.replace('.fasta', '')
            
            # Look for corresponding GFF file
            gff_file = os.path.join(BARRNAP_GFF_DIR, f"{lab_id}.gff")
            
            if not os.path.exists(gff_file):
                print(f"⚠ No GFF output found for {lab_id}")
                overall_stats['failed'].append((lab_id, "No GFF output"))
                continue
            
            # Parse GFF and extract sequences
            rna_features = parse_barrnap_gff(gff_file)
            
            if not rna_features:
                print(f"⚠ No rRNA features found in {lab_id}")
                overall_stats['failed'].append((lab_id, "No rRNA features"))
                continue
            
            extracted_count, failed_count, summary = extract_rrna_sequences(
                lab_id, fasta_file, gff_file, rna_features
            )
            
            if extracted_count > 0:
                overall_stats['processed'] += 1
                overall_stats['total_16S'] += summary['16S']
                overall_stats['total_23S'] += summary['23S']
                overall_stats['total_5S'] += summary['5S']
                overall_stats['total_tRNA'] += summary['tRNA']
                overall_stats['total_tmRNA'] += summary['tmRNA']
                overall_stats['total_other'] += summary['other']
                
                print(f"✓ {lab_id}: {extracted_count} sequences extracted " +
                      f"(16S:{summary['16S']}, 23S:{summary['23S']}, 5S:{summary['5S']}, " +
                      f"tRNA:{summary['tRNA']})")
            else:
                overall_stats['failed'].append((lab_id, "Extraction failed"))
        
        except Exception as e:
            lab_id = os.path.basename(fasta_file).replace('.fasta', '')
            overall_stats['failed'].append((lab_id, str(e)))
            print(f"✗ Error processing {lab_id}: {e}")
    
    return overall_stats


def get_extraction_options():
    """
    Prompt user for which outputs to save.
    
    Returns:
        List of selected options (1=FASTA, 2=CSV, 3=GFF)
    """
    print("\n--- EXTRACTION OUTPUT OPTIONS ---\n")
    print("What would you like to save?")
    print("1) rRNA sequences (FASTA files)")
    print("2) Summary CSV (counts per genome/type)")
    print("3) Raw GFF annotations (Barrnap output)")
    print("\nDefault (all): Press ENTER or enter '1,2,3'")
    
    user_input = input("\nSelect options (comma-separated): ").strip()
    
    if not user_input:
        return [1, 2, 3]  # Default: all
    
    try:
        options = [int(x.strip()) for x in user_input.split(',')]
        # Validate
        options = [opt for opt in options if opt in [1, 2, 3]]
        return options if options else [1, 2, 3]
    except ValueError:
        print("Invalid input. Using default (all options).")
        return [1, 2, 3]


def create_summary_csv(overall_stats, exported_files):
    """
    Create a CSV summary of extracted rRNA counts.
    
    Args:
        overall_stats: Statistics dictionary
        exported_files: List of processed files
    """
    try:
        summary_data = []
        
        for fasta_file in exported_files:
            lab_id = os.path.basename(fasta_file).replace('.fasta', '')
            gff_file = os.path.join(BARRNAP_GFF_DIR, f"{lab_id}.gff")
            
            if os.path.exists(gff_file):
                rna_features = parse_barrnap_gff(gff_file)
                
                # Count by type
                counts = {'16S': 0, '23S': 0, '5S': 0, 'tRNA': 0, 'tmRNA': 0, 'other': 0}
                for feature in rna_features:
                    product = feature['product']
                    if '16S' in product:
                        counts['16S'] += 1
                    elif '23S' in product:
                        counts['23S'] += 1
                    elif '5S' in product:
                        counts['5S'] += 1
                    elif 'tRNA' in product:
                        counts['tRNA'] += 1
                    elif 'tmRNA' in product:
                        counts['tmRNA'] += 1
                    else:
                        counts['other'] += 1
                
                summary_data.append({
                    'genome_id': lab_id,
                    '16S_count': counts['16S'],
                    '23S_count': counts['23S'],
                    '5S_count': counts['5S'],
                    'tRNA_count': counts['tRNA'],
                    'tmRNA_count': counts['tmRNA'],
                    'other_count': counts['other'],
                    'total_rRNA': sum(counts.values())
                })
        
        # Create DataFrame and save to CSV
        if summary_data:
            df = pd.DataFrame(summary_data)
            csv_path = os.path.join(BARRNAP_OUTPUT_DIR, 'rrna_summary.csv')
            df.to_csv(csv_path, index=False)
            print(f"\n✓ Summary CSV created: {csv_path}")
        
    except Exception as e:
        print(f"Error creating summary CSV: {e}")


def create_barrnap_summary(overall_stats, extraction_options):
    """
    Create a comprehensive summary report.
    
    Args:
        overall_stats: Statistics dictionary
        extraction_options: List of selected output options
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        summary_lines = [
            "="*60,
            "BARRNAP rRNA ANNOTATION PIPELINE - SUMMARY REPORT",
            "="*60,
            f"Generated: {timestamp}",
            "",
            "--- PROCESSING STATISTICS ---",
            f"Total genomes processed: {overall_stats['total_genomes']}",
            f"Successfully processed: {overall_stats['processed']}",
            f"Failed genomes: {len(overall_stats['failed'])}",
            "",
            "--- rRNA SEQUENCES FOUND ---",
            f"16S rRNA (small subunit): {overall_stats['total_16S']}",
            f"23S rRNA (large subunit): {overall_stats['total_23S']}",
            f"5S rRNA (small subunit): {overall_stats['total_5S']}",
            f"tRNA (transfer RNA): {overall_stats['total_tRNA']}",
            f"tmRNA (transfer-mRNA): {overall_stats['total_tmRNA']}",
            f"Other RNA features: {overall_stats['total_other']}",
            f"Total rRNA sequences: {overall_stats['total_16S'] + overall_stats['total_23S'] + overall_stats['total_5S'] + overall_stats['total_tRNA'] + overall_stats['total_tmRNA'] + overall_stats['total_other']}",
            "",
        ]
        
        if overall_stats['failed']:
            summary_lines.extend([
                "--- FAILED GENOMES ---",
            ])
            for lab_id, reason in overall_stats['failed']:
                summary_lines.append(f"  {lab_id}: {reason}")
            summary_lines.append("")
        
        summary_lines.extend([
            "--- OUTPUT FILES ---",
        ])
        
        if 1 in extraction_options:
            summary_lines.append(f"✓ rRNA sequences: {BARRNAP_RRNA_DIR}/")
        if 2 in extraction_options:
            summary_lines.append(f"✓ Summary CSV: {BARRNAP_OUTPUT_DIR}/rrna_summary.csv")
        if 3 in extraction_options:
            summary_lines.append(f"✓ GFF annotations: {BARRNAP_GFF_DIR}/")
        
        summary_lines.extend([
            "",
            "--- NEXT STEPS ---",
            "The extracted rRNA sequences are ready for:",
            "  - Sequence alignment (MAFFT, Clustal)",
            "  - Phylogenetic tree building (RAxML, FastTree, IQTree)",
            "  - Further analysis and visualization",
            "",
            "For alignment and tree building, use the extracted FASTA files in:",
            f"  {BARRNAP_RRNA_DIR}/",
            "",
            "="*60,
        ])
        
        # Write summary file
        summary_path = os.path.join(BARRNAP_OUTPUT_DIR, 'summary.txt')
        with open(summary_path, 'w') as f:
            f.write('\n'.join(summary_lines))
        
        # Print to console
        print('\n' + '\n'.join(summary_lines))
        print(f"\n✓ Summary report saved to: {summary_path}")
        
    except Exception as e:
        print(f"Error creating summary: {e}")


def run_barrnap_workflow():
    """
    Main workflow orchestration.
    Coordinates all steps of the Barrnap pipeline.
    """
    display_barrnap_menu()
    
    # Step 1: Initialize directories
    if not initialize_barrnap_directories():
        print("ERROR: Could not create necessary directories.")
        return
    
    # Step 2: Genome selection
    genomes = get_genome_selection()
    if not genomes:
        print("No genomes selected. Aborting.")
        return
    
    print(f"\n✓ Selected {len(genomes)} genome(s)")
    proceed = input("\nProceed with export and analysis? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Cancelled.")
        return
    
    # Step 3: Export genomes
    exported_files = export_genomes_for_barrnap(genomes)
    if not exported_files:
        print("ERROR: Failed to export genomes.")
        return
    
    # Step 4: Get Barrnap parameters
    params = get_barrnap_parameters()
    
    # Step 5: Run Barrnap
    success, _ = run_barrnap_on_staging(exported_files, params)
    if not success:
        print("\nERROR: Barrnap execution failed.")
        retry = input("Try again? (y/n): ").strip().lower()
        if retry == 'y':
            run_barrnap_workflow()
        return
    
    # Step 6: Organize results and extract sequences
    overall_stats = organize_results(exported_files)
    
    # Step 7: Get extraction options
    extraction_options = get_extraction_options()
    
    # Step 8: Create outputs
    if 2 in extraction_options:
        create_summary_csv(overall_stats, exported_files)
    
    # Step 9: Create final summary report
    create_barrnap_summary(overall_stats, extraction_options)
    
    print("\n✓ Barrnap workflow complete!")
    print(f"\nResults directory: {BARRNAP_OUTPUT_DIR}/")
