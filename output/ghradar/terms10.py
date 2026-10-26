#!/usr/bin/env python3
"""github-radar 第十轮：弱词跨窗 total_count 测量（7 / 30 / 60 天）。

7 天窗会把稀有词读成 0 —— 那不是「词废了」，是「窗口太短」。
SKILL 铁律：报零命中必须四分类，真零才谈删词。
"""
import json
import subprocess
import time
import urllib.parse

TERMS = ["verifiable inference", "proof of useful work", "maximal extractable value",
         "robotics data engine", "restaking", "intent-based", "data availability",
         "embodied data", "robot dataset", "world action model", "vision language action"]
WINS = ["2026-10-19..2026-10-26", "2026-09-26..2026-10-26", "2026-08-27..2026-10-26"]


def count(term, win):
    q = '"%s" in:name,description created:%s fork:false' % (term, win)
    qs = urllib.parse.urlencode({"q": q, "per_page": "1"})
    r = subprocess.run(["gh", "api", "search/repositories?" + qs, "--jq", ".total_count"],
                       capture_output=True, text=True, timeout=45)
    return r.stdout.strip() or ("ERR:" + r.stderr.strip()[:40])


res = {}
for t in TERMS:
    row = {}
    for w in WINS:
        row[w] = count(t, w)
        time.sleep(7)
    res[t] = row
    print("%-26s 7d=%-6s 30d=%-6s 60d=%-6s" % (t, row[WINS[0]], row[WINS[1]], row[WINS[2]]))

json.dump(res, open("output/ghradar/terms10.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
