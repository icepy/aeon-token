#!/usr/bin/env python3
"""把「被挡」拆成三桶：空 chains / 链不在白名单 / 其他。"""
import json, urllib.request
from datetime import datetime, timezone

req = urllib.request.Request('https://api.llama.fi/protocols',
                             headers={'User-Agent': 'defillama-radar/audit'})
p = json.load(urllib.request.urlopen(req, timeout=60))


def ts(v):
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v, tz=timezone.utc)
    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        except Exception:
            return None
    return None


now = datetime.now(timezone.utc)
CH = {"Ethereum", "Base", "Solana", "Arbitrum", "Ink", "Binance", "BSC",
      "Optimism", "OP Mainnet", "Hyperliquid L1", "Robinhood Chain"}
EXCL = {"CEX", "Chain", "Interface"}
ok = [x for x in p if isinstance(x, dict) and ts(x.get('listedAt'))]

hdr = '%-5s %5s %5s %5s %5s %5s %6s %7s %7s %7s'
print(hdr % ('win', 'new', 'par', 'exc', 'pass', 'bEmpty', 'bChain', 'empty%'
             , 'bE/in', 'bC/in'))
for d in (1, 3, 7, 14, 30, 90):
    sub = [x for x in ok if (now - ts(x.get('listedAt'))).total_seconds() <= d * 86400]
    par = [x for x in sub if x.get('parentProtocol')]
    exc = [x for x in sub if not x.get('parentProtocol') and x.get('category') in EXCL]
    rest = [x for x in sub if not x.get('parentProtocol') and x.get('category') not in EXCL]
    thru = [x for x in rest if [c for c in (x.get('chains') or []) if c in CH]]
    bE = [x for x in rest if not (x.get('chains') or [])]
    bC = [x for x in rest if (x.get('chains') or [])
          and not [c for c in x.get('chains') for _ in [0] if c in CH]]
    inp = len(thru) + len(bE) + len(bC)
    print(hdr % ('%dd' % d, len(sub), len(par), len(exc), len(thru),
                 len(bE), len(bC), '%.0f%%' % (100 * len(bE) / max(1, len(rest))),
                 '%.1f%%' % (100 * len(bE) / max(1, inp)),
                 '%.1f%%' % (100 * len(bC) / max(1, inp))))

print()
print('本轮 4 条明细（listedAt 全在 1d 窗内）:')
for i in ['9286', '9287', '9288', '9289']:
    x = next(y for y in p if str(y.get('id')) == i)
    print('  %s %-16s cat=%-18s parent=%-5s chains=%s url=%s'
          % (i, x.get('name'), x.get('category'), bool(x.get('parentProtocol')),
             x.get('chains'), x.get('url') or '-'))
