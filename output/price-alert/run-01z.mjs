// price-alert measurement, 2026-10-25 01:0xZ run
const RPC = 'https://base.gateway.tenderly.co';
const DEEP = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa';
const VIRTUAL = '0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b';
const USDC = '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913';
const VP = [
  '0x7CB770D0513c30e0CB45E4899e4a2CbEEd6F9830',
  '0x529d2863a1521d0b57db028168fdE2E97120017C',
];
const Q192 = 2n ** 192n;

async function post(body) {
  for (let i = 0; i < 5; i++) {
    try {
      const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const j = await r.json();
      if (j.error) { await new Promise((s) => setTimeout(s, 500 * 2 ** i)); continue; }
      return j;
    } catch (e) { await new Promise((s) => setTimeout(s, 500 * 2 ** i)); }
  }
  return null;
}
const hex = (n) => '0x' + n.toString(16);
const call = async (to, data, blk) => {
  const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to, data }, hex(blk)] });
  if (!j) return null;
  if (j.error) return { err: j.error.message };
  return j.result;
};
const blkAt = async (n) => {
  const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getBlockByNumber', params: [hex(n), false] });
  return j && j.result ? Number(BigInt(j.result.timestamp)) : null;
};

// binary search block whose timestamp <= target
async function findBlock(target, lo, hi) {
  let a = lo, b = hi;
  while (a < b) {
    const mid = Math.floor((a + b + 1) / 2);
    const t = await blkAt(mid);
    if (t === null) throw new Error('block fetch fail ' + mid);
    if (t <= target) a = mid; else b = mid - 1;
  }
  return a;
}

const word = (r, i) => '0x' + r.slice(2 + i * 64, 2 + (i + 1) * 64);

(async () => {
  const head = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getBlockByNumber', params: ['latest', false] });
  const HEAD = Number(BigInt(head.result.number));
  const HEAD_TS = Number(BigInt(head.result.timestamp));
  console.log('HEAD', HEAD, new Date(HEAD_TS * 1000).toISOString());

  const b1 = await findBlock(HEAD_TS - 3600, HEAD - 6000, HEAD);
  const b24 = await findBlock(HEAD_TS - 86400, HEAD - 120000, HEAD);
  const t1 = await blkAt(b1), t24 = await blkAt(b24);
  console.log('h1 block', b1, new Date(t1 * 1000).toISOString(), 'dt', HEAD_TS - t1);
  console.log('h24 block', b24, new Date(t24 * 1000).toISOString(), 'dt', HEAD_TS - t24);

  // deep pool reserves
  const res = {};
  for (const [k, b] of Object.entries({ now: HEAD, h1: b1, h24: b24 })) {
    const r = await call(DEEP, '0x0902f1ac', b);
    if (!r || r.err) { res[k] = 'ERR:' + JSON.stringify(r); continue; }
    const r0 = BigInt(word(r, 0)), r1 = BigInt(word(r, 1)), ts = BigInt(word(r, 2));
    res[k] = { virtual: Number(r0) / 1e18, deus: Number(r1) / 1e18, ts: Number(ts) };
  }
  console.log('DEEP_RESERVES', JSON.stringify(res));

  // VIRTUAL/USD from V3 pools
  const vp = {};
  for (const p of VP) {
    const t0 = await call(p, '0x0dfe1681', HEAD);
    const t1r = await call(p, '0xd21220a7', HEAD);
    const a0 = '0x' + t0.slice(-40), a1 = '0x' + t1r.slice(-40);
    const invert = a0 === USDC && a1 === VIRTUAL;
    if (!(a0 === VIRTUAL && a1 === USDC) && !invert) { console.log(p, 'NOT VIRTUAL/USDC', a0, a1); continue; }
    const out = {};
    for (const [k, b] of Object.entries({ now: HEAD, h1: b1, h24: b24 })) {
      const s = await call(p, '0x3850c7bd', b);
      if (!s || s.err) { out[k] = 'ERR'; continue; }
      const sq = BigInt(word(s, 0));
      const raw = Number(sq * sq) / Number(Q192);
      out[k] = invert ? +(1 / (raw * (1e6 / 1e18))).toFixed(8) : +(raw * (1e18 / 1e6)).toFixed(8);
    }
    vp[p] = { invert, out };
    console.log('VP', p, JSON.stringify(vp[p]));
  }
  // summary mark
  const mean = (o) => {
    const vals = Object.values(o).map((v) => v.out);
    return vals;
  };
  console.log('SUMMARY_BLOCKS', JSON.stringify({ head: HEAD, h1: b1, h24: b24 }));
})();
