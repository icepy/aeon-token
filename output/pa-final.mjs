// Final numbers: exact swap-block timestamps, executor in/out since sweep, mark math, gate distances.
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
const DEUS = '0x940A319B75861014A220D9c6c144d108552B089B';
const EXEC = '0x92325e5ac24ec4d8d0032cf4cb37b080f4a6374f';
const head = dec(await rpc('eth_blockNumber', []));

const BLKS = [53051313, 53051339, 53051420, 53051493, 53051573];
for (const b of BLKS) {
  const r = await rpc('eth_getBlockByNumber', [hex(b), false]);
  console.log('blk', b, new Date(dec(r.timestamp) * 1000).toISOString());
}

// executor: all DEUS transfers since sweep (in AND out)
const TR = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const toTopic = '0x' + pad(EXEC);
let inSum = 0, outSum = 0, inN = 0, outN = 0;
for (let s = 53051313; s <= head; s += 900) {
  const e = Math.min(s + 899, head);
  const r = await rpc('eth_getLogs', [{ address: DEUS, topics: [TR, null, toTopic], fromBlock: hex(s), toBlock: hex(e) }]);
  if (Array.isArray(r)) for (const l of r) { const v = Number(BigInt(l.data)) / 1e18; if (v > 1) { inSum += v; inN++; if (inN <= 6) console.log('  EXEC IN', v.toFixed(4), 'blk', dec(l.blockNumber), l.transactionHash.slice(0, 12)); } }
  await new Promise((x) => setTimeout(x, 110));
}
console.log('EXECUTOR incoming >1 DEUS since sweep: n=' + inN, 'sum=' + inSum.toFixed(4));
console.log('EXECUTOR outgoing >1 DEUS since sweep: n=0 (verified in pa-attr2)');

// mark
const VIRTUAL_USD_DEEP_WETH = 0.6283;   // 0x792f465e, liq $2.14M
const VIRTUAL_USD_USDC = 0.6289;        // 0x529d2863, liq $752k
const resV = 525651.4765648125, resD = 18944498.344048623;
const ratio = resV / resD;
for (const [tag, v] of [['deepWETH', VIRTUAL_USD_DEEP_WETH], ['USDC', VIRTUAL_USD_USDC]]) {
  console.log('MARK via VIRTUAL/' + tag, '$' + (ratio * v).toFixed(8));
}
const mark = ratio * VIRTUAL_USD_DEEP_WETH;
console.log('RATIO', ratio.toFixed(9));

const TARGETS = [0.012, 0.025, 0.032, 0.041];
for (const t of TARGETS) console.log('target', t, 'distance_pct', ((t / mark - 1) * 100).toFixed(2));
console.log('ATH_DISTANCE_PCT', ((0.06876 / mark - 1) * 100).toFixed(2));

// level math x*y=k
const D = resD;
for (const t of TARGETS) {
  const rTgt = t / VIRTUAL_USD_DEEP_WETH;
  const dNew = D * Math.sqrt(ratio / rTgt);
  const delta = dNew - D;
  console.log('level', t, delta > 0 ? 'net SELL' : 'net BUY', Math.abs(delta).toFixed(0), 'DEUS', '= $' + (Math.abs(delta) * mark).toFixed(0),
    'pct_of_pool', ((Math.abs(delta) / D) * 100).toFixed(1));
}
