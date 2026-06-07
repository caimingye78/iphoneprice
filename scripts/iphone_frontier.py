#!/usr/bin/env python3
# Efficient frontier: monthly cost vs "freshness" (average phone age held).
# Goal: minimize cost AND minimize average age (fresher tech). Find Pareto set.

pts = [(0,1.00),(6,0.82),(12,0.74),(14,0.70),(18,0.63),(24,0.55),
       (30,0.48),(36,0.42),(48,0.32),(60,0.25),(72,0.18),(84,0.12),(96,0.08)]
def rr(t):
    if t<=pts[0][0]: return pts[0][1]
    if t>=pts[-1][0]: return pts[-1][1]
    for (t0,r0),(t1,r1) in zip(pts,pts[1:]):
        if t0<=t<=t1: return r0+(r1-r0)*(t-t0)/(t1-t0)
    return pts[-1][1]
P=6000.0
def cost(a,h): return P*(rr(a)-rr(a+h))/h

strats=[]
for a in range(0,37,6):
    for h in range(12,49,6):
        avg=a+h/2.0
        strats.append((avg,cost(a,h),a,h))

def dominated(p,others):
    avg,c,_,_=p
    for o in others:
        if o is p: continue
        if o[0]<=avg and o[1]<=c and (o[0]<avg or o[1]<c):
            return True
    return False
pareto=sorted([p for p in strats if not dominated(p,strats)])

print("=== Pareto-optimal strategies (cheapest at each freshness) ===")
print(f"{'avg_age(mo)':>11} {'RMB/mo':>7}  strategy")
for avg,c,a,h in pareto:
    buy = "new" if a==0 else f"{a}mo-used"
    print(f"{avg:>11.1f} {c:>7.1f}  buy {buy}, hold {h}mo")

import json
json.dump({
  "all":[[round(a,1),round(c,1)] for a,c,_,_ in strats],
  "pareto":[[round(a,1),round(c,1),aa,hh] for a,c,aa,hh in pareto]
}, open("frontier_data.json","w"))
print("\nwrote frontier_data.json")
