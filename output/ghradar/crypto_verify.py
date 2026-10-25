#!/usr/bin/env python3
"""加密侧全部命中的提交核验（只有 ~39 个，全查得起）。"""
import json, subprocess, urllib.parse
from datetime import datetime, timedelta, timezone

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
now = datetime.now(timezone.utc)
CRY = ["verifiable inference", "proof of useful work", "data availability",
       "restaking", "intent-based", "maximal extractable value"]
cs = [c for c in out if c["term"] in CRY]

def gh(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None

print("加密侧命中 %d 个" % len(cs))
for c in sorted(cs, key=lambda x: -x["stars"]):
    qs = urllib.parse.urlencode({"since": (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                 "per_page": "100"})
    try:
        d = gh("repos/%s/commits?%s" % (c["repo"], qs))
        n = len(d) if isinstance(d, list) else "EMPTY/409"
    except Exception:
        n = "ERR"
    # size 单独看：size=0 = 空仓
    try:
        meta = gh("repos/%s" % c["repo"])
        size = meta.get("size") if meta else "?"
        lang = (meta or {}).get("language")
    except Exception:
        size, lang = "?", None
    print("  c30=%-9s size=%-7s lang=%-10s %4d ★ %s %-44s [%s]"
          % (str(n), str(size), str(lang), c["stars"], c["created"], c["repo"], c["term"]))
