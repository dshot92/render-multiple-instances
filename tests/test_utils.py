import sys
import os

# Add the parent directory to sys.path to allow importing from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import get_export_dir, flipbook_render_output_path
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import bpy

# ... rest of the file remains unchanged ...

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
            ("/absolute/path/to/export/v001/file.png",
             "/absolute/path/to/export/v001/"),
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
    @patch('os.makedirs')
    @patch('os.listdir')
    @patch('os.path.exists')
    def test_flipbook_render_output_path(self, mock_exists, mock_listdir, mock_makedirs, mock_context, mock_abspath):
        """
        Test the flipbook_render_output_path function with various scenarios.
        """
        # Setup mock for bpy.context.scene.RMI_Props
        mock_context.scene.RMI_Props = MagicMock()
        mock_context.scene.RMI_Props.flipbook_dir = Path("/flipbooks")

        # Mock the return value of bpy.path.abspath to simulate an absolute path
        mock_abspath.return_value = Path("/flipbooks")

        # Mock os.path.exists to return True
        mock_exists.return_value = True

        # Test case 1: No existing directories
        mock_listdir.return_value = []
        result = flipbook_render_output_path(mock_context, "flipbook_render")
        expected_output = Path("/flipbooks/flipbook_render_v000")
        self.assertEqual(Path(result), expected_output)

        # Test case 2: Existing directories with non-consecutive versions
        mock_listdir.return_value = ['flipbook_render_v000', 'flipbook_render_v002']
        result = flipbook_render_output_path(mock_context, "flipbook_render")
        expected_output = Path("/flipbooks/flipbook_render_v003")
        self.assertEqual(Path(result), expected_output)

        # Test case 3: Existing directories with consecutive versions and missing version
        mock_listdir.return_value = ['flipbook_render_v001', 'flipbook_render_v002']
        result = flipbook_render_output_path(mock_context, "flipbook_render")
        expected_output = Path("/flipbooks/flipbook_render_v003")
        self.assertEqual(Path(result), expected_output)

        # Test case 4: Flipbook viewport render
        mock_listdir.return_value = ['flipbook_viewport_v000']
        result = flipbook_render_output_path(mock_context, "flipbook_viewport")
        expected_output = Path("/flipbooks/flipbook_viewport_v001")
        self.assertEqual(Path(result), expected_output)


if __name__ == '__main__':
    unittest.main()
