# External Tool Integration Developer Guide

## Overview

This guide explains how the Barrnap integration was built and serves as a **template for adding future tools** to the relational database. The architecture is designed to be replicatable, allowing lab members to integrate similar tools with minimal effort.

---

## Core Architecture Principle

**Separation of Concerns:**
```
Database Layer (read-only)
         ↓
Workflow Module (tool-agnostic filtering & orchestration)
         ↓
External Tool (installed separately)
         ↓
Results Processing & Organization
```

The database never directly calls external tools. Instead, a workflow module:
1. Queries the database
2. Exports data to a staging area
3. Calls the external tool
4. Processes and organizes results

This keeps your database clean and independent.

---

## How Barrnap Integration Works

### File Structure

```
modules/
├── workflow_barrnap.py      ← NEW: Tool-specific module
├── search.py                ← EXISTING: Used for queries
├── data_output.py           ← EXISTING: Used for exports
└── utils.py                 ← EXISTING: Database utilities

main.py                       ← MODIFIED: Added menu option

config/
└── schema.yaml              ← MODIFIED: Added tool config

docs/
├── BARRNAP_USER_GUIDE.md    ← User documentation
└── BARRNAP_DEVELOPER_GUIDE.md ← This file
```

### Module Design Pattern

The `workflow_barrnap.py` module follows this structure:

```python
# 1. Constants & Initialization
STAGING_DIR = "tool_input/"
OUTPUT_DIR = "tool_output/"

def initialize_directories():
    """Create necessary directories"""
    
# 2. User Interface Functions
def display_menu():
    """Display workflow options"""
    
def get_user_input():
    """Collect configuration from user"""
    
# 3. Data Selection Functions
def query_database():
    """Search database using existing search module"""
    
# 4. Data Export Functions
def export_data():
    """Write data to staging directory"""
    
# 5. Tool Execution Functions
def validate_tool_installation():
    """Check if tool is installed"""
    
def run_external_tool():
    """Call the tool via subprocess"""
    
# 6. Results Processing Functions
def parse_output():
    """Parse tool output"""
    
def extract_results():
    """Extract relevant data from parsed output"""
    
# 7. Organization & Reporting Functions
def organize_results():
    """Create output directory structure"""
    
def create_summary():
    """Generate human-readable report"""
    
# 8. Main Orchestration Function
def run_workflow():
    """Coordinate all steps"""
```

---

## Step-by-Step Integration Template

Follow these steps to integrate a NEW tool (e.g., "MAFFT Alignment Tool"):

### Step 1: Create the Workflow Module

**File:** `modules/workflow_TOOLNAME.py`

