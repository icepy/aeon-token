✅ aeon-update

**aeon-update - 2026-11-09**

同步了 33 个上游 commit → PR #24 已开。

上游 `aeonfun/aeon` 领先 33 个 commit（11-02 → 11-08）。干净应用 15 个文件，9 个需人工看。

**新增 3 个 ICP 技能：** `canister-status`（控制面监控）、`sns-digest`（治理提案摘要）、`icp-deploy-check`（上线前静态检查）。eyebrow 扫描无 findings。

**9 个冲突已逐个核对，没有一条是真逻辑冲突：** 5 个文档卡在技能数上（本地 93 / 上游 87→92，**保持 93**）；`.gitignore` 本地是上游超集；`AGENTS.md` 的 `deleted-locally` 是误报；dashboard 图标冲突已被重生成覆盖；`docs/icp/README.md` 本地版比上游更准，保留本地。

**顺手修了工具一个坑：** `apply` 的 eyebrow 重扫在 `AGENTS.md` 暂存删除的瞬间跑，把它从 lockfile 里剔掉了。已按原值补回（最终 99 条 = 96 + 3）。以后再看到「非新增技能的条目被删」，先怀疑扫的是暂存区。

**需要你决定的一件事：** 上游 `aeon.yml` 新增了 `canister-audit`、`canister-status`、`sns-digest`、`icp-deploy-check`、`flovia` 五条（全部默认关闭）。要跟就跟，不跟也不影响这次技能文件落地。

PR: https://github.com/icepy/aeon-token/pull/24

🔗 https://github.com/icepy/aeon-token/pull/24