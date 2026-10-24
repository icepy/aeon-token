const RPC = 'https://base.gateway.tenderly.co';
const head = 53041380, dayAgo = 52998180;
const ESCROW = '0xA85A38796B951CE87B378538b32B3E6Ee3C4C373';
const CLAIM = '0x5cbF5DFAa5336ce0456e24217e7911365100879a';
const XDEUS = '0xe6d5f7434b1e3b3d1c8af25b6b9f7a5f6f0e2e2e'; // placeholder, resolved below
const DEUS = '0x940A319B75861014A220D9c6c144d108552B089B';

async function post(body) {
  const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  return r.json();
}
const bal = (to, data, blk) => post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to, data }, '0x' + blk.toString(16)] });
const pad = (a) => '0x000000000000000000000000' + a.slice(2).toLowerCase();
const u = (j) => (j.result ? Number(BigInt(j.result)) / 1e18 : 'ERR ' + JSON.stringify(j.error));
(async () => {
  const out = {};
  // DEUS balances of escrow and claim vault, now + 24h ago
  out.escrow_now = u(await bal(DEUS, '0x70a08231' + pad(ESCROW).slice(2), head));
  out.escrow_24h = u(await bal(DEUS, '0x70a08231' + pad(ESCROW).slice(2), dayAgo));
  out.claim_now = u(await bal(DEUS, '0x70a08231' + pad(CLAIM).slice(2), head));
  out.claim_24h = u(await bal(DEUS, '0x70a08231' + pad(CLAIM).slice(2), dayAgo));
  out.deus_total_supply = u(await bal(DEUS, '0x18160ddd', head));
  out.deus_total_supply_24h = u(await bal(DEUS, '0x18160ddd', dayAgo));
  console.log(JSON.stringify(out, null, 2));
})();
