import json
import subprocess
import time

RPC = 'https://base.gateway.tenderly.co'
POOL = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa'
DEUS = '0x940A319B75861014A220D9c6c144d108552B089B'
E = 10 ** 18


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


r = rpc('eth_call', [{'to': POOL, 'data': '0x0902f1ac'}, 'latest'])
s = r['result'][2:]
w = [int(s[i:i + 64], 16) for i in range(0, len(s), 64)]
V = w[0] / E
D = w[1] / E
vp = 0.6155012
mark = V / D * vp
print('V %.4f D %.4f mark %.7f' % (V, D, mark))

import math
for t in [0.012, 0.025, 0.032, 0.041]:
    rt = t / vp
    Dn = D * (math.sqrt((V / D) / rt) - 1)
    print('%s -> DEUS needed %.0f (%.2fM)  usd %.0f' % (t, Dn, Dn / 1e6, Dn * mark))
