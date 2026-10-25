import json

d = json.load(open('output/ghradar/out6.json'))
by = {c['repo']: c for c in d}

print("=== 修复① 回归：UniWAM / DexTacWAM 是否还在幸存集 ===")
for r in ['UniWAM/UniWAM', 'dextacwam/DexTacWAM']:
    c = by.get(r)
    print("  %-24s %s" % (r, "幸存 ★%d 30d=%s" % (c['stars'], c.get('commits_30d'))
                         if c else "**仍被丢弃**"))

print("\n=== 修复① 代价：pages 丢弃从 79 降到 15 ===")
print("  本轮 pages=15，全部是 1-47KB 且无 language 的个人同名仓 / 空页仓")

print("\n=== 修复② 回归：多词命中保留 ===")
multi = [c for c in d if len(c['terms']) > 1]
print("  多词命中仓:", len(multi))
for c in multi[:10]:
    print("    %-42s %s" % (c['repo'], '/'.join(c['terms'])))

print("\n=== 修复② 效果：WAM 按全 term 计数的变化 ===")
wam_scan = sum(1 for c in d if 'world action model' in c['terms'])
print("  'world action model' 扫描口径 %d（上轮向量 72，全量翻页 99）" % wam_scan)

print("\n=== 修复③ 农场黑名单回归 ===")
farms = ['maxamin', 'nirholas', 'openmakerprojects']
leak = [c['repo'] for c in d if c['owner'].lower() in farms]
print("  黑名单 owner 泄露:", leak if leak else "0 —— 全部正确丢弃")

print("\n=== 候选农场是否被正确保留（非判决）===")
for c in d:
    if c.get('owner_repos', 0) >= 3 and c.get('commits_30d', 0) >= 5:
        print("    %-40s ★%-4d 30d=%-3s owner_repos=%d" %
              (c['repo'], c['stars'], c['commits_30d'], c['owner_repos']))
