import json

p1 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p1.json'))}
p2 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p2.json'))}

print('--- 三份快照里的 parentProtocol（扫描时那份 = p1 缓存 / p2 源站）---')
for i in ['9313', '9314', '9315', '9316']:
    a, b = p1.get(i, {}), p2.get(i, {})
    print(i, a.get('name'),
          '| p1(parent)=', repr(a.get('parentProtocol')), 'tvl=', a.get('tvl'),
          '| p2(parent)=', repr(b.get('parentProtocol')), 'tvl=', b.get('tvl'))

print()
print('--- 是否存在 parent#exceed-finance / parent#bond-capital 的父条目 ---')
for key in ['exceed', 'bond']:
    kids = [x for x in p2.values() if key in str(x.get('parentProtocol') or '').lower()]
    print(key, '子条目数', len(kids), [x['name'] for x in kids][:10])

print()
print('--- TVL 完全相同的条目对（同一数值出现多次 = 端点串号嫌疑）---')
from collections import defaultdict
d = defaultdict(list)
for x in p2.values():
    t = x.get('tvl')
    if t:
        d[round(float(t), 2)].append((x['id'], x['name'], x.get('chains')))
dups = {k: v for k, v in d.items() if len(v) > 1}
print('重复 tvl 值组数:', len(dups))
for k, v in list(dups.items())[:15]:
    print(' ', k, v)
