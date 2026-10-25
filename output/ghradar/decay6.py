import json, subprocess, time, urllib.parse
from datetime import datetime, timedelta, timezone
from collections import Counter

now = datetime.now(timezone.utc)
d = json.load(open('output/ghradar/out6.json'))
CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}

def commits_since(rid, days):
    s = (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    qs = urllib.parse.urlencode({"since": s, "per_page": "100"})
    r = subprocess.run(["gh", "api", "repos/%s/commits?%s" % (rid, qs)],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return None
    x = json.loads(r.stdout)
    return len(x) if isinstance(x, list) else None

cry = [c for c in d if set(c['terms']) & CRYPTO and (c.get('commits_30d') or 0) >= 5]
print("=== 加密侧 ≥5 提交/30d 的 %d 仓：近 7 天是否还在写 ===" % len(cry))
rows = []
for c in sorted(cry, key=lambda x: -x['commits_30d']):
    n7 = commits_since(c['repo'], 7)
    c['commits_7d'] = n7
    rows.append((c['repo'], c['stars'], c['commits_30d'], n7, '/'.join(c['terms'])))
    print("  %-46s ★%-3d 30d=%-4d 7d=%-4s %s" %
          (c['repo'], c['stars'], c['commits_30d'], n7, '/'.join(c['terms'])))
    time.sleep(0.3)

active = [r for r in rows if isinstance(r[3], int) and r[3] > 0]
print("\n近 7 天仍活跃: %d/%d (%.0f%%)" % (len(active), len(rows), 100.0*len(active)/len(rows)))
stopped = [r for r in rows if r[3] == 0]
print("近 7 天零提交（爆完即停）: %d" % len(stopped))
for r in stopped:
    print("   ", r[0], "30d=%d" % r[2])

json.dump([{"repo": r[0], "stars": r[1], "c30": r[2], "c7": r[3], "terms": r[4]}
           for r in rows],
          open('output/ghradar/cry_activity6.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
