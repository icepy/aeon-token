#!/usr/bin/env python3
"""把第七轮全量核验的完整报告级追加到 candidates.md（scan 只写了 16，实为 107）。"""
import json, re

def clean(c):
    blob = ((c["repo"].split("/")[-1]) + " " + (c.get("desc") or "")).lower()
    if c["term"] == "vla" and re.search(
            r"\bvlan\b|intervlan|vlan-|_vlan|vlan_|\bvlad|\bvlaria|\bvlak|"
            r"vpn|router|switch|dhcp|packet.tracer|networking|subnet", blob):
        return False
    if c["term"] == "jepa" and re.search(
            r"jepang|jepara|bahasa|kuis|undangan|pernikahan|kotoba", blob):
        return False
    s = c["repo"].split("/")[-1]
    if (s.endswith(".github.io") or s.lower() == c["owner"].lower()) and c["size_kb"] < 300:
        return False
    return True

b = json.load(open("output/ghradar/full7b.json", encoding="utf-8"))
ok = [c for c in b if c.get("q_status") == "ok"]
rep = [c for c in ok if c["commits_30d"] >= 5 and clean(c)]
rep.sort(key=lambda c: (-c.get("commits_7d", 0), -c["commits_30d"], -c["stars"]))

with open("memory/github-candidates.md", "a", encoding="utf-8") as f:
    f.write("\n## 2026-10-25 · github-radar 第七轮全量核验（新增集 clean 报告级 %d）\n"
            % len(rep))
    f.write("> scan 自带核验只覆盖 97/332，只报了 16 个。本节是 332 仓全量核验、"
            "并剔除 `vla`/`jepa` 缩写污染与项目页后的完整清单。\n")
    for c in rep:
        tag = " [爆完即停]" if c.get("commits_7d", 0) == 0 else ""
        f.write("- [%s](%s) ★%d · 30d=%d 7d=%d%s · `%s` · %s\n"
                % (c["repo"], c["url"], c["stars"], c["commits_30d"],
                   c.get("commits_7d", -1), tag, c["term"], c["desc"][:100]))
print("appended %d reportable rows" % len(rep))
