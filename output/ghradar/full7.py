#!/usr/bin/env python3
"""第七轮：对第六轮全部幸存者做全量 30d/7d 提交核验。

前六轮的报告级一直是 250 仓抽样下的下限（第六轮核验 250/1251 = 20.0%）。
core quota 5000/h 足够覆盖 1251 仓 × 成本，本轮把它变成全量点估计。

用法: python3 output/ghradar/full7.py [threads:6] [limit:0]
"""
import json, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

SRC = "output/ghradar/out6.json"
DST = "output/ghradar/full7.json"
now = datetime.now(timezone.utc)

_args = sys.argv[1:]
def _arg(name, default):
    for a in _args:
        if a.startswith(name + ":"):
            return a.split(":", 1)[1]
    return default

THREADS = int(_arg("threads", 6))
LIMIT = int(_arg("limit", 0))

repos = json.load(open(SRC, encoding="utf-8"))
if LIMIT:
    repos = repos[:LIMIT]

def ncommits(rid, days):
    """返回 (n, status)。n 为 None 时 status 说明原因。"""
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
    rid = c["repo"]
    n30, st30 = ncommits(rid, 30)
    if st30 != "ok":
        c["q_status"] = st30
        c.pop("commits_30d", None)
        c.pop("commits_7d", None)
        return c
    c["commits_30d"] = n30
    if n30 == 0:
        c["commits_7d"] = 0
        c["stale"] = True
        c["q_status"] = "ok"
        return c
    n7, st7 = ncommits(rid, 7)
    if st7 == "ok":
        c["commits_7d"] = n7
        if n7 == 0:
            c["burst_only"] = True
    else:
        c["q_status"] = "30ok_7" + st7
        return c
    c["q_status"] = "ok"
    return c

t0 = time.time()
done = [0]
def run(c):
    r = work(c)
    done[0] += 1
    if done[0] % 100 == 0:
        print("  %d/%d  %.1fs" % (done[0], len(repos), time.time() - t0),
              flush=True)
    return r

with ThreadPoolExecutor(max_workers=THREADS) as ex:
    res = list(ex.map(run, repos))

json.dump(res, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

ok = [c for c in res if c.get("q_status") == "ok"]
bad = [c for c in res if c.get("q_status") != "ok"]
rep = [c for c in ok if c["commits_30d"] >= 5]
act = [c for c in ok if c.get("commits_7d", 0) >= 1]
print("\n全量核验 %d 仓 | ok=%d 失败=%d (%.1fs)"
      % (len(res), len(ok), len(bad), time.time() - t0))
print("≥5 提交/30d: %d (%.1f%%)" % (len(rep), 100.0 * len(rep) / max(len(ok), 1)))
print("≥1 提交/7d:  %d (%.1f%%)" % (len(act), 100.0 * len(act) / max(len(ok), 1)))
from collections import Counter
print("30d 分布: " + " · ".join("%s=%d" % kv for kv in
      sorted(Counter(min(c["commits_30d"] // 10 * 10, 100) if c["commits_30d"] < 100 else 100
                     for c in ok).items())))
