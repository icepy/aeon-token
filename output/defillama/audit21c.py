#!/usr/bin/env python3
"""查 id 9340-9353 区间 listedAt 覆盖，看 Vesper V2(9353, listedAt=null) 是孤例还是新形态。"""
import json
import urllib.request

p = json.load(urllib.request.urlopen("https://api.llama.fi/protocols", timeout=45))
d = {int(x["id"]): x for x in p if isinstance(x, dict) and str(x.get("id", "")).isdigit()}
ks = sorted(d)
tail = [k for k in ks if k >= 9330]
print("%-6s %-30s %-20s %-10s %s" % ("id", "name", "category", "listedAt", "parent"))
nulls = 0
for k in tail:
    x = d[k]
    la = x.get("listedAt")
    if la is None:
        nulls += 1
    print("%-6s %-30s %-20s %-10s %s"
          % (k, (x.get("name") or "")[:30], (x.get("category") or "-")[:20],
             la if la else "NULL", x.get("parentProtocol") or ""))
print("\nid 9330-9353: n=%d, listedAt null=%d (%.0f%%)"
      % (len(tail), nulls, 100.0 * nulls / len(tail)))
print("max id overall:", max(ks), " contiguous run at tail:",
      all(b - a == 1 for a, b in zip(tail, tail[1:])))

# 近 30 天可报候选里的 null listedAt 比例（用 id > 9300 近似近期段）
seg = [k for k in ks if k >= 9300]
n = sum(1 for k in seg if d[k].get("listedAt") is None)
print("id>=9300: n=%d, listedAt null=%d (%.1f%%)" % (len(seg), n, 100.0 * n / len(seg)))
print("nulls in id>=9300:", [(k, d[k].get("name")) for k in seg if d[k].get("listedAt") is None])
