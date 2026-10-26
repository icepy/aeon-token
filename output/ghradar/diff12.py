import json
prev = json.load(open('output/ghradar/tree11full.json'))
prevset = {x['repo'] for x in prev} if isinstance(prev, list) else set(prev)
print('prev11 n=', len(prevset))
d = json.load(open('output/ghradar/out.json'))
cur = {c['repo'] for c in d}
print('overlap', len(cur & prevset), 'new', len(cur - prevset), 'dropped', len(prevset - cur))
print('NEW:', sorted(cur - prevset))
print('DROPPED:', sorted(prevset - cur))
for c in d:
    if c['repo'] in ('huangkiki/huangkiki', 'Wade-Owo/Rob_Capstone',
                     'kevinc-lab/Structured-Latent-Dynamics',
                     'Zahraxy09/intent-centric-web3-2026'):
        print('SIZE', c['repo'], c['size_kb'], 'KB lang=', c['language'], 'created', c['created'])
