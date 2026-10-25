// Pending-unstake #1396 trigger check + precise mark + gate math.
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
const XDEUS = '0xe6d5f7439Bc236C40054e2275f765f59343D4431';
const PENDING = '0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63';
const head = dec(await rpc('eth_blockNumber', []));

const bal = await rpc('eth_call', [{ to: XDEUS, data: '0x70a08231' + pad(PENDING) }, hex(head)]);
console.log('PENDING xDEUS balance', dec(bal));
if (dec(bal) > 0) {
  const tok = await rpc('eth_call', [{ to: XDEUS, data: '0x2f745c59' + pad(PENDING) + pad('0x0') }, hex(head)]);
  console.log('  tokenOfOwnerByIndex(0) =', dec(tok));
}
const ts = await rpc('eth_call', [{ to: XDEUS, data: '0x18160ddd' }, hex(head)]);
console.log('xDEUS totalSupply', dec(ts));

// precise mark: ratio x mean of two live VIRTUAL/USDC pools
const resR0 = 525651.4765648125, resR1 = 18944498.344048623;
const ratio = resR0 / resR1;
const v1 = 0.6287, v2 = 0.6289;      // 0x7CB770D0 / 0x529d2863 (DexScreener, same print window)
const vDeep = 0.6283;                 // 0x792f465e deepest VIRTUAL/WETH
const vMean = (v1 + v2) / 2;
const MARK = ratio * vMean;
console.log('ratio', ratio.toFixed(10), 'VIRTUAL/USDC mean', vMean, 'MARK', MARK.toFixed(9));
console.log('cross-check deepWETH mark', (ratio * vDeep).toFixed(9));

const T = [0.012, 0.025, 0.032, 0.041];
for (const t of T) console.log('target', t, 'dist', ((t / MARK - 1) * 100).toFixed(2) + '%');

// h1 USD: ratio chg + VIRTUAL chg
const ratioPrev = 523886.9302269761 / 19008306.855478093;
console.log('ratio h1 chg pct', ((ratio / ratioPrev - 1) * 100).toFixed(4));
const virtualH1 = -0.23; // deepest live VIRTUAL/WETH h1
console.log('h1 USD approx', (((ratio / ratioPrev - 1) * 100) + virtualH1).toFixed(4));
const virtualH24 = -2.4;
const ratioH24 = 0.3018;
console.log('h24 USD approx', (ratioH24 + virtualH24).toFixed(4));
