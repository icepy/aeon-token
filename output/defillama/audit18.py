import json
import datetime

p2 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p2.json'))}

print('=== id 9290..9320 存在性 ===')
for i in range(9288, 9321):
    x = p2.get(str(i))
    if x is None:
        print(i, 'ABSENT')
    else:
        la = x.get('listedAt')
        t = datetime.datetime.fromtimestamp(la, datetime.timezone.utc).strftime('%m-%dT%H:%M:%SZ') if la else '-'
        print(i, x.get('name'), '| cat=', x.get('category'), '| chains=', x.get('chains'), '| listedAt=', t)

print()
print('=== robinhood 前缀条目中 chains 不含 Robinhood Chain 的（完整）===')
n = 0
for x in p2.values():
    a = str(x.get('address') or '')
    if a.startswith('robinhood:'):
        n += 1
        if 'Robinhood Chain' not in (x.get('chains') or []):
            print('  ', x['id'], x.get('name'), '| chains=', x.get('chains'), '| tvl=', x.get('tvl'),
                  '| cat=', x.get('category'), '| listedAt=', x.get('listedAt'))
print('robinhood 前缀总数:', n)

print()
print('=== 本轮 20 条中 parent 桶的 7 条逐条 ===')
seen = json.load(open('memory/defillama-seen.json'))
for i in ['9301', '9304', '9305', '9310', '9311', '9312', '9313', '9315', '9316']:
    x = p2[i]
    print(' ', i, x['name'], '| pp=', x.get('parentProtocol'), '| cats=', x.get('category'))
