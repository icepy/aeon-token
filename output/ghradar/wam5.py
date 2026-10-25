#!/usr/bin/env python3
"""WAM 簇第 5 轮复核：严格词表 60 天 + 按 ISO 周分布 + owner 集中度 + star/commit 背离。

独立于 scan.py，用 search 全量翻页（不受 100/窗 限制），因此数字可与前几轮对比。
"""
import json, subprocess, sys, time, urllib.parse
from collections import Counter
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
SINCE = (now - timedelta(days=60)).strftime("%Y-%m-%d")

def gh(path):
    for i in range(4):
        r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
        if "rate limit" in r.stderr.lower() or "403" in r.stderr:
            time.sleep(6 * (i + 1)); continue
        print("! %s" % r.stderr[:120], file=sys.stderr); return None
    return None

def all_pages(q, cap=10):
    items, page = [], 1
    while page <= cap:
        qs = urllib.parse.urlencode({"q": q, "sort": "created", "order": "desc",
                                     "per_page": "100", "page": str(page)})
        d = gh("search/repositories?" + qs)
        if not d:
            break
        got = d.get("items", [])
        items += got
        if len(got) < 100:
            break
        page += 1
        time.sleep(2.5)
    return items, (d or {}).get("total_count", 0)

q = '"world action model" in:name,description created:>=%s fork:false' % SINCE
items, total = all_pages(q)
print("严格词表 %s 起：total_count=%d 实取=%d" % (SINCE, total, len(items)))

def wk(d):
    y, m, dd = map(int, d[:10].split("-"))
    return datetime(y, m, dd).isocalendar()[1]

weeks = Counter("W%02d" % wk(it["created_at"]) for it in items)
owners = Counter((it.get("owner") or {}).get("login", "") for it in items)
print("owner 数 %d · owner 有 ≥2 仓: %d 个 %s"
      % (len(owners), len([o for o, n in owners.items() if n >= 2]),
         [o for o, n in owners.most_common(6) if n >= 2]))
print("按周: " + " · ".join("%s=%d" % (k, weeks[k]) for k in sorted(weeks)))
print("10 月新建 %d" % len([i for i in items if i["created_at"] >= "2026-10-01"]))

# name 含 wam 的放宽口径
q2 = 'wam in:name created:>=%s fork:false' % SINCE
it2, tot2 = all_pages(q2)
print("\n放宽口径（name 含 wam）: total=%d 实取=%d · owner %d · 10月新建 %d"
      % (tot2, len(it2), len(set((i.get('owner') or {}).get('login', '') for i in it2)),
         len([i for i in it2 if i["created_at"] >= "2026-10-01"])))

# 头部 star/commits 背离
def c30(rid):
    qs = urllib.parse.urlencode({"since": (now - timedelta(days=30))
                                 .strftime("%Y-%m-%dT%H:%M:%SZ"), "per_page": "100"})
    d = gh("repos/%s/commits?%s" % (rid, qs))
    if d is None:
        return None
    return len(d) if isinstance(d, list) else None

print("\n== 严格词表 ★>=20 的 star vs 30d 提交 ==")
top = sorted([i for i in items if i["stargazers_count"] >= 20],
             key=lambda x: -x["stargazers_count"])
for it in top[:22]:
    n = c30(it["full_name"]); time.sleep(1.2)
    print("  ★%-5d c30=%-4s %-10s %-46s pushed=%s"
          % (it["stargazers_count"], n if n is not None else "?",
             it["created_at"][:10], it["full_name"], it.get("pushed_at", "")[:10]))

json.dump([{k: it.get(k) for k in ("full_name", "stargazers_count",
           "created_at", "pushed_at", "description")} for it in items],
          open("output/ghradar/wam5.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
