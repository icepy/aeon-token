import json, time, urllib.request

RPC = "https://base.gateway.tenderly.co"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
BURN = "0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7ad6fabb7cd8caa254de14def35"
STAKE = "0x7162984403f6c73c8639375d45a9187dfd04602231bd8e587c415718b5f7e5f9"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"

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

head = int(rpc("eth_blockNumber", []), 16)
b24 = 53016186
found = {"burns": [], "stakes": []}
errs = []
for name, topic in [("burns", BURN), ("stakes", STAKE)]:
    s = b24
    while s <= head:
        e = min(s + 999, head)
        ok = False
        for attempt in range(3):
            try:
                r = rpc("eth_getLogs", [{"address": ESCROW, "fromBlock": hex(s), "toBlock": hex(e), "topics": [topic]}])
                found[name].extend(r); ok = True; break
            except Exception as ex:
                time.sleep(1 + attempt)
        if not ok:
            errs.append("%s %d-%d FAILED" % (name, s, e))
        s = e + 1

def fmt(l):
    t = l["topics"]
    d = l["data"][2:]
    w = [d[i:i+64] for i in range(0, len(d), 64)]
    return {
        "blk": int(l["blockNumber"], 16),
        "tx": l["transactionHash"],
        "owner": "0x" + t[1][-40:] if len(t) > 1 else None,
        "tokenId": int(t[2], 16) if len(t) > 2 else None,
        "words": [int(x, 16) for x in w],
    }

out = {"head": head, "window": [b24, head], "chunks": (head - b24) // 999 + 1,
       "burns_n": len(found["burns"]), "stakes_n": len(found["stakes"]),
       "burns": [fmt(l) for l in found["burns"]],
       "stakes": [fmt(l) for l in found["stakes"]],
       "errors": errs}
print(json.dumps(out, indent=1))