```python
"""
[Tool Name] Workflow Module

Brief description of what the tool does and how it integrates.
Author: [Your Name]
Version: 1.0
"""

import os
import subprocess
from pathlib import Path
from modules.utils import load_schema, engine
import pandas as pd

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

# Define directories for staging and output
TOOL_INPUT_DIR = "tool_input/sequences"
TOOL_OUTPUT_DIR = "tool_output"
TOOL_STAGING_DIR = f"{TOOL_OUTPUT_DIR}/staging"

# Tool-specific constants
TOOL_NAME = "MAFFT"
TOOL_EXECUTABLE = "mafft"  # Name of command-line tool


def initialize_directories():
    """Create necessary directories for the workflow."""
    try:
        for directory in [TOOL_INPUT_DIR, TOOL_STAGING_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directories: {e}")
        return False


# ============================================================================
# STEP 1: USER INTERFACE & MENU
# ============================================================================

def display_menu():
    """Display the tool's workflow menu with description."""
    print("\n" + "="*50)
    print(f"{TOOL_NAME.upper()} WORKFLOW")
    print("="*50)
    print("\nDescription: [What does this tool do?]")
    print("\nThis workflow will:")
    print("  1. [Step 1 description]")
    print("  2. [Step 2 description]")
    print("  3. [Step 3 description]")
    print("="*50)


def get_user_configuration():
    """
    Collect tool-specific configuration from user.
    
    Returns:
        dict: Configuration parameters
    """
    print("\n--- CONFIGURATION ---")
    config = {}
    
    # Example: ask for parameters
    config['param1'] = input("Parameter 1 [default: value]: ").strip() or "default_value"
    config['param2'] = input("Parameter 2 (y/n): ").strip().lower() == 'y'
    
    return config


# ============================================================================
# STEP 2: DATA SELECTION (Use existing search module)
# ============================================================================

def get_genome_selection():
    """
    Allow user to select genomes from database.
    Can reuse patterns from workflow_barrnap.py
    
    Returns:
        list: [(lab_id, fasta_data), ...]
    """
    # COPY ONE OF THESE FROM workflow_barrnap.py:
    # - select_by_lab_id()
    # - select_by_metadata_keyword()
    # - select_all_genomes()
    # - select_by_advanced_filter()
    pass


# ============================================================================
# STEP 3: DATA EXPORT
# ============================================================================

def export_data(genomes):
    """
    Export selected data to staging directory.
    
    Args:
        genomes: [(lab_id, data), ...] from get_genome_selection()
    
    Returns:
        list: Paths to exported files
    """
    print("\n--- EXPORTING DATA ---\n")
    
    exported_files = []
    
    for lab_id, data in genomes:
        try:
            filename = f"{lab_id}.fasta"  # Adjust extension as needed
            filepath = os.path.join(TOOL_INPUT_DIR, filename)
            
            with open(filepath, 'w') as f:
                f.write(data)
            
            exported_files.append(filepath)
            print(f"✓ Exported {lab_id}")
        except Exception as e:
            print(f"✗ Failed to export {lab_id}: {e}")
    
    return exported_files if exported_files else None


# ============================================================================
# STEP 4: TOOL VALIDATION & EXECUTION
# ============================================================================

def validate_tool_installation():
    """
    Check if the external tool is installed and accessible.
    
    Returns:
        bool: True if tool is found, False otherwise
    """
    try:
        result = subprocess.run(
            [TOOL_EXECUTABLE, '--version'],  # Adjust flag for your tool
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception:
        return False


def get_tool_parameters():
    """
    Get parameters for tool execution.
    Can offer defaults or custom options.
    
    Returns:
        dict: Tool parameters
    """
    print("\n--- TOOL PARAMETERS ---")
    print("[Tool] Default Settings:")
    print("  Param 1: default_value")
    print("  Param 2: default_value")
    
    use_defaults = input("\nUse defaults? (y/n): ").strip().lower()
    
    if use_defaults == 'y' or use_defaults == '':
        return {'param1': 'default1', 'param2': 'default2'}
    else:
        # Implement custom parameter input
        return {'param1': 'custom1', 'param2': 'custom2'}


def run_external_tool(input_files, params):
    """
    Execute the external tool on input files.
    
    Args:
        input_files: List of file paths to process
        params: Dictionary of tool parameters
    
    Returns:
        tuple: (success: bool, output: str)
    """
    print("\n--- RUNNING TOOL ---\n")
    
    if not validate_tool_installation():
        print(f"ERROR: {TOOL_EXECUTABLE} is not installed.")
        return False, None
    
    try:
        print(f"Processing {len(input_files)} file(s)...")
        
        # Build command - adjust based on your tool's CLI
        cmd = [TOOL_EXECUTABLE]
        cmd.extend(['--param1', params['param1']])
        cmd.extend(['--output-dir', TOOL_OUTPUT_DIR])
        cmd.extend(input_files)
        
        # Execute
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        if result.returncode != 0:
            print(f"Tool returned error code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False, None
        
        print("✓ Tool execution completed")
        return True, result.stdout
    
    except subprocess.TimeoutExpired:
        print("ERROR: Tool execution timed out")
        return False, None
    except FileNotFoundError:
        print(f"ERROR: {TOOL_EXECUTABLE} executable not found")
        return False, None
    except Exception as e:
        print(f"ERROR: {e}")
        return False, None


# ============================================================================
# STEP 5: RESULTS PROCESSING
# ============================================================================

def parse_tool_output(output_files):
    """
    Parse and process output from the external tool.
    This is tool-specific and depends on the output format.
    
    Args:
        output_files: Paths to tool output files
    
    Returns:
        Parsed data structure (dict, DataFrame, etc.)
    """
    print("\n--- PROCESSING RESULTS ---\n")
    
    results = {}
    
    for output_file in output_files:
        try:
            # Tool-specific parsing logic
            # Example: parse alignment file, GFF, JSON, etc.
            results[output_file] = "parsed_data"
            print(f"✓ Parsed {output_file}")
        except Exception as e:
            print(f"✗ Error parsing {output_file}: {e}")
    
    return results


# ============================================================================
# STEP 6: RESULTS ORGANIZATION
# ============================================================================

def organize_results(parsed_results):
    """
    Organize results into final output structure.
    
    Args:
        parsed_results: Results from parse_tool_output()
    
    Returns:
        dict: Summary statistics
    """
    print("\n--- ORGANIZING RESULTS ---\n")
    
    summary = {
        'total_processed': len(parsed_results),
        'successful': 0,
        'failed': 0,
        'output_location': TOOL_OUTPUT_DIR
    }
    
    for filename, data in parsed_results.items():
        try:
            # Save organized output
            summary['successful'] += 1
            print(f"✓ Organized {filename}")
        except Exception as e:
            summary['failed'] += 1
            print(f"✗ Failed to organize {filename}: {e}")
    
    return summary


# ============================================================================
# STEP 7: SUMMARY & REPORTING
# ============================================================================

def create_summary_report(summary):
    """
    Generate a human-readable summary report.
    
    Args:
        summary: Summary statistics from organize_results()
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_lines = [
        "="*60,
        f"{TOOL_NAME} WORKFLOW - SUMMARY REPORT",
        "="*60,
        f"Generated: {timestamp}",
        "",
        "--- STATISTICS ---",
        f"Total processed: {summary['total_processed']}",
        f"Successful: {summary['successful']}",
        f"Failed: {summary['failed']}",
        "",
        f"--- OUTPUT ---",
        f"Results saved to: {summary['output_location']}/",
        "",
        "--- NEXT STEPS ---",
        "[Describe what to do with these results]",
        "="*60,
    ]
    
    report = '\n'.join(report_lines)
    
    # Save to file
    report_path = os.path.join(TOOL_OUTPUT_DIR, 'summary.txt')
    with open(report_path, 'w') as f:
        f.write(report)
    
    # Print to console
    print('\n' + report)


# ============================================================================
# STEP 8: MAIN WORKFLOW ORCHESTRATION
# ============================================================================

def run_workflow():
    """
    Main workflow function - coordinates all steps.
    This is what gets called from main.py.
    """
    display_menu()
    
    if not initialize_directories():
        print("ERROR: Could not initialize directories")
        return
    
    genomes = get_genome_selection()
    if not genomes:
        print("No genomes selected. Aborting.")
        return
    
    exported_files = export_data(genomes)
    if not exported_files:
        print("ERROR: Export failed")
        return
    
    params = get_tool_parameters()
    
    success, output = run_external_tool(exported_files, params)
    if not success:
        print("ERROR: Tool execution failed")
        return
    
    parsed_results = parse_tool_output(exported_files)
    summary = organize_results(parsed_results)
    create_summary_report(summary)
    
    print("\n✓ Workflow complete!")
```

