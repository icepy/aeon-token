from decimal import Decimal, getcontext
getcontext().prec = 40

r0 = int("6f8a0e7cb128046a6871", 16)
r1 = int("fa371b2742fecff865f43", 16)
print("r0 raw", r0, "r1 raw", r1)

V = Decimal(r0) / Decimal(10**18)   # VIRTUAL (token0)
D = Decimal(r1) / Decimal(10**18)   # DEUS (token1)
print("VIRTUAL", V)
print("DEUS", D)
ratio = V / D
print("ratio VIRTUAL/DEUS", ratio)
