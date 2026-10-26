import json
cur = json.load(open('output/ghradar/out.json'))
seen = json.load(open('memory/github-seen.json'))
seen_keys = set(k.lower() for k in seen) if isinstance(seen, dict) else set()
print('seen size', len(seen_keys))

# crypto-side check
for term in ('intent-based', 'data availability', 'restaking', 'maximal extractable value', 'verifiable inference', 'proof of useful work'):
    rs = [r for r in cur if r['term'] == term]
    print(term, '-> survivors', len(rs))
    for r in rs:
        print('   ', r['repo'], r['stars'], r['commits_30d'], r['commits_7d'], r.get('language'), '|', (r['desc'] or '')[:90])

# report-level list with language
rl = [r for r in cur if (r.get('commits_30d') or 0) >= 5]
print('report-level', len(rl))
from collections import Counter
print('report-level language:', Counter((r.get('language') or 'NONE') for r in rl))
print('report-level 7d>=5:', sum(1 for r in rl if (r.get('commits_7d') or 0) >= 5))
print('report-level created sept:', [ (r['repo'], r['created']) for r in cur if r['created'] < '2026-10-01'])
# static-site suspects in report level
for r in rl:
    if (r.get('language') or '') in ('HTML', 'CSS', 'NONE') or r.get('size_kb', 0) < 60:
        print('suspect', r['repo'], r['stars'], r['commits_30d'], r['commits_7d'], r.get('language'), r.get('size_kb'), 'KB')
