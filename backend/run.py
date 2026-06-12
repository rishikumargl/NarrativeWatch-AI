#!/usr/bin/env python3
"""Simple startup script for NarrativeWatch backend."""

import uvicorn
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == '__main__':
    print("[OK] Starting NarrativeWatch AI Backend")
    print("[OK] URL: http://localhost:8000")
    print("[OK] Docs: http://localhost:8000/docs")
    print()

    uvicorn.run(
        'src.app:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
        log_level='info'
    )
