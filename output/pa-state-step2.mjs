// Append this run's attribution + supply-side findings to state.
import fs from 'node:fs';
const P = 'memory/topics/price-alert-state.json';
const st = JSON.parse(fs.readFileSync(P, 'utf8'));
const NOW = '2026-10-25T02:05:00Z';

st.deepest_pool_activity = {
  window: 'blk 53050450 -> 53052250 (01:04:07Z .. 02:04:07Z)',
  swap_events: 6,
  family: 'Solidly (Aerodrome classic) - Swap topic0 0xb3e27736...(full 64 hex)',
  buy_tx_count: 1,
  sell_tx_count: 5,
  deus_bought: 76803.0955,
  deus_sold: 13125.8425,
  net_deus_into_pool: -63677.253,
  reserves_ts_before: '2026-10-24T23:52:37Z',
  reserves_ts_after: '2026-10-25T01:41:33Z',
  observed_at: NOW,
  read: 'THE DEAD HOUR ENDED. The prior run measured a genuine zero-swap hour; this hour has 6 swaps and NET DEUS OUT of the pool (-63,677). That is the first net-withdrawal hour in the recorded series and it is the direction that RAISES the mark. Note the one buy is NOT a directional EOA position - see sweep_0145z.'
};

st.sweep_0145z = {
  observed_at: NOW,
  what: 'THE HOUR\'S LARGEST PRINT IS A MULTI-VENUE SWEEP THAT WAS PARKED IN A CONTRACT, NOT TAKEN INTO A POSITION.',
  tx: '0x53d72487d63c99679737551639f2f6b55c866a9ee7c672bdac76a9576460cd90',
  block: 53051313,
  ts: '2026-10-25T01:32:53Z',
  payer: '0xcdfd73794ec9d9b56c24f26dd21956dcb6e7ef82',
  payer_kind: 'plain EOA, nonce 11562, pays gas only',
  route: 'payer -> ERC-4337 EntryPoint 0x5ff137d4 -> sink 0x7d683941 -> executor 0x92325e5a',
  legs: {
    '0x58dBa34e (DEUS/USDC V3)': 16403.7822,
    '0x498581ff (Uniswap v4)': 3986.362,
    '0x1B2f3f5C (DEUS/USDC V3)': 10215.2829,
    '0x75bc1495 (DEUS/USDC V3)': 3982.6615,
    '0x3E97c5EC (deepest DEUS/VIRTUAL)': 76803.0955
  },
  total_deus: 111385.0628,
  endpoint_check: 'Sink 0x7d683941: balance EXACTLY 0.0000 before and after (pass-through). Executor 0x92325e5a: DEUS 0.0000 before the sweep -> 118,288.5940 now (111,385.06 from this sweep + 6,903.53 at blk 53051383), and ZERO outgoing DEUS transfers since. Payer EOA 0xcdfd7379: 0.0000 at -24h, before, and now.',
  read: 'THIS IS NOT NEW MONEY AND NOT A HELD POSITION. 111,385 DEUS bid across five venues and the entire amount came to rest inside 0x92325e5a - the IPSEITY/vault executor that also ran the 101,983 DEUS five-pool DUMP at 2026-10-24 15:53:59Z. One contract is now warehousing DEUS bought across venues and sitting on it (zero outflows). Treat it as an inventory build by a market maker, not a directional whale. TELL 8 (new money must be held by the payer) FAILS here: the payer ended at 0 and never held the coin.',
  prior_relationship: 'Same executor 0x92325e5a executed yesterday\'s 101,983.484653 DEUS record aggregator DUMP (outer tx 0x428bbb417b, EntryPoint 0x5ff137d4, router 0x11111605). It also received 65,552.78 DEUS from 1inch router 0x1111111254 at blk 52985282. So the SAME contract has been on BOTH sides of this book within 11 hours - bought 111k here, dumped 102k yesterday.',
  implication: 'Because the executor now shows zero outgoing DEUS, this inventory has not been re-offered yet. But it is a KNOWN dump venue: if it unwinds 118,288 DEUS the way it did yesterday\'s 101,983, that is a ~-0.7% to -0.9% single-block event. Watch 0x92325e5a for any DEUS transfer OUT as the next bearish tell.'
};

st.seller_0x96949fd5_0145z = {
  observed_at: NOW,
  wallet: '0x96949fd549d0da5ca279662264085a93138bdb17',
  what: 'The only sustained seller of the hour: THREE identical 2,899.5937 DEUS sells into the deepest pool at blk 53051420 / 53051493 / 53051573 (01:36:27Z, 01:38:53Z, 01:41:33Z), each with a 28.9959 fee to 0x205db642.',
  total_sold_1h: 8698.7811,
  pattern: 'SAME exact size three times in 5 minutes = an automated clip, not a decision. nonce 16675 -> 16678.',
  funding: 'Received 42,521.2837 DEUS at blk 53051528 (01:41:33Z) from 0x4e3ae00e8323558fa5cac04b152238924aa31b60 - an EOA holding 8,070,712.23 DEUS (nonce 2,562,393, ETH 428.53).',
  funder_profile: '0x4e3ae00e is a WHOLESALE-SCALE DEUS holder: 7,892,149.97 at -90d, 8,621,345.61 at -30d, 8,231,273.55 at -7d, 8,127,671.11 at -24h, 8,070,712.23 now. It is SLOWLY DRAINING (~50k/day over 7d), and it paid 11,599.66 to 0xf8d7467c and 42,521.28 to this seller within the hour. That is 0.9% of total supply in one EOA and it is distributing.',
  read: 'The hourly sell is a distribution clip fed by a 8.07M-DEUS wholesaler, not an independent retail seller. Balance trajectory of the seller: 13,778.66 at -24h/-6h -> 7,972.74 at -1h -> 41,795.24 now. It is being topped up faster than it sells, so its selling is RATE-LIMITED BY THE FUNDER, not by its own inventory. Whoever controls 0x4e3ae00e sets the pace of the next leg down.'
};

fs.writeFileSync(P, JSON.stringify(st, null, 2) + '\n');
console.log('STATE_WRITTEN step2');
