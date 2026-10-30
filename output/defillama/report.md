**defillama-radar** · 2026-10-30 00:02Z · 可报 1

来源：`https://api.llama.fi/protocols` · 源站 `last-modified 23:39:19Z` · `cf-cache-status: MISS` · 全量 8880 条（cache-bypass 与 CF HIT 两份 id 集合逐条相同，无漏条目）

**1. GongFu** · 收益 · Robinhood Chain · TVL $0 · 登记 2026-10-29 17:58Z · `id 9277`
链上代币锁定：用户把 GF 锁 1–180 天，到期原样取回同一批 GF；上限收益只由一笔固定的、不可提取的储备支付。
合约 `robinhood:0xFEd6b187F6Da04E2EAe5D3ea89B57129Da62b28A` · `audits: 0`（未审计）· 无站点

**漏斗**：新增 id 7（可报 1 / 过滤 6）· 重报 0 · parent 丢 2 · 类目丢 0 · 链白名单丢 4 · 拉取失败 0 · 基线轮 False

**被挡掉的 6 条**（记 `filtered`，永不补报）：`Nexus Mutual RWI Vault`（Ethereum，$2.04M，parent）· `Olive Exchange Options`（Solana 期权，parent）· `Faroo`（Pharos 流动性质押，$650K，链不在白名单）· `StonkDrop` / `OmenX` / `OTC`（后者 Solana launchpad —— 三条都 `chains=[]`）

**链命中**：Ethereum=1895 · Binance=1145 · Arbitrum=1045 · Base=915 · Solana=466 · Optimism=393 · Robinhood Chain=296 · Hyperliquid L1=212 · Ink=33 · BSC=0 · OP Mainnet=0

**单侧读数：加密侧 1 / AI 侧 0** —— 本源只有加密侧，这 1 条不构成 AI 方向的任何证据。

**判据读数（结构性，非本轮故障）**：全量 `chains=[]` 占 1541/8880 = 17.4%，但**近 3 天登记的 58 条里 38 条 `chains=[]`，占 65.5%** —— 新上架协议越来越不带链字段，链白名单这道漏斗对新登记的杀伤在放大。本轮 `OmenX`（预测市场 CLOB）、`OTC`（Solana launchpad）、`StonkDrop`（Robinhood Chain 抽奖）三条有实际业务描述却全被空 `chains` 挡掉。继续观察，若连续几轮保持这个比例，需议是否给空 `chains` 开一条旁路。
