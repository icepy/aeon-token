---
name: narrative-brief
description: 检查 Grok 自动化 crypto-narrative-brief-3day 写入的 narratives.md，有新内容才推送，推送前按整份哈希和重复标签去重。
metadata:
  title: Narrative Brief
  category: crypto
  var: ""
  tags:
    - crypto
    - research
  capabilities:
    - external_api
    - sends_notifications
---

> **${var}** — 可选。`dry-run` 不发 notify、不写 seen、不覆盖 `report.md`。**原样传给脚本，不要自己解析。**

转发层。判断在 Grok 自动化 `crypto-narrative-brief-3day` 里已经做完，写进 `memory/topics/narratives.md`。本 skill 只回答一件事：这份正文是不是新的，是就原样推过来。

**不改 `narratives.md`。** 那个文件归 Grok。覆盖写还是改成 append，都不在这里动。

## 铁律

- **预算：全程 1 次工具调用。** 就是下面那条 python。digest 在 stdout，正文也在 stdout。不要再 Read 文件、不要 `cat`、不要自己抓 URL。
- **不许现写 `python3 -c`。** 去重、哈希、空文件、已推过，全在 `check.py`。
- **不要重写脚本。** 只有去重规则错了才 Edit `check.py`。
- **不要改写通知。** 脚本拼好的正文就是推送正文。不要缩写、不要加观点、不要重排。
- **空的、只有日期的、整份已经推过的：脚本不发，你也不要补发。** 正常就是安静。
- **同一节里重复的「标签」只留先出现的一条。** 另一节里的同名标签留下。`变化` / `反身性` / `对我持仓的意义` 不是标签，不许删。
- **已推过按整份哈希记**，在 `memory/narrative-brief-seen.json`。近 3 天日志里 `推送: yes` 的 sha 也算推过。`dry-run` 不算。
- **文件里按日期切开。** 只推没见过的那几节。Grok 改成 append 之后，旧节不会再推一次。
- **日期节超过 4：只在 stdout 记一笔，不删。** 删最旧一节是 Grok 的事。
- **产物文件名固定**（`report.md` / `report.dry.md` / `pending.json`）。
- **日志脚本已经写入。** 不要再追加一节 `### narrative-brief`。

## Config

读：
- GitHub 上的 `memory/topics/narratives.md`（raw URL，以它为准）
- 抓失败时才读仓库里的同路径文件
- `memory/narrative-brief-seen.json`
- 近 3 天 `memory/logs/` 里 `推送: yes` 的 sha

写（脚本自己写，模型不用管）：
- `output/narrative-brief/report.md` —— 非 dry-run 且有新内容才写。**dry-run 不覆盖它**
- `output/narrative-brief/report.dry.md` —— dry-run
- `output/narrative-brief/pending.json` —— notify 没发出去时留下，`--commit-sent` 才入库
- `memory/narrative-brief-seen.json` —— 发出去之后才写。dry-run 不写
- `memory/logs/${today}.md` 的 `### narrative-brief`

## Steps

### 1. 跑（一次 bash，就这一条）

```bash
python3 skills/narrative-brief/check.py "${var}"
```

脚本自己抓文件、去重、决定发或不发。stdout 就是这一轮的全部结果。

### 2. notify 没发出去时才补这两条

只有 stdout 出现 `notify: **未发**` 或 `notify: 失败` 才做。顺序不能反：

```bash
./notify -f output/narrative-brief/report.md
python3 skills/narrative-brief/check.py --commit-sent
```

没有这两行就停。补发成功之前不要自己把哈希写进 seen。

### 3. 输出

最终输出照抄 stdout。不要另写一篇分析。

跑完在日志之外再给两行：

- **下一步** — 没有。不要改 `check.py`。
- **你要处理的** — 只有 `结果: FETCH_FAIL` 才需要人看。其他写「这轮不用你处理」。

## Network note

脚本用 `curl` 打公开 raw 地址：

`https://raw.githubusercontent.com/icepy/aeon-token/main/memory/topics/narratives.md`

页面地址（写进通知，供核对）：

`https://github.com/icepy/aeon-token/blob/main/memory/topics/narratives.md`

先看 stdout 的 `narratives http=`。`reason=ok` 就用这份。非 2xx、超时、空正文、HTML，脚本会改读仓库里的同路径文件并打 `fallback=local`。两边都没有才是 `FETCH_FAIL`。模型不要自己再 WebFetch 一遍。

不需要密钥。不要用 `./secretcurl`。

## 结果

| stdout | 含义 | notify |
|---|---|---|
| `结果: NEW` | 有没推过的节 | 已发 |
| `结果: UNCHANGED` | 哈希都见过 | 不发 |
| `结果: EMPTY` | 没有正文 | 不发 |
| `结果: DRY` | dry-run | 不发 |
| `结果: FETCH_FAIL` | 远程和本地都没有 | 不发 |
