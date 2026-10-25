// price-alert 2026-10-25T02:0xZ run — on-chain verification of the deepest-pool mark,
// exact-3600s h1, VIRTUAL/USD quote leg, and per-venue swap activity.
const RPCS = ['https://base.gateway.tenderly.co', 'https://mainnet.base.org'];
let ep = 0;
const pad = (a) => a.replace(/^0x/, '').toLowerCase().padStart(64, '0');

async function rpc(method, params) {
  for (let i = 0; i < 5; i++) {
    try {
      const r = await fetch(RPCS[ep], {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }),
      });
      const j = await r.json().catch(() => ({}));
      if (j.result !== undefined) return j.result;
    } catch (e) {}
    ep = (ep + 1) % RPCS.length;
    await new Promise((s) => setTimeout(s, 800 * 2 ** i));
  }
  return null;
}

const POOL = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa';
const DEUS = '0x940A319B75861014A220D9c6c144d108552B089B';
const ESCROW = '0xA85A38796B951CE87B378538b32B3E6Ee3C4C373';

const hex = (n) => '0x' + n.toString(16);
const dec = (h) => (h ? Number(BigInt(h)) : NaN);
const bi = (h) => BigInt(h.startsWith('0x') ? h : '0x' + h);

const head = dec(await rpc('eth_blockNumber', []));
const hb = await rpc('eth_getBlockByNumber', [hex(head), false]);
const headTs = dec(hb.timestamp);
console.log('HEAD', head, new Date(headTs * 1000).toISOString());

async function reserves(blk) {
  const r = await rpc('eth_call', [{ to: POOL, data: '0x0902f1ac' }, hex(blk)]);
  if (!r || r === '0x') return null;
  const d = r.slice(2);
  return { r0: bi(d.slice(0, 64)), r1: bi(d.slice(64, 128)), ts: bi(d.slice(128, 192)) };
}

// block ~3600s back
let lo = head - 4000, hi = head;
while (lo < hi) {
  const mid = Math.floor((lo + hi) / 2);
  const b = await rpc('eth_getBlockByNumber', [hex(mid), false]);
  if (dec(b.timestamp) < headTs - 3600) lo = mid + 1; else hi = mid;
}
const h1Blk = lo;
const h1b = await rpc('eth_getBlockByNumber', [hex(h1Blk), false]);
console.log('H1BLK', h1Blk, new Date(dec(h1b.timestamp) * 1000).toISOString(), 'delta_s', headTs - dec(h1b.timestamp));

const now = await reserves(head);
const prev = await reserves(h1Blk);
const iso = (s) => new Date(Number(s) * 1000).toISOString();
console.log('RESERVES_NOW VIRTUAL', Number(now.r0) / 1e18, 'DEUS', Number(now.r1) / 1e18, 'ts', iso(now.ts));
console.log('RESERVES_1H  VIRTUAL', Number(prev.r0) / 1e18, 'DEUS', Number(prev.r1) / 1e18, 'ts', iso(prev.ts));
const rNow = Number(now.r0) / Number(now.r1);   // VIRTUAL per DEUS
const rPrev = Number(prev.r0) / Number(prev.r1);
console.log('RATIO_VIRTUAL_PER_DEUS now', rNow.toFixed(9), '1h', rPrev.toFixed(9), 'chg_pct', ((rNow / rPrev - 1) * 100).toFixed(4));

// --- swap activity this hour, per venue --------------------------
const SOLIDLY_SWAP = '0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b';
const V3_SWAP = '0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67';
async function logs(addr, topic, from, to) {
  let out = [];
  for (let s = from; s <= to; s += 900) {
    const e = Math.min(s + 899, to);
    const r = await rpc('eth_getLogs', [{ address: addr, topics: [topic], fromBlock: hex(s), toBlock: hex(e) }]);
    if (Array.isArray(r)) out.push(...r);
    await new Promise((x) => setTimeout(x, 110));
  }
  return out;
}
const venues = [
  ['0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa', SOLIDLY_SWAP, 'deepest'],
  ['0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b', V3_SWAP, 'usdc-58db'],
  ['0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642', V3_SWAP, 'usdc-1b2f'],
  ['0x75bc14950Ab093cBd1f80BbbDf458596939180A3', V3_SWAP, 'usdc-75bc'],
];
const results = {};
for (const [addr, topic, label] of venues) {
  const r = await logs(addr, topic, h1Blk, head);
  results[label] = r;
  console.log('SWAPS_1H', label, 'n=' + r.length);
}

