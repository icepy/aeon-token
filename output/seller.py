#!/usr/bin/env python3
"""Trace the 52,737 DEUS seller: origin of coins, prior balance, whether it is a known wallet."""
import json
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"

def rpc(method, params, retries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={
                "Content-Type": "application/json", "User-Agent": "curl/8.5.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read().decode())
            if "error" in d:
                raise RuntimeError(d["error"])
            return d["result"]
        except Exception as e:
            last = e
            time.sleep(1.5 * (2 ** i))
    raise last

def call(to, data, tag="latest"):
    return rpc("eth_call", [{"to": to, "data": data}, tag])

SELLER = "0xbd6383c7cbe3ed150f662f70fd4f3a4a1816e13d"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
CLAIM = "0x5cbf5dfaa5336ce0456e24217e7911365100879a"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

head = int(rpc("eth_blockNumber", []), 16)
head_ts = int(rpc("eth_getBlockByNumber", [hex(head), False])["timestamp"], 16)
print("head=%d" % head)

print("code=%s" % rpc("eth_getCode", [SELLER, "latest"]))
print("nonce=%d" % int(rpc("eth_getTransactionCount", [SELLER, "latest"]), 16))
print("eth_bal=%d" % int(rpc("eth_getBalance", [SELLER, "latest"]), 16))

pad = "0" * 24 + SELLER[2:].lower()
def bal_at(blk):
    return int(call(DEUS, "0x70a08231" + pad, hex(blk)), 16) / 1e18

for mins, label in ((0, "now"), (60, "-1h"), (360, "-6h"), (1440, "-24h"),
                    (10080, "-7d"), (43200, "-30d")):
    blk = head - int(mins * 30)
    try:
        print("bal %s = %.6f (blk %d)" % (label, bal_at(blk), blk))
    except Exception as e:
        print("bal %s ERR %s" % (label, e))

# incoming/outgoing DEUS transfers, last ~3 days (windows of 4000 blocks to stay light)
print("--- DEUS transfers touching seller, last ~72h ---")
lo = head - 130000
cur = lo
rows = []
while cur < head:
    hi = min(cur + 4000, head)
    try:
        got = rpc("eth_getLogs", [{"address": DEUS, "fromBlock": hex(cur), "toBlock": hex(hi),
                                   "topics": [TRANSFER, None, "0x" + pad]}])
        rows.extend(got)
    except Exception:
        pass
    try:
        got = rpc("eth_getLogs", [{"address": DEUS, "fromBlock": hex(cur), "toBlock": hex(hi),
                                   "topics": [TRANSFER, "0x" + pad]}])
        rows.extend(got)
    except Exception:
        pass
    cur = hi + 1

seen = set()
for lg in rows:
    key = lg["transactionHash"] + lg["logIndex"]
    if key in seen:
        continue
    seen.add(key)
    frm = "0x" + lg["topics"][1][-40:]
    to = "0x" + lg["topics"][2][-40:]
    amt = int(lg["data"][2:], 16) / 1e18
    blk = int(lg["blockNumber"], 16)
    print(json.dumps({"blk": blk, "from": frm, "to": to, "amt": round(amt, 4),
                      "tx": lg["transactionHash"]}))
