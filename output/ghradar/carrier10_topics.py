#!/usr/bin/env python3
"""github-radar 第十轮：carrier 只查 description、漏 topics 的量化。

`UCSC-VLAA/ALPS` 被 carrier 丢掉，但它的 topics 是
["computer-vision","contrastive-learning","embodied-ai","jax","libero","pytorch",
 "representation-learning","robot-learning",...] —— 教科书级的具身世界模型工作。
CARRIER_BY_TERM 只扫 description，于是漏掉。这里量这条漏洞有多大。
"""
import json
import subprocess
import time

ROBOT_TOPICS = {"robotics", "robot", "robot-learning", "embodied-ai", "embodied",
                "manipulation", "robot-manipulation", "sim2real", "sim-to-real",
                "teleoperation", "vla", "vision-language-action", "lerobot",
                "libero", "humanoid", "humanoid-robot", "world-models",
                "reinforcement-learning", "mujoco", "isaaclab", "robosuite"}

killed = json.load(open("output/ghradar/carrier10.json", encoding="utf-8"))


def topics(repo):
    for i in range(3):
        r = subprocess.run(["gh", "api", "repos/%s" % repo, "--jq", ".topics|join(\",\")"],
                           capture_output=True, text=True, timeout=45)
        if r.returncode == 0:
            return r.stdout.strip()
        time.sleep(6 * (i + 1))
    return ""


hits = []
for c in killed:
    tp = [t for t in topics(c["repo"]).split(",") if t]
    c["topics"] = tp
    ov = sorted(set(tp) & ROBOT_TOPICS)
    if ov:
        hits.append((c, ov))
    time.sleep(0.4)

hits.sort(key=lambda x: -x[0]["stars"])
print("carrier 丢弃 %d 个，其中 topics 明确属机器人/具身 %d 个" % (len(killed), len(hits)))
for c, ov in hits:
    print("  ★%-4d %-44s %s | %s" % (c["stars"], c["repo"][:44], ",".join(ov[:4]),
                                     c["desc"][:60]))

json.dump(hits and [{"repo": c["repo"], "stars": c["stars"], "topics": c["topics"],
                     "desc": c["desc"], "matched": ov} for c, ov in hits]
          or [], open("output/ghradar/carrier10_topics.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
