import json

BASE = 'output/tmp/'


def load_words(name):
    d = json.load(open(BASE + name + '.json'))
    if d.get('error'):
        return None, d['error']
    s = d['result'][2:]
    return [int(s[i:i + 64], 16) for i in range(0, len(s), 64)], None


h, e1 = load_words('slot0_head')
a, e2 = load_words('slot0_1h')
print('err', e1, e2)
print('slot0 head words', h)
print('slot0 1h words', a)

# VIRTUAL/USDC uni V3: token0=VIRTUAL(18), token1=USDC(6)
# price token1/token0 = (sqrtX96/2^96)^2  => USDC raw per VIRTUAL raw
def usd_per_virtual(w):
    sq = w[0]
    p = (sq / 2 ** 96) ** 2 * 10 ** 18 / 10 ** 6
    return p


ph = usd_per_virtual(h)
pa = usd_per_virtual(a)
print('VIRTUAL usd head %.7f  1h %.7f  chg %.4f%%' % (ph, pa, (ph / pa - 1) * 100))

reverse = False
if not (0.01 < ph < 10):
    reverse = True
    def usd_per_virtual2(w):
        sq = w[0]
        p = (sq / 2 ** 96) ** 2
        return 1 / (p * 10 ** 18 / 10 ** 6)
    ph = usd_per_virtual2(h)
    pa = usd_per_virtual2(a)
    print('REVERSED: VIRTUAL usd head %.7f  1h %.7f  chg %.4f%%' % (ph, pa, (ph / pa - 1) * 100))

rh, _ = load_words('res_head')
ra, _ = load_words('res_1h')
E = 10 ** 18
ratio_h = rh[0] / rh[1]
ratio_a = ra[0] / ra[1]
print('ratio head %.9f  1h %.9f  chg %.4f%%' % (ratio_h, ratio_a, (ratio_h / ratio_a - 1) * 100))
print('mark head %.7f  1h %.7f  chg %.4f%%' % (ratio_h * ph, ratio_a * pa, (ratio_h * ph) / (ratio_a * pa) * 100 - 100))
print('DEUS net into pool %.4f' % ((rh[1] - ra[1]) / E))
print('VIRTUAL net %.4f' % ((rh[0] - ra[0]) / E))
