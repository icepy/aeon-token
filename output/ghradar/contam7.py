#!/usr/bin/env python3
"""第七轮核心：缩写词的子串污染量化。

铁律写着「缩写必然脏，用全称」，但词表里就有 vla / jepa 两个缩写。
第七轮加深翻页（2 页/窗）后，长尾里的污染全部浮出来了。
"""
import json, re
from collections import Counter

new = json.load(open("output/ghradar/full7b.json", encoding="utf-8"))
all6 = json.load(open("output/ghradar/full7.json", encoding="utf-8"))

# ── 污染判据（可审计，每条都要能说出是哪个子串撞的）──
def classify(c):
    name = c["repo"].split("/")[-1]
    owner = c["owner"]
    desc = (c.get("desc") or "")
    blob = (name + " " + desc).lower()
    term = c["term"]

    if term == "vla":
        # VLAN = 网络；vlad/vlaria/vlak = 人名或捷克语；VPN 仓的 vladoss
        if re.search(r"\bvlan\b|intervlan|vlan-|_vlan|vlan_", blob):
            return "vlan-network"
        if re.search(r"\bvlad|\bvlaria|\bvlak|\bvlastimil", blob):
            return "name-substring"
        if re.search(r"vpn|router|switch|dhcp|packet.tracer|networking|subnet",
                     blob):
            return "network"
    if term == "jepa":
        # jepang/jepara = 印尼语「日本」/ 印尼城市 Jepara
        if re.search(r"jepang|jepara", blob):
            return "indonesian"
        if re.search(r"bahasa|kuis|undangan|pernikahan|kotoba", blob):
            return "indonesian"
    return "clean"

for label, data in (("第七轮新增 332", new), ("第六轮存量 1251", all6)):
    print("=" * 72)
    print(label)
    for term in ("vla", "jepa"):
        xs = [c for c in data if c["term"] == term]
        if not xs:
            continue
        cl = Counter(classify(c) for c in xs)
        dirty = sum(v for k, v in cl.items() if k != "clean")
        print("\n  [%s] 共 %d 仓，污染 %d (%.1f%%)"
              % (term, len(xs), dirty, 100.0 * dirty / len(xs)))
        print("    分类: " + " · ".join("%s=%d" % kv for kv in cl.most_common()))
        # 污染是否也伪造了「活跃」
        rep = [c for c in xs if (c.get("commits_30d") or 0) >= 5]
        dirty_rep = [c for c in rep if classify(c) != "clean"]
        if rep:
            print("    ≥5 提交 %d，其中污染 %d (%.1f%%)"
                  % (len(rep), len(dirty_rep),
                     100.0 * len(dirty_rep) / len(rep)))
        act = [c for c in xs if (c.get("commits_7d") or 0) >= 1]
        dirty_act = [c for c in act if classify(c) != "clean"]
        if act:
            print("    7d 活跃 %d，其中污染 %d (%.1f%%)"
                  % (len(act), len(dirty_act), 100.0 * len(dirty_act) / len(act)))

# ── 污染样本（可审计）──
print("\n" + "=" * 72)
print("第七轮新增里的污染样本（按 commits_7d 排序，前 20）:")
dirty = [c for c in new if classify(c) != "clean"]
for c in sorted(dirty, key=lambda c: -(c.get("commits_7d") or 0))[:20]:
    print("  %-50s ★%-3d 30d=%-4s 7d=%-4s %-16s %s"
          % (c["repo"], c["stars"], c.get("commits_30d"), c.get("commits_7d"),
             classify(c), (c.get("desc") or "")[:44]))

# ── 修正后的全量数字 ──
print("\n" + "=" * 72)
print("修正后的报告级（剔除 vla/jepa 污染）")
for label, data in (("第六轮存量", all6), ("第七轮新增", new)):
    ok = [c for c in data if c.get("q_status") == "ok"]
    rep = [c for c in ok if c["commits_30d"] >= 5]
    rep_clean = [c for c in rep if classify(c) == "clean"]
    act = [c for c in ok if c.get("commits_7d", 0) >= 1]
    act_clean = [c for c in act if classify(c) == "clean"]
    print("  %s: 核验 %d | ≥5提交 %d→%d | 7d活跃 %d→%d"
          % (label, len(ok), len(rep), len(rep_clean), len(act), len(act_clean)))
