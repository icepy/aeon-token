#!/usr/bin/env python3
"""量化新候选分支：chains=[] 但 description 提到白名单链名。"""
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
# 描述里出现这些词 → 至少一条白名单链
KW = {
    "Ethereum": r"\bethereum\b|\beth\b|\berc-?20\b|\bmainnet\b",
    "Base": r"\bbase\b",
    "Solana": r"\bsolana\b|\bsol\b",
    "Arbitrum": r"\barbitrum\b|\barb\b",
    "Ink": r"\bink\b",
    "Binance": r"\bbinance\b|\bbnb\b|\bbsc\b",
    "Optimism": r"\boptimism\b|\bop mainnet\b|\bop stack\b",
    "Hyperliquid L1": r"\bhyperliquid\b|\bhyperevm\b",
    "Robinhood Chain": r"\brobinhood\b",
}
rows = [x for x in p if isinstance(x, dict)]
emp = [x for x in rows if not (x.get('chains') or [])]
cand = [x for x in emp if not x.get('parentProtocol') and x.get('category') not in EXCL]

print('空chains 全量 %d · 去掉 parent/EXCL 后 %d' % (len(emp), len(cand)))


def hitkw(x):
    d = (x.get('description') or '').lower()
    return [ch for ch, pat in KW.items() if re.search(pat, d)]


withkw = [(x, hitkw(x)) for x in cand]
withkw = [(x, k) for x, k in withkw if k]
withurl = [x for x in cand if x.get('url')]
both = [x for x in cand if x.get('url') and hitkw(x)]
print('  有 url            %d' % len(withurl))
print('  描述提到白名单链  %d' % len(withkw))
print('  两者都满足        %d' % len(both))

print()
print('窗口内（只含带 listedAt）：')
print('%-5s %7s %9s %9s %9s' % ('win', 'cand', 'url', 'descKW', 'both'))
for d in (3, 7, 14, 30, 90):
    sub = [x for x in cand
           if ts(x.get('listedAt')) and (now - ts(x.get('listedAt'))).total_seconds() <= d * 86400]
    u = [x for x in sub if x.get('url')]
    k = [x for x in sub if hitkw(x)]
    b = [x for x in sub if x.get('url') and hitkw(x)]
    print('%-5s %7d %9d %9d %9d' % ('%dd' % d, len(sub), len(u), len(k), len(b)))

print()
print('近 30d 描述命中白名单链的条目（名 · 命中词 · 类目）:')
for x, k in [(x, hitkw(x)) for x in cand
             if hitkw(x) and ts(x.get('listedAt'))
             and (now - ts(x.get('listedAt'))).total_seconds() <= 30 * 86400][:40]:
    print('  %-28s %-24s %s' % ((x.get('name') or '')[:28], ','.join(k), x.get('category')))

print()
print('本轮 4 条命中检查：')
for i in ['9286', '9287', '9288', '9289']:
    x = next(y for y in p if str(y.get('id')) == i)
    print('  %s %-16s urL=%-5s kw=%s' % (i, x.get('name'), bool(x.get('url')),
                                          ','.join(hitkw(x)) or '-'))
