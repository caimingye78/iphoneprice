#!/usr/bin/env python3
# Forecast iPhone 18 (standard) second-hand RECYCLE value over the next ~4 years
# and mark the best "buy-the-dip" windows.
#
# Assumptions:
#  - iPhone 18 launches 2026-09, China launch price 5999 RMB (same as 15/16/17).
#  - Residual curve rr(t) calibrated earlier (recycle value / launch price).

import json

P = 5999.0
LAUNCH = (2026, 9)

pts=[(0,1.00),(6,0.82),(12,0.74),(14,0.70),(18,0.63),(24,0.55),(30,0.48),
     (36,0.42),(48,0.32),(60,0.25)]
def rr(t):
    if t<=pts[0][0]:return pts[0][1]
    if t>=pts[-1][0]:return pts[-1][1]
    for (a,r0),(b,r1) in zip(pts,pts[1:]):
        if a<=t<=b:return r0+(r1-r0)*(t-a)/(b-a)
    return pts[-1][1]

def cal(t):
    m = LAUNCH[1]-1 + t
    return (LAUNCH[0] + m//12, m%12 + 1)

months = list(range(0, 49))
series = []
for t in months:
    y, mo = cal(t)
    series.append({"t":t, "ym":f"{y}-{mo:02d}", "value":round(P*rr(t)), "residual":round(rr(t)*100)})

events = {
    12: "2027-09 iPhone19 发布(台阶下跌)",
    14: "2027 双11 促销低点",
    24: "2028-09 iPhone20 发布",
    26: "2028 双11",
}

print(f"{'月':>3} {'日期':>8} {'残值':>5} {'预测回收价':>8}")
for s in series:
    if s["t"]%3==0 or s["t"] in events:
        tag = "  <-- "+events[s["t"]] if s["t"] in events else ""
        print(f"{s['t']:>3} {s['ym']:>8} {s['residual']:>4}% {s['value']:>8}{tag}")

print("\n=== 买入抄底分析: 在某机龄买入并持有24个月的月成本 ===")
best=None
for a in [0,6,12,14,18,24]:
    cost = P*(rr(a)-rr(a+24))/24
    y,mo = cal(a)
    if best is None or cost<best[1]: best=(a,cost,y,mo)
    print(f"  机龄{a:>2}月 (≈{y}-{mo:02d}) 买入{round(P*rr(a)):>4} 持有24月 月成本 {cost:5.1f} 元/月")
print(f"\n推荐抄底点: 机龄约 {best[0]} 个月(≈{best[2]}-{best[3]:02d})买入,月成本最低 {best[1]:.1f} 元/月")

json.dump({"P":P,"launch":f"{LAUNCH[0]}-{LAUNCH[1]:02d}","series":series,"events":events},
          open("../data/iphone18_forecast.json","w"), ensure_ascii=False)
print("\nwrote data/iphone18_forecast.json")
