python3 - <<'PY'
import json, subprocess, sys, hashlib

def stage(n):
    out = subprocess.check_output(['git', 'show', f':{n}:eyebrowlock.json'])
    return json.loads(out)

ours, theirs = stage(2), stage(3)

have  = {a['name'] for a in ours['artifacts']}
other = {a['name'] for a in theirs['artifacts']}

added = [a for a in theirs['artifacts'] if a['name'] not in have]
lost  = sorted(have - other)

print('上游新增 :', [a['name'] for a in added])
print('你独有   :', lost)

if [a['name'] for a in added] != ['flovia']:
    print('!! 上游新增不是只有 flovia，检查后再继续'); sys.exit(1)

must = {'arxiv-radar', 'defillama-radar', 'github-radar', 'narrative-brief'}
missing = must - have
if missing:
    print('!! 你的技能丢了:', missing); sys.exit(1)

ours['artifacts'].extend(added)

# 修掉因 .gitignore 改动而失效的 anatomy 哈希
h = hashlib.sha256(open('.gitignore', 'rb').read()).hexdigest()
for a in ours['artifacts']:
    if a['name'] == 'anatomy':
        for f in a.get('files', []):
            if f['path'] == '.gitignore':
                f['hash'] = h

with open('eyebrowlock.json', 'w') as f:
    json.dump(ours, f, indent=2, ensure_ascii=False); f.write('\n')

names = {a['name'] for a in ours['artifacts']}
print('总条目   :', len(names))
print('flovia 在 :', 'flovia' in names)
print('自检      :', 'PASS' if not (must - names) and 'flovia' in names else 'FAIL')
PY