import math
V = 524920.706698271817352904
D = 18970871.981723613047481457
virt = 0.6182951082201115
mark = (V/D)*virt
k = V*D

def sell(deus_amt):
    Dn = D + deus_amt
    Vn = k/Dn
    out = V - Vn
    newm = (Vn/Dn)*virt
    return {"deus_in": deus_amt, "virt_out": out, "usd_out": out*virt,
            "new_mark": newm, "impact_pct": (newm/mark-1)*100}

for amt in (85828.91, 398969.152081, 200000, 500000):
    print(sell(amt))
