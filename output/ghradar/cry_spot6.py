import json
d = json.load(open('output/ghradar/out6.json'))
CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}
cry = [c for c in d if set(c['terms']) & CRYPTO]

print("=== 加密侧 ★0 且高提交（可疑刷量）逐个体检 ===")
for c in sorted([x for x in cry if (x.get('commits_30d') or 0) >= 5],
                key=lambda x: -x['commits_30d']):
    print("\n%-46s ★%d 30d=%s" % (c['repo'], c['stars'], c['commits_30d']))
    print("  created=%s  size=%dKB  lang=%s  topics=%s" %
          (c['created'], c['size_kb'], c['lang'], c['topics']))
    print("  desc: %s" % c['desc'])

print("\n=== 空仓 ===")
for c in cry:
    if c.get('maybe_empty'):
        print("  %s ★%d created=%s" % (c['repo'], c['stars'], c['created']))
        print("    desc: %s" % c['desc'])
