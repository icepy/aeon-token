import json, re, glob

# 收过往日志里出现过的仓库名
mentioned = set()
for f in glob.glob('memory/logs/2026-10-2*.md'):
    txt = open(f, encoding='utf-8').read()
    for m in re.findall(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', txt):
        if not m.startswith(('api.', 'www.')) and len(m) > 3:
            mentioned.add(m.lower())
print("过往日志提到过的仓库名:", len(mentioned))

rob = json.load(open('output/ghradar/rob_activity6.json'))
cry = json.load(open('output/ghradar/cry_activity6.json'))

print("\n=== 机器人侧：新面孔（首次出现 AND 近 7 天活跃）===")
new = [r for r in rob if r['repo'].lower() not in mentioned and (r['c7'] or 0) > 0]
for r in sorted(new, key=lambda x: -x['c7']):
    print("  %-46s ★%-4d 30d=%-4d 7d=%d" % (r['repo'], r['stars'], r['c30'], r['c7']))

print("\n=== 加密侧：新面孔（首次出现 AND 近 7 天活跃）===")
new2 = [r for r in cry if r['repo'].lower() not in mentioned and (r['c7'] or 0) > 0]
for r in sorted(new2, key=lambda x: -(x['c7'] or 0)):
    print("  %-46s ★%-4d 30d=%-4d 7d=%-4s %s" % (r['repo'], r['stars'], r['c30'], r['c7'], r['terms']))
