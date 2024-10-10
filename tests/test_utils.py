import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import os

# Add the parent directory to sys.path to allow importing from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import get_export_dir

class TestUtils(unittest.TestCase):

    @patch('bpy.path.abspath')
    @patch('bpy.context')
    @patch('pathlib.Path.is_dir')
    def test_get_export_dir(self, mock_is_dir, mock_context, mock_abspath):
        """
        Test the get_export_dir function with various input paths.
        
        This test checks if the function correctly extracts the export directory
        from different types of input paths, including relative and absolute paths,
        with and without file names or frame numbers.
        """
        # Setup mock for bpy.context.scene.render.filepath
        mock_context.scene.render.filepath = MagicMock()
        # Set is_dir to always return False for this test
        mock_is_dir.return_value = False

        test_cases = [
            ("//export/v001/", "//export/v001/"),
            ("//export/v001/temp", "//export/v001/"),
            ("//export/v001/temp###", "//export/v001/"),
            ("//export/v001/temp###.png", "//export/v001/"),
            ("/absolute/path/to/export/v001/", "/absolute/path/to/export/v001/"),
            ("/absolute/path/to/export/v001/file.png", "/absolute/path/to/export/v001/"),
        ]

        for input_path, expected_output in test_cases:
            # Set the mock return value for bpy.path.abspath
            mock_abspath.return_value = input_path

            # Call the function
            result = get_export_dir()

            # Assert the result
            self.assertEqual(result, Path(expected_output))

    @patch('bpy.path.abspath')
    @patch('bpy.context')
    @patch('pathlib.Path.is_dir')
    def test_get_export_dir_with_is_dir(self, mock_is_dir, mock_context, mock_abspath):
        """
        Test the get_export_dir function when the input path is a directory.
        
        This test verifies that the function returns the input path unchanged
        when it represents a directory, simulating the behavior of Path.is_dir()
        returning True.
        """
        # Setup mock for bpy.context.scene.render.filepath
        mock_context.scene.render.filepath = MagicMock()
        # Set is_dir to return True for this test
        mock_is_dir.return_value = True

        # Test case for when the path is a directory
        input_path = "//export/v001/"
        mock_abspath.return_value = input_path

        result = get_export_dir()
        self.assertEqual(result, Path(input_path))

if __name__ == '__main__':
    unittest.main()