import json, subprocess, time

d = json.load(open('output/ghradar/out6.json'))
CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}

def has_agentfile(rid):
    r = subprocess.run(["gh", "api", "repos/%s/contents" % rid],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return None
    names = {x["name"].lower() for x in json.loads(r.stdout)}
    hits = names & {"agents.md", "claude.md", ".clinerules", ".agents",
                    ".cursorrules", "gemini.md", "copilot-instructions.md"}
    return sorted(hits)

cry = [c for c in d if set(c['terms']) & CRYPTO and (c.get('commits_30d') or 0) >= 5]
rob = [c for c in d if not (set(c['terms']) & CRYPTO) and (c.get('commits_30d') or 0) >= 20]

def survey(label, items, cap):
    print("\n=== %s（抽样 %d）===" % (label, min(cap, len(items))))
    n_hit = n_tot = 0
    for c in sorted(items, key=lambda x: -x['commits_30d'])[:cap]:
        h = has_agentfile(c['repo'])
        if h is None:
            continue
        n_tot += 1
        if h:
            n_hit += 1
            print("  %-44s ★%-3d 30d=%-4d %s" % (c['repo'], c['stars'], c['commits_30d'], h))
        time.sleep(0.25)
    print("  → %d/%d 含 agent 指令文件 (%.0f%%)" % (n_hit, n_tot, 100.0 * n_hit / max(n_tot, 1)))

survey("加密侧 ≥5 提交", cry, 18)
survey("机器人侧 ≥20 提交", rob, 25)
