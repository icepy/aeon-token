#!/usr/bin/env python3
"""github-radar 第十轮：carrier 误杀的实际代价 —— 被丢的 120 个里有多少是报告级。

SKILL 铁律：「每条丢弃规则都要能被审计」「覆盖率必须报」。
只看 star 会重犯第九轮的错（star 与 commits 反相关），所以这里对全部 120 个
逐一查 30d 提交数，而不是抽样。
"""
import json
import subprocess
import time

killed = json.load(open("output/ghradar/carrier10.json", encoding="utf-8"))


def ncommit(repo, since):
    for i in range(3):
        r = subprocess.run(["gh", "api",
                            "repos/%s/commits?since=%s&per_page=100" %
                            (repo, since), "--jq", "length"],
                           capture_output=True, text=True, timeout=45)
        if r.returncode == 0:
            try:
                return int(r.stdout.strip() or 0)
            except ValueError:
                return None
        if "409" in r.stderr or "empty" in r.stderr.lower():
            return 0
        time.sleep(6 * (i + 1))
    return None


for c in killed:
    c["c30"] = ncommit(c["repo"], "2026-09-26T00:00:00Z")
    time.sleep(0.25)
    c["c7"] = ncommit(c["repo"], "2026-10-19T00:00:00Z")
    time.sleep(0.25)

rep = [c for c in killed if (c["c30"] or 0) >= 5]
rep.sort(key=lambda c: (-(c["c7"] or 0), -(c["c30"] or 0)))
print("carrier 丢弃 %d · 其中 30d>=5 提交（报告级）%d" % (len(killed), len(rep)))
print("%-52s %5s %5s %5s %s" % ("repo", "★", "30d", "7d", "desc"))
for c in rep:
    print("%-52s %5d %5s %5s %s" % (c["repo"][:52], c["stars"], c["c30"], c["c7"],
                                    c["desc"][:66]))

json.dump(killed, open("output/ghradar/carrier10_commits.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
