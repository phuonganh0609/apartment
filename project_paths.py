"""Make the backend and chatbot Django applications importable."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for directory in (ROOT / "backend", ROOT / "chatbot"):
    value = str(directory)
    if value not in sys.path:
        sys.path.insert(0, value)
