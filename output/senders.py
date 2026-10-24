import json, urllib.request

URL = "https://base.gateway.tenderly.co"
TXS = [
    "0x54badcc889aea57d7cbe230d2976ae5a580427b0f04116f7db6467f48c441b6e",
    "0x6fb67d50feca12788a51cc4c88335bf166bd9b47e68fa5ae0018fceb02f210c7",
    "0xd50d1de55fbb0ade1f43c71ac268e35d68305a8fae75e61e24a1810542d2295b",
    "0x67ff04af2400edab2e90dd26d4cf4d6c98698451af235e71a64279db4baa5ff3",
    "0xa6ae6bec28e7484d4767b78dd8bb83455afdfc97ba4f1127cdbd074e41c6c204",
    "0xc23fe4476e893dcb6fc27bf24a1d77e92a7ab5a91067c2de5bb3855cf5c6f816",
    "0x563ae8d8fb473551a0a8218065cd3cb81402e48e4839ce231015dd7ed744b07e",
    "0xdd4df341059cebfb173be13d890fe4378cc994c7151905f76f0dafd41f2a3b74",
    "0x929d4c23281f42bb1f3c153f42619064ab570e28418bb4223bf6cfcdec095364",
]


def rpc(payload):
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    return json.load(urllib.request.urlopen(req, timeout=30))


for t in TXS:
    r = rpc({"jsonrpc": "2.0", "id": 1, "method": "eth_getTransactionByHash", "params": [t]})
    res = r.get("result")
    if not res:
        print(t[:18], "NO RESULT", r.get("error"))
        continue
    print(t[:18], "from", res["from"], "to", res["to"], "blk", int(res["blockNumber"], 16))
