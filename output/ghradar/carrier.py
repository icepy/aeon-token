#!/usr/bin/env python3
"""carrier 过滤按词归因 —— 铁律要求报告这项丢弃的去向。"""
import json, os, subprocess, time, urllib.parse
from collections import Counter

CARRIER_BY_TERM = {
    "data availability": ["blockchain", "crypto", "ethereum", "onchain", "web3",
                          "rollup", "celestia", "modular", "da layer", "zk-", "zk"],
    "intent-based": ["blockchain", "crypto", "ethereum", "onchain", "web3",
                     "solver", "swap", "defi", "amm", "wallet"],
}
from datetime import datetime, timedelta, timezone
now = datetime.now(timezone.utc)
DAYS = 60; NWIN = 3; step = DAYS / NWIN
WINS = [f"{(now - timedelta(days=step*(i+1))):%Y-%m-%d}..{(now - timedelta(days=step*i)):%Y-%m-%d}"
        for i in range(NWIN)]

def search(q):
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": "100", "page": "1"})
    r = subprocess.run(["gh", "api", "search/repositories?" + qs],
                       capture_output=True, text=True, timeout=60)
    return json.loads(r.stdout) if r.returncode == 0 else None

for term in CARRIER_BY_TERM:
    tot = keep = 0
    for w in WINS:
        res = search('"%s" in:name,description created:%s fork:false stars:>=0' % (term, w))
        if not res:
            continue
        tot += res.get("total_count", 0)
        for it in res.get("items", []):
            d = (it.get("description") or "").lower()
            if any(c in d for c in CARRIER_BY_TERM[term]):
                keep += 1
        time.sleep(2)
    print("%-22s total_count=%-6d 采样内过 carrier=%-3d  (%.1f%%)"
          % (term, tot, keep, 100.0 * keep / tot if tot else 0))
