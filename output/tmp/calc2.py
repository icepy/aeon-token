import json

d = json.load(open('output/tmp/slot0_usdc.json'))
print('err', d.get('error'))
s = d['result'][2:]
w = [int(s[i:i + 64], 16) for i in range(0, len(s), 64)]
print('words', w[:3])
sq = w[0]
p_usdc_per_deus_raw = (sq / 2 ** 96) ** 2  # token1(DEUS) per token0(USDC) raw units
# token0=USDC 6dp, token1=DEUS 18dp
# raw ratio = DEUS_raw/USDC_raw ; price USD per DEUS = (USDC_raw/DEUS_raw) adj decimals
usd_per_deus = 1 / p_usdc_per_deus_raw * 10 ** 6 / 10 ** 18 * 1
# careful: p = token1_raw/token0_raw
# USDC_raw per DEUS_raw = 1/p ; USD per DEUS = (1/p) * 10^-6 / 10^-18 = (1/p)*10^12
usd_per_deus = (1 / p_usdc_per_deus_raw) * 10 ** 12
print('mark_usd_from_usdc_pool %.7f' % usd_per_deus)
