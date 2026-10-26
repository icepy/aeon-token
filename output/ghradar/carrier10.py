#!/usr/bin/env python3
"""github-radar 第十轮：carrier 误杀审计。

本轮 carrier 丢弃 123 个（其中 `world model` 一支占大头）。SKILL 的铁律是
「每条丢弃规则都要能被审计」——这里把 7 天窗内 `world model` 命中、但没进幸存
的仓库按 star 拉出来看，判断 carrier 是否把真机器人/具身仓也殃及了。
"""
import json
import subprocess
import time
import urllib.parse

WINS = ["2026-10-19..2026-10-26", "2026-10-22..2026-10-26", "2026-10-24..2026-10-26"]
CARRIER = ["embodied", "robot", "vla", "manipulation", "sim2real", "sim-to-real",
           "teleop", "egocentric", "action", "policy", "rlbench", "lerobot"]


def gh(path):
    for i in range(3):
        r = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=45)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
        time.sleep(8 * (i + 1))
    return None


seen = json.load(open("memory/github-seen.json", encoding="utf-8"))
cur = {c["repo"] for c in json.load(open("output/ghradar/out10.json", encoding="utf-8"))}

items = {}
for w in WINS:
    q = '"world model" in:name,description created:%s fork:false' % w
    for page in (1, 2, 3):
        qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                     "per_page": "100", "page": str(page)})
        r = gh("search/repositories?" + qs)
        if not r:
            break
        its = r.get("items", [])
        for it in its:
            items[it["full_name"]] = it
        time.sleep(7)
        if len(its) < 100:
            break

carrier_killed = []
for rid, it in items.items():
    if rid in seen or rid in cur:
        continue
    desc = (it.get("description") or "").strip()
    lowall = (rid + " " + desc).lower()
    if any(c in desc.lower() for c in CARRIER):
        continue          # carrier 放行了，是被别的规则丢的
    carrier_killed.append({
        "repo": rid, "stars": it.get("stargazers_count", 0),
        "created": (it.get("created_at") or "")[:10],
        "lang": it.get("language"), "desc": " ".join(desc.split())[:110]})

carrier_killed.sort(key=lambda x: -x["stars"])
print("7 天窗 `world model` 命中 %d 个；未被 carrier 放行且未进幸存 %d 个"
      % (len(items), len(carrier_killed)))
for r in carrier_killed[:25]:
    print("  ★%-5d %-46s %-10s %s" % (r["stars"], r["repo"][:46], r["lang"], r["desc"][:80]))

json.dump(carrier_killed, open("output/ghradar/carrier10.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
