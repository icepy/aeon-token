const RPC = 'https://base.gateway.tenderly.co';
const DEUS = '0x940A319B75861014A220D9c6c144d108552B089B';
const T = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const TXS = [
  '0x54113567f99967e52900b94c01c88514f3351ba4a679ee9dfb251074facae05d',
  '0x480bea69de58be2baf8b3696fd0fb4930063d24225d9f37d767c6e986e86c605',
  '0x5bfb4328ab33498591952f71eee333f73b806598e4080d0954adcc93dae0ea5c',
  '0x6779c1ed761b0a63e44f229a56c4cf549ad39d2a67c599690e8b37834fb06012',
];
async function post(body) {
  for (let i = 0; i < 4; i++) {
    const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const j = await r.json();
    if (j.error) { await new Promise((s) => setTimeout(s, 700 * 2 ** i)); continue; }
    return j;
  }
  return null;
}
(async () => {
  for (const t of TXS) {
    const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getLogs', params: [{ address: DEUS, topics: [T], fromBlock: '0x' + (53041367).toString(16), toBlock: '0x' + (53041377).toString(16) }] });
    if (!j) { console.log(t, 'ERR'); continue; }
    // filter to this tx
    const legs = j.result.filter((l) => l.transactionHash === t).map((l) => ({
      from: '0x' + l.topics[1].slice(-40),
      to: '0x' + l.topics[2].slice(-40),
      deus: +(Number(BigInt(l.data)) / 1e18).toFixed(4),
    }));
    console.log(JSON.stringify({ tx: t.slice(0, 12), legs }, null, 1));
  }
})();
