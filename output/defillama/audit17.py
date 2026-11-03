import json

p2 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p2.json'))}
vals = sorted((float(x['tvl']), x['id'], x['name']) for x in p2.values() if x.get('tvl'))
big = [v for v in vals if v[0] >= 1000]
print('tvl>=1000 条目:', len(big))

pairs = []
for i in range(len(big) - 1):
    d = big[i + 1][0] - big[i][0]
    if d < 5:
        pairs.append((big[i], big[i + 1], d))
print('相邻且差<5 美元的对数:', len(pairs))
for a, b, d in pairs[:20]:
    print('   %.2f %s | %.2f %s | Δ=%.4f' % (a[0], a[2], b[0], b[2], d))

print()
print('=== address 前缀 vs chains 一致性（tvl 非空子集）===')
PREF2CHAIN = {'robinhood': 'Robinhood Chain', 'arbitrum': 'Arbitrum', 'base': 'Base', 'solana': 'Solana',
              'bsc': 'Binance', 'avax': 'Avalanche', 'polygon': 'Polygon', 'era': 'zkSync Era',
              'optimism': 'Optimism', 'ethereum': 'Ethereum', 'hyperliquid': 'Hyperliquid L1'}
tot = mis = 0
mism = []
for x in p2.values():
    addr = str(x.get('address') or '')
    if ':' not in addr:
        continue
    pref = addr.split(':', 1)[0]
    want = PREF2CHAIN.get(pref)
    chains = x.get('chains') or []
    if not want or not chains:
        continue
    tot += 1
    if want not in chains:
        mis += 1
        mism.append((x['id'], x['name'], pref, chains, x.get('tvl'), x.get('chainTvls')))
print('可比 %d · 不一致 %d (%.1f%%)' % (tot, mis, 100.0 * mis / max(tot, 1)))
for m in mism:
    print('  ', m[0], m[1], '| addr前缀=', m[2], '| chains=', m[3], '| tvl=', m[4], '| chainTvls=', list((m[5] or {}).keys()))
