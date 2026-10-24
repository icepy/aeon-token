import json
import subprocess
import time

RPC = 'https://base.gateway.tenderly.co'
ESCROW = '0xA85A38796B951CE87B378538b32B3E6Ee3C4C373'
CLAIM = '0x5cbF5DfAa5336CE0456E24217E7911365100879a'
XDEUS = '0xe6d5f7439Bc236C40054e2275f765f59343D4431'
DEUS = '0x940A319B75861014A220D9c6c144d108552B089B'
E = 10 ** 18


def rpc(method, params):
    payload = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})
    delay = 1
    for attempt in range(6):
        p = subprocess.run([
            'curl', '-sS', '-X', 'POST', RPC,
            '-H', 'Content-Type: application/json',
            '-A', 'curl/8.5.0',
            '-d', payload], capture_output=True, text=True)
        out = p.stdout.strip()
        if out:
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                pass
        print('retry', attempt, 'rc', p.returncode, 'stderr', p.stderr.strip()[:80], 'out', out[:80])
        time.sleep(delay)
        delay = min(delay * 2, 8)
    return {'error': {'message': 'rpc failed'}}


def call(to, data, blk):
    r = rpc('eth_call', [{'to': to, 'data': data}, blk])
    if 'error' in r:
        return None, r['error'].get('message', r['error'])
    return int(r['result'], 16), None


HEAD = 53037772
B24 = 52994572

for label, blk in [('head', HEAD), ('-24h', B24)]:
    v, e = call(ESCROW, '0x18160ddd', hex(blk))
    print('escrow totalSupply', label, (v / E) if v is not None else e)

adata = '0x70a08231' + '0' * 24 + ESCROW.lower()[2:]
v, e = call(DEUS, adata, hex(HEAD))
v2, e2 = call(DEUS, adata, hex(B24))
print('escrow DEUS bal head', (v / E) if v is not None else e, '24h', (v2 / E) if v2 is not None else e2)

v, e = call(XDEUS, '0x18160ddd', hex(HEAD))
v2, e2 = call(XDEUS, '0x18160ddd', hex(B24))
print('xDEUS supply head', v, e, '24h', v2, e2)

v, e = call(DEUS, '0x18160ddd', hex(HEAD))
v2, e2 = call(DEUS, '0x18160ddd', hex(B24))
print('DEUS supply head', v, e, '24h', v2, e2, 'delta', (v - v2) if (v is not None and v2 is not None) else 'na')

cb = '0x70a08231' + '0' * 24 + CLAIM.lower()[2:]
v, e = call(DEUS, cb, hex(HEAD))
v2, e2 = call(DEUS, cb, hex(B24))
print('CLAIM head', (v / E) if v is not None else e, '24h', (v2 / E) if v2 is not None else e2,
      'delta', ((v - v2) / E) if (v is not None and v2 is not None) else 'na')
