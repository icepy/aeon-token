#!/usr/bin/env python3
"""设置 github-radar 的 var 变量后执行加固版扫描。"""
import os, runpy

os.environ["DRY"] = "1"    # dry-run
os.environ["DAYS"] = "60"  # days:60
os.environ["MIN"] = "0"
os.environ["CHK"] = "5"

runpy.run_path("output/ghradar/scan_paced.py", run_name="__main__")
