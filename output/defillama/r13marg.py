import json
import urllib.request

CH = ["Ethereum", "Base", "Solana", "Arbitrum", "Ink", "Binance", "BSC",
      "Optimism", "OP Mainnet", "Hyperliquid L1", "Robinhood Chain"]
EXCL = set(["CEX", "Chain", "Interface"])
WANT = ["9354", "9355", "9356", "9357", "9358", "9359", "9360", "9361", "9362"]
req = urllib.request.Request("https://api.llama.fi/protocols?_cb=m13",
                             headers={"User-Agent": "defillama-radar/dl-v1"})
raw = json.load(urllib.request.urlopen(req, timeout=60))
byid = {str(p.get("id")): p for p in raw if isinstance(p, dict)}

print("== per-record bucket membership ==")
parent_marginal = 0
for i in WANT:
    p = byid[i]
    ch = p.get("chains") or []
    hit = [c for c in ch if c in CH]
    has_p = bool(p.get("parentProtocol"))
    has_c = p.get("category") in EXCL
    has_ch = not hit
    only = []
    if has_p and not has_c and not has_ch:
        only.append("parent-ONLY")
        parent_marginal += 1
    print(i, p.get("name"), "parent=", has_p, "excl=", has_c,
          "chainblock=", has_ch, "chains=", ch, only)
print("parent true marginal:", parent_marginal, "/ 7")

print("== category check (are any new entries EXCL?) ==")
print([byid[i].get("category") for i in WANT])

print("== id continuity ==")
ids = sorted(int(k) for k in byid)
print("max id in payload", max(ids))
pre = [x for x in ids if 9340 <= x <= 9370]
print("window", pre)

print("== same-second listedAt clusters among all payload ==")
from collections import Counter
c = Counter(p.get("listedAt") for p in raw if isinstance(p, dict) and p.get("listedAt"))
big = {k: v for k, v in c.items() if v >= 3}
import datetime
for k, v in sorted(big.items())[-8:]:
    print(k, datetime.datetime.fromtimestamp(k, datetime.timezone.utc).isoformat(), "n=", v)
