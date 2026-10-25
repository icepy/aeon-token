import os, shutil, json
P = "memory/topics/price-alert-state.json"
shutil.copyfile(P, P + ".bak")
os.replace(P + ".tmp", P)
json.load(open(P))
print("ok", os.path.getsize(P))
