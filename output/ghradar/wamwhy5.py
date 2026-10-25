#!/usr/bin/env python3
"""被 「scan 全量有、幸存无」的 27 个逐个归因：pages 规则 / 多词去重 / 其他过滤器。"""
import json

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
by = {c["repo"]: c for c in out}
missing = ["Agentic-WAM/agentic-wam.github.io", "Alexi1984/MT-WAM",
           "Anonymoussdaui/Cat", "Clausy9/clausy9.github.io", "DAGroup-PKU/ViGAR",
           "HealorCai/Skel-WAM", "KevinGeng3/TrajWAM", "Na2Ssss/realtimewam-project",
           "OpenWAM-Official/OpenWAM-Official.github.io", "Prism-WAM/prism-wam.github.io",
           "RealtimeWAM/realtimewam.github.io", "Skywalker-yqz/AffordanceWAM",
           "UniWAM/UniWAM", "aws-samples/sample-dreamzero-finetuning-on-sagemaker",
           "cw-wam-project/cw-wam-project.github.io", "ddm-robo/ddm-robo.github.io",
           "dextacwam/DexTacWAM", "drejrnal/wam-icl", "fengddrobot/fengddrobot.github.io",
           "fleeinlightspeed/World-action-model-Reinforce-learning-finetuning-project",
           "iitimii/SmolWAM", "kf953741/kf953741", "lixuan27/World-Action-Model-Pretraining",
           "wa-jepa/wa-jepa.github.io", "wzx16/ddm-project-page",
           "yinghuagangshi/so101-vla-wam", "zzmmzzm/diffwam.github.io"]

print("%-58s %s" % ("repo", "归因"))
print("-" * 90)
for r in missing:
    short = r.split("/")[-1]
    owner = r.split("/")[0]
    if short.endswith(".github.io") or short.lower() == owner.lower():
        print("%-58s pages 规则（项目页/列表页，设计内丢弃）" % r)
    elif r in by:
        print("%-58s 在幸存集，但 term=%s（多词去重，只记首个词）" % (r, by[r]["term"]))
    else:
        print("%-58s 其他过滤器（excl/short_desc/carrier/farm）" % r)

print("\n按 term 统计：world action model 相关但归到别的词的仓")
for c in out:
    if "wam" in c["repo"].lower() and c["term"] != "world action model":
        print("   term=%-22s %s" % (c["term"], c["repo"]))
