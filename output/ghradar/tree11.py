import json, subprocess
repos = ['syaok1/wm-outcome-pilot', 'BasisResearch/empiric', 'KAI030113/safedojo',
         'kevinc-lab/Structured-Latent-Dynamics', 'Wade-Owo/Rob_Capstone',
         'YG3-ai/yg3-agent-garden', 'EVE-World/EVEWorld', 'huangkiki/huangkiki']
out = {}
for r in repos:
    p = subprocess.run(['gh', 'api', 'repos/' + r + '/contents'],
                       capture_output=True, text=True)
    if p.returncode != 0:
        out[r] = 'ERR ' + (p.stderr or '').strip()[:100]
        continue
    try:
        items = json.loads(p.stdout)
        names = [(i['type'], i['name']) for i in items]
        out[r] = names[:12]
    except Exception as e:
        out[r] = 'PARSE ' + str(e)
    print('==', r)
    print(out[r])
json.dump(out, open('output/ghradar/tree11.json', 'w'), ensure_ascii=False, indent=1)
