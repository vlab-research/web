#!/usr/bin/env python3
"""Group US-EU, Ireland and Germany: built by ../US/cells.py together with the United States.

    python3 cells.py [--fetch]

The recruitments IE-* and DE-* are listed in scripts/pilot-maps/private/US-EU.map.json and their raw
pulls live in ../US/raw/ (gitignored). This wrapper only runs that script, so the three countries
stay in one set of files: scripts/data/cells/US-EU.{cells,criteria,places}.json.
"""
import os, runpy, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv[0] = os.path.join(HERE, "..", "US", "cells.py")
runpy.run_path(sys.argv[0], run_name="__main__")
