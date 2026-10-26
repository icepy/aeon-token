import json, subprocess, time

repos = ['Hostileoracle0606/motion-lab', 'mayuelala/EgoACT', 'ZaidKamil1574/Robot-Teleoperation',
         'shangchaohu718/supermimic-pera', 'eshaan2418/Recall', 'Kushaan-N/SyncSim',
         'Hchnr/s2a', 'sirosiro/SpaceGuidance-FBB', 'SetsunaFSeiei21/Circuit-OP-JEPA',
         'ideal-sisyphus/embodied-ai-learning', 'Katherine624/Paper_Reproduction',
         'PreshenNaidoo/applied-pytorch-bootcamp', 'Nikhildusa07/AEGIS-Autonomous-Multimodal-World-Understanding',
         'tsadi/worldsim-guard']
for r in repos:
    p = subprocess.run(['gh', 'api', 'repos/' + r + '/contents'], capture_output=True, text=True)
    if p.returncode != 0:
        print('ERR', r); continue
    items = json.loads(p.stdout)
    dirs = [i['name'] for i in items if i['type'] == 'dir']
    files = [i['name'] for i in items if i['type'] == 'file']
    print(r)
    print('   dirs:', dirs[:10])
    print('   files:', [f for f in files if not f.startswith('.')][:10])
    time.sleep(0.3)
