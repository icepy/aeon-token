import json, collections

cur = json.load(open('output/ghradar/out.json'))
prev = json.load(open('output/ghradar/out10.json'))
prevset = set(r['repo'].lower() for r in prev)
curset = set(r['repo'].lower() for r in cur)
new = [r for r in cur if r['repo'].lower() not in prevset]
print('prev', len(prevset), 'cur', len(curset), 'new', len(new), 'overlap', len(curset & prevset))
print('new created months:', collections.Counter(r['created'][:7] for r in new))
print('new created <=2026-10-01:', sum(1 for r in new if r['created'] <= '2026-10-01'))
for r in sorted(new, key=lambda x: -(x.get('commits_7d') or 0))[:15]:
    print(r['commits_7d'], r['commits_30d'], r['stars'], r['created'], r['repo'], '|', r['term'])
print('new 7d>=5:', sum(1 for r in new if (r['commits_7d'] or 0) >= 5))
print('cur 7d>=5:', sum(1 for r in cur if (r['commits_7d'] or 0) >= 5))
print('new 30d>=5:', sum(1 for r in new if (r['commits_30d'] or 0) >= 5))
print('terms(new):', collections.Counter(r['term'] for r in new).most_common())
print('--- all cur top by 7d ---')
for r in sorted(cur, key=lambda x: (-(x.get('commits_7d') or 0), -(x.get('commits_30d') or 0)))[:12]:
    print(r['commits_7d'], r['commits_30d'], r['stars'], r['created'], r['repo'], '|', r['term'], '|', (r.get('language') or 'NONE'))
print('--- created spread (all cur) ---')
print(collections.Counter(r['created'][:7] for r in cur))
