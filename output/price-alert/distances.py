p = 0.017918
print("=== distance to operator targets from $" + str(p) + " ===")
for t in [0.012, 0.025, 0.032, 0.041]:
    print(f"  ${t:<7} {(t/p-1)*100:+.2f}%")
print(f"  ATH $0.06876  {(0.06876/p-1)*100:+.2f}%")

print()
print("=== deepest-pool mark converted at each VIRTUAL print ===")
m = 0.028008543545418863
for v in [0.6405, 0.6366, 0.6355, 0.6342]:
    print(f"  VIRTUAL ${v} -> DEUS ${m*v:.6f}")

print()
print("=== deepest-pool mark vs live USDC venue median ===")
live = 0.017918
print(f"  deepest-pool (DEUS/VIRTUAL, stale): ${m*0.6342:.6f}")
print(f"  live USDC venues median:            ${live:.6f}")
print(f"  divergence: {(m*0.6342/live-1)*100:+.2f}%")
