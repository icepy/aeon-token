import json
import datetime
import collections

b = json.load(open('output/defillama/cb/p2.json'))
seen = json.load(open('memory/defillama-seen.json'))
today = '2026-11-03'

old = [int(k) for k, v in seen.items() if isinstance(v, dict) and v.get('first') != today and k.isdigit()]
print('历史最大 id 本轮之前:', max(old))
print('seen 总数', len(seen), '今天新增 20')

empty = [x for x in b if not (x.get('chains') or [])]
print('全量 chains=[]:', len(empty), '/', len(b), '= %.1f%%' % (100.0 * len(empty) / len(b)))
print('  其中 tvl 非空:', sum(1 for x in empty if x.get('tvl') is not None))
print('  其中 parent:', sum(1 for x in empty if x.get('parentProtocol')))

now = 1793664000
recent3 = [x for x in b if x.get('listedAt') and x['listedAt'] > now - 3 * 86400]
recent30 = [x for x in b if x.get('listedAt') and x['listedAt'] > now - 30 * 86400]
print('近3天登记(带 listedAt):', len(recent3), '其中 chains=[]:', sum(1 for x in recent3 if not (x.get('chains') or [])))
print('近30天登记:', len(recent30), '其中 chains=[]:', sum(1 for x in recent30 if not (x.get('chains') or [])))

c = collections.Counter(x.get('listedAt') for x in b if x.get('listedAt'))
big = [(k, v) for k, v in c.items() if v >= 3]
print('同秒>=3条 的秒数:', len(big), '涉及条数', sum(v for k, v in big))

CHAINS = ['Ethereum', 'Base', 'Solana', 'Arbitrum', 'Ink', 'Binance', 'BSC',
          'Optimism', 'OP Mainnet', 'Hyperliquid L1', 'Robinhood Chain']
EXCL = {'CEX', 'Chain', 'Interface'}
HITS = [x for x in b if [ch for ch in (x.get('chains') or []) if ch in CHAINS]]

# 旁路可行性: 今日 20 条里空 chains 且 url/desc 命中白名单链
W = {'Ethereum': 'ethereum', 'Base': 'base', 'Solana': 'solana', 'Arbitrum': 'arbitrum',
     'Ink': 'ink', 'Binance': 'bsc', 'Hyperliquid L1': 'hyperliquid', 'Robinhood Chain': 'robinhood'}
print('\n--- 今日 20 条旁路读数 ---')
for x in b:
    pid = str(x.get('id'))
    if pid not in seen or seen[pid].get('first') != today:
        continue
    if x.get('chains'):
        continue
    u = (x.get('url') or '').lower()
    d = (x.get('description') or '').lower()
    uh = [k for k, v in W.items() if v in u]
    dh = [k for k, v in W.items() if v in d]
    print(pid, x.get('name'), '| url_hit=', uh, '| desc_hit=', dh, '| parent=', bool(x.get('parentProtocol')), '| cat=', x.get('category'))
