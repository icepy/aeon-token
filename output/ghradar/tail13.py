import json, subprocess, time

seen = json.load(open('memory/github-seen.json'))
S = set(k.lower() for k in (seen.keys() if isinstance(seen, dict) else seen))

BAD = ('awesome', 'tutorial', 'course', 'survey', 'cheatsheet', 'roadmap',
       'learning', 'study', 'homework', 'capstone', 'bootcamp')


def q(query, sort, page=1):
    r = subprocess.run(
        ['gh', 'api', '-X', 'GET', 'search/repositories', '-f', 'q=' + query,
         '-f', 'sort=' + sort, '-f', 'order=desc', '-f', 'per_page=100',
         '-f', 'page=' + str(page),
         '--jq', '.items[]|[.full_name,.description,.language,.created_at,.pushed_at,.stargazers_count]|@tsv'],
        capture_output=True, text=True)
    time.sleep(2.5)
    if r.returncode != 0:
        print('  GH-ERR', r.stderr.strip()[:100])
        return []
    return [l.split('\t') for l in r.stdout.strip().split('\n') if l.strip()]


def commits(rid, days):
    since = time.strftime('%Y-%m-%dT%H:%M:%SZ',
                          time.gmtime(time.time() - days * 86400))
    r = subprocess.run(
        ['gh', 'api', '-X', 'GET', 'repos/%s/commits' % rid,
         '-f', 'since=' + since, '-f', 'per_page=100', '--jq', '.|length'],
        capture_output=True, text=True)
    time.sleep(0.6)
    return r.stdout.strip() if r.returncode == 0 else 'ERR'


pool = {}
for term in ['"world model"', 'teleoperation', 'jepa']:
    for sort in ['stars', 'updated']:
        items = q(term + ' created:>2026-09-26 fork:false', sort)
        fresh = [x for x in items if x[0].lower() not in S]
        print('%-22s sort=%-8s n=%3d  not_in_seen=%3d' % (term, sort, len(items), len(fresh)))
        if sort == 'updated':
            pool.update({x[0]: x for x in fresh})

cand = []
for name, x in pool.items():
    desc = (x[1] or '').lower()
    if len(desc) < 20:
        continue
    if any(b in desc for b in BAD):
        continue
    if name.lower().endswith(('.github.io', '-page', '-site', '-website', '-homepage', '-showcase')):
        continue
    if not x[2]:
        continue
    cand.append(x)

cand.sort(key=lambda x: x[4], reverse=True)
print('\ncandidates after light filter:', len(cand))
print('%s\t%s\t%s\t%s\t%s\t%s' % ('repo', 'stars', 'c30d', 'c7d', 'lang', 'desc'))
live = 0
for x in cand[:18]:
    c30 = commits(x[0], 30)
    c7 = commits(x[0], 7)
    try:
        if int(c7 or 0) >= 5 or int(c30 or 0) >= 10:
            live += 1
    except ValueError:
        pass
    print('%s\t%s\t%s\t%s\t%s\t%s' % (x[0], x[5], c30, c7, x[2], (x[1] or '')[:52]))
print('\nlive(30d>=10 or 7d>=5) among first 18:', live)
