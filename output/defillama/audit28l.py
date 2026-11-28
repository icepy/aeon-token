#!/usr/bin/env python3
"""第 33 轮补十二：单子家族（母体缺失 + 仅 1 条子条目 + 真量）—— parent 桶最脆的一面。只读。"""
import json
import time
import urllib.request
from datetime import datetime, timezone

API = "https://api.llama.fi/protocols"


def get(url, hdrs):
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


cb = get(API + "?_cb=%d" % int(time.time()),
         {"User-Agent": "defillama-radar/audit33l",
          "Cache-Control": "no-cache", "Pragma": "no-cache"})
seen = json.load(open("memory/defillama-seen.json", encoding="utf-8"))
now = time.time()
slugs = {p.get("slug") for p in cb if isinstance(p, dict)}
fam = {}
for p in cb:
    if isinstance(p, dict) and (p.get("parentProtocol") or "").startswith("parent#"):
        fam.setdefault(p["parentProtocol"].split("#", 1)[1], []).append(p)

single_live = []
for f, members in fam.items():
    if f in slugs:
        continue
    live = [p for p in members if isinstance(p.get("tvl"), (int, float)) and p["tvl"] > 0]
    if len(members) == 1 and live:
        single_live.append((f, live[0]))
print("母体缺失 + 家族仅 1 条 + 有真量 = %d 个家族（这些与独立协议在数据上不可区分）" % len(single_live))
tot = sum(p["tvl"] for _, p in single_live)
print("合计 TVL $%.2fB" % (tot / 1e9))
print("\nTop 12:")
for f, p in sorted(single_live, key=lambda x: -x[1]["tvl"])[:12]:
    la = p.get("listedAt")
    print("  parent#%-26s %-24s $-14s%-.0f  chains=%-20s listedAt=%s"
          % (f, (p.get("name") or "")[:24], p["tvl"], str(p.get("chains"))[:20],
             datetime.fromtimestamp(la, timezone.utc).strftime("%Y-%m-%d") if la else "-"))

print("\n其中母体缺失 + 单子的条目里，首次入库在近 90d 的：")
n90 = 0
for f, p in single_live:
    st = seen.get(str(p.get("id"))) or {}
    first = st.get("first")
    if first and first >= "2026-08-30":
        n90 += 1
        print("  %s %-24s first=%s notified=%s tvl=$%.0f"
              % (p.get("id"), p.get("name"), first, st.get("notified"), p["tvl"]))
print("  共 %d 条" % n90)

print("\n== Pear 家族在 seen 里的历史 ==")
for i in ("5151", "7075", "9527"):
    st = seen.get(i) or {}
    print("  %s first=%s notified=%s" % (i, st.get("first"), st.get("notified")))
