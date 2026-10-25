#!/usr/bin/env python3
"""第七轮补：对第七轮新增的 332 幸存者做全量 30d/7d 核验。"""
import json, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

SRC = "output/ghradar/out7.json"
DST = "output/ghradar/full7b.json"
now = datetime.now(timezone.utc)

_args = sys.argv[1:]
def _arg(name, default):
    for a in _args:
        if a.startswith(name + ":"):
            return a.split(":", 1)[1]
    return default
THREADS = int(_arg("threads", 6))

repos = json.load(open(SRC, encoding="utf-8"))

def ncommits(rid, days):
    since = (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    path = "repos/%s/commits?since=%s&per_page=100" % (rid, since)
    last = ""
    for attempt in range(3):
        try:
            r = subprocess.run(["gh", "api", path], capture_output=True,
                               text=True, timeout=60)
            if r.returncode == 0 and r.stdout.strip():
                d = json.loads(r.stdout)
                return (len(d) if isinstance(d, list) else None), "ok"
            last = (r.stderr or "").strip()
            if "409" in last or "empty" in last.lower():
                return None, "empty"
            if "404" in last:
                return None, "gone"
            if ("rate limit" in last.lower() or "429" in last or "403" in last
                    or "secondary" in last.lower()):
                time.sleep(4 * (attempt + 1)); continue
            break
        except Exception as ex:
            last = str(ex); time.sleep(2)
    return None, "err"

def work(c):
    n30, st30 = ncommits(c["repo"], 30)
    if st30 != "ok":
        c["q_status"] = st30
        return c
    c["commits_30d"] = n30
    if n30 == 0:
        c["commits_7d"] = 0; c["stale"] = True; c["q_status"] = "ok"
        return c
    n7, st7 = ncommits(c["repo"], 7)
    if st7 == "ok":
        c["commits_7d"] = n7
        if n7 == 0:
            c["burst_only"] = True
        c["q_status"] = "ok"
    else:
        c["q_status"] = "30ok_7" + st7
    return c

with ThreadPoolExecutor(max_workers=THREADS) as ex:
    res = list(ex.map(work, repos))

json.dump(res, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
ok = [c for c in res if c.get("q_status") == "ok"]
rep = [c for c in ok if c["commits_30d"] >= 5]
act = [c for c in ok if c.get("commits_7d", 0) >= 1]
print("新增幸存 %d | ok=%d | ≥5提交 %d (%.1f%%) | 7d活跃 %d (%.1f%%)"
      % (len(res), len(ok), len(rep), 100.0 * len(rep) / max(len(ok), 1),
         len(act), 100.0 * len(act) / max(len(ok), 1)))
print("\n≥5 提交/30d 且 7d 活跃（本轮真正的新增活仓）:")
for c in sorted([c for c in rep if c.get("commits_7d", 0) >= 1],
                key=lambda c: -c["commits_7d"]):
    print("  %-52s ★%-4d 30d=%-4d 7d=%-4d [%s] %s"
          % (c["repo"], c["stars"], c["commits_30d"], c["commits_7d"],
             c["term"], c.get("lang", "")))
