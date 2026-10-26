import json, subprocess, time

def search(q):
    p = subprocess.run(['gh', 'api', '-X', 'GET', 'search/repositories',
                        '-f', 'q=' + q, '-f', 'per_page=100',
                        '-f', 'sort=updated'], capture_output=True, text=True)
    if p.returncode != 0:
        return None, (p.stderr or '').strip()[:120]
    d = json.loads(p.stdout)
    return d.get('total_count'), [i['full_name'] for i in d.get('items', [])]

out = {}
for label, q in [
    ('supermimic_30d', 'supermimic in:name,description created:>2026-09-26'),
    ('supermimic_7d', 'supermimic in:name,description created:>2026-10-19'),
    ('worldmodel_30d', '"world model" OR "world models" in:name,description created:>2026-09-26'),
]:
    tot, items = search(q)
    out[label] = {'total': tot, 'n_items': len(items) if isinstance(items, list) else items}
    print(label, 'total=', tot, 'items=', len(items) if isinstance(items, list) else items)
    time.sleep(7)

# which supermimic repos did the 18-term scan catch?
cur = json.load(open('output/ghradar/out.json'))
caught = [r['repo'] for r in cur if 'supermimic' in r['repo'].lower() or 'minimic' in r['repo'].lower()]
print('caught by 18-term scan:', caught)
out['caught'] = caught
json.dump(out, open('output/ghradar/probe11b.json', 'w'), ensure_ascii=False, indent=1)
