#!/usr/bin/env python3
"""第九轮：全量核验 234 幸存者（core 配额 5,000/h，与 search 独立池）。
补 scan 的 PER_TERM_CAP=25 造成的长尾未核验。409(空仓) 与 429(限速) 分开。"""
import json, subprocess, sys, time
from datetime import datetime, timedelta, timezone

OUT = "output/ghradar/out.json"
now = datetime.now(timezone.utc)

def gh(path, tries=4):
    last = ""
    for i in range(tries):
        try:
            r = subprocess.run(["gh", "api", path], capture_output=True,
                               text=True, timeout=60)
            if r.returncode == 0 and r.stdout.strip():
                return json.loads(r.stdout), "ok"
            last = (r.stderr or "").strip()
            if "409" in last or "empty" in last.lower():
                return None, "409"          # 真空仓：不降级
            if ("rate limit" in last.lower() or "429" in last
                    or "secondary" in last.lower() or "abuse" in last.lower()):
                time.sleep(6 * (i + 1)); continue
            return None, "err:" + last[:80]
        except Exception as ex:
            last = str(ex); time.sleep(3)
    return None, "429:" + last[:60]

def count(rid, days):
    qs = "since=%s&per_page=100" % (
        (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ"))
    d, st = gh("repos/%s/commits?%s" % (rid, qs))
    if st == "409":
        return None, "409"
    if st != "ok" or not isinstance(d, list):
        return None, st
    return len(d), "ok"

out = json.load(open(OUT, encoding="utf-8"))
stats = {"ok": 0, "409": 0, "fail": 0}
for i, c in enumerate(out):
    rid = c["repo"]
    n30, st = count(rid, 30)
    if st == "409":
        c["maybe_empty"] = True; c.pop("commits_30d", None)
        stats["409"] += 1; continue
    if st != "ok":
        c["unverified"] = True; c.pop("commits_30d", None)
        stats["fail"] += 1; continue
    c["unverified"] = False
    c["commits_30d"] = n30
    c["commits_30d_ge"] = n30 >= 100
    c["stale"] = n30 == 0
    c.pop("burst_only", None); c.pop("commits_7d", None)
    c.pop("commits_7d_ge", None)
    if n30 > 0:
        n7, st7 = count(rid, 7)
        if st7 == "ok":
            c["commits_7d"] = n7
            c["commits_7d_ge"] = n7 >= 100
            c["burst_only"] = n7 == 0
        else:
            c["commits_7d"] = None
    if not c.get("language"):
        c["no_lang"] = True
    else:
        c.pop("no_lang", None)
    stats["ok"] += 1
    if (i + 1) % 25 == 0:
        print("  ..%d/%d" % (i + 1, len(out)), file=sys.stderr, flush=True)
    time.sleep(0.2)

json.dump(out, open("output/ghradar/out9full.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

ver = [c for c in out if c.get("commits_30d") is not None]
rep = sorted([c for c in ver if c["commits_30d"] >= 5 and not c.get("stale")],
             key=lambda c: (-(c.get("commits_7d") or 0), -c["commits_30d"], -c["stars"]))
L = ["全量核验 %d/%d = %.1f%% · ok=%d 409空仓=%d 失败=%d"
     % (len(ver), len(out), 100.0 * len(ver) / max(1, len(out)),
        stats["ok"], stats["409"], stats["fail"]),
     "≥5 提交/30d 报告级 %d · 7d 仍在写 %d（%.1f%%）"
     % (len(rep), sum(1 for c in rep if (c.get("commits_7d") or 0) > 0),
        100.0 * sum(1 for c in rep if (c.get("commits_7d") or 0) > 0) / max(1, len(rep))),
     "30d 零提交 %d · 爆完即停 %d · 撞≥100 上限 %d · 无 language %d"
     % (sum(1 for c in ver if c.get("stale")),
        sum(1 for c in rep if c.get("burst_only")),
        sum(1 for c in ver if c.get("commits_30d_ge")),
        sum(1 for c in out if c.get("no_lang")))]
for c in rep:
    L.append("  %s ★%d 30d=%s%s 7d=%s%s [%s] %s" % (
        c["repo"], c["stars"],
        "≥100" if c.get("commits_30d_ge") else c["commits_30d"],
        " [爆完即停]" if c.get("burst_only") else "",
        "≥100" if c.get("commits_7d_ge") else c.get("commits_7d", "-"),
        " [页形态]" if c.get("page_form") else "",
        c["term"], c["desc"][:90]))
open("output/ghradar/full9.log", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
