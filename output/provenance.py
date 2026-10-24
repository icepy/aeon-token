#!/usr/bin/env python3
"""Where did the 52,737 DEUS come from? Scan DEUS transfers to/from the seller, last 36h."""
import json
import time
import urllib.request

RPC = "https://base.gateway.tenderly.co"

def rpc(method, params, retries=5):
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
            time.sleep(0.8 * (2 ** i))
    raise last

DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
SELLER = "0xbd6383c7cbe3ed150f662f70fd4f3a4a1816e13d"
pad = "0x" + "0" * 24 + SELLER[2:].lower()

head = int(rpc("eth_blockNumber", []), 16)
lo = head - 65000   # ~36h at 2s blocks
print("head=%d range=%d..%d" % (head, lo, head), flush=True)

rows = []
cur = lo
calls = 0
while cur < head:
    hi = min(cur + 999, head)
    for topic_pattern in ((TRANSFER, None, pad), (TRANSFER, pad)):
        try:
            got = rpc("eth_getLogs", [{"address": DEUS, "fromBlock": hex(cur),
                                       "toBlock": hex(hi), "topics": list(topic_pattern)}])
            rows.extend(got)
            calls += 1
        except Exception as e:
            print("err %s..%s %s" % (cur, hi, e), flush=True)
    cur = hi + 1
    if calls % 20 == 0:
        print("progress cur=%d rows=%d" % (cur, len(rows)), flush=True)

seen = set()
out = []
for lg in rows:
    k = lg["transactionHash"] + lg["logIndex"]
    if k in seen:
        continue
    seen.add(k)
    frm = "0x" + lg["topics"][1][-40:]
    to = "0x" + lg["topics"][2][-40:]
    amt = int(lg["data"][2:], 16) / 1e18
    out.append((int(lg["blockNumber"], 16), frm, to, amt, lg["transactionHash"]))

out.sort()
print("total_transfers=%d" % len(out), flush=True)
for blk, frm, to, amt, tx in out:
    print(json.dumps({"blk": blk, "from": frm, "to": to, "amt": round(amt, 4),
                      "tx": tx[:20]}), flush=True)
