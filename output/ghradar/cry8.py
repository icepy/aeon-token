#!/usr/bin/env python3
"""Round-8: re-verify the crypto cohort from round 7 (saturated by `seen`, not empty)."""
import json
import subprocess
import time
import urllib.parse
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
CRY = {"verifiable inference", "proof of useful work", "data availability",
       "restaking", "intent-based", "maximal extractable value"}

prev = json.load(open("output/ghradar/full7.json", encoding="utf-8"))
cry = [c for c in prev if c.get("term") in CRY]
print("第七轮加密侧仓数: %d" % len(cry))


def gh_get(path):
    for i in range(3):
        r = subprocess.run(["gh", "api", path], capture_output=True,
                           text=True, timeout=45)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout), None
        if "409" in r.stderr:
            return None, "409"
        time.sleep(4 * (i + 1))
    return None, "fail"


def cs(rid, days):
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    d, e = gh_get("repos/%s/commits?%s" % (rid, qs))
    if d is None:
        return None, e
    return len(d), "ok"


res = []
for c in cry:
    n30, s30 = cs(c["repo"], 30)
    n7 = None
    if s30 == "ok" and n30:
        n7, _ = cs(c["repo"], 7)
    res.append({**c, "r8_30d": n30, "r8_7d": n7, "r8_status": s30})
    time.sleep(0.1)

json.dump(res, open("output/ghradar/cry8.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

ver = [c for c in res if c["r8_30d"] is not None]
act = [c for c in ver if c["r8_30d"] >= 5]
live = [c for c in act if (c["r8_7d"] or 0) > 0]
print("复核 %d · ≥5 提交/30d %d (%.1f%%) · 7d 仍活跃 %d (%.1f%%)"
      % (len(ver), len(act), 100.0 * len(act) / max(1, len(ver)),
         len(live), 100.0 * len(live) / max(1, len(ver))))
print()
print("仍在写（7d>0）:")
for c in sorted(live, key=lambda x: -(x["r8_7d"] or 0)):
    print("  %-46s ★%-4d 30d=%-4s 7d=%-4s %-26s %s"
          % (c["repo"][:46], c["stars"], c["r8_30d"], c["r8_7d"], c["term"],
             c["desc"][:44]))
print()
print("爆完即停（30d≥5 / 7d=0）:")
for c in sorted([x for x in act if (x["r8_7d"] or 0) == 0],
                key=lambda x: -x["r8_30d"]):
    print("  %-46s ★%-4d 30d=%-4s %-26s %s"
          % (c["repo"][:46], c["stars"], c["r8_30d"], c["term"], c["desc"][:44]))
