const RPC = 'https://base.gateway.tenderly.co';
const DEUS = '0x940A319B75861014A220D9c6c144d108552B089B';
const W = '0xe338adc6c0fb242ca5bb2711c7f789c24486e61d';
const head = 53041380;
const T = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const pad = (a) => '0x000000000000000000000000' + a.slice(2).toLowerCase();

async function logs(params) {
  for (let i = 0; i < 4; i++) {
    const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'eth_getLogs', params: [params] }) });
    const j = await r.json();
    if (j.error) { await new Promise((s) => setTimeout(s, 1000 * 2 ** i)); continue; }
    return j.result;
  }
  return null;
}
async function page(topics, from, to) {
  let out = [], fails = 0;
  for (let a = from; a <= to; a += 1000) {
    const b = Math.min(a + 999, to);
    const r = await logs({ address: DEUS, topics, fromBlock: '0x' + a.toString(16), toBlock: '0x' + b.toString(16) });
    if (r === null) { fails++; continue; }
    out = out.concat(r);
  }
  return { logs: out, failed_windows: fails };
}
(async () => {
  const span = 30000;
  const inc = await page([T, null, pad(W)], head - span, head);
  const out = await page([T, pad(W)], head - span, head);
  console.log(JSON.stringify({
    failed_windows: inc.failed_windows + out.failed_windows,
    incoming: inc.logs.map((l) => ({ blk: parseInt(l.blockNumber, 16), from: '0x' + l.topics[1].slice(-40), deus: Number(BigInt(l.data)) / 1e18 })),
    outgoing: out.logs.map((l) => ({ blk: parseInt(l.blockNumber, 16), to: '0x' + l.topics[2].slice(-40), deus: Number(BigInt(l.data)) / 1e18 })),
  }, null, 2));
})();
