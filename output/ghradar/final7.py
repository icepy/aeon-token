#!/usr/bin/env python3
"""第七轮最终清单：剔除缩写污染与项目页后的可执行候选。"""
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
    if s.endswith(".github.io") and c["size_kb"] < 300:
        return False
    return True

CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}

for tag, f in (("第六轮存量", "output/ghradar/full7.json"),
               ("第七轮新增", "output/ghradar/full7b.json")):
    d = json.load(open(f, encoding="utf-8"))
    ok = [c for c in d if c.get("q_status") == "ok"]

    print("=" * 74)
    print(tag + " — 加密侧 7d 活跃")
    cr = [c for c in ok if c["term"] in CRYPTO and (c.get("commits_7d") or 0) >= 1]
    for c in sorted(cr, key=lambda c: -c["commits_7d"]):
        print("  %-46s ★%-3d 30d=%-4d 7d=%-3d [%s]"
              % (c["repo"], c["stars"], c["commits_30d"], c["commits_7d"], c["term"]))

    print("\n" + tag + " — 机器人侧 clean · 7d 活跃 TOP 25")
    r = [c for c in ok if c["term"] not in CRYPTO and clean(c)
         and (c.get("commits_7d") or 0) >= 1]
    r.sort(key=lambda c: (-c["commits_7d"], -c["commits_30d"], -c["stars"]))
    for c in r[:25]:
        print("  %-46s ★%-3d 30d=%-4d 7d=%-3d [%s] %s"
              % (c["repo"], c["stars"], c["commits_30d"], c["commits_7d"],
                 c["term"], c.get("lang") or "-"))
    print()
