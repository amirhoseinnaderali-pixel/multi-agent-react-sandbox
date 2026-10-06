"""Compatibility entry point for the VMAR-PS research framework."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from vmar_ps.cli import main

if __name__ == "__main__":
    main("configs/vmar_ps.yaml")
