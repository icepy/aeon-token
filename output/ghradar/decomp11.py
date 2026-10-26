import json, subprocess, time, collections

cur = json.load(open('output/ghradar/out.json'))
prev = json.load(open('output/ghradar/out10.json'))
prevset = set(r['repo'].lower() for r in prev)
new = [r for r in cur if r['repo'].lower() not in prevset]

# how much of "new" is explained by the creation-window change (round10 window started 10-19)
w = collections.Counter()
for r in new:
    c = r['created']
    if c < '2026-10-01':
        w['created in Sept (outside both)'] += 1
    elif c < '2026-10-19':
        w['created 10-01..10-18 (outside round10 window)'] += 1
    else:
        w['created inside round10 window -> true miss'] += 1
print('44 new decomposition:', dict(w))
inside = [r for r in new if r['created'] >= '2026-10-19']
print('  inside-window new (true re-catch / miss):', [(r['repo'], r['commits_7d']) for r in inside])
print()
# activity of the 30d window that a 7d creation window cannot see
window_recovered = [r for r in new if '2026-10-01' <= r['created'] < '2026-10-19' and (r.get('commits_7d') or 0) >= 5]
print('30d window recovers 7d>=5 repos invisible to a 7d creation window:', len(window_recovered))
for r in window_recovered:
    print('  ', r['repo'], 'created', r['created'], '30d=%s 7d=%s' % (r['commits_30d'], r['commits_7d']))
print()

# SuperMimic cluster re-verify under 30d window
def gh(path):
    p = subprocess.run(['gh', 'api', path], capture_output=True, text=True)
    return json.loads(p.stdout) if p.returncode == 0 else None

items, page = [], 1
while page <= 2:
    d = gh('search/repositories?q=supermimic+in:name,description+created:%3E2026-09-26&per_page=100&page=' + str(page))
    if not d:
        break
    items += d.get('items', [])
    if len(d.get('items', [])) < 100:
        break
    page += 1
    time.sleep(7)
print('supermimic cluster (30d window) items:', len(items))

rows = []
for it in items:
    fn = it['full_name']
    c = gh('repos/%s/commits?since=2026-09-26T00:00:00Z&per_page=100' % fn)
    c7 = gh('repos/%s/commits?since=2026-10-19T00:00:00Z&per_page=100' % fn)
    n30 = len(c) if isinstance(c, list) else -1
    n7 = len(c7) if isinstance(c7, list) else -1
    rows.append((fn, it.get('stargazers_count', 0), n30, n7))
    time.sleep(0.35)

rows.sort(key=lambda x: -x[3])
alive = [x for x in rows if x[2] >= 5]
live7 = [x for x in rows if x[3] >= 5]
print('cluster verified:', len(rows), '| 30d>=5:', len(alive), '| 7d>=5:', len(live7))
print('top10 by 7d:')
for x in rows[:10]:
    print('  ', x[0], 'star=%d 30d=%d 7d=%d' % (x[1], x[2], x[3]))
json.dump({'rows': rows, 'n': len(rows), '30d5': len(alive), '7d5': len(live7)},
          open('output/ghradar/cluster11.json', 'w'), ensure_ascii=False, indent=1)
