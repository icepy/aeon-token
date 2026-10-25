import json, urllib.request, datetime, time

RPC = "https://base.gateway.tenderly.co"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
BURN_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
_ids = [5000]

def rpc(method, params):
    _ids[0] += 1
    body = json.dumps({"jsonrpc":"2.0","id":_ids[0],"method":method,"params":params}).encode()
    for a in range(6):
        req = urllib.request.Request(RPC, data=body, headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                j = json.loads(r.read())
            if "error" in j: raise RuntimeError(j["error"])
            return j["result"]
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503) and a < 5:
                time.sleep(2+3*a); continue
            raise

head = int(rpc("eth_blockNumber", []), 16)
HTS = int(rpc("eth_getBlockByNumber",[hex(head),False])["timestamp"],16)

# 1) xDEUS transfers involving escrow, last ~30h
start = head - 78000
logs = []
b = start
while b <= head:
    e = min(b+999, head)
    part = rpc("eth_getLogs",[{"address":XDEUS,"fromBlock":hex(b),"toBlock":hex(e),
              "topics":[BURN_TOPIC, "0x000000000000000000000000"+ESCROW[2:].lower()]}])
    logs.extend(part)
    b = e+1

tsc = {}
def bts(n):
    if n not in tsc: tsc[n] = int(rpc("eth_getBlockByNumber",[hex(n),False])["timestamp"],16)
    return tsc[n]

esc = []
for lg in logs:
    esc.append({"blk": int(lg["blockNumber"],16),
                "iso": datetime.datetime.fromtimestamp(bts(int(lg["blockNumber"],16)), datetime.UTC).strftime("%m-%d %H:%M:%SZ"),
                "to_topic": lg["topics"][1][-40:],
                "tokenId": int(lg["topics"][3],16) if len(lg["topics"])>3 else None,
                "tx": lg["transactionHash"]})

# 2) total supply + escrow DEUS balance
sup = int(rpc("eth_call",[{"to":DEUS,"data":"0x18160ddd"},hex(head)]),16)
bal = int(rpc("eth_call",[{"to":DEUS,"data":"0x70a08231"+"0"*24+ESCROW[2:].lower()},hex(head)]),16)

print(json.dumps({
 "head": head, "head_iso": datetime.datetime.fromtimestamp(HTS, datetime.UTC).strftime("%FT%TZ"),
 "window_blocks": [start, head],
 "xdeus_escrow_transfers_30h": esc,
 "escrow_deus_balance": bal/1e18,
 "total_supply": sup/1e18,
 "escrow_pct_of_supply": bal/sup*100,
}, indent=1))
