#!/usr/bin/env python3
"""核实空链 +6 的来源：重复 id？字段被清空？只读。"""
import json
import urllib.request
from collections import Counter

req = urllib.request.Request("https://api.llama.fi/protocols?_cb=d26e",
                             headers={"User-Agent": "defillama-radar/audit26e",
                                      "Cache-Control": "no-cache"})
raw = json.load(urllib.request.urlopen(req, timeout=60))
print("rows=%d" % len(raw))

ids = [str(p.get("id")) for p in raw if isinstance(p, dict) and p.get("id")]
c = Counter(ids)
dup = {k: v for k, v in c.items() if v > 1}
print("unique ids=%d | 重复 id: %s" % (len(c), dup or "无"))

# 空链统计两种口径
empty_rows = [p for p in raw if isinstance(p, dict) and p.get("id")
              and not (p.get("chains") or [])]
empty_ids = {str(p.get("id")) for p in empty_rows}
print("空链 行数=%d 去重后=%d" % (len(empty_rows), len(empty_ids)))

print("\n== 空链集合里 id 最大 25 条（看新老分布）==")
for pid in sorted(empty_ids, key=lambda x: int(x) if x.isdigit() else 0)[-25:]:
    p = next((x for x in raw if str(x.get("id")) == pid), {})
    print("  %s %-30s %s" % (pid, p.get("name"), p.get("category")))

print("\n== 空链里 max_id 段 9470+ ==")
print(sorted(k for k in empty_ids if k.isdigit() and int(k) >= 9470))
