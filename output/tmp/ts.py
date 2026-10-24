import json
import subprocess

RPC = 'https://base.gateway.tenderly.co'


def rpc(method, params):
    p = subprocess.run([
        'curl', '-fsS', '-X', 'POST', RPC,
        '-H', 'Content-Type: application/json',
        '-A', 'curl/8.5.0',
        '-d', json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})],
        capture_output=True, text=True)
    return json.loads(p.stdout)


blocks = [53036820, 53036858, 53037326, 53037442]
for b in blocks:
    r = rpc('eth_getBlockByNumber', [hex(b), False])
    print(b, 'ts', int(r['result']['timestamp'], 16))

txs = [
    ('0xf0694e8d', None),
]
