#!/usr/bin/env python3
"""两个补充：
1. 最近 48h 新建（相对今晨 run2 的增量）
2. 对高信号簇（★>=5 且 10 月）做 30 天提交核验 —— 默认 audit 只查创建时间最新的 25 个，
   全是 ★0，永远碰不到真正值得看的仓。
"""
import json, subprocess, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
now = datetime.now(timezone.utc)
since48 = (now - timedelta(hours=48)).strftime("%Y-%m-%d")

print("== 最近 48h 新建（created >= %s）==" % since48)
new48 = [c for c in out if c["created"] >= since48]
print("共 %d 个；★>=2 的：" % len(new48))
for c in sorted([x for x in new48 if x["stars"] >= 2], key=lambda x: -x["stars"]):
    print("  %4d ★ %s %-46s [%s] %s" % (c["stars"], c["created"], c["repo"], c["term"], c["desc"][:70]))

def gh(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return json.loads(r.stdout)

def commits(rid, days=30):
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    try:
        d = gh("repos/%s/commits?%s" % (rid, qs))
        return len(d) if isinstance(d, list) else None
    except Exception:
        return None

# 高信号集：10 月新建 且 ★>=5（86 个），另加所有 ★>=50 的非 10 月仓
cand = [c for c in out if c["created"] >= "2026-10-01" and c["stars"] >= 5]
cand += [c for c in out if c["created"] < "2026-10-01" and c["stars"] >= 50]
seen = set()
uniq = []
for c in cand:
    if c["repo"] not in seen:
        seen.add(c["repo"]); uniq.append(c)

print("\n== 提交核验：%d 个高信号仓（30 天窗口）==" % len(uniq))
res = []
for c in uniq:
    n = commits(c["repo"])
    c["c30"] = n
    res.append(c)
    print("  c30=%-5s ★%-5d %-52s %s" % (str(n), c["stars"], c["repo"], c["created"]))

json.dump(res, open("output/ghradar/highsig.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("\n== 活/死 分界 ==")
dead = [c for c in res if c["c30"] == 0]
empty = [c for c in res if c["c30"] is None]
alive = [c for c in res if isinstance(c["c30"], int) and c["c30"] > 0]
print("alive=%d  dead(0 commits)=%d  empty/409=%d" % (len(alive), len(dead), len(empty)))
print("\nDEAD（★在骗人）:")
for c in sorted(dead, key=lambda x: -x["stars"]):
    print("  %5d ★ %-50s %s" % (c["stars"], c["repo"], c["desc"][:60]))
print("\nEMPTY（只有 description）:")
for c in empty:
    print("  %5d ★ %-50s" % (c["stars"], c["repo"]))
print("\n最活跃（按 30d 提交数）:")
for c in sorted(alive, key=lambda x: -x["c30"])[:25]:
    print("  c30=%-4d ★%-5d %-52s %s" % (c["c30"], c["stars"], c["repo"], c["created"]))
