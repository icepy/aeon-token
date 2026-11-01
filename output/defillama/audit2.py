#!/usr/bin/env python3
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
for i in ['9286', '9287', '9288', '9289']:
    x = next(y for y in p if str(y.get('id')) == i)
    print(i, x.get('name'), 'listedAt=', ts(x.get('listedAt')))

rows = [(x, ts(x.get('listedAt'))) for x in p if isinstance(x, dict)]
rows = [(x, t) for x, t in rows if t]
print()
print('%-6s %6s %6s %8s' % ('win', 'new', 'empty', 'pct'))
for d in (1, 3, 7, 14, 30):
    sub = [x for x, t in rows if (now - t).total_seconds() <= d * 86400]
    e = [x for x in sub if not (x.get('chains') or [])]
    print('%-6s %6d %6d %7.1f%%' % ('%dd' % d, len(sub), len(e), 100 * len(e) / max(1, len(sub))))
alle = [x for x, _t in rows if not (x.get('chains') or [])]
print('全量 %d · 空chains %d = %.1f%%' % (len(rows), len(alle), 100 * len(alle) / len(rows)))

sub = [x for x, t in rows if (now - t).total_seconds() <= 30 * 86400 and not (x.get('chains') or [])]
npar = sum(1 for x in sub if x.get('parentProtocol'))
print('近30d 空chains %d · 带parent %d = %.1f%%' % (len(sub), npar, 100 * npar / max(1, len(sub))))

# 近3天：通过漏斗 / 只被空chains挡
s3 = [x for x, t in rows if (now - t).total_seconds() <= 3 * 86400]
CH = {"Ethereum", "Base", "Solana", "Arbitrum", "Ink", "Binance", "BSC",
      "Optimism", "OP Mainnet", "Hyperliquid L1", "Robinhood Chain"}
EXCL = {"CEX", "Chain", "Interface"}
thru = [x for x in s3 if not x.get('parentProtocol') and x.get('category') not in EXCL
        and [c for c in (x.get('chains') or []) if c in CH]]
blocked = [x for x in s3 if not x.get('parentProtocol') and x.get('category') not in EXCL
           and not (x.get('chains') or [])]
print('近3d 漏斗输入=%d · 通过=%d · 只被空chains挡=%d (%.1f%%)'
      % (len(thru) + len(blocked), len(thru), len(blocked),
         100 * len(blocked) / max(1, len(thru) + len(blocked))))
