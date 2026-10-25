#!/usr/bin/env python3
"""量化 farm_hit 规则误杀：owner>=3 里哪些其实是活仓。"""
import json
from collections import Counter, defaultdict

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
by_owner = defaultdict(list)
for c in out:
    by_owner[c["owner"]].append(c)

killed = []
for o, cs in by_owner.items():
    if len(cs) < 3:
        continue
    for c in cs:
        if c.get("commits_30d") is not None and c["commits_30d"] >= 5:
            killed.append(c)

killed.sort(key=lambda c: -c["commits_30d"])
print("== 被 farm_hit(owner>=3) 判掉、但 30d>=5 提交的仓: %d ==" % len(killed))
print("%-48s %-18s ★%-5s %6s" % ("repo", "owner", "", "cmts"))
for c in killed:
    print("%-48s %-18s ★%-5d %6d" % (c["repo"], c["owner"][:18],
                                     c["stars"], c["commits_30d"]))

print("\n== 这些 owner 的全部仓（看是否同质/同批）==")
for o in sorted({c["owner"] for c in killed}):
    print("\n  [%s]" % o)
    for c in sorted(by_owner[o], key=lambda x: x["created"]):
        v = c.get("commits_30d")
        print("    %-56s %s ★%-4d size=%-7s cmts=%s" % (
            c["repo"].split("/")[-1], c["created"], c["stars"],
            c.get("size_kb"), v if v is not None else "未验"))
