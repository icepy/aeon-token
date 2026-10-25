import json
from decimal import Decimal, getcontext
getcontext().prec = 40

rv_head = Decimal(524920706539548794602224) / Decimal(10**18)
rd_head = Decimal(18970871987459934948375054) / Decimal(10**18)
rv_1h   = Decimal(524920706539548794602224) / Decimal(10**18)
rd_1h   = Decimal(18970871987459934948375054) / Decimal(10**18)
rv_24h  = Decimal(528123827377027278187734) / Decimal(10**18)
rd_24h  = Decimal(18855811853287470198627995) / Decimal(10**18)

def vusd(sq):
    return (Decimal(sq) / (Decimal(2) ** 96)) ** 2 * Decimal(10**18) / Decimal(10**6)

v_head = vusd("62421401283812501687483")
v_1h   = vusd("62713894624950468313603")
v_24h  = vusd("63405137418929809058347")

ratio_h = rv_head / rd_head
ratio_1h = rv_1h / rd_1h
ratio_24h = rv_24h / rd_24h

mark_h = ratio_h * v_head
mark_1h = ratio_1h * v_1h
mark_24h = ratio_24h * v_24h

print("VIRTUAL/USD  head %.6f  1h %.6f  24h %.6f" % (v_head, v_1h, v_24h))
print("ratio V/D   head %.10f 1h %.10f 24h %.10f" % (ratio_h, ratio_1h, ratio_24h))
print("MARK USD    head %.8f  1h %.8f  24h %.8f" % (mark_h, mark_1h, mark_24h))
print("h1  %.4f%%" % ((mark_h/mark_1h - 1) * 100))
print("h24 %.4f%%" % ((mark_h/mark_24h - 1) * 100))
print("virt leg h1  %.4f%%  h24 %.4f%%" % ((v_head/v_1h-1)*100, (v_head/v_24h-1)*100))
print("ratio leg h1 %.4f%%  h24 %.4f%%" % ((ratio_h/ratio_1h-1)*100, (ratio_h/ratio_24h-1)*100))
print("DEUS in pool h24 delta %.2f (%.4f%%)" % (rd_head-rd_24h, (rd_head/rd_24h-1)*100))
print("VIRT in pool h24 delta %.2f (%.4f%%)" % (rv_head-rv_24h, (rv_head/rv_24h-1)*100))

targets = [Decimal("0.012"), Decimal("0.025"), Decimal("0.032"), Decimal("0.041")]
for t in targets:
    d = (t/mark_h - 1) * 100
    print("target %s distance %+.2f%%" % (t, d))

ath = Decimal("0.06876")
print("ATH distance %+.2f%%" % ((ath/mark_h - 1) * 100))
print("ath/now x%.2f" % (ath/mark_h))

# constant-product level math, zero-fee, single net flow
V, D = rv_head, rd_head
for t in targets:
    # mark = (V/D) * vusd ; solve for D_new with k constant and only DEUS in/out
    k = V * D
    # price_target_ratio = mark_usd/v_head
    r_t = t / v_head
    # r = V/D ; V = k/D -> r = k/D^2 -> D = sqrt(k/r)
    import math
    D_t = (k / r_t).sqrt()
    dd = D_t - D
    print("to %s: DEUS %+.0f (%.1f%% of pool DEUS)  USD %+.0f  action %s" % (
        t, dd, dd/D*100, dd*mark_h, "SELL" if dd > 0 else "BUY"))

print("last swap ts 1792900663 -> head 1792908119 = %.1f min dead" % ((1792908119-1792900663)/60))
