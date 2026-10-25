#!/usr/bin/env python3
"""农场候选仓库的结构核验：size / fork / 提交数 / 一批同构检查。"""
import json, subprocess

repos = [
    "origin-data-lab/egocentric-keystep-annotation",
    "origin-data-lab/egocentric-rgb-imu-sample",
    "origin-data-lab/stereo-imu-egocentric-evaluation",
    "origin-data-lab/egocentric-motion-blur-gyro-vs-sharpness",
    "NEBULIS-Lab/D-JEPA", "NEBULIS-Lab/VLA-Fabric", "NEBULIS-Lab/BAS-VLA",
    "Roboparty/P-BFM", "Roboparty/roboparty_dexhand_teleop",
    "Roboparty/roboparty_teleop_wam",
    "SajjadPSavoji/Distracted-Robot", "SajjadPSavoji/AnyBox",
    "SajjadPSavoji/NICE-Scene-Surgery", "SajjadPSavoji/World-Action-Model-Robustness",
    "rzc156/dreamforge", "rzc156/vla-diag", "rzc156/near-zero-headroom",
    "muhamuttaqien/orpa", "muhamuttaqien/robosuite-project",
    "muhamuttaqien/vispro", "muhamuttaqien/cwm-manipulator",
    "liaohello/lelab", "liaohello/GigaWorld-Policy-Sim2Real",
    "liaohello/cosmos3-robot-lab",
    "sraentertainment17-code/robot-dataset-audit",
    "sraentertainment17-code/robotics-dataset-qa-learning-log",
    "sraentertainment17-code/sra-robotics-sample-audit",
    "maxamin/data-availability-layer-security",
    "maxamin/restaking-shared-security-risk",
    "maxamin/intent-solver-security",
    "nirholas/quiver",
    "OpenMakerProjects/warehouse-rover-manual-teleoperation",
]

print("%-52s %8s %4s %5s %6s %-11s %-11s" % (
    "repo", "sizeKB", "★", "fork", "cmts", "created", "pushed"))
print("-" * 108)
for r in repos:
    d = subprocess.run(["gh", "api", "repos/" + r], capture_output=True, text=True)
    if d.returncode != 0:
        print("%-52s  ERR %s" % (r, d.stderr.strip()[:40]))
        continue
    j = json.loads(d.stdout)
    c = subprocess.run(["gh", "api", "repos/%s/commits?per_page=100" % r],
                       capture_output=True, text=True)
    n = len(json.loads(c.stdout)) if c.returncode == 0 and c.stdout.strip() else -1
    print("%-52s %8d %4d %5d %6d %-11s %-11s" % (
        r, j.get("size", 0), j.get("stargazers_count", 0),
        j.get("forks_count", 0), n,
        (j.get("created_at") or "")[:10], (j.get("pushed_at") or "")[:10]))
