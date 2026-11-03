import json
import urllib.request

p1 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p1.json'))}
p2 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p2.json'))}

print('=== 1) BOND Capital vs Camelot V4 TVL 同步性 ===')
for tag, s in [('p1(HIT 11-01T23:38Z)', p1), ('p2(MISS 11-02T23:38Z)', p2)]:
    a = s['9314'].get('tvl')
    b = s['9313'].get('tvl')
    print(' %s  BOND=%r  CamelotV4=%r  差=%.3f' % (tag, a, b, (b - a) if a and b else -1))

print()
print('=== 2) 全量里最近登记的一批条目，TVL 是否互相串号（|Δ|<5）===')
new_ids = ['9313', '9314']
for i in new_ids:
    x = p2[i]
    t = x.get('tvl')
    if not t:
        continue
    close = [(y['id'], y['name'], y.get('tvl')) for y in p2.values()
             if y.get('tvl') and y['id'] != i and abs(float(y['tvl']) - float(t)) < 5]
    print(i, x['name'], t, '-> 5 美元内的邻居:', close)

print()
print('=== 3) 白名单链名做子串匹配的假阳性面（空 chains 群体）===')
empty = [x for x in p2.values() if not (x.get('chains') or [])]
KEY = {'ethereum': 'Ethereum', 'base': 'Base', 'solana': 'Solana', 'arbitrum': 'Arbitrum',
       'ink': 'Ink', 'binance': 'Binance', 'bsc': 'BSC', 'optimism': 'Optimism',
       'hyperliquid': 'Hyperliquid L1', 'robinhood': 'Robinhood Chain'}
import re
fp = []
for x in empty:
    blob = ((x.get('url') or '') + ' ' + (x.get('description') or '')).lower()
    hits = [v for k, v in KEY.items() if k in blob]
    if not hits:
        continue
    # 词边界版
    hits_wb = [v for k, v in KEY.items() if re.search(r'(?<![a-z0-9])' + re.escape(k) + r'(?![a-z0-9])', blob)]
    if hits and not hits_wb:
        fp.append((x['id'], x.get('name'), hits, blob[:70]))
print('子串命中但词边界不命中的条数:', len(fp))
for r in fp[:12]:
    print('  ', r)
