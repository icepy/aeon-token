#!/usr/bin/env python3
"""第 33 轮补六：可报条目字段补全 + change 读数。只读。"""
import json
import time
import urllib.request

API = "https://api.llama.fi/protocols"


def get(url, hdrs):
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


cb = get(API + "?_cb=%d" % int(time.time()),
         {"User-Agent": "defillama-radar/audit33f",
          "Cache-Control": "no-cache", "Pragma": "no-cache"})
cm = {str(p.get("id")): p for p in cb if isinstance(p, dict) and p.get("id")}
p = cm["9528"]
print("== Stoxes.fun (9528) ==")
for k in ("name", "symbol", "category", "chains", "tvl", "change_1d", "change_1h",
          "change_7d", "mcap", "gecko_id", "cmcId", "audits", "twitter", "domain",
          "url", "github", "address", "listedAt", "misrepresentedTokens",
          "wrongLiquidity", "tags", "parentProtocol", "module"):
    print("  %-22s %r" % (k, p.get(k)))
print("  chainTvls = %r" % p.get("chainTvls"))
print("  methodology = %s" % p.get("methodology"))
print("  description = %s" % p.get("description"))
print("  tokenBreakdowns = %r" % (p.get("tokenBreakdowns"),))
print("  logo = %s" % (p.get("logo") or "")[:120])

print("\n== Pear Vaults (9527) 全字段 ==")
q = cm["9527"]
for k in ("name", "category", "chains", "tvl", "change_1d", "change_7d", "mcap",
          "gecko_id", "audits", "twitter", "url", "listedAt", "module", "tags"):
    print("  %-14s %r" % (k, q.get(k)))
print("  methodology = %s" % (q.get("methodology") or "")[:400])
