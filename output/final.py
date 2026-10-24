from decimal import Decimal, getcontext
getcontext().prec = 50

ratio_now = Decimal("0.027860832")
V_now = (Decimal("0.6235623") + Decimal("0.6246790")) / 2
V_1h  = (Decimal("0.6254557") + Decimal("0.6246790")) / 2   # 1h-ago leg (0x529d read at head; use same)
ratio_1h = Decimal("0.027869409")
ratio_24 = Decimal("0.027514726")
V_24 = Decimal("0.6555188")

mark = ratio_now * V_now
mark_1h = ratio_1h * V_1h
mark_24 = ratio_24 * V_24
print("VIRTUAL/USD avg now %.7f" % V_now)
print("MARK now  $%.8f" % mark)
print("MARK 1h   $%.8f  -> h1 %+.4f%%" % (mark_1h, (mark / mark_1h - 1) * 100))
print("MARK 24h  $%.8f  -> h24 %+.4f%%" % (mark_24, (mark / mark_24 - 1) * 100))

usdc = [Decimal("0.01721955"), Decimal("0.01720974"), Decimal("0.01716328")]
med = sorted(usdc)[1]
print("\nUSDC median $%.8f  premium %+.3f%%" % (med, (mark / med - 1) * 100))
print("band $%.6f - $%.6f" % (min(usdc), max(usdc)))

print("\ngates from $%.8f:" % mark)
for t in ("0.012", "0.025", "0.032", "0.041"):
    print("  $%s  %+8.2f%%" % (t, (Decimal(t) / mark - 1) * 100))
print("  ATH $0.06876  %+.2f%%" % ((Decimal("0.06876") / mark - 1) * 100))

# level math at this block
V_res = Decimal("526729.374184701610846321")
D_res = Decimal("18905730.371963049965150019")
vn = Decimal("0.62412")
print("\n--- level math (x*y=k, ratio space) ---")
for t in ("0.012", "0.025", "0.032", "0.041"):
    target_ratio = Decimal(t) / vn
    deus = D_res * ((ratio_now / target_ratio) ** Decimal("0.5") - 1)
    side = "SELL" if deus > 0 else "BUY"
    print("  $%s  %s  %.0f DEUS  (%.1f%% of pool DEUS)" % (t, side, abs(deus), abs(deus) / D_res * 100))
