import json
import subprocess
import time

RPC = 'https://base.gateway.tenderly.co'
POOL = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa'
TOPIC = '0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b'
XDEUS = '0xe6d5f7439Bc236C40054e2275f765f59343D4431'
W = '0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63'


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


# CONTROL 1: known-good window (contains the 17:50:31 sell at blk 53037442)
r = rpc('eth_getLogs', [{'address': POOL, 'fromBlock': hex(53037442), 'toBlock': hex(53037442), 'topics': [TOPIC]}])
print('control exact-block 53037442 ->', 'err' if 'error' in r else len(r['result']))

# CONTROL 2: same window shifted, must be 0
r = rpc('eth_getLogs', [{'address': POOL, 'fromBlock': hex(53037443), 'toBlock': hex(53037443), 'topics': [TOPIC]}])
print('control shifted-block 53037443 ->', 'err' if 'error' in r else len(r['result']))

# CONTROL 3: deliberately wrong topic (1 char off), known-nonzero window
BAD = TOPIC[:-1] + ('0' if TOPIC[-1] != '0' else '1')
r = rpc('eth_getLogs', [{'address': POOL, 'fromBlock': hex(53035973), 'toBlock': hex(53037772), 'topics': [BAD]}][:0] or
        [{'address': POOL, 'fromBlock': hex(53036973), 'toBlock': hex(53037772), 'topics': [BAD]}])
print('control wrong-topic ->', 'err' if 'error' in r else len(r['result']))

# topic0 histogram over the hour, address only
r = rpc('eth_getLogs', [{'address': POOL, 'fromBlock': hex(53035973), 'toBlock': hex(53036972)}])
print('histogram window1 err/len ->', r.get('error') or len(r['result']))

# 0xbb0f7533 still holds #1396 ?
r = rpc('eth_call', [{'to': XDEUS, 'data': '0x70a08231' + '0' * 24 + W.lower()[2:]}, 'latest'])
print('xDEUS balanceOf(0xbb0f7533) ->', int(r['result'], 16) if 'result' in r else r.get('error'))
r = rpc('eth_call', [{'to': XDEUS, 'data': '0x2f745c59' + '0' * 24 + W.lower()[2:] + '0' * 64}, 'latest'])
print('tokenOfOwnerByIndex(0) ->', int(r['result'], 16) if 'result' in r else r.get('error'))
