import json, urllib.request, time
RPC="https://base.gateway.tenderly.co"
DEUS="0x940A319B75861014A220D9c6c144d108552B089B"
TR="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
WALLETS = [
 ("0x4af20629b81dd0ddef1bbac1b72b4c1594a18f9a", 8612.177673333446),
 ("0x393f8accc70a73862ecda51bd3b1395e55631f3b", 12951.379476673497),
 ("0x5318d687f24c9bbfc3ac67b27331d96c117e777c", 14621.912849993054),
 ("0x380ce63e3368e2dff6ba351647eb9396815ce61e", 6970.444099295909),
 ("0xfb4224282a67cff86b7780d408e2c4da840f6c78", 11926.293411159739),
 ("0x9be2134e02465ce9b20ce99d6160e9a6a46677ee", 7593.334848594693),
 ("0xd50de17126280a31afee93d5e4d830233e19473d", 10459.28808898746),
 ("0x3d1aa83e5bf6b3d254e8f56b587b034613529c8e", 12694.079551962197),
]
_id=[21000]
def rpc(m,p):
    _id[0]+=1
    body=json.dumps({"jsonrpc":"2.0","id":_id[0],"method":m,"params":p}).encode()
    for a in range(6):
        req=urllib.request.Request(RPC,data=body,headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=45) as r: j=json.loads(r.read())
            if "error" in j: raise RuntimeError(f"{m}: {j['error']}")
            return j["result"]
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503) and a<5: time.sleep(2+3*a); continue
            raise
def bal(a,n):
    return int(rpc("eth_call",[{"to":DEUS,"data":"0x70a08231"+"0"*24+a[2:].lower()},hex(n)]),16)/1e18

head=int(rpc("eth_blockNumber",[]),16)
MINT_BLK=53061481
rows=[]
for a,amt in WALLETS:
    n=int(rpc("eth_getTransactionCount",[a,hex(head)]),16)
    now=bal(a,head)
    # first ever DEUS inbound? scan from MINT_BLK only for outflows
    tw="0x"+"0"*24+a[2:].lower()
    outs=[]
    b=MINT_BLK
    while b<=head:
        e=min(b+999,head)
        outs.extend(rpc("eth_getLogs",[{"address":DEUS,"fromBlock":hex(b),"toBlock":hex(e),"topics":[TR,tw]}]))
        b=e+1
    outs=[o for o in outs if int(o["data"],16)/1e18>0.001]
    rows.append({"wallet":a,"received":round(amt,6),"nonce":n,
                 "bal_now":round(now,6),"sold_moved":round(amt-now,6),
                 "n_out_tx":len({o["transactionHash"] for o in outs}),
                 "out_total":round(sum(int(o["data"],16)/1e18 for o in outs),6),
                 "code":rpc("eth_getCode",[a,hex(head)])[:12]})
tot=sum(r["received"] for r in rows)
print(json.dumps({"head":head,"n":len(rows),"mint_total":round(tot,6),
 "moved_out":round(sum(r["sold_moved"] for r in rows),6),
 "still_held":round(sum(r["bal_now"] for r in rows),6),
 "fresh_all_nonce0":all(r["nonce"]==0 for r in rows),
 "rows":rows},indent=1))
