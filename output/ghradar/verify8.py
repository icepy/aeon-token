#!/usr/bin/env python3
"""Round-8 full verification pass: completes commits_30d/7d for every survivor.

Reads output/ghradar/out8.json, verifies repos lacking commits_30d, rewrites
out8.json and regenerates audit8.log's verification sections.
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

OUTD = "output/ghradar"
OUT = OUTD + "/out8.json"
MMD = OUTD + "/verify8.json"

now = datetime.now(timezone.utc)
GH = True
gh_lost = [False]


def gh_get(path):
    global GH
    last = ""
    if GH:
        for i in range(3):
            try:
                r = subprocess.run(["gh", "api", path], capture_output=True,
                                   text=True, timeout=45)
                if r.returncode == 0 and r.stdout.strip():
                    return json.loads(r.stdout), None
                last = r.stderr.strip()
                if "409" in last or "empty" in last.lower():
                    return None, "HTTP 409"
                if ("rate limit" in last.lower() or "429" in last
                        or "403" in last or "secondary" in last.lower()):
                    time.sleep(5 * (i + 1))
                    continue
                break
            except Exception as ex:
                last = str(ex)
                time.sleep(3)
        print("  ! gh api 放弃: %s" % last[:140], file=sys.stderr)
        GH = False
        gh_lost[0] = True
    for i in range(2):
        try:
            req = urllib.request.Request("https://api.github.com/" + path, headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "aeon-github-radar"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.load(resp), None
        except urllib.error.HTTPError as he:
            last = "HTTP %s" % he.code
            if he.code in (403, 429):
                time.sleep(8 * (i + 1))
                continue
            return None, last
        except Exception as ex:
            last = str(ex)
            time.sleep(3)
    return None, last


def commits_since(rid, days):
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    data, err = gh_get("repos/%s/commits?%s" % (rid, qs))
    if data is None:
        return None, ("empty" if err and "409" in err else "unverified")
    return (len(data) if isinstance(data, list) else None), "ok"


out = json.load(open(OUT, encoding="utf-8"))
stats = {"ok": 0, "empty": 0, "unverified": 0, "skipped": 0}
t0 = time.time()

for c in out:
    if c.get("commits_30d") is not None or c.get("maybe_empty"):
        stats["skipped"] += 1
        continue
    n30, st = commits_since(c["repo"], 30)
    if st == "empty":
        c["maybe_empty"] = True
        stats["empty"] += 1
        continue
    if st != "ok":
        c["unverified"] = True
        stats["unverified"] += 1
        continue
    c.pop("unverified", None)
    c["commits_30d"] = n30
    stats["ok"] += 1
    if n30 >= 100:
        c["commits_30d_ge"] = True
    if n30 == 0:
        c["stale"] = True
        continue
    n7, st7 = commits_since(c["repo"], 7)
    if st7 == "ok":
        c["commits_7d"] = n7
        if n7 >= 100:
            c["commits_7d_ge"] = True
        if n7 == 0:
            c["burst_only"] = True
    if not c.get("language"):
        c["no_lang"] = True
    if stats["ok"] % 25 == 0:
        print("  ... %d verified (%.0fs)" % (stats["ok"], time.time() - t0))

owner_n = Counter(c["owner"] for c in out)
for c in out:
    if owner_n[c["owner"]] >= 3:
        c["owner_repos"] = owner_n[c["owner"]]

json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(stats, open(MMD, "w", encoding="utf-8"), indent=1)

ver = [c for c in out if c.get("commits_30d") is not None]
rep = sorted([c for c in out
              if c.get("commits_30d") is not None and c["commits_30d"] >= 5
              and not c.get("stale") and not c.get("maybe_empty")],
             key=lambda c: (-c.get("commits_7d", 0), -c["commits_30d"], -c["stars"]))
print(json.dumps(stats, indent=1))
print("幸存 %d | 已核验 %d (%.1f%%) | 报告级 %d (%.1f%%) | 7d活跃 %d"
      % (len(out), len(ver), 100.0 * len(ver) / max(1, len(out)), len(rep),
         100.0 * len(rep) / max(1, len(ver)),
         len([c for c in ver if c.get("commits_7d", 0) > 0])))
if gh_lost[0]:
    print("⚠️ gh 认证丢失，降级未认证")
