import json

p2 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p2.json'))}
vals = sorted((float(x['tvl']), x['id'], x['name']) for x in p2.values() if x.get('tvl'))
print('非零 tvl 条目:', len(vals))

# 基准: 全量里 tvl 差 <5 美元的相邻对有多少（判断 9313/9314 是否稀有）
pairs = []
for i in range(len(vals) - 1):
    if vals[i + 1][0] - vals[i][0] < 5:
        pairs.append((vals[i], vals[i + 1], vals[i + 1][0] - vals[i][0]))
print('相邻且差<5 美元的对数:', len(pairs))
for a, b, d in pairs:
    print('   %.2f %s | %.2f %s | Δ=%.4f' % (a[0], a[2], b[0], b[2], d))

print()
print('=== address 前缀 vs chains 的全局一致率 ===')
PREF2CHAIN = {'robinhood': 'Robinhood Chain', 'arbitrum': 'Arbitrum', 'base': 'Base', 'solana': 'Solana',
              'bsc': 'Binance', 'era': 'zkSync Era', 'avax': 'Avalanche', 'polygon': 'Polygon'}
tot = mis = 0
mismatches = []
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
        mismatches.append((x['id'], x['name'], pref, chains, x.get('tvl')))
print('可比条目 %d · chains 不含地址前缀所在链的 %d (%.1f%%)' % (tot, mis, 100.0 * mis / max(tot, 1)))
for m in mismatches[:20]:
    print('  ', m)
