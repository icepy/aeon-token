// Binary-search Base for the block whose timestamp is <= targetTs, using eth_getBlockByNumber.
const RPC = 'https://base.gateway.tenderly.co';
const target = Number(process.argv[2]); // unix seconds

async function blk(n) {
  const r = await fetch(RPC, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0', id: 1, method: 'eth_getBlockByNumber',
      params: ['0x' + n.toString(16), false],
    }),
  });
  const j = await r.json();
  if (!j.result) throw new Error('no result: ' + JSON.stringify(j));
  return { n, ts: parseInt(j.result.timestamp, 16) };
}

(async () => {
  const hn = await fetch(RPC, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'eth_blockNumber', params: [] }),
  }).then((r) => r.json());
  let hi = parseInt(hn.result, 16);
  let lo = hi - 4000;
  // ensure lo.ts < target < hi.ts
  let H = await blk(hi);
  if (H.ts <= target) { console.log(JSON.stringify(H)); return; }
  let L = await blk(lo);
  while (L.ts > target) { lo -= 4000; L = await blk(lo); }
  while (hi - lo > 1) {
    const mid = Math.floor((lo + hi) / 2);
    const M = await blk(mid);
    if (M.ts <= target) { lo = mid; L = M; } else { hi = mid; }
  }
  const out = await blk(lo);
  console.log(JSON.stringify({ block: out.n, ts: out.ts, iso: new Date(out.ts * 1000).toISOString(), target_iso: new Date(target * 1000).toISOString(), drift_s: target - out.ts }));
})();
