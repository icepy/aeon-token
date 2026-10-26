import json, subprocess, time

cur = json.load(open('output/ghradar/out.json'))
rl = set(r['repo'] for r in cur if (r.get('commits_30d') or 0) >= 5)
hits, page_like = [], []
for r in cur:
    fn = r['repo']
    p = subprocess.run(['gh', 'api', 'repos/' + fn + '/contents'], capture_output=True, text=True)
    if p.returncode != 0:
        time.sleep(0.3)
        continue
    names = [i['name'] for i in json.loads(p.stdout)]
    if any(n in names for n in ('AGENTS.md', 'CLAUDE.md', '.clinerules')):
        hits.append(fn)
    if 'index.html' in names and '.nojekyll' in names:
        page_like.append(fn)
    time.sleep(0.25)
print('survivors', len(cur), 'report-level', len(rl))
print('agent fingerprint:', len(hits), [h for h in hits])
print('  of which report-level:', [h for h in hits if h in rl])
print('page-like (index.html + .nojekyll):', len(page_like))
print('  of which report-level:', [h for h in page_like if h in rl])
json.dump({'agent': hits, 'pagelike': page_like}, open('output/ghradar/fp11.json', 'w'), ensure_ascii=False, indent=1)
