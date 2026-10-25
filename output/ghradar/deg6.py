import json

d = json.load(open('output/ghradar/out6.json'))
# 找 409 空仓在 out 中的位置（是否 ★>=5 优先组）
empty = [c for c in d if c.get('maybe_empty')]
print("409 空仓:", [c['repo'] for c in empty])
for c in empty:
    print("  ★%d created=%s" % (c['stars'], c['created']))

# 关键验证：★>=5 的仓是否全部核验成功（修复后应无 unverified）
hi = [c for c in d if c['stars'] >= 5]
print("\n★>=5 总数 %d，已核验 %d，未核验 %d，空仓 %d" %
      (len(hi), sum(1 for c in hi if 'commits_30d' in c),
       sum(1 for c in hi if c.get('unverified')),
       sum(1 for c in hi if c.get('maybe_empty'))))

lo = [c for c in d if c['stars'] < 5]
print("★<5 总数 %d，已核验 %d，未核验 %d" %
      (len(lo), sum(1 for c in lo if 'commits_30d' in c),
       sum(1 for c in lo if c.get('unverified'))))

# 409 之后是否还有成功核验（证明未降级）
print("\n409 之后是否仍有正常核验数据（抽查 5 个最新创建且已核验的 ★<5 仓）:")
for c in sorted([x for x in lo if 'commits_30d' in x], key=lambda x: x['created'])[-5:]:
    print("  %-42s ★%d created=%s 30d=%s" % (c['repo'], c['stars'], c['created'], c['commits_30d']))
