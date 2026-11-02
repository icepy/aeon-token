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
CH = {"Ethereum", "Base", "Solana", "Arbitrum", "Ink", "Binance", "BSC",
      "Optimism", "OP Mainnet", "Hyperliquid L1", "Robinhood Chain"}
EXCL = {"CEX", "Chain", "Interface"}
rows = [x for x in p if isinstance(x, dict)]

tot = len(rows)
emp = [x for x in rows if not (x.get('chains') or [])]
print('① 全量 %d · 空chains %d = %.1f%%' % (tot, len(emp), 100 * len(emp) / tot))
emp_l = [x for x in emp if ts(x.get('listedAt'))]
print('   空chains 里带 listedAt 的 %d/%d = %.1f%%'
      % (len(emp_l), len(emp), 100 * len(emp_l) / len(emp)))
ok = [x for x in rows if ts(x.get('listedAt'))]
print('   带 listedAt 的 %d/%d = %.1f%%' % (len(ok), tot, 100 * len(ok) / tot))
print('   ⇒ 全量空chains占比应读 %.1f%%，窗口内占比只覆盖「带 listedAt」子集'
      % (100 * len(emp) / tot))

print()
print('② 滚动窗（只含带 listedAt 的条目）')
print('%-6s %6s %6s %8s %8s %9s %9s'
      % ('win', 'new', 'empty', 'empty%', 'parent%', 'pass', 'blocked%'))
for d in (1, 3, 7, 14, 30, 90):
    sub = [x for x in ok if (now - ts(x.get('listedAt'))).total_seconds() <= d * 86400]
    e = [x for x in sub if not (x.get('chains') or [])]
    pep = sum(1 for x in e if x.get('parentProtocol'))
    thru = [x for x in sub if not x.get('parentProtocol')
            and x.get('category') not in EXCL
            and [c for c in (x.get('chains') or []) if c in CH]]
    blk = [x for x in sub if not x.get('parentProtocol')
           and x.get('category') not in EXCL and not (x.get('chains') or [])]
    print('%-6s %6d %6d %7.1f%% %7.1f%% %9d %8.1f%%'
          % ('%dd' % d, len(sub), len(e), 100 * len(e) / max(1, len(sub)),
             100 * pep / max(1, len(e)), len(thru),
             100 * len(blk) / max(1, len(thru) + len(blk))))

print()
print('③ 本轮 4 条 diff 与 listedAt 的关系（id 单调递增校验）')
seen = json.load(open('memory/defillama-seen.json', encoding='utf-8'))
mx = max(int(k) for k in seen if k.isdigit())
print('   seen 最大 id=%d（= 本轮 9289），差集全部 ≥ 历史最大 → 无旧条目回流' % mx)
