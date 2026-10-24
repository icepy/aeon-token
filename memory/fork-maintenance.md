# Fork 维护备忘

本仓库是 `aeonfun/aeon` 的 fork。这张卡片记录「改哪里安全、改哪里要收尾」，
以及加一个自定义 skill 的标准流程。

放在 `memory/` 是因为它是 OPERATOR-owned：`aeon-update` 永远不会写入它。

---

## 一句话规则

| 想干的事 | 动哪里 | 安全吗 |
|---|---|---|
| 启用 / 停用官方 skill | `aeon.yml` 改一个词 | 安全 |
| 改调度 / 模型 / 通知渠道 | `aeon.yml` | 安全 |
| 加自己的 skill | `skills/<自己的slug>/SKILL.md` | 安全（fork-only，上游从不碰） |
| 写策略 / 记忆 / 观察清单 | `STRATEGY.md`、`memory/`、`soul/` | 安全 |
| 加完 skill 的收尾 | README + `docs/skill-packs.md`、`docs/aeon-setup.md`、`docs/examples/README.md` | **必须跑收尾命令** |
| 改框架代码 | `scripts/`、`bin/`、`.github/`、`apps/`、`harness-adapter/` | **谨慎**：要么别动，要么改完给上游提 PR |

「用官方 skill」零成本 —— 87 个技能已经全在仓库里，`enabled: false` 只是没排班。

---

## 为什么前四行安全：aeon-update 的文件分类

`skills/aeon-update/SKILL.md` 把仓库分成两类。

**OPERATOR-owned —— 上游改了只写进 PR 正文，绝不写入树：**

    aeon.yml            STRATEGY.md         soul/**             memory/**
    output/**           .mcp.json           .env*               aeon.db
    skills.lock         eyebrowlock.json    .claude/**
    catalog/*.json（除 catalog/skill-packs.json）
    apps/dashboard/outputs/**               .github/dependabot.yml

**OWNED —— 上游的改动会被应用：**

    skills/**  scripts/**  bin/**  harness-adapter/**  .github/**  apps/**
    docs/**  CLAUDE.md  AGENTS.md  CHANGELOG.md  .gitignore
    eyebrow.policy.json  catalog/skill-packs.json

三条原文保证：

1. `Fork-only skills are never touched (only upstream paths are ever in the change set).`
2. `Never copy catalog/*.json / eyebrowlock.json from upstream - regenerate them.`
3. 上游退役了你启用的 skill → 判为 `enabled-skill-removed-upstream`，**不删**，让你决定。

未解决的冲突会写进 `pending_conflicts` 并跟着 baseline 往前带，不会静默丢。

---

## 唯一要收尾的地方

`docs/**` 和 `.github/README.md` 是 OWNED，上游改动会被应用；同时 apply 又会从
最终目录树重新生成 `catalog/packs.json`。于是：

    packs.json 的 total_skills = 上游技能数 + 你自己的技能数
    README/docs 里手写的计数 = 只有上游那一份

必然对不上 → `ci-readme-catalog` 红。上游每加一个技能，同步 PR 就带一个
「计数漂了 N」的失败，N = 你自己加的 skill 数。合并前手动补，机械但每次都要做。

---

## 加一个自定义 skill 的标准流程

```bash
# 1. 用模板起手（保证 frontmatter 跟上游当前契约一致；不带参数可列模板）
bin/new-from-template <模板> <slug> --category crypto

# 2. 写 skills/<slug>/SKILL.md

# 3. 生成三件套（前两个是 bash，第三个是 node）
bin/generate-skills-json
bin/generate-packs-json
node bin/generate-skill-icons

# 4. 补 README/docs —— 让校验器告诉你要改哪几行
node scripts/validate-readme-catalog.mjs

# 5. 补指纹
eyebrow scan --path . --lockfile eyebrowlock.json

# 6. 本地验收，全绿再提交
node scripts/validate-readme-catalog.mjs
node scripts/validate-config.js
bash scripts/tests/test_validate_readme_catalog.sh
