import json, os, shutil
P = "memory/topics/price-alert-state.json"
S = json.load(open(P))
S["deus_total_supply"] = {
    "total_supply": 876263456.7232751,
    "h1_back": 876177627.813275,
    "h24_back": 876190274.819517,
    "h48_back": 876209967.4847519,
    "change_1h": 85828.9100001,
    "change_24h": 73181.90375804901,
    "change_48h": 53489.2385231,
    "observed_at": "2026-10-25T08:09:17Z",
    "remeasured": True,
    "note": (
        "CORRECTION, supersedes the -29,152.63 / -12,373.69 deflation reads. Nine-point series: "
        "supply was byte-identical for 12h then jumped +85,828.91 in ONE block at 07:11:49Z (blk 53061481), "
        "the largest single mint on record. Total supply is NET INFLATIONARY: +73,181.90 over 24h, "
        "+53,489.24 over 48h. Repeated 'unchanged' reads were the mint missing the observation window, "
        "never evidence of deflation. Do not cite single unchanged reads as deflation again."
    ),
}
shutil.copyfile(P, P + ".bak")
os.replace(P + ".tmp", P) if os.path.exists(P + ".tmp") else None
json.dump(S, open(P, "w"), indent=1, ensure_ascii=False)
json.load(open(P))
print("ok", S["deus_total_supply"]["change_24h"])
