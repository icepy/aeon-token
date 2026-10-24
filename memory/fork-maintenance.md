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
| 加完 skill 的收尾 | README + `docs/skill-packs.md`、`docs/aeon-setup.md`、`docs/examples/README.md` | **已自动化** —— push 后 `register-skill` 会改 |
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

## 收尾：计数漂移（原因仍在，但已自动化）

`docs/**` 和 `.github/README.md` 是 OWNED，上游改动会被应用；同时 apply 又会从
最终目录树重新生成 `catalog/packs.json`。于是：

    packs.json 的 total_skills = 上游技能数 + 你自己的技能数
    README/docs 里手写的计数 = 只有上游那一份

必然对不上 → `ci-readme-catalog` 红。上游每加一个技能，同步 PR 就带一个
「计数漂了 N」的失败，N = 你自己加的 skill 数。

**2026-10 起这一步由 `register-skill` 自动完成** —— push 后它重算计数并提交，
`ci-readme-catalog` 会自己转绿。本地不再需要手补，也不再需要装 eyebrow。

---

## 加一个自定义 skill 的标准流程（2026-10 起 · CI 自动化版）

本地只做三件事：

1. 写 `skills/<slug>/SKILL.md`（frontmatter 必须有 `name` / `description` / `metadata.category`）
2. 在 `aeon.yml` 加一行：`<slug>: { enabled: false, schedule: "..." }`
3. `git add -A && git commit -m "feat(<slug>): ..." && git push`

push 之后 `register-skill` 自动完成旧流程的第 3–6 步：生成 `skills.json` / `packs.json` /
图标、补 README 与 `docs/**` 的计数、重刷 `eyebrowlock.json`，然后重跑各道 gate。

**本地不用装 eyebrow。**

### 手动兜底（只在 CI 挂了时用）

```bash
bin/new-from-template <模板> <slug> --category crypto   # 起手模板，可选
bin/generate-skills-json
bin/generate-packs-json
node bin/generate-skill-icons
node scripts/validate-readme-catalog.mjs
eyebrow scan --path . --lockfile eyebrowlock.json
node scripts/validate-config.js
bash scripts/tests/test_validate_readme_catalog.sh
```

### skill 的 var 语法（只有三个 token）

`dry-run` · `days:N` · `names`，空格分隔可组合。

**内容不写进 var** —— 词表写 SKILL.md 的 `TERMS` 块，名字写 `memory/universe-names.txt`。
填了不认识的 token 会被**静默忽略**（填 `DEUS` 等于没填）。

### 本地不手改的三处

- `docs/**` 与 `.github/README.md` 里的计数
- `catalog/*.json`
- `eyebrowlock.json`

（都会被 register-skill 覆盖，手改等于白改）

---

## 触发链

    Cloudflare Worker（外部闹钟）→ Aeon · Scheduler（读 aeon.yml）→ Skill Runner

**Worker 里没有任何 skill 名单**，加 skill 只改 aeon.yml。

判调度有没有真跑：看 `memory/cron-state.json` 里有没有该 skill 的 `last_dispatch`。
**`enabled: true` ≠ 跑过。**

---

## PR 分支规则（踩过坑）

- fork 内的 PR：从 `origin/main` 起分支
- 给上游 `aeonfun/aeon` 的 PR：必须从 `upstream/main` 起分支
- GitHub 对 fork 的 PR 默认把 base 设成**父仓库**，必须手动改回自己的
- 踩过：PR #1265，base 设错，diff 变成 293 个 commit

bot 开的 PR 上 workflow 会卡 `Action required` 等人工批准 —— 但**同一批 gate 在 main 上会自动跑**，
PR 分支那几条失败可以不管。

---

## 预检清单（push 前）

- [ ] `SKILL.md` 第一行是 `---`
- [ ] frontmatter 有 `name` / `description` / `metadata.category`
- [ ] 改过的代码块没破坏语法
- [ ] `git status` 干净，没夹带无关文件

---

## 踩坑史（按时间）

1. `register-skill.yml` 的 `paths` 只写了 `skills/**` → 推 workflow 自己不触发 → 补上 `.github/scripts/**` 与 workflow 自身
2. `install.sh` 走 `api.github.com` 匿名请求 → 共享 runner IP 被限流 → 403 → 改直连 pinned release asset + `checksums.txt` 校验
3. 下载文件名与 checksums.txt 里的名字不一致 → `sha256sum: No such file` → 按原 asset 名保存，`grep -F` 匹配
4. `catalog/packs.json` 的 skills 是对象不是字符串 → 写出 `[object Object]` → 加 slug 取值兜底
5. `DRY=1 python3 ...` 前缀赋值被权限层拒 → **静默以非 dry 执行并写盘** → 必须 `export` 单独一行
6. 跨词命中在扫描循环里就写 `seen` → 同一篇被第二词命中时被短路 → 改 run 内 `hit_ids` 判重、run 结束才 merge
7. `per_term` 只计新收 → 把存量全 seed 进 `seen` 后词表健康度假性归零 → 拆出 `raw_term`
8. `GITHUB_TOKEN` 推的 commit 不会重新触发 workflow → 需要显式 `gh workflow run`

---

## 附录：arXiv 铁律

- 只用 `ti:`（`abs:` 是松散匹配，`abs:"MEV"` 会命中兆电子伏特）
- 写长短语，不写单词
- 多词必须带引号（`ti:foo bar` 会被解析成 `ti:foo AND bar`）
- 零命中不等于废词
- 加新领域的词必须同时配 carrier 并登记进 `CARRIER_BY_TERM`
- 看到 0 命中先看 `raw_term` 和「窗口内最新收录日期」，分清滞后 / seen / carrier 误杀
- 词表写机制，不写项目名 —— 名字交给下一条通道

---

## 附录：日常检查

- 调度有没有跑：`memory/cron-state.json` 的 `last_dispatch`
- 落后上游多少：仓库首页的 fork 横幅（"This branch is X commits ahead"）
- 有没有 PR 挂着：PR 列表；bot 开的要人工点批准
