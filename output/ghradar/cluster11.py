import json, subprocess, time

items = json.load(open('output/ghradar/sm_items11.json'))
cur = json.load(open('output/ghradar/out.json'))
caught = set(r['repo'].lower() for r in cur)

rows = []
for it in items:
    fn = it['full_name']
    def cnt(since):
        p = subprocess.run(['gh', 'api', 'repos/' + fn + '/commits?since=' + since + '&per_page=100'],
                           capture_output=True, text=True)
        if p.returncode != 0:
            return -1
        try:
            return len(json.loads(p.stdout))
        except Exception:
            return -1
    n30 = cnt('2026-09-26T00:00:00Z')
    time.sleep(0.3)
    n7 = cnt('2026-10-19T00:00:00Z')
    time.sleep(0.3)
    rows.append({'repo': fn, 'star': it.get('stargazers_count', 0),
                 'lang': it.get('language'), 'size': it.get('size', 0),
                 'created': it['created_at'][:10], '30d': n30, '7d': n7,
                 'caught': fn.lower() in caught,
                 'desc': (it.get('description') or '')[:100]})

rows.sort(key=lambda x: -x['7d'])
print('n =', len(rows))
print('30d>=5:', sum(1 for r in rows if r['30d'] >= 5), '| 7d>=5:', sum(1 for r in rows if r['7d'] >= 5),
      '| 7d=0:', sum(1 for r in rows if r['7d'] == 0), '| err:', sum(1 for r in rows if r['7d'] < 0))
print('caught by 18-term scan:', sum(1 for r in rows if r['caught']), [r['repo'] for r in rows if r['caught']])
print()
for r in rows[:12]:
    print('%3d %3d star=%-4d %s %s' % (r['7d'], r['30d'], r['star'], r['repo'], ('' if r['caught'] else '')))
print()
print('--- index/list-shaped (name or desc says awesome/index/repro index) ---')
for r in rows:
    d = (r['repo'] + ' ' + r['desc']).lower()
    if any(k in d for k in ('awesome', 'index', 'list', 'collection')):
        print('  ', r['repo'], r['star'], r['30d'], r['7d'], '|', r['desc'][:70])
json.dump(rows, open('output/ghradar/cluster11.json', 'w'), ensure_ascii=False, indent=1)
