import json, subprocess, time
cur = json.load(open('output/ghradar/out.json'))
seen = json.load(open('memory/github-seen.json'))
seen_keys = set(k.lower() for k in seen)

res = {}
for r in cur:
    name = r['repo']
    p = subprocess.run(['gh', 'api', 'repos/' + name + '/contents'],
                       capture_output=True, text=True)
    if p.returncode != 0:
        res[name] = {'err': (p.stderr or '').strip()[:80]}
        time.sleep(1)
        continue
    try:
        items = json.loads(p.stdout)
        names = [i['name'] for i in items]
        dirs = [i['name'] for i in items if i['type'] == 'dir']
        res[name] = {'n': len(items), 'nojekyll': '.nojekyll' in names,
                     'index': 'index.html' in names, 'dirs': dirs[:8],
                     'code_dirs': [d for d in dirs if d in ('src', 'lib', 'tests', 'test', 'scripts', 'engine', 'configs')]}
    except Exception as e:
        res[name] = {'err': 'parse'}
    time.sleep(0.4)

page = [n for n, v in res.items() if v.get('nojekyll')]
noindex = [n for n, v in res.items() if v.get('index') and not v.get('code_dirs')]
nocode = [n for n, v in res.items() if not v.get('code_dirs') and not v.get('err')]
errs = [n for n, v in res.items() if v.get('err')]
rl = [r['repo'] for r in cur if (r.get('commits_30d') or 0) >= 5]
print('survivors', len(cur), 'checked', len(res), 'errors', len(errs), errs[:5])
print('root .nojekyll (static site):', len(page))
print(page)
print('root index.html & no code dir:', len(noindex))
print(noindex)
print('no code dir at all:', len(nocode))
print('--- report-level 35 ---')
print('report-level with .nojekyll:', [n for n in rl if n in page])
print('report-level without code dir:', [n for n in rl if n in nocode])
print('--- seen overlap of survivors ---')
print('in seen:', sum(1 for r in cur if r['repo'].lower() in seen_keys), '/', len(cur))
json.dump(res, open('output/ghradar/tree11full.json', 'w'), ensure_ascii=False, indent=1)
