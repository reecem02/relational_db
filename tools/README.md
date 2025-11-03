Benchmark helper

This folder contains a simple benchmark script to measure import performance for FASTA files.

Usage (from project root):

PowerShell:

python .\tools\benchmark_import.py

The script copies `example_files/example_gen.fasta` into a temporary folder multiple times (controlled by NUM_FILES) and imports them using the current import code. It runs non-interactively by supplying a fixed lab id `BENCH1` for all files. Adjust NUM_FILES in the script as needed.
