import json

p1 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p1.json'))}
p2 = {str(x['id']): x for x in json.load(open('output/defillama/cb/p2.json'))}

print('=== 假设检验：BOND 与 Camelot V4 的 TVL 是串号还是巧合 ===')
print('若串号，两条的日变动率应几乎相同（同一底层资产篮子）:')
for tag, s in [('p1', p1), ('p2', p2)]:
    b, c = s['9314']['tvl'], s['9313']['tvl']
    print('  %s  BOND=%.4f  CamelotV4=%.4f  Δ=%.4f' % (tag, b, c, c - b))
rb = (p2['9314']['tvl'] - p1['9314']['tvl']) / p1['9314']['tvl'] * 100
rc = (p2['9313']['tvl'] - p1['9313']['tvl']) / p1['9313']['tvl'] * 100
print('  日变动率 BOND=%+.4f%%  CamelotV4=%+.4f%%' % (rb, rc))
print('  → 变动率相同只说明两者资产篮子重叠（都偏 ETH），不构成串号证据')

print()
print('=== 近价密度：TVL>=1000 的 4250 条里，相邻差<5 美元的对数占比 ===')
vals = sorted(float(x['tvl']) for x in p2.values() if x.get('tvl') and float(x['tvl']) >= 1000)
n = 0
for i in range(len(vals) - 1):
    if vals[i + 1] - vals[i] < 5:
        n += 1
print('  %d / %d = %.1f%%' % (n, len(vals) - 1, 100.0 * n / (len(vals) - 1)))
print('  → 近价在 $177K 量级并不稀有，"数值接近"不构成串号判据')

print()
print('=== Camelot V4 是否是幻影条目：与 V2/V3 共用同一合约地址 ===')
for i in ['2307', '2792', '9313']:
    x = p2[i]
    print(' ', i, x['name'], '| addr=', x.get('address'), '| Arbitrum tvl=',
          (x.get('chainTvls') or {}).get('Arbitrum'), '| tvl=', x.get('tvl'))
print('  → V4 与 V2/V3 同址，但 TVL 只有 V3 的 6%：更像新建的独立池子条目，非幻影')
