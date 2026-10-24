import json
import subprocess

RPC = 'https://base.gateway.tenderly.co'
TOPIC = '0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b'
POOL = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa'

start = 53035973
end = 53037772


def rpc(payload):
    p = subprocess.run([
        'curl', '-fsS', '-X', 'POST', RPC,
        '-H', 'Content-Type: application/json',
        '-A', 'curl/8.5.0',
        '-d', json.dumps(payload)], capture_output=True, text=True)
    return json.loads(p.stdout)


logs = []
lo = start
while lo <= end:
    hi = min(lo + 999, end)
    r = rpc({'jsonrpc': '2.0', 'id': 1, 'method': 'eth_getLogs', 'params': [{
        'address': POOL, 'fromBlock': hex(lo), 'toBlock': hex(hi), 'topics': [TOPIC]}]})
    if 'error' in r:
        print('ERROR', lo, hi, r['error'])
        raise SystemExit(1)
    got = r.get('result', [])
    logs.extend(got)
    print('window %d..%d -> %d logs' % (lo, hi, len(got)))
    lo = hi + 1

print('total swaps', len(logs))


def word(h, i):
    return int(h[2 + i * 64:2 + (i + 1) * 64], 16)


E = 10 ** 18
buys = 0.0
sells = 0.0
txs = []
for lg in logs:
    data = lg['data']
    n = (len(data) - 2) // 64
    w = [word(data, i) for i in range(n)]
    # Solidly Swap: amount0In, amount1Out, amount1In, amount0Out  (varies)
    # token0=VIRTUAL, token1=DEUS -> use reserve direction via amount1In/amount1Out if 4 words
    if n >= 4:
        a0in, a1out, a1in, a0out = w[0], w[1], w[2], w[3]
    else:
        print('unexpected word count', n, data)
        continue
    deus_bought = a1out / E
    deus_sold = a1in / E
    if deus_bought > 0:
        buys += deus_bought
    if deus_sold > 0:
        sells += deus_sold
    txs.append((lg['blockNumber'], lg['transactionHash'], deus_bought, deus_sold))

print('swaps=%d buys_deus_out=%.4f sells_deus_in=%.4f net_into_pool=%.4f' %
      (len(logs), buys, sells, sells - buys))
for b, h, db, ds in txs:
    print(int(b, 16), h[:12], 'buy %.2f' % db if db else 'sell %.2f' % ds)
