#!/usr/bin/env python3
"""Identify the 1h swap counterparties on the deepest DEUS pool."""
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

DEEP = "0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
SWAP = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"

head = int(rpc("eth_blockNumber", []), 16)
head_ts = int(rpc("eth_getBlockByNumber", [hex(head), False])["timestamp"], 16)
lo = head - 1900

logs = []
cur = lo
while cur < head:
    hi = min(cur + 999, head)
    logs.extend(rpc("eth_getLogs", [{"address": DEEP, "fromBlock": hex(cur), "toBlock": hex(hi),
                                     "topics": [SWAP]}]))
    cur = hi + 1

def bal(tok, holder):
    return int(call(tok, "0x70a08231" + "0" * 24 + holder[2:].lower()), 16) / 1e18

print("swaps=%d" % len(logs))
for lg in logs:
    w = lg["data"][2:]
    a0i, a1i = int(w[0:64], 16), int(w[64:128], 16)
    a0o, a1o = int(w[128:192], 16), int(w[192:256], 16)
    sender = "0x" + lg["topics"][1][-40:]
    to = "0x" + lg["topics"][2][-40:]
    txh = lg["transactionHash"]
    blk = int(lg["blockNumber"], 16)
    ts = int(rpc("eth_getBlockByNumber", [hex(blk), False])["timestamp"], 16)
    tx = rpc("eth_getTransactionByHash", [txh])
    frm = tx["from"]
    code = rpc("eth_getCode", [frm, "latest"])
    try:
        nb = int(rpc("eth_getTransactionCount", [frm, "latest"]), 16)
    except Exception:
        nb = -1
    d = {
        "blk": blk, "ts": ts, "tx": txh,
        "sender_topic": sender, "to": to, "tx_from": frm,
        "code": code[:20], "nonce": nb,
        "virtual_in": a0i / 1e18, "deus_in": a1i / 1e18,
        "virtual_out": a0o / 1e18, "deus_out": a1o / 1e18,
    }
    try:
        d["tx_from_deus_bal"] = bal(DEUS, frm)
    except Exception as e:
        d["tx_from_deus_bal"] = "err:" + str(e)
    print(json.dumps(d))
