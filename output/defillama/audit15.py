import json

p2 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p2.json'))}

print('=== address 前缀 vs chains 字段 的一致性（全量）===')
bad = []
for x in p2.values():
    addr = str(x.get('address') or '')
    if ':' not in addr:
        continue
    pref = addr.split(':', 1)[0]
    chains = x.get('chains') or []
    ct = list((x.get('chainTvls') or {}).keys())
    # 只看有 tvl 的
    if not chains:
        continue
    bad.append((x['id'], x.get('name'), pref, chains, ct, x.get('tvl')))

from collections import Counter
print('前缀分布（有 chains 的条目）:', Counter(b[2] for b in bad).most_common(12))

print()
print('--- robinhood: 前缀的条目，其 chains 字段是什么 ---')
rh = [b for b in bad if b[2] == 'robinhood']
print('n =', len(rh))
for b in rh[:25]:
    flag = '' if ('Robinhood Chain' in b[3]) else '  <== chains 里没有 Robinhood Chain'
    print(' ', b[0], b[1], '| chains=', b[3], '| chainTvls=', b[4], '| tvl=', b[5], flag)
