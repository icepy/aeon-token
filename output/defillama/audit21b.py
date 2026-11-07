#!/usr/bin/env python3
"""量化桶序掩蔽：parent 在 category 之前，有多少 Interface/CEX/Chain 被记到 parent 名下。"""
import json
import time
import urllib.request

EX = {"CEX", "Chain", "Interface"}
CH = {"Ethereum", "Base", "Solana", "Arbitrum", "Ink", "Binance", "BSC",
      "Optimism", "OP Mainnet", "Hyperliquid L1", "Robinhood Chain"}
now = time.time()
p = json.load(urllib.request.urlopen("https://api.llama.fi/protocols", timeout=45))

def win(days):
    lo = now - days * 86400
    rows = []
    for x in p:
        if not isinstance(x, dict):
            continue
        la = x.get("listedAt")
        if not la:
            continue
        try:
            la = int(la)
        except Exception:
            continue
        if la < lo:
            continue
        rows.append(x)
    par = [x for x in rows if x.get("parentProtocol")]
    cat = [x for x in par if x.get("category") in EX]
    both_par_only = [x for x in par if x.get("category") in EX]
    print("window %2dd: listed=%4d  parent=%4d  parent∩EXCLcat=%4d (%.0f%% of parent)"
          % (days, len(rows), len(par), len(cat),
             100.0 * len(cat) / len(par) if par else 0))
    return rows, par, cat

for d in (7, 30, 90):
    rows, par, cat = win(d)

# 全量：parent 与 EXCL category 的重叠
allp = [x for x in p if isinstance(x, dict) and x.get("parentProtocol")]
allc = [x for x in allp if x.get("category") in EX]
print("\nALL-TIME parent=%d  of which EXCL-category=%d (%.1f%%)"
      % (len(allp), len(allc), 100.0 * len(allc) / len(allp) if allp else 0))

# 不加 parent 过滤时，近 30d 会被 category 挡掉多少
lo = now - 30 * 86400
blocked_cat = [x for x in p if isinstance(x, dict) and x.get("listedAt")
               and int(x["listedAt"]) >= lo and x.get("category") in EX]
print("30d EXCL-category total=%d ; of which have parent=%d ; parentless=%d"
      % (len(blocked_cat),
         sum(1 for x in blocked_cat if x.get("parentProtocol")),
         sum(1 for x in blocked_cat if not x.get("parentProtocol"))))
