import json

p2 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p2.json'))}

for i in ['9314', '9313', '2792', '2307']:
    x = p2[i]
    print(i, x.get('name'))
    print('   address =', repr(x.get('address')))
    print('   chainTvls keys =', sorted((x.get('chainTvls') or {}).keys())[:12])
    ct = x.get('chainTvls') or {}
    print('   Arbitrum tvl =', ct.get('Arbitrum'))
    print()

print('--- 谁共享 Camelot V4 的 address ---')
addr = p2['9313'].get('address')
print('Camelot V4 address:', addr)
bond = p2['9314'].get('address')
print('BOND Capital address:', bond)
for x in p2.values():
    if bond and str(x.get('address')) == str(bond):
        print('  addr 匹配:', x['id'], x['name'])

print()
print('--- 近 6 小时登记的条目其 tvl 与邻居的差 ---')
recent = [x for x in p2.values() if x.get('listedAt') and x['listedAt'] >= 1793650000]
recent.sort(key=lambda x: x['listedAt'])
import datetime
for x in recent:
    t = datetime.datetime.fromtimestamp(x['listedAt'], datetime.timezone.utc).strftime('%m-%d %H:%M:%SZ')
    print(x['id'], t, x.get('name'), '| chains=', x.get('chains'), '| tvl=', x.get('tvl'), '| cat=', x.get('category'), '| parent=', repr(x.get('parentProtocol')))
