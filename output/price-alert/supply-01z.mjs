// escrow + xDEUS pending-unstake trigger check
const RPC = 'https://base.gateway.tenderly.co';
const ESCROW = '0xA85A38796B951CE87B378538b32B3E6Ee3C4C373';
const XDEUS = '0xe6d5f7439Bc236C40054e2275f765f59343D4431';
const DEUS = '0x940A319B75861014A220D9c6c144d108552B089B';
const WATCH = '0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63';
const HEAD = 53050396, H24 = 53007196;

async function post(body) {
  for (let i = 0; i < 5; i++) {
    try {
      const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const j = await r.json();
      if (j.error) { await new Promise((s) => setTimeout(s, 500 * 2 ** i)); continue; }
      return j;
    } catch { await new Promise((s) => setTimeout(s, 500 * 2 ** i)); }
  }
  return { error: { message: 'rpc-fail' } };
}
const hex = (n) => '0x' + n.toString(16);
const pad = (a) => a.toLowerCase().replace(/^0x/, '').padStart(64, '0');
const call = async (to, data, blk) => {
  const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to, data }, hex(blk)] });
  if (!j) return null;
  return j.error ? { err: j.error.message } : j.result;
};
const uint = (r) => (r && !r.err ? Number(BigInt(r)) : null);
const bal = (tok, who, blk) => call(tok, '0x70a08231' + pad(who), blk);
(async () => {
  const eNow = uint(await bal(DEUS, ESCROW, HEAD));
  const e24 = uint(await bal(DEUS, ESCROW, H24));
  const xNow = uint(await call(XDEUS, '0x18160ddd', HEAD));
  const x24 = uint(await call(XDEUS, '0x18160ddd', H24));
  const wDeus = uint(await bal(DEUS, WATCH, HEAD));
  const wX = uint(await bal(XDEUS, WATCH, HEAD));
  const nft = await call(XDEUS, '0x2f745c59' + pad(WATCH) + pad('0'), HEAD);
  console.log(JSON.stringify({
    escrow_now: eNow / 1e18,
    escrow_24h: e24 / 1e18,
    escrow_delta_24h: (eNow - e24) / 1e18,
    escrow_delta_pct: (((eNow / e24) - 1) * 100).toFixed(4),
    five_pct_line: (eNow * 0.05 / 1e18),
    pressure_ratio: (Math.abs(eNow - e24) / (eNow * 0.05)).toFixed(4),
    xdeus_now: xNow, xdeus_24h: x24, xdeus_delta: xNow - x24,
    watch_deus: wDeus / 1e18, watch_xdeus_balance: wX,
    watch_tokenid: nft && !nft.err ? Number(BigInt(nft)) : (nft && nft.err) || 'ERR',
  }, null, 1));
  // escrow burns/stakes in the last hour
  const BURN = '0xe08737ac48a1dab4b1a46c7dc9398bd5bfc6d7ad6fabb7cd8caa254de14def35';
  const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getLogs', params: [{ address: ESCROW, fromBlock: hex(HEAD - 1900), toBlock: hex(HEAD), topics: [BURN] }] });
  console.log('BURNS_1H', j.error ? 'ERR:' + j.error.message : j.result.length);
  if (!j.error) for (const l of j.result) {
    const w = l.data.slice(2).match(/.{64}/g).map((x) => BigInt('0x' + x));
    console.log(' burn tokenId', Number(BigInt(l.topics[2])), 'owner', '0x' + l.topics[1].slice(-40), 'deus', Number(w[0]) / 1e18, 'ts', Number(w[1]));
  }
})();
