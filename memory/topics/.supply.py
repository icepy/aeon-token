import json, urllib.request, datetime

RPC = "https://base.gateway.tenderly.co"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"
ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
CLAIM = "0x5cbf5dfaa5336ce0456e24217e7911365100879a"


def call(method, params):
    req = urllib.request.Request(
        RPC,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"content-type": "application/json", "User-Agent": "curl/8.5.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if "error" in out:
        raise RuntimeError(out["error"])
    return out["result"]


def bal(tok, who, tag="latest"):
    d = call("eth_call", [{"to": tok, "data": "0x70a08231" + who[2:].lower().rjust(64, "0")}, tag])
    return int(d, 16) / 1e18


head = int(call("eth_blockNumber", []), 16)
hdr = call("eth_getBlockByNumber", [hex(head), False])
ts = datetime.datetime.fromtimestamp(int(hdr["timestamp"], 16), datetime.UTC).isoformat()
print("head", head, ts)

esc = bal(DEUS, ESCROW)
print(f"escrow DEUS      {esc:,.6f}   (prior 29,103,661.674664 -> {esc-29103661.674664:+,.6f})")
print(f"xDEUS totalSupply {int(call('eth_call', [{'to': XDEUS, 'data': '0x18160ddd'}, 'latest']), 16)}")
print(f"CLAIM vault DEUS {bal(DEUS, CLAIM):,.2f}")
print(f"DEUS totalSupply {int(call('eth_call', [{'to': DEUS, 'data': '0x18160ddd'}, 'latest']), 16)/1e18:,.6f}")
print(f"5pct line        {esc*0.05:,.2f}")