---

### Step 2: Update main.py

Add import and menu option:

```python
# At the top of main.py
from modules.workflow_toolname import run_workflow as run_tool_workflow

# In analysis_workflows_ui() function
def analysis_workflows_ui():
    print("\n========== ANALYSIS WORKFLOWS ==========")
    print("1) Barrnap rRNA Annotation Pipeline")
    print("2) Your New Tool Name")  # ← ADD THIS
    print("3) Back to Main Menu")
    
    choice = input("\nSelect workflow (1/2/3): ").strip()
    
    if choice == "1":
        run_barrnap_workflow()
    elif choice == "2":
        run_tool_workflow()  # ← ADD THIS
    elif choice == "3":
        return
    else:
        print("Invalid choice.")
```

---

### Step 3: Update config/schema.yaml

Add configuration section:

```yaml
toolname_config:
  param1: default_value
  param2: default_value
  input_directory: tool_input/sequences
  output_directory: tool_output
  enable_filtering: true
  description: "[Description of what this tool does]"
```

---

### Step 4: Create Documentation

Create two documentation files:

**File 1:** `docs/TOOLNAME_USER_GUIDE.md`
- How to use the tool from user perspective
- Screenshots/examples
- Troubleshooting

**File 2:** `docs/TOOLNAME_DEVELOPER_GUIDE.md`
- Technical details
- Architecture decisions
- How to modify/extend

