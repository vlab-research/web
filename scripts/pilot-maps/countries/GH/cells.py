#!/usr/bin/env python3
"""Ghana's half of group NG-GH. The group is built by one script, ../NG/cells.py, because the
four output files are per group; this wrapper runs it with the same arguments.

    PILOT_GEO=<dir with build_maps.py + Natural Earth + geonames/GH.txt> <venv python> cells.py [--fetch] [--only=GH]
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.exit(subprocess.run([sys.executable, os.path.join(HERE, "..", "NG", "cells.py")] + sys.argv[1:]).returncode)
