import json, subprocess, time, urllib.parse
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
since = (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
d = json.load(open('output/ghradar/out6.json'))
CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}
cry = [c for c in d if set(c['terms']) & CRYPTO and 'commits_30d' not in c]
print("补核验加密侧 %d 仓" % len(cry))

res = []
for c in cry:
    qs = urllib.parse.urlencode({"since": since, "per_page": "100"})
    for i in range(3):
        r = subprocess.run(["gh", "api", "repos/%s/commits?%s" % (c['repo'], qs)],
                           capture_output=True, text=True, timeout=60)
        if r.returncode == 0 and r.stdout.strip():
            data = json.loads(r.stdout)
            n = len(data) if isinstance(data, list) else None
            c['commits_30d'] = n
            res.append((c['repo'], c['stars'], n, '/'.join(c['terms'])))
            break
        e = r.stderr.strip()
        if "409" in e or "empty" in e.lower():
            c['maybe_empty'] = True
            res.append((c['repo'], c['stars'], 'EMPTY', '/'.join(c['terms'])))
            break
        if "rate limit" in e.lower() or "403" in e:
            time.sleep(6 * (i + 1)); continue
        print("  ! %s %s" % (c['repo'], e[:80])); break
    time.sleep(0.4)

json.dump(d, open('output/ghradar/out6.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

print("\n=== 加密侧全量核验结果（按提交数）===")
alive = [x for x in res if isinstance(x[2], int)]
for repo, s, n, t in sorted(alive, key=lambda x: -x[2]):
    print("  %-46s ★%-3d 30d=%-4d %s" % (repo, s, n, t))
print("\n报告级(>=5):", sum(1 for x in alive if x[2] >= 5))
print("零提交:", sum(1 for x in alive if x[2] == 0))
print("空仓:", sum(1 for x in res if x[2] == 'EMPTY'))
