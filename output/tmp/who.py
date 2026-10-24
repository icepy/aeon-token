import json
import subprocess
import datetime

RPC = 'https://base.gateway.tenderly.co'
DEUS = '0x940A319B75861014A220D9c6c144d108552B089B'


def rpc(method, params):
    p = subprocess.run([
        'curl', '-fsS', '-X', 'POST', RPC,
        '-H', 'Content-Type: application/json',
        '-A', 'curl/8.5.0',
        '-d', json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})],
        capture_output=True, text=True)
    return json.loads(p.stdout)


def bal(addr, block='latest'):
    data = '0x70a08231' + '0' * 24 + addr.lower()[2:]
    r = rpc('eth_call', [{'to': DEUS, 'data': data}, block])
    if 'error' in r:
        return 'ERR ' + str(r['error'])
    return int(r['result'], 16) / 10 ** 18


head = int(rpc('eth_blockNumber', [])['result'], 16)
print('head', head)

for addr in ['0x9d1c316f1f307894c80e7d2963454e6342c8e0a9', '0x30d36b45592eba2f810596d9357dc1101b5afbdb']:
    code = rpc('eth_getCode', [addr, 'latest'])['result']
    nonce = int(rpc('eth_getTransactionCount', [addr, 'latest'])['result'], 16)
    eth = int(rpc('eth_getBalance', [addr, 'latest'])['result'], 16) / 10 ** 18
    print('===', addr)
    print('  code', code[:42], 'len', (len(code) - 2) // 2, 'nonce', nonce, 'eth %.6f' % eth)
    for label, b in [('now', head), ('-1h', head - 1800), ('-6h', head - 10800), ('-24h', head - 43200), ('-7d', head - 302400), ('-30d', head - 1296000)]:
        print('   bal %-5s %s' % (label, bal(addr, hex(b))))
