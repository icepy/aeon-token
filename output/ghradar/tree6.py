import json, subprocess, time

REPOS = ["xXGuilasXx/spark-pearl-miner", "Ulysse98/prism", "samooth/zig-zkml",
         "opodark/hyperspace-agi-1.05", "itzebe/intent-pay",
         "sublimestate/swap-RFQ", "SlipGuard-HQ/stellar-slipguard",
         "netzo92/pearl-fast-matmul", "prabhu-omkar/AIRcoin",
         "pastaisfine/swapsos", "Trustlink-Labs/TSN-Protocol",
         "HansDeploy/Flash-DeFi", "Dhaiwat10/openinstinct-qwen"]

def gh(p):
    r = subprocess.run(["gh", "api", p], capture_output=True, text=True, timeout=60)
    return json.loads(r.stdout) if r.returncode == 0 else None

for rid in REPOS:
    cur = gh("repos/%s/contents" % rid)
    d = gh("repos/" + rid)
    files = sorted([x["name"] + ("/" if x["type"] == "dir" else "") for x in cur]) if cur else []
    print("\n%-40s lang=%s forks=%s open_issues=%s" %
          (rid, d.get("language") if d else "?", d.get("forks_count") if d else "?",
           d.get("open_issues_count") if d else "?"))
    print("  " + " · ".join(files[:18]))
    time.sleep(0.3)
