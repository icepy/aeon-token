import json, subprocess, time, urllib.parse
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
d = json.load(open('output/ghradar/out6.json'))
CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}

def csince(rid, days):
    s = (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    qs = urllib.parse.urlencode({"since": s, "per_page": "100"})
    r = subprocess.run(["gh", "api", "repos/%s/commits?%s" % (rid, qs)],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return None
    x = json.loads(r.stdout)
    return len(x) if isinstance(x, list) else None

rob = [c for c in d if not (set(c['terms']) & CRYPTO) and (c.get('commits_30d') or 0) >= 10]
print("=== 机器人侧 ≥10 提交/30d 的 %d 仓：近 7 天活跃度 ===" % len(rob))
rows = []
for c in sorted(rob, key=lambda x: -x['commits_30d']):
    n7 = csince(c['repo'], 7)
    rows.append((c['repo'], c['stars'], c['commits_30d'], n7))
    time.sleep(0.3)

act = [r for r in rows if isinstance(r[3], int) and r[3] > 0]
dead = [r for r in rows if r[3] == 0]
print("  近 7 天仍活跃: %d/%d (%.0f%%)" % (len(act), len(rows), 100.0*len(act)/len(rows)))
print("  近 7 天零提交: %d" % len(dead))
print("\n  零提交清单（30d 高但已停）:")
for r in sorted(dead, key=lambda x: -x[2]):
    print("    %-44s ★%-4d 30d=%d" % (r[0], r[1], r[2]))
print("\n  最活跃（7d>0，按 7d 排序）:")
for r in sorted(act, key=lambda x: -x[3])[:20]:
    print("    %-44s ★%-4d 30d=%-4d 7d=%d" % (r[0], r[1], r[2], r[3]))

json.dump([{"repo": a, "stars": b, "c30": c, "c7": e} for a, b, c, e in rows],
          open('output/ghradar/rob_activity6.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
