V = 527414.139280572029731259
D = 18881184.226331996630621331
vp = 0.6155012
r = V / D
print('ratio %.9f mark %.9f' % (r, r * vp))

# 1h
V1 = 525727.752125275261972133
D1 = 18941749.768910564661785084
vp1 = 0.6160457
r1 = V1 / D1
print('1h ratio %.9f mark %.9f' % (r1, r1 * vp1))
print('h1 pct %.4f  vp chg %.4f  ratio chg %.4f' %
      ((r * vp) / (r1 * vp1) * 100 - 100, (vp / vp1 - 1) * 100, (r / r1 - 1) * 100))

# 24h
V24 = 521045.2904
D24 = 19111973.0063
vp24 = 0.6617060
r24 = V24 / D24
print('24h ratio %.9f mark %.9f' % (r24, r24 * vp24))
print('h24 pct %.4f vp chg %.4f ratio chg %.4f' %
      ((r * vp) / (r24 * vp24) * 100 - 100, (vp / vp24 - 1) * 100, (r / r24 - 1) * 100))
print('ath_dist %.2f' % ((r * vp) / 0.06876 * 100 - 100))
