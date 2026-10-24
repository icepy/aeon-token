import math

ratio = 0.027883145675288927
vusd = 0.6224733418595573
deus = 18898164.07523058
virtual = 526940.2619051661
mark = ratio * vusd
targets = [0.012, 0.025, 0.032, 0.041]

print("mark", round(mark, 8))
print()
print("== distances ==")
for t in targets:
    print(t, round((t / mark - 1) * 100, 2), "%")

print()
print("== level math (x*y=k, zero fee) ==")
print("D_needed = D*(sqrt(r_cur/r_target)-1), r_target = target/vusd")
for t in targets:
    rt = t / vusd
    if rt >= ratio:
        # need to buy DEUS out: ratio falls... careful
        pass
    d_needed = deus * (math.sqrt(ratio / rt) - 1)
    action = "net SELL into pool" if d_needed > 0 else "net BUY out of pool"
    print(
        f"  {t}: r_t={rt:.8f} dD={d_needed:+,.0f} DEUS ({action})  usd~{abs(d_needed)*mark:,.0f}"
    )

print()
print("== h1 decomposition ==")
r1, v1 = 0.02793331885110427, 0.6155011945638854
m1 = r1 * v1
print("mark_1h", round(m1, 8), "->", round(mark, 8), "=", round((mark / m1 - 1) * 100, 3), "%")
print("ratio", round((ratio / r1 - 1) * 100, 3), "%")
print("vusd ", round((vusd / v1 - 1) * 100, 3), "%")

print()
print("== h24 decomposition ==")
r24, v24 = 0.02739505337861316, 0.6585793045999944
m24 = r24 * v24
print("mark_24h", round(m24, 8), "->", round(mark, 8), "=", round((mark / m24 - 1) * 100, 3), "%")
print("ratio", round((ratio / r24 - 1) * 100, 3), "%")
print("vusd ", round((vusd / v24 - 1) * 100, 3), "%")
print()
print("D24", 19065773.246059906, "D_now", deus, "net deus into pool", round(deus - 19065773.246059906, 2))
print("V24", 522307.8757803458, "V_now", virtual, "dV", round(virtual - 522307.8757803458, 2))
