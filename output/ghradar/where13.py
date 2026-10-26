import json, subprocess, time

seen = json.load(open('memory/github-seen.json'))
S = set(seen.keys()) if isinstance(seen, dict) else set()

SITE_SUFFIX = ('.github.io', '-page', '-site', '-website', '-homepage', '-showcase')
EXCL = ["awesome", "tutorial", "course", "survey", "cheatsheet", "roadmap",
        "interview", "homework", "assignment", "lecture", "book",
        "template", "boilerplate", "starter", "example", "demo", "playground",
        "sniper", "sandwich", "airdrop", "faucet", "scaffold"]
# carriers copied from scan.py
CAR = {}
import re
src = open('skills/github-radar/scan.py').read()
m = re.search(r'CARRIER_BY_TERM\s*=\s*\{', src)
# crude: just check world model carrier
CAR['world model'] = ['embodied', 'robot', 'vla', 'manipulation', 'sim2real',
                      'sim-to-real', 'teleop', 'egocentric', 'action', 'policy',
                      'rlbench', 'lerobot']

def q(term, win):
    query = '"%s" in:name,description created:%s fork:false stars:>=0' % (term, win)
    r = subprocess.run(
        ['gh', 'api', '-X', 'GET', 'search/repositories', '-f', 'q=' + query,
         '-f', 'sort=stars', '-f', 'order=desc', '-f', 'per_page=100', '-f', 'page=1',
         '--jq', '.items[]|[.full_name,.description,.language,.size,.archived]|@tsv'],
        capture_output=True, text=True)
    time.sleep(2.5)
    if r.returncode != 0:
        print('GH-ERR', r.stderr.strip()[:100])
        return []
    return [l.split('\t') for l in r.stdout.strip().split('\n') if l.strip()]

wins = ['2026-09-26..2026-10-06', '2026-10-06..2026-10-16', '2026-10-16..2026-10-26']
buckets = {}
samples = {}
for term in ['world model']:
    for w in wins:
        for x in q(term, w):
            rid, desc, lang, size, arch = x[0], x[1] or '', x[2], int(x[3] or 0), x[4]
            owner, short = rid.split('/')[0], rid.split('/')[-1]
            low = (rid + ' ' + desc).lower()
            if rid in S:
                k = 'seen'
            elif arch == 'true':
                k = 'archived'
            elif short.lower().endswith(SITE_SUFFIX):
                k = 'pages_suffix'
            elif short.lower() == owner.lower() and size < 300 and not lang:
                k = 'pages_same'
            elif len(desc.strip()) < 25:
                k = 'short_desc'
            elif any(e in low for e in EXCL):
                k = 'excl'
            elif not any(c in desc.lower() for c in CAR[term]):
                k = 'carrier'
            else:
                k = 'SURVIVE'
            buckets[k] = buckets.get(k, 0) + 1
            samples.setdefault(k, []).append((rid, len(desc.strip()), lang, desc[:45]))

for k, v in sorted(buckets.items(), key=lambda t: -t[1]):
    print('%-14s %3d  %s' % (k, v, samples[k][:3]))
