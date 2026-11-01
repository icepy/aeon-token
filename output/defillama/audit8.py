#!/usr/bin/env python3
"""本轮收尾核对：chains=[] ⟺ tvl 缺失是否仍成立 + seen 完整性 + 漏斗输入拆分。"""
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


rows = [x for x in p if isinstance(x, dict)]
e = [x for x in rows if not (x.get('chains') or [])]
n = [x for x in rows if (x.get('chains') or [])]
print('① 全量 %d · 空chains %d (%.1f%%)' % (len(rows), len(e), 100 * len(e) / len(rows)))
print('   空chains 中 tvl 非空: %d' % sum(1 for x in e if x.get('tvl') is not None))
print('   有chains 中 tvl>0 : %d/%d = %.1f%%'
      % (sum(1 for x in n if (x.get('tvl') or 0) > 0), len(n),
         100 * sum(1 for x in n if (x.get('tvl') or 0) > 0) / len(n)))
print('   空chains 中 有url: %d (%.1f%%)' % (sum(1 for x in e if x.get('url')),
                                             100 * sum(1 for x in e if x.get('url')) / len(e)))

print()
print('② seen 完整性')
seen = json.load(open('memory/defillama-seen.json', encoding='utf-8'))
ids = {str(x.get('id')) for x in rows if x.get('id')}
print('   seen=%d · payload id 数=%d' % (len(seen), len(ids)))
stale = [k for k in seen if k not in ids]
print('   seen 有但 payload 无（下架）: %d %s' % (len(stale), stale[:10]))
nonnum = [k for k in seen if not k.isdigit()]
print('   非数字 key: %d %s' % (len(nonnum), nonnum[:5]))
from collections import Counter
print('   notified 分布:', dict(Counter(
    (v.get('notified') if isinstance(v, dict) else 'BAD') for v in seen.values()).most_common()))

print()
print('③ 今日漏斗输入拆分（新增 4 条）')
new = {k: v for k, v in seen.items() if v.get('first') == '2026-11-01'}
print('   本轮入表 %d：%s' % (len(new), dict(Counter(v.get('notified') for v in new.values()))))
