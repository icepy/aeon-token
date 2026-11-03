import json
import datetime

p2 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p2.json'))}
seen = json.load(open('memory/defillama-seen.json'))


def t(la):
    if not la:
        return '-'
    return datetime.datetime.fromtimestamp(la, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')


print('--- 9290-9293（上轮被判为永久空洞的号段）---')
for i in ['9290', '9291', '9292', '9293']:
    x = p2.get(i, {})
    print(i, x.get('name'), '| cat=', x.get('category'), '| chains=', x.get('chains'),
          '| tvl=', x.get('tvl'), '| listedAt=', t(x.get('listedAt')), '| url=', repr(x.get('url')))

print()
print('--- exUSDC 9200 ---')
x = p2['9200']
print('listedAt=', t(x.get('listedAt')), 'pp=', x.get('parentProtocol'), 'tvl=', x.get('tvl'))

print()
print('--- 今日 20 条的 listedAt 跨度 ---')
ids = [str(i) for i in range(9290, 9317)]
ts = sorted([p2[i]['listedAt'] for i in ids if i in p2 and p2[i].get('listedAt')])
print(t(ts[0]), '→', t(ts[-1]))

print()
print('--- 全量里 name 前缀相同但 parent 不一致的组（版本铺开风险面）---')
from collections import defaultdict
groups = defaultdict(list)
for x in p2.values():
    n = (x.get('name') or '').strip()
    if not n:
        continue
    head = n.split(' ')[0].lower()
    groups[head].append(x)
n_risk = 0
for head, xs in groups.items():
    if len(xs) < 2:
        continue
    pars = {x.get('parentProtocol') for x in xs}
    if None in pars and len(pars) > 1:
        n_risk += 1
        if n_risk <= 8:
            print(' °', head, [(x['id'], x['name'], x.get('parentProtocol')) for x in xs][:6])
print('此类组数:', n_risk)
