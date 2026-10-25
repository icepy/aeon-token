#!/usr/bin/env python3
"""判定测试：找出哪一种查询写法能同时复现 84 与上轮逐周曲线 5/9/5/6/17/18/6/10/8。"""
import json, subprocess, time, urllib.parse

PREV = {"W35": 5, "W36": 9, "W37": 5, "W38": 6, "W39": 17,
        "W40": 18, "W41": 6, "W42": 10, "W43": 8}

def gh(path):
    for i in range(4):
        r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
        if "rate limit" in r.stderr.lower():
            time.sleep(7 * (i + 1)); continue
        return None
    return None

def total(expr):
    qs = urllib.parse.urlencode({"q": expr, "per_page": "1"})
    d = gh("search/repositories?" + qs)
    time.sleep(3)
    return d.get("total_count", -1) if d else -1

VARIANTS = {
    "exact+forks:false (用今日)":
        '"world action model" in:name,description created:>=2026-08-26 fork:false',
    "exact 无 fork":
        '"world action model" in:name,description created:>=2026-08-26',
    "exact in:name only":
        '"world action model" in:name created:>=2026-08-26 fork:false',
    "无引号 in:name,desc":
        'world action model in:name,description created:>=2026-08-26 fork:false',
    "exact 默认范围":
        '"world action model" created:>=2026-08-26 fork:false',
    "连字符形式":
        '"world-action-model" in:name,description created:>=2026-08-26 fork:false',
    "exact 上轮同日窗":
        '"world action model" in:name,description created:2026-08-26..2026-10-24 fork:false',
}
for name, expr in VARIANTS.items():
    print("%-30s total=%s" % (name, total(expr)))

print("\n上轮逐周曲线合计 = %d" % sum(PREV.values()))
