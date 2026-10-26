import json, subprocess, time

seen = json.load(open('memory/github-seen.json'))
S = set(seen.keys()) if isinstance(seen, dict) else set()
SITE_SUFFIX = ('.github.io', '-page', '-site', '-website', '-homepage', '-showcase')
EXCL = ["awesome", "tutorial", "course", "survey", "cheatsheet", "roadmap",
        "interview", "homework", "assignment", "lecture", "book",
        "template", "boilerplate", "starter", "example", "demo", "playground",
        "sniper", "sandwich", "airdrop", "faucet", "scaffold"]
CAR = ['embodied', 'robot', 'vla', 'manipulation', 'sim2real', 'sim-to-real',
       'teleop', 'egocentric', 'action', 'policy', 'rlbench', 'lerobot']


def gh(path, params):
    a = ['gh', 'api', '-X', 'GET', path]
    for k, v in params.items():
        a += ['-f', '%s=%s' % (k, v)]
    r = subprocess.run(a, capture_output=True, text=True)
    time.sleep(0.55)
    return r.stdout.strip() if r.returncode == 0 else 'ERR'


def search(term, win, page=1):
    q = '"%s" in:name,description created:%s fork:false stars:>=0' % (term, win)
    out = gh('search/repositories', {'q': q, 'sort': 'stars', 'order': 'desc',
                                     'per_page': '100', 'page': str(page)})
    if out == 'ERR':
        return []
    d = json.loads(out)
    return d.get('items', [])


def commits(rid, days):
    since = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - days * 86400))
    r = gh('repos/%s/commits' % rid, {'since': since, 'per_page': '100'})
    if r == 'ERR':
        return None
    try:
        return len(json.loads(r))
    except Exception:
        return None


wins = ['2026-09-26..2026-10-06', '2026-10-06..2026-10-16', '2026-10-16..2026-10-26']
car, sht = {}, {}
for w in wins:
    for it in search('world model', w):
        rid = it['full_name']
        if rid in S or it.get('archived'):
            continue
        desc = (it.get('description') or '').strip()
        owner, short = rid.split('/')[0], rid.split('/')[-1]
        low = (rid + ' ' + desc).lower()
        if short.lower().endswith(SITE_SUFFIX):
            continue
        if short.lower() == owner.lower() and it.get('size', 0) < 300 and not it.get('language'):
            continue
        if any(e in low for e in EXCL):
            continue
        if len(desc) < 25:
            sht[rid] = (desc, it.get('language'), it.get('created_at', '')[:10], it.get('pushed_at', '')[:10])
        elif not any(c in desc.lower() for c in CAR):
            car[rid] = (desc, it.get('language'), it.get('created_at', '')[:10], it.get('pushed_at', '')[:10])

print('carrier-dropped unique:', len(car))
print('short_desc-dropped unique:', len(sht))

for label, pool, n in [('CARRIER', car, 14), ('SHORTDESC', sht, 14)]:
    rows = sorted(pool.items(), key=lambda kv: kv[1][3], reverse=True)[:n]
    print('\n=== %s (top %d by pushed_at) ===' % (label, len(rows)))
    live = 0
    for rid, (desc, lang, cre, push) in rows:
        c30, c7 = commits(rid, 30), commits(rid, 7)
        ok = (c7 or 0) >= 5 or (c30 or 0) >= 10
        live += 1 if ok else 0
        print('%-52s p=%-10s c30=%-5s c7=%-4s lang=%-8s | %s' %
              (rid[:52], push, c30, c7, (lang or '-'), desc[:40]))
    print('%s live(30d>=10 or 7d>=5): %d/%d' % (label, live, len(rows)))
