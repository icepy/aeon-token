import json
import shutil
import datetime

now = '2026-10-24T18:01:31Z'
mark = 0.0171930
h1 = 0.5536
h24 = -4.6948

targets = [0.012, 0.025, 0.032, 0.041]
for t in targets:
    print('%.3f distance %+.2f%%' % (t, (t / mark - 1) * 100))
    print('   level_math check')
