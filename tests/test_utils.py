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

        # Mock os.path.exists to return True
        mock_exists.return_value = True

        # Test case 1: Absolute path
        mock_context.scene.RMI_Props.flipbook_dir = "/flipbooks"
        mock_abspath.return_value = "/flipbooks"
        mock_listdir.return_value = []
        result = flipbook_render_output_path(mock_context, "flipbook_render")
        expected_output = Path("/flipbooks/flipbook_render_v000")
        self.assertEqual(Path(result), expected_output)

        # Test case 2: Relative path (starting with "//")
        mock_context.scene.RMI_Props.flipbook_dir = "//flipbooks"
        mock_abspath.return_value = "/base/flipbooks"
        mock_listdir.return_value = ['flipbook_render_v000']
        result = flipbook_render_output_path(mock_context, "flipbook_render")
        expected_output = Path("/base/flipbooks/flipbook_render_v001")
        self.assertEqual(Path(result), expected_output)

        # Test case 3: Path with existing versions
        mock_context.scene.RMI_Props.flipbook_dir = "/renders/flipbooks"
        mock_abspath.return_value = "/renders/flipbooks"
        mock_listdir.return_value = ['flipbook_render_v000', 'flipbook_render_v001', 'flipbook_render_v003']
        result = flipbook_render_output_path(mock_context, "flipbook_render")
        expected_output = Path("/renders/flipbooks/flipbook_render_v004")
        self.assertEqual(Path(result), expected_output)

        # Test case 4: Different render type
        mock_context.scene.RMI_Props.flipbook_dir = "/tmp/flipbooks"
        mock_abspath.return_value = "/tmp/flipbooks"
        mock_listdir.return_value = ['flipbook_viewport_v000']
        result = flipbook_render_output_path(mock_context, "flipbook_viewport")
        expected_output = Path("/tmp/flipbooks/flipbook_viewport_v001")
        self.assertEqual(Path(result), expected_output)

        # Test case 5: Path with spaces and special characters
        mock_context.scene.RMI_Props.flipbook_dir = "//My Projects/Blender Renders/Flipbooks!"
        mock_abspath.return_value = "/home/user/My Projects/Blender Renders/Flipbooks!"
        mock_listdir.return_value = []
        result = flipbook_render_output_path(mock_context, "flipbook_render")
        expected_output = Path("/home/user/My Projects/Blender Renders/Flipbooks!/flipbook_render_v000")
        self.assertEqual(Path(result), expected_output)

if __name__ == '__main__':
    unittest.main()
