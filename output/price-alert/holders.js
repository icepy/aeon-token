const RPC = 'https://base.gateway.tenderly.co';
const XDEUS = '0xe6d5f7439Bc236C40054e2275f765f59343D4431';
const DEUS = '0x940A319B75861014A220D9c6c144d108552B089B';
const head = 53041380;
const W = {
  '0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63': 'record unstaker (holds #1396?)',
  '0x9d1c316f1f307894c80e7d2963454e6342c8e0a9': 'fresh directional buyer',
  '0x7f6aba7563cb5d31980d440337d3d1a6e3db58f3': 'largest new-money buyer',
  '0x6a45ca8bb30f396f40721e105e0aa6cabf326657': 'second new-money buyer',
  '0xf0a04b079dcf7b9d92682123ba2e2180109cb650': 'incumbent trimmer 250k',
};
const pad = (a) => '0x000000000000000000000000' + a.slice(2).toLowerCase();
async function post(body) {
  for (let i = 0; i < 3; i++) {
    const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const j = await r.json();
    if (j.error) { await new Promise((s) => setTimeout(s, 700)); continue; }
    return j;
  }
  return null;
}
(async () => {
  const out = {};
  for (const [a, label] of Object.entries(W)) {
    const d = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to: DEUS, data: '0x70a08231' + pad(a).slice(2) }, '0x' + head.toString(16)] });
    const n = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to: XDEUS, data: '0x70a08231' + pad(a).slice(2) }, '0x' + head.toString(16)] });
    out[a] = {
      label,
      deus: d && d.result ? Number(BigInt(d.result)) / 1e18 : 'ERR',
      xdeus_nfts: n && n.result ? parseInt(n.result, 16) : 'ERR',
    };
    if (n && n.result && parseInt(n.result, 16) > 0) {
      const t = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to: XDEUS, data: '0x2f745c59' + pad(a).slice(2) + '0'.repeat(64) }, '0x' + head.toString(16)] });
      out[a].token0 = t && t.result ? parseInt(t.result, 16) : 'ERR';
    }
  }
  console.log(JSON.stringify(out, null, 2));
})();
