import json
import urllib.request

CH = ["Ethereum", "Base", "Solana", "Arbitrum", "Ink", "Binance", "BSC",
      "Optimism", "OP Mainnet", "Hyperliquid L1", "Robinhood Chain"]
EXCL = set(["CEX", "Chain", "Interface"])
req = urllib.request.Request("https://api.llama.fi/protocols?_cb=brk13",
                             headers={"User-Agent": "defillama-radar/dl-v1"})
raw = json.load(urllib.request.urlopen(req, timeout=60))
only_chain = []
empty = []
for p in raw:
    ch = p.get("chains") or []
    hit = [c for c in ch if c in CH]
    if p.get("parentProtocol"):
        continue
    if p.get("category") in EXCL:
        continue
    if ch and not hit:
        only_chain.append((p["id"], p.get("name"), p.get("category"), ch))
    if not ch:
        empty.append((p["id"], p.get("name"), p.get("category")))
print("non_whitelist_with_chains", len(only_chain))
for r in only_chain:
    print("   ", r)
print("empty_chains", len(empty))
