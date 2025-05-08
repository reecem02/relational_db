import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from modules.data_import import import_metadata, validate_columns
from modules.data_output import display_data_by_lab_id, print_row_key_value
from modules.db_info import get_database_info, ensure_file_uploaded_field
from modules.search import search_db


class TestMycoResearch(unittest.TestCase):

    def setUp(self):
        """
        Runs before each test. Prints the name of the test being executed.
        """
        print(f"\nRunning test: {self._testMethodName}")

    def tearDown(self):
        """
        Runs after each test. Prints a separator for clarity.
        """
        print(f"Finished test: {self._testMethodName}")
        print("-" * 50)

    @patch("modules.data_import.pd.read_excel")
    @patch("modules.data_import.Session")
    def test_import_metadata(self, mock_session, mock_read_excel):
        # Mock data
        mock_data = pd.DataFrame({
            "Uehling Lab ID": ["UL001", "UL002"],
            "Sample Location Plate": ["A1", "B2"],
            "GC3F Submission Sample ID": ["GC001", "GC002"],
            "Extraction Date": [datetime(2025, 1, 1), datetime(2025, 1, 2)],
        })
        mock_read_excel.return_value = mock_data

        # Mock session behavior
        mock_session.return_value.__enter__.return_value.execute = MagicMock()

        # Call the function
        import_metadata("mock_file_path.xlsx")

        # Assert that the session's execute method was called
        self.assertTrue(mock_session.return_value.__enter__.return_value.execute.called)

    @patch("modules.data_output.engine.connect")
    def test_display_data_by_lab_id(self, mock_connect):
        # Mock query results for Metadata and GenomicData tables
        mock_connect.return_value.execute.side_effect = [
            MagicMock(fetchall=lambda: [{"lab_id": "UL001", "sample_location_plate": "A1"}]),
        ]

        # Call the function
        display_data_by_lab_id("UL001")

        # Assert that the database connection was used
        self.assertTrue(mock_connect.called)

    @patch("modules.db_info.engine.connect")
    def test_get_database_info(self, mock_connect):
        # Mock query results
        mock_connect.return_value.execute.side_effect = [
            MagicMock(mappings=lambda: {"count": 10, "last_uploaded": "2025-01-01"}),  # Metadata
            MagicMock(mappings=lambda: {"count": 5, "last_uploaded": "2025-01-02"}),   # GenomicData
        ]

        # Call the function
        get_database_info()

        # Assert that the database connection was used
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
        # Mock data
        mock_df = pd.DataFrame({
            "Uehling Lab ID": ["UL001", "UL002"],
            "Sample Location Plate": ["A1", "B2"],
        })

        # Mock database schema
        with patch("modules.data_import.inspect") as mock_inspect:
            mock_inspect.return_value.get_columns.return_value = [
                {"name": "Uehling Lab ID"},
                {"name": "Sample Location Plate"},
            ]

            # Call the function
            validate_columns("Metadata", mock_df)

            # Assert no exceptions raised
            self.assertTrue(True)

    @patch("modules.search.engine.connect")
    def test_search_db(self, mock_connect):
        # Mock query results
        mock_connect.return_value.execute.return_value.fetchall.return_value = [
            {"lab_id": "UL001", "sample_location_plate": "A1"}
        ]

        # Call the function
        results = search_db("Uehling Lab ID", "UL001")

        # Assert that results are returned
        self.assertIsNotNone(results)

    def test_print_row_key_value(self):
        # Mock data
        mock_row = {"lab_id": "UL001", "sample_location_plate": "A1"}

        # Call the function
        with patch("builtins.print") as mock_print:
            print_row_key_value(mock_row, "Test Row")

            # Assert that print was called
            self.assertTrue(mock_print.called)


if __name__ == "__main__":
    unittest.main()