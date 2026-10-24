#!/usr/bin/env python3
"""Continuity: escrow balance + recent Burn events, pending xDEUS #1396, holder balances, supply."""
import json, time, urllib.request

RPC = "https://base.gateway.tenderly.co"

def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    last=None
    for i in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={
                "Content-Type":"application/json","User-Agent":"curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                d = json.loads(r.read().decode())
            if "error" in d: raise RuntimeError(d["error"])
            return d["result"]
        except Exception as e:
            last=e; time.sleep(1.5*(2**i))
    raise last

def calli(to, data, tag="latest"):
    r = rpc("eth_call", [{"to":to,"data":data}, tag])
    return int(r[2:][0:64], 16) if r and len(r) >= 66 else None

def pad(a):
    return a.lower().replace("0x","").rjust(64,"0")

head = int(rpc("eth_blockNumber", []), 16)
hb = rpc("eth_getBlockByNumber", [hex(head), False])
hts = int(hb["timestamp"],16)
print("head=%d ts=%d (%s)" % (head, hts, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(hts))))

ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
XDEUS  = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
DEUS   = "0x940a319b75861014a220d9c6c144d108552b089b"
CLAIM  = "0x5cbf5dfaa5336ce0456e24217e7911365100879a"

# escrow DEUS balance
eb = calli(DEUS, "0x70a08231" + pad(ESCROW))
print("escrow_balance_deus=%.6f" % (eb/1e18))
# xDEUS total supply
xs = calli(XDEUS, "0x18160ddd")
print("xdeus_total_supply=%d" % xs)
# DEUS total supply
ts = calli(DEUS, "0x18160ddd")
print("deus_total_supply=%.6f" % (ts/1e18))
# CLAIM vault balance
cb = calli(DEUS, "0x70a08231" + pad(CLAIM))
print("claim_vault_balance_deus=%.4f" % (cb/1e18))

# pending unstaker 0xbb0f7533
PEND = "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63"
pb = calli(DEUS, "0x70a08231" + pad(PEND))
px = calli(XDEUS, "0x70a08231" + pad(PEND))
print("pending_0xbb0f7533 deus=%.6f xdeus_nfts=%d" % (pb/1e18, px or 0))
if px:
    tid = calli(XDEUS, "0x2f745c59" + pad(PEND) + hex(0)[2:].rjust(64,"0"))
    print("  tokenOfOwnerByIndex(0)=%s" % tid)

# holder balances
for name, addr in [("0x7f6aba75","0x7f6aba7563cb5d31980d440337d3d1a6e3db58f3"),
                   ("0x6a45ca8b","0x6a45ca8bb30f396f40721e105e0aa6cabf326657"),
                   ("0xf0a04b07","0xf0a04b079dcf7b9d92682123ba2e2180109cb650"),
                   ("0xcae798c0","0xcae798c0c6958df8299df4f13726da433b8ba7ba")]:
    v = calli(DEUS, "0x70a08231" + pad(addr))
    print("holder %s = %.6f" % (name, v/1e18))

# escrow Burn events in last ~24h. Burn topic0
BURN = "0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d6adfabb7cd8caa254de14def35"
# Use a bounded backward scan (blocks ~34k/hour on Base)
lo_start = head - 90000
found = []
lo = lo_start
while lo < head:
    hi = min(lo + 999, head)
    got = rpc("eth_getLogs", [{"address": ESCROW, "fromBlock": hex(lo), "toBlock": hex(hi),
                               "topics": [BURN]}])
    found.extend(got)
    lo = hi + 1
print("burn_events_last_90000_blocks=%d" % len(found))
for lg in found[-10:]:
    blk = int(lg["blockNumber"],16)
    b = rpc("eth_getBlockByNumber", [hex(blk), False])
    bts = int(b["timestamp"],16)
    w = lg["data"][2:]
    amt = int(w[0:64],16)/1e18
    owner = "0x"+lg["topics"][1][-40:]
    tid = int(lg["topics"][2],16)
    print("  blk=%d %s owner=%s tokenId=%d amount=%.4f" % (
        blk, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(bts)), owner, tid, amt))
