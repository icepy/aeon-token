#!/usr/bin/env python3
"""github-radar 第十轮：carrier 修法的净效果（不能只看「被 carrier 丢了 43 个」）。

carrier10.py 的探测只排除了 seen / 已幸存 / carrier，**没有过其他过滤器**
（EXCL / short_desc / pages / NEG / farm）。所以「43 个报告级」是上界，不是净增。
这里按 scan 的真实顺序重放一遍，只把 carrier 判据从「只看 desc」放宽成
「desc 或 repo 名或 topics」，量净增。
"""
import json

EXCL = ["awesome", "tutorial", "course", "survey", "cheatsheet", "roadmap",
        "interview", "homework", "assignment", "lecture", "book",
        "template", "boilerplate", "starter", "example", "demo", "playground",
        "sniper", "sandwich", "airdrop", "faucet", "scaffold"]
CARRIER = ["embodied", "robot", "vla", "manipulation", "sim2real", "sim-to-real",
           "teleop", "egocentric", "action", "policy", "rlbench", "lerobot"]
SITE_SUFFIX = (".github.io", "-page", "-site", "-website", "-homepage", "-showcase")

killed = json.load(open("output/ghradar/carrier10_commits.json", encoding="utf-8"))
topics = {h["repo"]: h["topics"]
          for h in json.load(open("output/ghradar/carrier10_topics.json", encoding="utf-8"))}

passed, dropped = [], {}
for c in killed:
    rid = c["repo"]
    short = rid.split("/")[-1].lower()
    desc = c["desc"]
    lowall = (rid + " " + desc).lower()
    if short.endswith(SITE_SUFFIX):
        dropped.setdefault("pages-suffix", []).append(rid); continue
    if len(desc) < 25:
        dropped.setdefault("short_desc", []).append(rid); continue
    if any(x in lowall for x in EXCL):
        dropped.setdefault("excl", []).append(rid); continue
    # 放宽后的 carrier：desc / 仓库名 / topics 任一命中即放行
    tp = " ".join(topics.get(rid, []))
    hay = (desc + " " + short + " " + tp).lower()
    if not any(x in hay for x in CARRIER):
        dropped.setdefault("still-offtopic", []).append(rid); continue
    passed.append(c)

rep = [c for c in passed if (c["c30"] or 0) >= 5]
rep.sort(key=lambda c: (-(c["c7"] or 0), -c["c30"]))
print("被 carrier 丢的 %d 个，放宽 carrier 后：过其他过滤器 %d，仍判离题 %d"
      % (len(killed), len(passed), len(dropped.get("still-offtopic", []))))
print("其中报告级（30d>=5 提交）净增 %d，7d>=5 活跃 %d"
      % (len(rep), len([c for c in rep if (c["c7"] or 0) >= 5])))
print()
for k, v in sorted(dropped.items(), key=lambda kv: -len(kv[1])):
    print("  仍丢弃 %-16s %3d" % (k, len(v)))
print()
print("%-52s %5s %5s %5s" % ("净增报告级", "★", "30d", "7d"))
for c in rep:
    print("%-52s %5d %5s %5s | %s" % (c["repo"][:52], c["stars"], c["c30"], c["c7"],
                                      c["desc"][:58]))

json.dump(rep, open("output/ghradar/carrier10_net.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
