const RPC = 'https://base.gateway.tenderly.co';
const txs = [
  '0x54113567f99967e52900b94c01c88514f3351ba4a679ee9dfb251074facae05d',
  '0x480bea69de58be2baf8b3696fd0fb4930063d24225d9f37d767c6e986e86c605',
  '0x5bfb4328ab33498591952f71eee333f73b806598e4080d0954adcc93dae0ea5c',
  '0x6779c1ed761b0a63e44f229a56c4cf549ad39d2a67c599690e8b37834fb06012',
];
async function post(body) {
  const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  return r.json();
}
(async () => {
  for (const t of txs) {
    const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getTransactionByHash', params: [t] });
    const x = j.result;
    const blk = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getBlockByNumber', params: [x.blockNumber, false] });
    console.log(JSON.stringify({
      tx: t.slice(0, 12), from: x.from, to: x.to,
      blk: parseInt(x.blockNumber, 16),
      ts: new Date(parseInt(blk.result.timestamp, 16) * 1000).toISOString(),
      selector: x.input.slice(0, 10), input_len: x.input.length,
      nonce: parseInt(x.nonce, 16),
    }));
  }
  // control: wrong topic0 (one char off) over same window must return 0
  const wrong = '0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75c';
  const c = await post({
    jsonrpc: '2.0', id: 1, method: 'eth_getLogs',
    params: [{ address: '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa', topics: [wrong], fromBlock: '0x32958d2', toBlock: '0x32958e4' }],
  });
  console.log('CONTROL_wrong_topic0 count=' + (c.result ? c.result.length : 'ERR:' + JSON.stringify(c.error)));
  const g = await post({
    jsonrpc: '2.0', id: 1, method: 'eth_getLogs',
    params: [{ address: '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa', topics: ['0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b'], fromBlock: '0x32958d2', toBlock: '0x32958e4' }],
  });
  console.log('CONTROL_right_topic0 count=' + (g.result ? g.result.length : 'ERR:' + JSON.stringify(g.error)));
})();
