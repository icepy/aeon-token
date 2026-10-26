import json, collections
cur = json.load(open('output/ghradar/out.json'))
rl = [r for r in cur if (r.get('commits_30d') or 0) >= 5]
live = [r for r in rl if (r.get('commits_7d') or 0) >= 1]
print('survivors by term:', collections.Counter(r['term'] for r in cur).most_common())
print()
print('report-level by term:', collections.Counter(r['term'] for r in rl).most_common())
print()
print('report-level total', len(rl), '| 7d>=5:', sum(1 for r in rl if (r.get('commits_7d') or 0) >= 5),
      '| 7d>=1:', len(live), '| 7d=0 (dead):', sum(1 for r in rl if (r.get('commits_7d') or 0) == 0))
print()
print('survivors 30d>=5 but 7d=0:', sum(1 for r in cur if (r.get('commits_30d') or 0) >= 5 and (r.get('commits_7d') or 0) == 0))
print('survivors with commits>=100 (capped):', [r['repo'] for r in cur if (r.get('commits_30d') or 0) >= 100])
print()
print('--- world model 一支的 30d 分布 ---')
wm = [r for r in cur if r['term'] == 'world model']
print('n', len(wm), 'repo w/ 30d=1..4:', sum(1 for r in wm if 1 <= (r.get('commits_30d') or 0) < 5))
print('--- per-term 30d median-ish ---')
for t in sorted(set(r['term'] for r in cur)):
    xs = sorted((r.get('commits_30d') or 0) for r in cur if r['term'] == t)
    print(t, 'n=%d max=%d' % (len(xs), xs[-1] if xs else 0))
