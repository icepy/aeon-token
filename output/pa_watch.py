import json, time, urllib.request

RPC = "https://base.gateway.tenderly.co"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
CLAIM = "0x5cbf5dfaa5336ce0456e24217e7911365100879a"

def rpc(method, params, tries=5):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.2
    for i in range(tries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as r:
                j = json.loads(r.read())
            if "error" in j:
                e = j["error"]; raise RuntimeError("%s %s" % (e.get("code"), e.get("message")))
            return j["result"]
        except Exception as ex:
            last = ex; time.sleep(delay); delay *= 2
    raise RuntimeError("rpc %s: %s" % (method, last))

def words(h):
    h = h[2:] if h.startswith("0x") else h
    return [h[i:i+64] for i in range(0, len(h), 64)]

def call(to, data, blk="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, blk if isinstance(blk, str) else hex(blk)])

def bal(token, holder, blk="latest"):
    return int(words(call(token, "0x70a08231" + "0" * 24 + holder[2:].lower(), blk))[0], 16) / 1e18

head = int(rpc("eth_blockNumber", []), 16)
b24 = 53016186
out = {"head": head}

W = {
    "inventory_0x92325e5a": "0x92325e5ac24ec4d8d0032cf4cb37b080f4a6374f",
    "wholesaler_0x4e3ae00e": "0x4e3ae00e8323558fa5cac04b152238924aa31b60",
    "pending_unstake_0xbb0f7533": "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63",
    "buyer_0x9d1c316f": "0x9d1c316f1f307894c80e7d2963454e6342c8e0a9",
}
for k, a in W.items():
    try:
        out[k + "_deus"] = bal(DEUS, a)
    except Exception as e:
        out[k + "_deus"] = "ERR"

def supply(token, blk="latest"):
    return int(words(call(token, "0x18160ddd", blk))[0], 16) / 1e18

out["claim_main_vault_deus"] = bal(DEUS, CLAIM)
out["claim_24h_ago"] = bal(DEUS, CLAIM, b24)
out["claim_net_out_24h"] = out["claim_24h_ago"] - out["claim_main_vault_deus"]
out["deus_total_supply"] = supply(DEUS)
out["supply_24h_ago"] = supply(DEUS, b24)
out["supply_24h_delta"] = out["deus_total_supply"] - out["supply_24h_ago"]
out["xdeus_total_supply"] = int(words(call(XDEUS, "0x18160ddd"))[0], 16)
out["xdeus_24h_ago"] = int(words(call(XDEUS, "0x18160ddd", b24))[0], 16)

# pending unstake NFT check
try:
    out["bb_nft_count"] = int(words(call(XDEUS, "0x70a08231" + "0" * 24 + W["pending_unstake_0xbb0f7533"][2:].lower()))[0], 16)
    if out["bb_nft_count"] > 0:
        r = call(XDEUS, "0x2f745c59" + "0"*24 + W["pending_unstake_0xbb0f7533"][2:].lower() + "0"*64)
        out["bb_nft_id"] = int(words(r)[0], 16)
except Exception as e:
    out["bb_err"] = str(e)[:120]

print(json.dumps(out, indent=1))