---

## Key Design Patterns

### Pattern 1: Multi-Step Filtering

From `workflow_barrnap.py`, these functions are reusable:

```python
# Copy these functions to your new module:
- select_by_lab_id()
- select_by_metadata_keyword()
- select_all_genomes()
- select_by_advanced_filter()  # AND logic filtering
- get_genomic_data_for_lab_ids()
```

### Pattern 2: Error Handling with User Prompts

```python
failed_items = []

for item in items:
    try:
        process(item)
    except Exception as e:
        failed_items.append((item, str(e)))
        print(f"✗ Failed: {item}: {e}")

if failed_items:
    print(f"\nFailed items: {len(failed_items)}")
    for item, error in failed_items:
        print(f"  {item}: {error}")
```

### Pattern 3: Staged Directories

Always use separate directories:
```
TOOL_INPUT_DIR      = "tool_input/"      # Temporary staging
TOOL_OUTPUT_DIR     = "tool_output/"     # Final results
TOOL_STAGING_DIR    = "tool_output/staging/"  # Intermediate
```

### Pattern 4: Configuration Management

Store tool-specific settings in `schema.yaml`:

```yaml
your_tool_config:
  default_param1: value
  default_param2: value
  paths:
    input: tool_input/
    output: tool_output/
```

Access in code:
```python
schema = load_schema()
config = schema.get('your_tool_config', {})
```

---

## Common Gotchas & Solutions

| Issue | Solution |
|-------|----------|
| Tool not in PATH | Check with `which toolname` on Linux/Mac or check Windows registry |
| Relative vs absolute paths | Always use `os.path.abspath()` for clarity |
| Large file handling | Process in chunks if >1GB |
| Special characters in filenames | Use `lab_id` directly; it's already sanitized |
| Tool output encoding | Specify UTF-8: `open(file, encoding='utf-8')` |
| Subprocess blocking | Use `timeout=` parameter to prevent hangs |

---

## Testing Your Integration

### Unit Test Template

```python
# tests/test_workflow_toolname.py

import pytest
from modules.workflow_toolname import (
    initialize_directories,
    validate_tool_installation,
    run_workflow
)

def test_directories_created():
    """Test that directories are created correctly"""
    assert initialize_directories() == True

def test_tool_installed():
    """Test that external tool is available"""
    # This will be True/False depending on user's system
    result = validate_tool_installation()
    print(f"Tool available: {result}")

def test_workflow_with_mock_data():
    """Test workflow with sample genomes"""
    # Create test genomes
    # Run workflow
    # Verify output structure
    pass
```

### Manual Testing Checklist

- [ ] Tool installation validation works
- [ ] Genome selection (all 4 modes) works
- [ ] Export creates correct file structure
- [ ] External tool executes without errors
- [ ] Results are organized correctly
- [ ] Summary report is generated
- [ ] All output files are readable

---

## Architecture Decision: Why Separate Modules?

1. **Modularity** - Each tool is independent, easy to add/remove
2. **Maintainability** - Changes to one tool don't affect others
3. **Testability** - Each module can be tested in isolation
4. **Scalability** - Support for many tools without complexity
5. **Clarity** - Users navigate menus, see clear separation

---

## Summary: What You Need to Create

For each new tool, create:

1. ✅ **One Python module:** `modules/workflow_TOOLNAME.py`
   - Follow the 8-function pattern above
   - Reuse filtering functions from `workflow_barrnap.py`
   
2. ✅ **Update main.py:**
   - Import your workflow
   - Add to analysis_workflows_ui()
   
3. ✅ **Update schema.yaml:**
   - Add `toolname_config` section
   
4. ✅ **Create documentation:**
   - User guide
   - Developer guide (optional but helpful)

That's it! The structure handles everything else.

---

## Questions?

- How does multi-criteria filtering work? → See `select_by_advanced_filter()` in `workflow_barrnap.py`
- How do I handle tool parameters? → See `get_barrnap_parameters()` pattern
- How do I process different output types? → See parsing functions in `workflow_barrnap.py`
- Can I reuse code between tools? → Yes! Extract common functions into `modules/workflow_utils.py`

---

**Last Updated:** January 21, 2025
**Version:** 1.0
