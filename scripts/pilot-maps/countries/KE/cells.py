#!/usr/bin/env python3
"""Kenya is built with Bolivia, Argentina and Honduras as country group KE-LAC.
The Kenya recruitments are in ke_cells.py; the engine and the writer are countries/LAC/cells.py.

    python3 cells.py [--fetch]    # same as running ../LAC/cells.py
"""
import os, runpy, sys

if __name__ == "__main__":
    runpy.run_path(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "LAC", "cells.py"), run_name="__main__")
