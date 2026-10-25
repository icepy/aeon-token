import json
from collections import Counter

d = json.load(open('output/ghradar/out6.json'))
CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}
cry = [c for c in d if set(c['terms']) & CRYPTO]
print("加密侧幸存总数:", len(cry))
print("★0 占比:", sum(1 for c in cry if c['stars'] == 0))
print("\n逐个（按 ★ 降序）:")
for c in sorted(cry, key=lambda x: -x['stars']):
    print("  %-46s ★%-4d 30d=%-5s %-11s %s" %
          (c['repo'], c['stars'], c.get('commits_30d', 'n/a'), c['created'],
           '/'.join(c['terms'])))

print("\n=== 各加密词命中数（全 term）===")
pt = Counter()
for c in cry:
    for t in c['terms']:
        pt[t] += 1
for k, v in pt.most_common():
    print("  %-26s %d" % (k, v))
