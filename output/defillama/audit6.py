#!/usr/bin/env python3
"""descKW 分支的误命中体检 + 桥占比 + 相对现行漏斗的增量。"""
import json, re, urllib.request
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
EXCL = {"CEX", "Chain", "Interface"}
CH = {"Ethereum", "Base", "Solana", "Arbitrum", "Ink", "Binance", "BSC",
      "Optimism", "OP Mainnet", "Hyperliquid L1", "Robinhood Chain"}

KW_STRICT = {
    "Ethereum": r"\bethereum\b|\berc-?20\b|\beth mainnet\b",
    "Base": r"\bbase\b",
    "Solana": r"\bsolana\b",
    "Arbitrum": r"\barbitrum\b",
    "Ink": r"\bink\b",
    "Binance": r"\bbinance\b|\bbnb chain\b",
    "Optimism": r"\boptimism\b|\bop mainnet\b",
    "Hyperliquid L1": r"\bhyperliquid\b|\bhyperevm\b",
    "Robinhood Chain": r"\brobinhood\b",
}
KW_LOOSE = dict(KW_STRICT)
KW_LOOSE["Ethereum"] = r"\bethereum\b|\beth\b|\berc-?20\b|\bmainnet\b"

rows = [x for x in p if isinstance(x, dict)]
cand = [x for x in rows if not (x.get('chains') or []) and not x.get('parentProtocol')
        and x.get('category') not in EXCL and ts(x.get('listedAt'))]


def hit(x, kw):
    d = (x.get('description') or '').lower()
    return [c for c, pat in kw.items() if re.search(pat, d)]


def inwin(x, d):
    return ts(x.get('listedAt')) and (now - ts(x.get('listedAt'))).total_seconds() <= d * 86400


print('%-5s %6s %7s %7s %7s' % ('win', 'cand', 'strict', 'loose', 'diff'))
for d in (7, 30, 90):
    s = [x for x in cand if inwin(x, d)]
    a = [x for x in s if hit(x, KW_STRICT)]
    b = [x for x in s if hit(x, KW_LOOSE)]
    print('%-5s %6d %7d %7d %7d' % ('%dd' % d, len(s), len(a), len(b), len(b) - len(a)))

print()
print('loose 多出的条目（strict 漏、只靠 eth/mainnet 命中）：')
for x in [x for x in cand if inwin(x, 30)]:
    if hit(x, KW_LOOSE) and not hit(x, KW_STRICT):
        print('  %-26s %s' % ((x.get('name') or '')[:26], (x.get('description') or '')[:110]))

print()
print('strict 分支近 30d：桥类目占比')
s30 = [x for x in cand if inwin(x, 30) and hit(x, KW_STRICT)]
BR = [x for x in s30 if 'Bridge' in (x.get('category') or '')]
print('  %d 条 · 桥 %d = %.0f%%' % (len(s30), len(BR), 100 * len(BR) / max(1, len(s30))))
from collections import Counter
print('  类目:', dict(Counter(x.get('category') for x in s30).most_common()))

print()
print('现行漏斗（近 30d，带 listedAt）通过数：')
thru = [x for x in rows if ts(x.get('listedAt')) and inwin(x, 30)
        and not x.get('parentProtocol') and x.get('category') not in EXCL
        and [c for c in (x.get('chains') or []) if c in CH]]
print('  %d 条 · strict 增量 +%d (+%.0f%%)'
      % (len(thru), len(s30), 100 * len(s30) / max(1, len(thru))))

print()
print('本轮 4 条在 strict 下的判定：')
for i in ['9286', '9287', '9288', '9289']:
    x = next(y for y in p if str(y.get('id')) == i)
    print('  %s %-16s strict=%s loose=%s' % (i, x.get('name'),
                                             hit(x, KW_STRICT) or '-', hit(x, KW_LOOSE) or '-'))
