#!/usr/bin/env python3
"""Round-8 runner: pins run parameters so the command line carries no env prefix."""
import os
import runpy
import sys

os.environ["DRY"] = "1"
os.environ["DAYS"] = "60"
os.environ["MIN"] = "0"
os.environ["CHK"] = "5"

sys.argv = ["output/ghradar/scan8.py"]
runpy.run_path("output/ghradar/scan8.py", run_name="__main__")
