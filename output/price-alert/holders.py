import json, urllib.request, time

RPC = "https://base.gateway.tenderly.co"
ESCROW = "0xa85a38796b951ce87b378538b32b3e6ee3c4c373"
DEUS    = "0x940a319b75861014a220d9c6c144d108552b089b"

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
    for attempt, back in enumerate([1, 2, 4, 8]):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                out = json.loads(r.read())
            if "error" in out:
                raise RuntimeError(out["error"])
            return out["result"]
        except Exception:
            if attempt == 3:
                raise
            time.sleep(back)

head = int(rpc("eth_blockNumber", []), 16)
print("head", head)

def call(to, data, blk=None):
    return rpc("eth_call", [{"to": to, "data": data}, hex(blk) if blk else "latest"])

def bal(token, holder, blk=None):
    data = "0x70a08231" + holder[2:].lower().rjust(64, "0")
    return int(call(token, data, blk), 16)

holders = {
    "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63": "pending xDEUS #1396",
    "0xf0a04b079dcf7b9d92682123ba2e2180109cb650": "250k incumbent trimmer",
    "0x7f6aba7563cb5d31980d440337d3d1a6e3db58f3": "record-dump absorber",
    "0x6a45ca8bb30f396f40721e105e0aa6cabf326657": "second absorber",
    "0xcae798c0c6958df8299df4f13726da433b8ba7ba": "5k unstaker",
}
print("\n--- DEUS balances (native, 18dp) ---")
for a, label in holders.items():
    now = bal(DEUS, a) / 1e18
    ago = bal(DEUS, a, head - 1800) / 1e18   # ~1h
    print(f"  {a[:10]} {label:26s} {now:>16,.4f}   (1h ago {ago:,.4f})")

print("\n--- escrow DEUS balance ---")
esc = bal(DEUS, ESCROW) / 1e18
esc24 = bal(DEUS, ESCROW, head - 43200) / 1e18
print(f"  now {esc:,.4f}   24h ago {esc24:,.4f}   delta {esc-esc24:+,.2f} ({(esc/esc24-1)*100:+.3f}%)")
print(f"  5%/day line {esc24*0.05:,.0f}  ratio {(esc24-esc)/(esc24*0.05):.3f}")

# xDEUS totalSupply (ERC-721 count)
xs = int(call(ESCROW, "0x18160ddd"), 16)
print(f"\n  xDEUS totalSupply {xs}")
