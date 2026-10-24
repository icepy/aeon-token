import json, urllib.request, time

URL = "https://base.gateway.tenderly.co"
DEUS = "0x940a319b75861014a220d9c6c144d108552b089b"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
TXS = {
    "6414_sell_0xa6ae6bec": "0xa6ae6bec28e7484d4767b78dd8bb83455afdfc97ba4f1127cdbd074e41c6c204",
    "767_sell_0xd50d1de5": "0xd50d1de55fbb0ade1f43c71ac268e35d68305a8fae75e61e24a1810542d2295b",
    "5500_sell_0x6fb67d50": "0x6fb67d50feca12788a51cc4c88335bf166bd9b47e68fa5ae0018fceb02f210c7",
}


def rpc(payload, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(
                URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
            )
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None


for name, tx in TXS.items():
    r = rpc({"jsonrpc": "2.0", "id": 1, "method": "eth_getTransactionReceipt", "params": [tx]})
    if not r or "result" not in r or not r["result"]:
        print(name, "FAIL")
        continue
    rec = r["result"]
    print("==", name, "status", rec["status"])
    for L in rec["logs"]:
        if L["address"].lower() != DEUS:
            continue
        if L["topics"][0].lower() != TRANSFER:
            continue
        frm = "0x" + L["topics"][1][-40:]
        to = "0x" + L["topics"][2][-40:]
        amt = int(L["data"], 16) / 1e18
        print(f"   {amt:>12,.2f}  {frm} -> {to}")
    time.sleep(1)
