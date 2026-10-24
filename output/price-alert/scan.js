// Scan Solidly Swap logs for the deepest DEUS/VIRTUAL pool over [from,to] in <=1000-block windows.
const RPC = 'https://base.gateway.tenderly.co';
const POOL = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa';
const TOPIC0 = '0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b';
const from = Number(process.argv[2]);
const to = Number(process.argv[3]);

async function post(body) {
  for (let i = 0; i < 4; i++) {
    const r = await fetch(RPC, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const j = await r.json();
    if (j.error) { await new Promise((s) => setTimeout(s, 1000 * 2 ** i)); continue; }
    return j;
  }
  throw new Error('rpc failed ' + JSON.stringify(body));
}

(async () => {
  let all = [];
  for (let a = from; a <= to; a += 1000) {
    const b = Math.min(a + 999, to);
    const j = await post({
      jsonrpc: '2.0', id: 1, method: 'eth_getLogs',
      params: [{ address: POOL, topics: [TOPIC0], fromBlock: '0x' + a.toString(16), toBlock: '0x' + b.toString(16) }],
    });
    if (!j.result) throw new Error(JSON.stringify(j));
    // print error object if present, per lesson: never read a zero without checking .error
    all = all.concat(j.result);
  }
  const dec = (x) => Number(BigInt('0x' + x)) / 1e18;
  let buys = 0, sells = 0, buyDeus = 0, sellDeus = 0;
  const rows = [];
  for (const l of all) {
    const d = l.data.slice(2);
    const words = [];
    for (let i = 0; i < d.length; i += 64) words.push(d.slice(i, i + 64));
    // layout empirically fixed: (amount0In, amount1In, amount0Out, amount1Out)
    const a0in = dec(words[0]), a1in = dec(words[1]), a0out = dec(words[2]), a1out = dec(words[3]);
    // token0=VIRTUAL, token1=DEUS. amount1Out>0 => taker BOUGHT DEUS out of pool.
    const boughtDeus = a1out > 0;
    if (boughtDeus) { buys++; buyDeus += a1out; } else { sells++; sellDeus += a1in; }
    rows.push({
      blk: parseInt(l.blockNumber, 16),
      tx: l.transactionHash,
      side: boughtDeus ? 'BUY' : 'SELL',
      deus: boughtDeus ? a1out : a1in,
      virtual: boughtDeus ? a0in : a0out,
    });
  }
  rows.sort((x, y) => x.blk - y.blk);
  console.log(JSON.stringify({
    pool: POOL, from, to, window_blocks: to - from + 1,
    swap_count: all.length, buys, sells,
    deus_bought: +buyDeus.toFixed(4), deus_sold: +sellDeus.toFixed(4),
    net_deus_into_pool: +(sellDeus - buyDeus).toFixed(4),
    largest: rows.slice().sort((x, y) => y.deus - x.deus).slice(0, 5),
    rows,
  }, null, 2));
})();
