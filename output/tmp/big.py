import json
import subprocess
import datetime

RPC = 'https://base.gateway.tenderly.co'
TOPIC = '0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b'
POOL = '0x3E97c5EC8c73e7d566eCA606472141a9b9a8C1Fa'.replace('566e', '566e')
POOL = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa'


def rpc(method, params):
    p = subprocess.run([
        'curl', '-fsS', '-X', 'POST', RPC,
        '-H', 'Content-Type: application/json',
        '-A', 'curl/8.5.0',
        '-d', json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})],
        capture_output=True, text=True)
    return json.loads(p.stdout)


logs = []
lo, end = 53035973, 53037772
while lo <= end:
    hi = min(lo + 999, end)
    r = rpc('eth_getLogs', [{'address': POOL, 'fromBlock': hex(lo), 'toBlock': hex(hi), 'topics': [TOPIC]}])
    logs.extend(r['result'])
    lo = hi + 1

E = 10 ** 18
for lg in logs:
    d = lg['data'][2:]
    w = [int(d[i:i + 64], 16) for i in range(0, len(d), 64)]
    a0in, a1in, a0out, a1out = w
    deus_in = a1in / E
    deus_out = a1out / E
    h = lg['transactionHash']
    if max(deus_in, deus_out) > 5000:
        tx = rpc('eth_getTransactionByHash', [h])['result']
        rec = rpc('eth_getTransactionReceipt', [h])['result']
        blk = rpc('eth_getBlockByNumber', [lg['blockNumber'], False])['result']
        ts = int(blk['timestamp'], 16)
        print('=== tx', h)
        print('  block', int(lg['blockNumber'], 16), datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).isoformat())
        print('  from', tx['from'], 'to', tx['to'], 'nonce', int(tx['nonce'], 16))
        print('  DEUS_in %.2f DEUS_out %.2f' % (deus_in, deus_out))
        # DEUS transfer legs
        DEUS = '0x940a319b75861014a220d9c6c144d108552b089b'
        for rl in rec['logs']:
            if rl['address'].lower() == DEUS and len(rl['topics']) == 3:
                val = int(rl['data'], 16) / E
                frm = '0x' + rl['topics'][1][-40:]
                to = '0x' + rl['topics'][2][-40:]
                print('    DEUS %.2f  %s -> %s' % (val, frm[:10], to[:10]))
