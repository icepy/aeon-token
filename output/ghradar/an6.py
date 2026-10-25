import json
from collections import Counter

d = json.load(open('output/ghradar/out6.json'))
print('幸存', len(d))
print('已核验', sum(1 for c in d if 'commits_30d' in c))
print('未核验', sum(1 for c in d if c.get('unverified')))
print('空仓409', sum(1 for c in d if c.get('maybe_empty')))
print('stale零提交', sum(1 for c in d if c.get('stale')))

def rep(c):
    return (c.get('commits_30d') is not None and c['commits_30d'] >= 5
            and not c.get('stale') and not c.get('maybe_empty'))

R = [c for c in d if rep(c)]
print('报告级(脚本口径)', len(R))

# 分域
CRYPTO = {"verifiable inference", "proof of useful work", "data availability",
          "restaking", "intent-based", "maximal extractable value"}
rob = [c for c in R if not (set(c['terms']) & CRYPTO)]
cry = [c for c in R if set(c['terms']) & CRYPTO]
print('机器人侧', len(rob), '加密侧', len(cry))

print('\n--- 加密侧报告级 ---')
for c in cry:
    print('  %-40s ★%-4d 30d=%-4s %s %s' % (c['repo'], c['stars'], c['commits_30d'],
                                            c['created'], '/'.join(c['terms'])))

print('\n--- 提交数分层 (报告级) ---')
b = Counter()
for c in R:
    n = c['commits_30d']
    b['>=100' if n >= 100 else '50-99' if n >= 50 else '20-49' if n >= 20
      else '10-19' if n >= 10 else '5-9'] += 1
for k in ['>=100', '50-99', '20-49', '10-19', '5-9']:
    print('  %-6s %d' % (k, b.get(k, 0)))

print('\n--- 10 月新建报告级 ---')
oct_ = [c for c in R if c['created'] >= '2026-10-01']
print('  ', len(oct_))
for c in sorted(oct_, key=lambda x: -x['commits_30d'])[:20]:
    print('  %-40s ★%-4d 30d=%-4s %s' % (c['repo'], c['stars'], c['commits_30d'],
                                         '/'.join(c['terms'])))

print('\n--- 按词（全 term 口径）---')
pt = Counter()
for c in R:
    for t in c['terms']:
        pt[t] += 1
for k, v in pt.most_common():
    print('  %-24s %d' % (k, v))

print('\n--- 核验覆盖 ---')
print('  核验 250 / 幸存 %d = %.1f%%' % (len(d), 100 * 250 / len(d)))
