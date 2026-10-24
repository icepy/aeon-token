from decimal import Decimal, getcontext
getcontext().prec = 50

def sqrtp(slot0):
    h = slot0[2:]
    return int(h[0:40], 16)

# VIRTUAL(18dp) / USDC(6dp), token0=VIRTUAL
for name, s in [
    ("0x7CB770D0 pancake", "0x000000000000000000000000000000000000000000000d3f8ff151bf2bb961bfffffffffffffff"),
    ("0x529d2863 uni",     "0x000000000000000000000000000000000000000000000d429908c6d6c4944fc8ffffffffffffff"),
]:
    p = Decimal(sqrtp(s)) / (Decimal(2) ** 96)
    raw = p * p                     # USDC_raw per VIRTUAL_raw
    usd = raw * Decimal(10**12)     # adjust 18dp vs 6dp
    print(name, "sqrtP=%s" % sqrtp(s), "VIRTUAL=%.7f" % usd)