// discriminative control: prior 900-block window on the deepest pool
const ctrl = await logs('0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa', SOLIDLY_SWAP, head - 2700, head - 1801);
const ctrlBad = await rpc('eth_getLogs', [{
  address: '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa',
  topics: ['0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf76b'],
  fromBlock: hex(head - 2700), toBlock: hex(head - 1801),
}]);
console.log('CONTROL real_topic n=' + ctrl.length, 'wrong_topic n=' + (Array.isArray(ctrlBad) ? ctrlBad.length : 'ERR'));

// --- deepest-pool swap detail this hour --------------------------
const swaps = results.deepest.map((l) => {
  const d = l.data.slice(2);
  const a0In = bi(d.slice(0 * 64, 1 * 64));
  const a1In = bi(d.slice(1 * 64, 2 * 64));
  const a0Out = bi(d.slice(2 * 64, 3 * 64));
  const a1Out = bi(d.slice(3 * 64, 4 * 64));
  return { blk: dec(l.blockNumber), tx: l.transactionHash, deusOut: a1Out, deusIn: a1In, virtualIn: a0In, virtualOut: a0Out };
});
const buys = swaps.filter((s) => s.deusOut > 0n);
const sells = swaps.filter((s) => s.deusIn > 0n);
const sum = (arr, k) => arr.reduce((a, b) => a + b[k], 0n);
console.log('DEEPEST buys', buys.length, 'sells', sells.length,
  '| deus_bought', (Number(sum(buys, 'deusOut')) / 1e18).toFixed(4),
  '| deus_sold', (Number(sum(sells, 'deusIn')) / 1e18).toFixed(4));
for (const s of swaps.sort((a, b) => a.blk - b.blk)) {
  console.log('  ', s.deusOut > 0n ? 'BUY ' : 'SELL', s.blk, 'deus', (Number(s.deusOut + s.deusIn) / 1e18).toFixed(4), s.tx);
}

// --- escrow ------------------------------------------------------
async function balanceOf(token, who, blk) {
  const r = await rpc('eth_call', [{ to: token, data: '0x70a08231' + pad(who) }, hex(blk)]);
  return r ? Number(BigInt(r)) / 1e18 : NaN;
}
const escNow = await balanceOf(DEUS, ESCROW, head);
const esc24 = await balanceOf(DEUS, ESCROW, head - 43200);
console.log('ESCROW now', escNow, '24h', esc24, 'delta', (escNow - esc24).toFixed(6), 'pct', ((escNow / esc24 - 1) * 100).toFixed(4));

const BURN = '0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7ad6fabb7cd8caa254de14def35';
const b1 = await logs(ESCROW, BURN, h1Blk, head);
console.log('ESCROW_BURNS_1H', b1.length);

// --- DEUS/USD via VIRTUAL/USD from DexScreener (quote leg) --------
const vres = await fetch('https://api.dexscreener.com/latest/dex/tokens/0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b').then(r => r.json()).catch(() => null);
if (vres && vres.pairs) {
  const base = vres.pairs.filter(p => p.chainId === 'base' && p.priceUsd);
  base.sort((a, b) => (b.liquidity?.usd || 0) - (a.liquidity?.usd || 0));
  for (const p of base.slice(0, 4)) {
    console.log('VIRTUAL', p.baseToken.symbol + '/' + p.quoteToken.symbol, 'px=' + p.priceUsd, 'liq=' + p.liquidity?.usd, 'h1=' + p.priceChange?.h1);
  }
}
