"""
Test runner for the Screencast Keys addon.

This script discovers and runs all tests in the 'tests' directory.
It can be run both inside and outside of the Blender environment.
If run outside Blender, it mocks the 'bpy' module to allow tests to execute.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock bpy module if we're not in Blender environment
if 'bpy' not in sys.modules:
    sys.modules['bpy'] = MagicMock()

# Discover and run tests
test_suite = unittest.TestLoader().discover('tests')
result = unittest.TextTestRunner(verbosity=2).run(test_suite)

# Exit with non-zero status if tests failed
sys.exit(not result.wasSuccessful())