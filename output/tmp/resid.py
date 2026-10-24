import json
import subprocess
import time

RPC = 'https://base.gateway.tenderly.co'
POOL = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa'
TOPIC = '0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b'


def rpc(method, params):
    payload = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})
    delay = 1
    for _ in range(6):
        p = subprocess.run(['curl', '-sS', '-X', 'POST', RPC,
                            '-H', 'Content-Type: application/json', '-A', 'curl/8.5.0',
                            '-d', payload], capture_output=True, text=True)
        if p.stdout.strip():
            try:
                return json.loads(p.stdout)
            except json.JSONDecodeError:
                pass
        time.sleep(delay)
        delay = min(delay * 2, 8)
    return {'error': {'message': 'rpc failed'}}


E = 10 ** 18
for b in [53035972]:
    r = rpc('eth_getLogs', [{'address': POOL, 'fromBlock': hex(b), 'toBlock': hex(b), 'topics': [TOPIC]}])
    print('block', b, 'err' if 'error' in r else len(r['result']))
    if 'result' in r:
        for lg in r['result']:
            d = lg['data'][2:]
            w = [int(d[i:i + 64], 16) for i in range(0, len(d), 64)]
            print('  a1in %.4f a1out %.4f' % (w[1] / E, w[3] / E))
    blk = rpc('eth_getBlockByNumber', [hex(b), False])
    print('  ts', int(blk['result']['timestamp'], 16))
