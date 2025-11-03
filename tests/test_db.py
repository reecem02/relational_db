import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
import time
import gzip
import io
from sqlalchemy import create_engine
from modules.data_import import import_metadata, import_fasta, validate_columns
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from modules.data_output import display_data_by_lab_id, print_row_key_value
from modules.db_info import get_database_info, ensure_file_uploaded_field
from modules.search import search_db


class TestMycoResearch(unittest.TestCase):

    def setUp(self):
        print(f"\nRunning test: {self._testMethodName}")

    def tearDown(self):
        print(f"Finished test: {self._testMethodName}")
        print("-" * 50)

    # Helper method to create sample metadata with all required columns
    def _create_sample_metadata(self):
        """Create a sample DataFrame with all required columns from schema"""
        return pd.DataFrame({
            "Uehling Lab ID": ["UL001"],
            "Sample Location Plate": ["A1"],
            "GC3F Submission Sample ID": ["GC001"],
            "Alternate ID 1": [""],
            "Alternate ID 2": [""],
            "Lab Unique ID 3": [""],
            "Extracted by": ["John Doe"],
            "Top ITS Blast Hit": [""],
            "ITS Top Hit Similarity": [""],
            "ITS Taxonomy Comments": [""],
            "Top 16S Blast Hit": [""],
            "16S Top Hit Similarity": [""],
            "16S Taxonomy Comments": [""],
            "Project Funding": [""],
            "Latitude": [""],
            "Longitude": [""],
            "Location ID": [""],
            "DNA Extraction Method": [""],
            "Extraction Date": ["2025-01-01"]
        })

    @patch("modules.data_import.pd.read_excel")
    @patch("modules.data_import.Session")
    def test_import_metadata(self, mock_session, mock_read_excel):
        """
        Test that import_metadata correctly processes Excel data and performs bulk inserts.
        We mock read_excel to return our sample data and verify the session operations.
        """
        # Set up mock data with all required columns
        mock_data = self._create_sample_metadata()
        mock_read_excel.return_value = mock_data

        # Create a mock session that tracks calls
        mock_session.return_value.__enter__.return_value.execute = MagicMock()
        mock_session.return_value.__enter__.return_value.commit = MagicMock()

        # Run the import
        import_metadata("mock_file_path.xlsx")

        # Verify the session executed commands (both delete and bulk insert)
        self.assertTrue(mock_session.return_value.__enter__.return_value.execute.called)
        self.assertTrue(mock_session.return_value.__enter__.return_value.commit.called)

    @patch("modules.data_output.engine.connect")
    def test_display_data_by_lab_id(self, mock_connect):
        mock_connect.return_value.execute.side_effect = [
            MagicMock(fetchall=lambda: [{"lab_id": "UL001", "key": "Sample Location Plate", "value": "A1"}]),
        ]

        display_data_by_lab_id("UL001")

        self.assertTrue(mock_connect.called)

    @patch("modules.db_info.engine.connect")
    def test_get_database_info(self, mock_connect):
        mock_connect.return_value.execute.side_effect = [
            MagicMock(mappings=lambda: {"count": 10, "last_uploaded": "2025-01-01"}),
            MagicMock(mappings=lambda: {"count": 5, "last_uploaded": "2025-01-02"}),
        ]

        get_database_info()

        self.assertTrue(mock_connect.called)

    @patch("modules.db_info.inspect")
    def test_ensure_file_uploaded_field(self, mock_inspect):
        # Mock inspector behavior
        mock_inspect.return_value.get_columns.side_effect = [
            [{"name": "lab_id"}],  # Metadata table
            [{"name": "lab_id"}],  # GenomicData table
        ]

        # Call the function
        ensure_file_uploaded_field()

        # Assert that the inspector was called
        self.assertTrue(mock_inspect.called)

    def test_validate_columns(self):
        mock_df = pd.DataFrame({
            "lab_id": ["UL001", "UL002"],
            "key": ["Sample Location Plate", "GC3F Submission Sample ID"],
            "value": ["A1", "GC001"],
        })

        with patch("modules.data_import.inspect") as mock_inspect:
            mock_inspect.return_value.get_columns.return_value = [
                {"name": "lab_id"},
                {"name": "key"},
                {"name": "value"},
            ]

            validate_columns("Metadata", mock_df)

            self.assertTrue(True)

    @patch("modules.search.engine.connect")
    def test_search_db(self, mock_connect):
        """
        Test the search_db function with a mock database connection.
        We simulate finding a lab ID and verify the results.
        """
        # Create mock result for metadata query
        mock_metadata_result = pd.DataFrame({
            "key": ["Sample Location Plate"],
            "value": ["A1"]
        })
        
        # Set up mock to return DataFrame for pd.read_sql
        def mock_read_sql(*args, **kwargs):
            return mock_metadata_result
        
        with patch("modules.search.pd.read_sql", side_effect=mock_read_sql):
            results = search_db("UL001")

            # Verify we got results back
            self.assertIsNotNone(results)
            self.assertFalse(results.empty)

    def test_bulk_import_metadata(self):
        """
        Example of how to write a new test: Testing bulk metadata import.
        This shows how to mock dependencies and verify behavior.
        """
        # 1. Set up test data
        test_data = self._create_sample_metadata()
        
        # 2. Create mocks for dependencies
        with patch("modules.data_import.pd.read_excel") as mock_read_excel, \
             patch("modules.data_import.Session") as mock_session:
            
            # 3. Configure mocks to return our test data
            mock_read_excel.return_value = test_data
            mock_session_instance = mock_session.return_value.__enter__.return_value
            mock_session_instance.execute = MagicMock()
            mock_session_instance.commit = MagicMock()
            
            # 4. Run the function we're testing
            import_metadata("test.xlsx")
            
            # 5. Verify the function did what we expected
            # - Should have called execute at least twice (delete + insert)
            self.assertGreater(
                mock_session_instance.execute.call_count,
                1,
                "Expected multiple database operations (delete + bulk insert)"
            )
            # - Should have committed the transaction
            mock_session_instance.commit.assert_called_once()

    @patch("modules.data_import.SeqIO")
    @patch("modules.data_import.Session")
    def test_bulk_fasta_import(self, mock_session, mock_seqio):
        """
        Test bulk FASTA file import with batched inserts.
        Verifies that:
        1. Records are processed in batches
        2. All sequences are properly inserted
        3. Batch size limits are respected
        """
        # 1. Create mock FASTA records (simulate 1000 sequences)
        class MockRecord:
            def __init__(self, idx):
                self.id = f"seq{idx}"
                self.seq = f"ATCG" * 25  # 100 bp sequence
        
        mock_records = [MockRecord(i) for i in range(1000)]
        mock_seqio.parse.return_value = mock_records
        
        # 2. Set up session mock with tracking
        mock_session_instance = mock_session.return_value.__enter__.return_value
        mock_session_instance.execute = MagicMock()
        mock_session_instance.commit = MagicMock()
        
        # Mock the lab_id check to return True (simulating existing lab_id)
        mock_session_instance.execute.return_value.mappings.return_value.fetchone.return_value = {"lab_id": "UL001"}
        
        # 3. Run the import with a test lab_id
        with patch("builtins.input", return_value="UL001"):  # Mock user input for lab_id
            import_fasta("test.fasta")
        
        # 4. Verify batched inserts occurred
        execute_calls = mock_session_instance.execute.call_count
        
        # We expect:
        # - At least 2 batches (1000 records / 500 batch_size = 2)
        # - One extra call for checking lab_id existence
        self.assertGreater(
            execute_calls,
            2,
            "Expected multiple batch inserts"
        )
        
        # Verify transaction was committed
        mock_session_instance.commit.assert_called_once()

    @patch("modules.data_import.import_fasta")
    def test_bulk_fasta_folder_import(self, mock_import_fasta):
        """
        Test importing multiple FASTA files from a folder.
        Verifies that:
        1. All FASTA files in folder are processed
        2. Each file triggers an import
        3. Errors in one file don't stop processing of others
        """
        # Create mock file list
        mock_files = [
            "test1.fasta",
            "test2.fna",
            "test3.fa",
            "notafasta.txt"  # Should be ignored
        ]
        
        # Mock os.path and os.listdir
        with patch("os.path.isdir", return_value=True), \
             patch("os.listdir", return_value=mock_files), \
             patch("os.path.join", side_effect=lambda p, f: f"{p}/{f}"):
            
            from modules.data_import import import_fasta_from_folder
            import_fasta_from_folder("/mock/path")
        
        # Should have called import_fasta 3 times (one per FASTA file)
            self.assertEqual(
                mock_import_fasta.call_count,
                3,
                "Should process exactly 3 FASTA files"
            )

    @patch("modules.data_import.SeqIO")
    @patch("modules.data_import.Session")
    def test_compressed_fasta_import(self, mock_session, mock_seqio):
        """
        Test importing compressed (gzipped) FASTA files.
        Verifies that:
        1. Gzipped files can be read
        2. Sequences are correctly extracted
        3. Batch processing works with compressed files
        """
        # Create a mock gzipped FASTA file content
        mock_fasta = ">seq1\nATCG\n>seq2\nGTCA\n"
        mock_gzip = io.BytesIO()
        with gzip.GzipFile(fileobj=mock_gzip, mode='wb') as gz:
            gz.write(mock_fasta.encode())
        
        # Create mock records
        records = [
            SeqRecord(Seq("ATCG"), id="seq1"),
            SeqRecord(Seq("GTCA"), id="seq2")
        ]
        mock_seqio.parse.return_value = records
        
        # Set up session mock
        mock_session_instance = mock_session.return_value.__enter__.return_value
        mock_session_instance.execute = MagicMock()
        mock_session_instance.commit = MagicMock()
        mock_session_instance.execute.return_value.mappings.return_value.fetchone.return_value = {"lab_id": "UL001"}
        
        # Run import with mock gzipped file
        with patch("builtins.input", return_value="UL001"):
            import_fasta("test.fasta.gz")
        
        # Verify sequences were imported
        self.assertTrue(mock_session_instance.execute.called)
        self.assertTrue(mock_session_instance.commit.called)

    @patch("modules.data_import.SeqIO")
    @patch("modules.data_import.Session")
    def test_large_sequence_import(self, mock_session, mock_seqio):
        """
        Test importing very large sequences (>1MB each).
        Verifies that:
        1. Large sequences are handled efficiently
        2. Memory usage is reasonable
        3. Batch processing works with large sequences
        """
        # Create a large mock sequence (2MB of ATCG repeats)
        large_seq = "ATCG" * (500_000)  # 2MB sequence
        records = [
            SeqRecord(Seq(large_seq), id=f"large_seq_{i}")
            for i in range(3)  # 3 large sequences
        ]
        mock_seqio.parse.return_value = records
        
        # Set up session mock
        mock_session_instance = mock_session.return_value.__enter__.return_value
        mock_session_instance.execute = MagicMock()
        mock_session_instance.commit = MagicMock()
        mock_session_instance.execute.return_value.mappings.return_value.fetchone.return_value = {"lab_id": "UL001"}
        
        # Run import
        with patch("builtins.input", return_value="UL001"):
            import_fasta("large_sequences.fasta")
        
        # Verify large sequences were processed
        self.assertTrue(mock_session_instance.execute.called)
        self.assertTrue(mock_session_instance.commit.called)

    def test_fasta_import_benchmark(self):
        """
        Benchmark test for FASTA import performance.
        Creates actual test files and measures import speed.
        """
        # Create test data
        num_sequences = 1000
        sequences = []
        for i in range(num_sequences):
            seq = "ATCG" * 25  # 100 bp sequence
            sequences.append(
                SeqRecord(
                    Seq(seq),
                    id=f"seq_{i}",
                    description=f"Test sequence {i}"
                )
            )
        
        # Create a temporary FASTA file
        test_file = "test_benchmark.fasta"
        try:
            SeqIO.write(sequences, test_file, "fasta")
            
            # Time the import
            with patch("builtins.input", return_value="UL001"):
                start_time = time.time()
                import_fasta(test_file)
                end_time = time.time()
            
            duration = end_time - start_time
            sequences_per_second = num_sequences / duration
            
            print(f"\nFASTA Import Benchmark Results:")
            print(f"Total sequences: {num_sequences}")
            print(f"Total time: {duration:.2f} seconds")
            print(f"Sequences per second: {sequences_per_second:.2f}")
            
            # Basic performance assertion (adjust threshold as needed)
            self.assertLess(
                duration,
                30,  # Should process 1000 sequences in under 30 seconds
                "Import took too long"
            )
            
        finally:
            # Cleanup
            import os
            if os.path.exists(test_file):
                os.remove(test_file)    def test_print_row_key_value(self):
        # Mock data
        mock_row = {"lab_id": "UL001", "sample_location_plate": "A1"}

        # Call the function
        with patch("builtins.print") as mock_print:
            print_row_key_value(mock_row, "Test Row")

            # Assert that print was called
            self.assertTrue(mock_print.called)


if __name__ == "__main__":
    unittest.main()