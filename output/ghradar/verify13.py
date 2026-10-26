import json, subprocess

seen = json.load(open('memory/github-seen.json'))
S = set(k.lower() for k in (seen.keys() if isinstance(seen, dict) else seen))
print('seen=', len(S))


def q(query):
    r = subprocess.run(
        ['gh', 'api', '-X', 'GET', 'search/repositories', '-f', 'q=' + query,
         '-f', 'per_page=100', '-f', 'sort=updated',
         '--jq', '.items[]|[.full_name,.stargazers_count,.created_at,.pushed_at,.language]|@tsv'],
        capture_output=True, text=True)
    if r.returncode != 0:
        print('  GH-ERR', r.stderr.strip()[:120])
        return []
    return [l.split('\t') for l in r.stdout.strip().split('\n') if l.strip()]


for term in ['"world model"', 'teleoperation', 'jepa', 'vision language action']:
    it = q(term + ' created:>2026-09-26 fork:false')
    new = [x for x in it if x[0].lower() not in S]
    print(term, 'n=', len(it), 'not_in_seen=', len(new), [x[0] for x in new[:4]])

sm = q('supermimic created:>2026-09-26')
ins = [x for x in sm if x[0].lower() in S]
print('SM n=', len(sm), 'in_seen=', len(ins),
      'owners=', len(set(x[0].split('/')[0] for x in sm)))
