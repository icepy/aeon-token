import json
import subprocess
import datetime

RPC = 'https://base.gateway.tenderly.co'
POOL = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa'
VPOOL = '0x529d2863a1521d0b57db028168fdE2E97120017C'
ESCROW = '0xA85A38796B951CE87B378538b32B3E6Ee3C4C373'
CLAIM = '0x5cbF5DfAa5336CE0456E24217E7911365100879a'
XDEUS = '0xe6d5f7439Bc236C40054e2275f765f59343D4431'
DEUS = '0x940A319B75861014A220D9c6c144d108552B089B'


def rpc(method, params):
    p = subprocess.run([
        'curl', '-fsS', '-X', 'POST', RPC,
        '-H', 'Content-Type: application/json',
        '-A', 'curl/8.5.0',
        '-d', json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})],
        capture_output=True, text=True)
    return json.loads(p.stdout)


HEAD = 53037772


def block_ts(n):
    return int(rpc('eth_getBlockByNumber', [hex(n), False])['result']['timestamp'], 16)


# find block exactly 86400s before head
lo, hi = HEAD - 60000, HEAD
ts_head = block_ts(HEAD)
target = ts_head - 86400
b = HEAD - 43200
while True:
    t = block_ts(b)
    if t <= target:
        break
    b -= 250
print('24h block', b, 'ts', datetime.datetime.fromtimestamp(block_ts(b), datetime.timezone.utc).isoformat(),
      'head ts', datetime.datetime.fromtimestamp(ts_head, datetime.timezone.utc).isoformat())

E = 10 ** 18


def reserves(blk):
    r = rpc('eth_call', [{'to': POOL, 'data': '0x0902f1ac'}, blk])
    s = r['result'][2:]
    w = [int(s[i:i + 64], 16) for i in range(0, len(s), 64)]
    return w[0] / E, w[1] / E


def vusd(blk):
    r = rpc('eth_call', [{'to': VPOOL, 'data': '0x3850c7bd'}, blk])
    if 'error' in r:
        return None, r['error']
    s = r['result'][2:]
    sq = int(s[:64], 16)
    return (sq / 2 ** 96) ** 2 * 10 ** 12, None


def bal(addr, blk, selector='0x70a08231'):
    data = selector + '0' * 24 + addr.lower()[2:]
    r = rpc('eth_call', [{'to': DEUS if addr != XDEUS else XDEUS, 'data': data}, blk])
    if 'error' in r:
        return None
    return int(r['result'], 16) / E


now_v, now_d = reserves(hex(HEAD))
old_v, old_d = reserves(hex(b))
now_p, e1 = vusd(hex(HEAD))
old_p, e2 = vusd(hex(b))
print('res now V %.4f D %.4f ratio %.9f' % (now_v, now_d, now_v / now_d))
print('res 24h V %.4f D %.4f ratio %.9f' % (old_v, old_d, old_v / old_d))
print('VIRTUAL now %.7f 24h %.7f chg %.4f%%' % (now_p, old_p, (now_p / old_p - 1) * 100))
mark_now = now_v / now_d * now_p
mark_old = old_v / old_d * old_p
print('mark now %.7f  24h %.7f  chg %.4f%%' % (mark_now, mark_old, (mark_now / mark_old - 1) * 100))
print('DEUS net into pool 24h %.2f' % (now_d - old_d))


def supply(addr, blk):
    r = rpc('eth_call', [{'to': addr, 'data': '0x18160ddd'}, blk])
    if 'error' in r:
        return None
    return int(r['result'], 16)


def bbal(addr_holder, blk):
    data = '0x70a08231' + '0' * 24 + addr_holder.lower()[2:]
    r = rpc('eth_call', [{'to': ESCROW, 'data': data}, blk])
    if 'error' in r:
        return None
    return int(r['result'], 16) / E


print('escrow now %.6f 24h %.6f delta %.6f' % (bbal(ESCROW, hex(HEAD)), bbal(ESCROW, hex(b)), bbal(ESCROW, hex(HEAD)) - bbal(ESCROW, hex(b))))
print('xDEUS supply now %d 24h %d' % (supply(XDEUS, hex(HEAD)), supply(XDEUS, hex(b))))
print('DEUS supply now %d 24h %d delta %d' % (supply(DEUS, hex(HEAD)), supply(DEUS, hex(b)), supply(DEUS, hex(HEAD)) - supply(DEUS, hex(b))))

cb = '0x70a08231' + '0' * 24 + CLAIM.lower()[2:]
r = rpc('eth_call', [{'to': DEUS, 'data': cb}, hex(HEAD)])
r2 = rpc('eth_call', [{'to': DEUS, 'data': cb}, hex(b)])
print('CLAIM now %.2f 24h %.2f delta %.2f' % (int(r['result'], 16) / E, int(r2['result'], 16) / E,
                                              (int(r['result'], 16) - int(r2['result'], 16)) / E))
