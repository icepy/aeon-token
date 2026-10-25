import json
d = json.load(open('output/ghradar/wam6.json'))
pages = [r for r in d if 'github.io' in r['repo'].lower() or r['repo'].lower().endswith('-page') or 'projectpage' in r['repo'].lower()]
print('项目页型:', len(pages))
for r in pages:
    print('  ', r['repo'], '★%d' % r['stars'], '30d=%s' % r.get('commits_30d'), r['created'])
eng = [r for r in d if (r.get('commits_30d') or 0) >= 5 and r not in pages]
print('非项目页 报告级:', len(eng))
for r in sorted(eng, key=lambda x: -x['commits_30d']):
    print('  %-40s ★%-5d 30d=%-4s %s' % (r['repo'], r['stars'], r['commits_30d'], r['created']))
