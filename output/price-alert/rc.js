const RPC = 'https://base.gateway.tenderly.co';
const TX = '0x8897062a3f6cadfa5efe8c75af1f27248838ed5fbce7bf783071c14aee62545d';
async function post(body) {
  for (let i = 0; i < 5; i++) {
    const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const j = await r.json();
    if (j.error || j.result === null) { console.log('retry', i, JSON.stringify(j.error || 'null result')); await new Promise((s) => setTimeout(s, 1000 * 2 ** i)); continue; }
    return j;
  }
  throw new Error('fail');
}
(async () => {
  const rc = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getTransactionReceipt', params: [TX] });
  console.log(JSON.stringify({ from: rc.result.from, to: rc.result.to, status: rc.result.status, block: parseInt(rc.result.blockNumber, 16) }));
})();
