# Make tests directory a Python package
import os
import sys

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Make tests directory a Python package
