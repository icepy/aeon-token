// Block-pinned 24h move + seller funding source identity.
const RPCS = ['https://base.gateway.tenderly.co', 'https://mainnet.base.org'];
let ep = 0;
const pad = (a) => a.replace(/^0x/, '').toLowerCase().padStart(64, '0');
async function rpc(method, params) {
  for (let i = 0; i < 5; i++) {
    try {
      const r = await fetch(RPCS[ep], {
        method: 'POST', headers: { 'content-type': 'application/json' },
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
const hex = (n) => '0x' + n.toString(16);
const dec = (h) => (h ? Number(BigInt(h)) : NaN);
const bi = (h) => BigInt(h.startsWith('0x') ? h : '0x' + h);
const POOL = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa';
const head = dec(await rpc('eth_blockNumber', []));
const hb = await rpc('eth_getBlockByNumber', [hex(head), false]);
const headTs = dec(hb.timestamp);

// exact 86400s back
let lo = head - 50000, hi = head;
while (lo < hi) {
  const mid = Math.floor((lo + hi) / 2);
  const b = await rpc('eth_getBlockByNumber', [hex(mid), false]);
  if (dec(b.timestamp) < headTs - 86400) lo = mid + 1; else hi = mid;
}
const b24 = lo;
const b24b = await rpc('eth_getBlockByNumber', [hex(b24), false]);
console.log('24H_BLK', b24, new Date(dec(b24b.timestamp) * 1000).toISOString(), 'delta_s', headTs - dec(b24b.timestamp));

async function reserves(blk) {
  const r = await rpc('eth_call', [{ to: POOL, data: '0x0902f1ac' }, hex(blk)]);
  const d = r.slice(2);
  return { r0: bi(d.slice(0, 64)), r1: bi(d.slice(64, 128)) };
}
const n = await reserves(head), p = await reserves(b24);
const rN = Number(n.r0) / Number(n.r1), rP = Number(p.r0) / Number(p.r1);
console.log('ratio now', rN.toFixed(9), '24h ago', rP.toFixed(9), 'RATIO_CHG_PCT', ((rN / rP - 1) * 100).toFixed(4));
console.log('DEUS in pool now', Number(n.r1) / 1e18, '24h ago', Number(p.r1) / 1e18, 'net', ((Number(n.r1) - Number(p.r1)) / 1e18).toFixed(2));
console.log('VIRTUAL in pool now', Number(n.r0) / 1e18, '24h ago', Number(p.r0) / 1e18);

// VIRTUAL/USD 24h ago from DexScreener h24 on the deepest VIRTUAL pools
(async () => {
  const j = await fetch('https://api.dexscreener.com/latest/dex/tokens/0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b').then(r => r.json()).catch(() => null);
  if (j?.pairs) {
    const keep = j.pairs.filter(p => p.chainId === 'base' && (p.quoteToken.symbol === 'USDC' || p.quoteToken.symbol === 'WETH') && p.priceUsd && p.priceChange?.h24 != null)
      .sort((a, b) => (b.liquidity?.usd || 0) - (a.liquidity?.usd || 0)).slice(0, 5);
    for (const p of keep) console.log('VIRTUAL', p.baseToken.symbol + '/' + p.quoteToken.symbol, 'px=' + p.priceUsd, 'h24=' + p.priceChange.h24, 'liq=' + Math.floor(p.liquidity.usd), p.pairAddress);
    const med = keep.map(p => Number(p.priceChange.h24)).sort((a, b) => a - b);
    console.log('VIRTUAL h24 median', med[Math.floor(med.length / 2)]);
  }
})();

// seller funding source identity
const SRC = '0x4e3ae00e8323558fa5cac04b152238924aa31b60';
const code = await rpc('eth_getCode', [SRC, 'latest']);
console.log('\nFUNDER', SRC, 'code', code === '0x' ? 'EOA' : 'CONTRACT len=' + (code.length - 2) / 2);
for (const fn of [['name', '0x06fdde03'], ['symbol', '0x95d89b41']]) {
  const r = await rpc('eth_call', [{ to: SRC, data: fn[1] }, 'latest']);
  console.log(' ', fn[0], r && r !== '0x' ? Buffer.from(r.slice(130), 'hex').toString().replace(/\0/g, '') : 'n/a');
}
// does the funder still hold DEUS? what's its role?
const bal = await rpc('eth_call', [{ to: '0x940A319B75861014A220D9c6c144d108552B089B', data: '0x70a08231' + pad(SRC) }, hex(head)]);
console.log('  DEUS balance now', (Number(BigInt(bal)) / 1e18).toFixed(4));
