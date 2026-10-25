import json, time, urllib.request

RPC = "https://base.gateway.tenderly.co"
POOL = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
BURN = "0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7ad6fabb7cd8caa254de14def35"
STAKE = "0x7162984403f6c73c8639375d45a9187dfd04602231bd8e587c415718b5f7e5f9"
XDEUS = "0xe6d5f7434bd1a5b0e0b6ecb3ee6c3bb8e0e5d0d0"  # placeholder, replaced below

def rpc(method, params, tries=5):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    delay = 1.5
    for i in range(tries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as r:
                j = json.loads(r.read())
            if "error" in j:
                e = j["error"]
                raise RuntimeError("%s %s" % (e.get("code"), e.get("message")))
            return j["result"]
        except Exception as ex:
            last = ex
            time.sleep(delay); delay *= 2
    raise RuntimeError("rpc %s: %s" % (method, last))

def words(h):
    h = h[2:] if h.startswith("0x") else h
    return [h[i:i+64] for i in range(0, len(h), 64)]

head = int(rpc("eth_blockNumber", []), 16)
b1h = 53057586
out = {"head": head, "scan_from": b1h, "scan_to": head}

# chunked scan for swaps in the last hour
logs = []
start = b1h
while start < head:
    end = min(start + 999, head)
    try:
        res = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(start), "toBlock": hex(end), "topics": [SWAP]}])
    except Exception as e:
        res = None
        out.setdefault("errors", []).append("%d-%d: %s" % (start, end, e))
    if res:
        logs.extend(res)
    start = end + 1
out["swaps_1h"] = len(logs)
out["swap_txs"] = [l["transactionHash"] for l in logs]

# discriminative control: known-active block from prior state (53055658)
ctl = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(53055658), "toBlock": hex(53055658), "topics": [SWAP]}])
out["control_known_block_logs"] = len(ctl)
# negative control: same block, topic0 last char flipped
bad = SWAP[:-1] + ("a" if SWAP[-1] != "a" else "b")
ctl2 = rpc("eth_getLogs", [{"address": POOL, "fromBlock": hex(53055658), "toBlock": hex(53055658), "topics": [bad]}])
out["control_flipped_topic_logs"] = len(ctl2)

# escrow balance + events last hour and 24h
def bal(addr, blk="latest"):
    r = rpc("eth_call", [{"to": "0x940A319B75861014A220D9c6c144d108552B089B",
                          "data": "0x70a08231" + "0"*24 + addr[2:].lower()}, blk if isinstance(blk, str) else hex(blk)])
    return int(words(r)[0], 16) / 1e18

out["escrow_deus"] = bal(ESCROW)
b24 = 53016186
out["escrow_deus_24h_ago"] = bal(ESCROW, b24)
out["escrow_24h_delta"] = out["escrow_deus"] - out["escrow_deus_24h_ago"]

for name, topic in [("burns", BURN), ("stakes", STAKE)]:
    try:
        r = rpc("eth_getLogs", [{"address": ESCROW, "fromBlock": hex(b24), "toBlock": hex(head), "topics": [topic]}])
    except Exception as e:
        r = []
        out.setdefault("errors", []).append("escrow %s: %s" % (name, e))
    out["escrow_" + name + "_24h"] = len(r)
    out["escrow_" + name + "_detail"] = [
        {"blk": int(l["blockNumber"], 16), "tx": l["transactionHash"],
         "topics": l["topics"], "data": l["data"]} for l in r
    ]

print(json.dumps(out, indent=1))
