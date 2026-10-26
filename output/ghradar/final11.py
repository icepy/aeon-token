import json
cur = json.load(open('output/ghradar/out.json'))
rl = [r for r in cur if (r.get('commits_30d') or 0) >= 5]
print('survivor max star:', max(r['stars'] for r in cur), '| report-level max star:', max(r['stars'] for r in rl))
print('survivors stars>=5:', sum(1 for r in cur if r['stars'] >= 5), '| report-level stars>=5:', sum(1 for r in rl if r['stars'] >= 5))
print('report-level repo list (30d,7d,star):')
for r in sorted(rl, key=lambda x: -(x['commits_7d'] or 0)):
    print('  %-62s %4s %4s %3s %s' % (r['repo'], r['commits_30d'], r['commits_7d'], r['stars'], r.get('language')))
# deceleration: 30d vs 7d rate
print()
print('deceleration = 7d commits vs (30d/30*7) rate, top by 7d:')
for r in sorted(cur, key=lambda x: -(x['commits_7d'] or 0))[:12]:
    exp = (r['commits_30d'] or 0) / 30 * 7
    print('  %-55s 30d=%-3s expected7d=%.1f actual7d=%s ratio=%.2f' % (r['repo'], r['commits_30d'], exp, r['commits_7d'], (r['commits_7d'] or 0) / max(exp, 0.1)))
