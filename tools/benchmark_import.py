import time
import os
import shutil
import tempfile
from modules.data_import import import_fasta_from_folder

# Configurable parameters
NUM_FILES = 10
SAMPLE_FASTA = os.path.join('example_files', 'example_gen.fasta')


def prepare_test_folder(num_files):
    tmpdir = tempfile.mkdtemp(prefix='fasta_bench_')
    base_name = os.path.splitext(os.path.basename(SAMPLE_FASTA))[0]
    for i in range(num_files):
        dst = os.path.join(tmpdir, f"{base_name}_{i}.fasta")
        shutil.copyfile(SAMPLE_FASTA, dst)
    return tmpdir


if __name__ == '__main__':
    if not os.path.exists(SAMPLE_FASTA):
        print(f"Sample FASTA not found at {SAMPLE_FASTA}. Please provide an example or update SAMPLE_FASTA.")
        raise SystemExit(1)

    test_folder = prepare_test_folder(NUM_FILES)
    print(f"Prepared {NUM_FILES} FASTA files in {test_folder}")

    start = time.time()
    # import_fasta_from_folder prompts for lab_id; to make the benchmark non-interactive,
    # we'll temporarily monkeypatch input to return a generated lab id.
    import builtins
    real_input = builtins.input
    try:
        builtins.input = lambda prompt='': 'BENCH1'
        import_fasta_from_folder(test_folder)
    finally:
        builtins.input = real_input

    elapsed = time.time() - start
    print(f"Import of {NUM_FILES} files completed in {elapsed:.2f} seconds")

    # cleanup
    shutil.rmtree(test_folder)
    print("Temporary files removed.")
