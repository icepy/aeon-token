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

E = 10 ** 18
buys = 0.0
sells = 0.0
rows = []
for lg in logs:
    d = lg['data'][2:]
    w = [int(d[i:i + 64], 16) for i in range(0, len(d), 64)]
    ntopics = len(lg['topics'])
    if len(w) == 4:
        # Solidly: amount0In, amount1In, amount0Out, amount1Out
        a0in, a1in, a0out, a1out = w
    elif len(w) == 5:
        # UniV2 style: sender(not indexed), amount0In, amount1In, amount0Out, amount1Out
        a0in, a1in, a0out, a1out = w[1], w[2], w[3], w[4]
    else:
        print('WEIRD words=%d topics=%d' % (len(w), ntopics), lg['data'])
        continue
    deus_in = a1in / E   # taker sold DEUS into pool
    deus_out = a1out / E  # taker bought DEUS out
    sells += deus_in
    buys += deus_out
    rows.append((int(lg['blockNumber'], 16), lg['transactionHash'], deus_in, deus_out))

print('swaps=%d DEUS_in(sells)=%.4f DEUS_out(buys)=%.4f net_into_pool=%.4f' %
      (len(logs), sells, buys, sells - buys))
for b, h, di, do in rows:
    print('%d %s %s' % (b, h[:12], ('sell %.2f' % di) if di else ('buy %.2f' % do)))
