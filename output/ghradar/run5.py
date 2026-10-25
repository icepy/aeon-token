#!/usr/bin/env python3
"""github-radar 第 5 轮 runner：设置环境后执行 scan.py（避开 shell 的 VAR= 前缀限制）。"""
import os, runpy, sys

os.environ["DRY"] = "1"
os.environ["DAYS"] = "60"
os.environ["MIN"] = "0"
os.environ["CHK"] = "5"
sys.argv = ["scan.py"]
runpy.run_path("output/ghradar/scan.py", run_name="__main__")
