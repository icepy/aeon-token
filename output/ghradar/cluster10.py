#!/usr/bin/env python3
"""github-radar 第十轮：词表外的簇探测。

7 天窗内 SuperMimic 出现大量复现仓，但词表 18 词几乎抓不到它 ——
仓名/描述里写的是 SuperMimic，不是 world model / embodied data。
这里量三个口径：簇总量、窗口内新仓、以及它们的提交活性。
"""
import json
import subprocess
import time
import urllib.parse

PROBES = ["SuperMimic", "BeyondMimic", "vibe coded", "whole-body tracking"]
WINS = ["2026-10-19..2026-10-26", "2026-08-27..2026-10-26"]
PER_PAGE = 100


def gh(path):
    for i in range(3):
        r = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=45)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
        time.sleep(8 * (i + 1))
    return None


def search(q, page=1):
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": str(PER_PAGE), "page": str(page)})
    return gh("search/repositories?" + qs)


def ncommits(rid, days):
    since = "2026-10-19T00:00:00Z" if days == 7 else "2026-09-26T00:00:00Z"
    qs = urllib.parse.urlencode({"since": since, "per_page": "100"})
    d = gh("repos/%s/commits?%s" % (rid, qs))
    if d is None:
        return None
    return len(d)


res = {}
for p in PROBES:
    row = {}
    for w in WINS:
        q = '"%s" in:name,description created:%s fork:false' % (p, w)
        r = search(q)
        row[w] = r.get("total_count") if r else None
        time.sleep(7)
    res[p] = row
    print("%-22s 7d=%-6s 60d=%-6s" % (p, row[WINS[0]], row[WINS[1]]))

# SuperMimic 簇明细：7 天窗内，取前 2 页
print("\n=== SuperMimic 7 天窗明细 ===")
items = []
for page in (1, 2):
    r = search('"SuperMimic" in:name,description created:%s fork:false' % WINS[0], page)
    if not r:
        break
    items.extend(r.get("items", []))
    time.sleep(7)
    if len(r.get("items", [])) < PER_PAGE:
        break

rows = []
for it in items:
    rid = it["full_name"]
    c30 = ncommits(rid, 30)
    time.sleep(1)
    c7 = ncommits(rid, 7) if c30 else None
    time.sleep(1)
    rows.append({"repo": rid, "stars": it.get("stargazers_count", 0),
                 "created": (it.get("created_at") or "")[:10],
                 "lang": it.get("language"), "c30": c30, "c7": c7,
                 "desc": (it.get("description") or "")[:100]})

rows.sort(key=lambda x: (-(x["c7"] or 0), -(x["c30"] or 0), -x["stars"]))
print("%-52s %5s %5s %5s %s" % ("repo", "★", "30d", "7d", "created"))
for r in rows:
    print("%-52s %5d %5s %5s %s" % (r["repo"][:52], r["stars"], r["c30"], r["c7"], r["created"]))

res["_superminic_7d_items"] = rows
json.dump(res, open("output/ghradar/cluster10.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n簇内已核验 %d 仓 · 30d>=5 提交 %d · 7d>=5 提交 %d" % (
    len(rows), sum(1 for r in rows if (r["c30"] or 0) >= 5),
    sum(1 for r in rows if (r["c7"] or 0) >= 5)))
