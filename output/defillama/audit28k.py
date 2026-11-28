#!/usr/bin/env python3
"""第 33 轮补十一：parent 桶挡掉的"家族唯一真量"子情形 —— 母协议本体是否在 /protocols。只读。"""
import json
import time
import urllib.request

API = "https://api.llama.fi/protocols"


def get(url, hdrs):
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


cb = get(API + "?_cb=%d" % int(time.time()),
         {"User-Agent": "defillama-radar/audit33k",
          "Cache-Control": "no-cache", "Pragma": "no-cache"})
slugs = {p.get("slug"): p for p in cb if isinstance(p, dict)}

for fam in ("pear-protocol", "ravn"):
    print("== parent#%s ==" % fam)
    members = [p for p in cb if isinstance(p, dict)
               and (p.get("parentProtocol") or "") == "parent#" + fam]
    print("  子条目 %d 条:" % len(members))
    for p in members:
        print("    %s %-22s cat=%-18s tvl=%-14s chains=%s"
              % (p.get("id"), p.get("name"), p.get("category"), p.get("tvl"), p.get("chains")))
    body = slugs.get(fam)
    print("  母协议本体在 /protocols: %s" % ("是 → id=%s name=%s tvl=%s chains=%s"
          % (body.get("id"), body.get("name"), body.get("tvl"), body.get("chains"))
          if body else "**否**（无 slug=%s 的顶层条目）" % fam))
    # 家族真量
    live = [(p.get("id"), p.get("name"), p.get("tvl")) for p in members
            if isinstance(p.get("tvl"), (int, float)) and p["tvl"] > 0]
    print("  家族内 tvl>0 的条目: %s" % (live if live else "无"))
    print()

print("== 全量普查：parent 家族的「母体缺失」比例 ==")
families = {}
for p in cb:
    if not isinstance(p, dict):
        continue
    pp = p.get("parentProtocol") or ""
    if pp.startswith("parent#"):
        families.setdefault(pp.split("#", 1)[1], []).append(p)
missing = [f for f in families if f not in slugs]
print("家族总数=%d · 母体不在 /protocols 的家族=%d（%.1f%%）"
      % (len(families), len(missing), 100.0 * len(missing) / len(families)))
only_live = []
for f in missing:
    live = [p for p in families[f] if isinstance(p.get("tvl"), (int, float)) and p["tvl"] > 0]
    if live:
        only_live.append((f, len(families[f]), [(p.get("id"), p.get("name"), p.get("tvl")) for p in live]))
print("其中「母体缺失但子条目有真量」的家族=%d 个" % len(only_live))
for f, n, live in sorted(only_live, key=lambda x: -max(v[2] for v in x[2]))[:10]:
    print("  parent#%-28s 子条目 %d · 真量 %s" % (f, n, [(i, nm, "$%.0f" % v) for i, nm, v in live]))
