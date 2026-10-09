"""
HealthGuard Application Launcher.
Starts the backend server and serves the full pharmaceutical e-commerce,
3D medicine reminder, adherence dashboard, and ecosystem platform.
"""

import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.server import run_server

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port=port)
