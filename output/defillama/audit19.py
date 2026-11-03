import json

p1 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p1.json'))}
p2 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p2.json'))}

print('=== BOND 9314 在 /protocols 与 /protocol 两端点的一致性 ===')
det = json.load(open('output/defillama/cb/bond.json'))
print(' /protocols HIT :', p1['9314']['tvl'])
print(' /protocols MISS:', p2['9314']['tvl'])
print(' /protocol  detail:', det['currentChainTvls'])
print(' detail tvl 末点:', (det.get('tvl') or [])[-1])
print(' detail chains:', det.get('chains'), '| address:', det.get('address'))

print()
print('=== 同步位移量 ===')
for tag, s in [('p1', p1), ('p2', p2)]:
    print(' %s BOND=%.4f CamelotV4=%.4f' % (tag, s['9314']['tvl'], s['9313']['tvl']))
d_b = p2['9314']['tvl'] - p1['9314']['tvl']
d_c = p2['9313']['tvl'] - p1['9313']['tvl']
print(' 位移 BOND=+%.4f CamelotV4=+%.4f 差=%.4f' % (d_b, d_c, d_c - d_b))

print()
print('=== Exceed 两条：扫到的快照 vs 源站 ===')
for i in ['9315', '9316']:
    print(' ', i, p1[i]['name'], '| HIT pp=', repr(p1[i].get('parentProtocol')), '| MISS pp=', repr(p2[i].get('parentProtocol')))

print()
print('=== 上轮判定「永久空洞」的 9290-9293 与本轮最大 id 的关系 ===')
old_max = 9300
for i in ['9290', '9291', '9292', '9293']:
    print(' ', i, p2[i]['name'], '| listedAt=', p2[i]['listedAt'], '| 小于上轮最大 id 9300 =', p2[i]['id'] < str(old_max))
