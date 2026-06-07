#!/usr/bin/env python3
# iPhone ownership-cost optimizer.
# Metric (user-defined): monthly cost of a holding segment =
#     (buy_price - resale_price) / hold_months
# Long-run average monthly cost = sum(segment depreciation) / sum(months).
# So minimizing long-run cost == minimizing each segment's depreciation/month.
#
# We model RECYCLE residual value rr(age_months) for a ~6000 RMB standard
# flagship, calibrated to real recycle quotes and the user's own data point
# (iPhone 16: 6069 -> 4150 recycle at 14 months = 68%).

# ---- residual model (recycle value as fraction of launch price) ----
# calibration points: (age in months, residual fraction)
pts = [(0,1.00),(6,0.82),(12,0.74),(14,0.70),(18,0.63),(24,0.55),
       (30,0.48),(36,0.42),(48,0.32),(60,0.25),(72,0.18),(84,0.12),(96,0.08)]

def rr(t):
    """linear-interpolated recycle residual fraction at age t months"""
    if t <= pts[0][0]: return pts[0][1]
    if t >= pts[-1][0]: return pts[-1][1]
    for (t0,r0),(t1,r1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            return r0 + (r1-r0)*(t-t0)/(t1-t0)
    return pts[-1][1]

P = 6000.0  # launch price of a standard flagship (RMB)

def monthly_cost(buy_age, hold):
    """cost/month buying a phone aged buy_age months, holding `hold` months.
       buy_age=0 means buying brand new."""
    buy_price = P*rr(buy_age)
    sell_price = P*rr(buy_age+hold)
    return (buy_price - sell_price)/hold

print("=== A. Buy NEW, hold H months ===")
for H in [12,14,24,36,48,60,72]:
    print(f"  hold {H:>2} mo: {monthly_cost(0,H):6.1f} 元/月   "
          f"(买{P*rr(0):.0f} 卖{P*rr(H):.0f})")

print("\n=== B. Buy USED at age A, hold 24 months ===")
for A in [0,12,24,36,48]:
    print(f"  buy {A:>2}-mo-old: {monthly_cost(A,24):6.1f} 元/月  "
          f"(买{P*rr(A):.0f} 卖{P*rr(A+24):.0f})")

print("\n=== C. user's actual path: 16 (14mo) -> 17 ===")
print(f"  iPhone16 14mo segment: {(6069-4150)/14:.1f} 元/月")

# ---- export data for charts ----
import json
months = list(range(0, 97, 3))
resid = [round(P*rr(m)) for m in months]

# monthly cost vs hold, for several buy ages
holds = list(range(6, 73, 3))
curves = {}
for A in [0,12,24,36]:
    curves[A] = [round(monthly_cost(A,h),1) for h in holds]

with open("strategy_data.json","w") as f:
    json.dump({"months":months,"resid":resid,"holds":holds,"curves":curves}, f)
print("\nwrote strategy_data.json")
