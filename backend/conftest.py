"""
Pytest configuration file to set up Python path for tests.
"""
import sys
from pathlib import Path

# Add the backend directory to Python path so 'app' module can be found
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
