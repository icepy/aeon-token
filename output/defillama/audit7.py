#!/usr/bin/env python3
"""strict 分支近 30d 全部 30 条逐条看，判断误命中。"""
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
KW = {
    "Ethereum": r"\bethereum\b|\berc-?20\b|\beth mainnet\b",
    "Base": r"\bbase\b", "Solana": r"\bsolana\b", "Arbitrum": r"\barbitrum\b",
    "Ink": r"\bink\b", "Binance": r"\bbinance\b|\bbnb chain\b",
    "Optimism": r"\boptimism\b|\bop mainnet\b",
    "Hyperliquid L1": r"\bhyperliquid\b|\bhyperevm\b",
    "Robinhood Chain": r"\brobinhood\b",
}
rows = [x for x in p if isinstance(x, dict)]
cand = [x for x in rows if not (x.get('chains') or []) and not x.get('parentProtocol')
        and x.get('category') not in EXCL and ts(x.get('listedAt'))
        and (now - ts(x.get('listedAt'))).total_seconds() <= 30 * 86400]
for x in cand:
    d = (x.get('description') or '')
    k = [c for c, pat in KW.items() if re.search(pat, d.lower())]
    if not k:
        continue
    print('%-26s %-18s %-34s %s' % ((x.get('name') or '')[:26],
                                    ','.join(k)[:18], (x.get('category') or '')[:34],
                                    ' '.join(d.split())[:120]))
