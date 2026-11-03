import json

p1 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p1.json'))}
p2 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p2.json'))}
seen = json.load(open('memory/defillama-seen.json'))

print('--- Exceed Finance 全族 ---')
for x in p2.values():
    n = x.get('name') or ''
    if 'exceed' in n.lower():
        s = seen.get(str(x['id']), {})
        print(x['id'], n, '| pp=', x.get('parentProtocol'), '| chains=', x.get('chains'),
              '| tvl=', x.get('tvl'), '| seen.first=', s.get('first'), 'seen.notified=', s.get('notified'))
        print('    url=', x.get('url'))

print()
print('--- Exceed 父协议条目（若有）---')
for x in p2.values():
    if x.get('slug') in ('exceed-finance', 'exceed') or (x.get('name') or '').lower() == 'exceed finance':
        print(x['id'], x.get('name'), x.get('slug'), 'pp=', x.get('parentProtocol'), 'tvl=', x.get('tvl'))

print()
print('--- BOND Capital 详情 vs Camelot V4 ---')
for i in ['9314', '9313', '2792', '2307']:
    x = p2.get(i, {})
    print(i, x.get('name'), '| tvl=', x.get('tvl'), '| chains=', x.get('chains'),
          '| cat=', x.get('category'), '| url=', repr(x.get('url')))
    print('    desc=', ' '.join((x.get('description') or '').split())[:220])
    print('    full keys with addresses:', [k for k in x.keys() if 'addr' in k.lower()])
