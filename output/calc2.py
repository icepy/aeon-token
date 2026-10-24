from decimal import Decimal, getcontext
getcontext().prec = 40

def dec(h):
    return Decimal(int(h, 16)) / Decimal(10**18)

now = "0x000000000000000000000000000000000000000000006f8a0e7cb128046a68710000000000000000000000000000000000000000000fa371b2742fecff865f43000000000000000000000000000000000000000000000000000000006add12d5"
prev = "0x000000000000000000000000000000000000000000006f8e7389e07a34406d940000000000000000000000000000000000000000000fa2d3fb8d172d61d75a91000000000000000000000000000000000000000000000000000000006add0ea3"

def parse(s):
    s = s[2:]
    return dec(s[0:64]), dec(s[64:128])

vn, dn = parse(now)
vp, dp = parse(prev)
rn, rp = vn/dn, vp/dp
print("now  V=%.6f D=%.6f ratio=%.9f" % (vn, dn, rn))
print("prev V=%.6f D=%.6f ratio=%.9f" % (vp, dp, rp))
print("ratio h1 pct = %.4f%%" % ((rn/rp - 1) * 100))
print("DEUS net into pool (h1) = %.4f" % (dn - dp))
print("VIRTUAL net into pool (h1) = %.4f" % (vn - vp))
