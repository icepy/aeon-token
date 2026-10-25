#!/usr/bin/env python3
"""第七轮核心缺陷：`真零命中` 把「all-seen」误标成「废词」。

scan 里 per_term[term] 只数**新幸存者**。有了 seen 基线之后，
一个词的命中若全部已见过 → per_term=0 → 审计日志打成「⚠️ 真零命中」。
但 SKILL 要求「查询失败 / 真零命中 / 未核验」三者分开写，
「全已见」是第四类，且它恰恰说明**该词没废、是饱和了**。

本脚本按词单查 60 天 total_count，把三类分开：
  A 查询失败  B 真零命中（total=0）  C 全已见（total>0 但新=0）
"""
import json, subprocess, sys, time, urllib.parse

TERMS = [t.strip() for t in """
embodied data
robot manipulation
robot dataset
teleoperation
sim2real
sim-to-real
world model
world action model
vla
jepa
egocentric
robotics data engine
verifiable inference
proof of useful work
data availability
restaking
intent-based
maximal extractable value
""".strip().split("\n")]

new7 = json.load(open("output/ghradar/full7b.json", encoding="utf-8"))
new7_n = {}
for c in new7:
    new7_n[c["term"]] = new7_n.get(c["term"], 0) + 1

def total_count(term):
    q = '"%s" in:name,description created:>=2026-08-26 fork:false stars:>=0' % term
    qs = urllib.parse.urlencode({"q": q, "per_page": "1"})
    for i in range(3):
        r = subprocess.run(["gh", "api", "search/repositories?" + qs],
                           capture_output=True, text=True, timeout=60)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout).get("total_count", 0), None
        err = (r.stderr or "").strip()
        if "rate limit" in err.lower() or "403" in err or "429" in err:
            time.sleep(20 * (i + 1)); continue
        return None, err[:100]
    return None, "rate-limited"

rows = []
for t in TERMS:
    n, err = total_count(t)
    rows.append((t, n, err, new7_n.get(t, 0)))
    time.sleep(2.5)

print("%-30s %8s %8s  %s" % ("term", "60d total", "new(r7)", "判读"))
print("-" * 78)
A, B, C = [], [], []
for t, n, err, nw in rows:
    if n is None:
        verdict = "A 查询失败: " + (err or "")
        A.append(t)
    elif n == 0:
        verdict = "B 真零命中"
        B.append(t)
    elif nw == 0:
        verdict = "C 全已见（饱和，非废词）"
        C.append(t)
    else:
        verdict = "有新增"
    print("%-30s %8s %8s  %s" % (t, n if n is not None else "-", nw, verdict))

print("\n汇总: A 查询失败=%d · B 真零命中=%d · C 全已见=%d · 有新增=%d"
      % (len(A), len(B), len(C), len(TERMS) - len(A) - len(B) - len(C)))
if C:
    print("\n🔴 被 scan 误标为「真零命中」的词（实际是饱和，不该删）:")
    for t, n, err, nw in rows:
        if t in C:
            print("   %-28s 60天 %d 仓，本轮 0 新增 → 全部已在 seen" % (t, n))
if B:
    print("\n真的零命中: " + " · ".join(B))

json.dump([{"term": t, "total60": n, "err": e, "new": nw} for t, n, e, nw in rows],
          open("output/ghradar/terms7.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
