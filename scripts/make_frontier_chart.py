#!/usr/bin/env python3
import json
d=json.load(open("frontier_data.json"))
allp=d["all"]; par=d["pareto"]
W,H,ml,mr,mt,mb=900,520,70,40,60,70
pw,ph=W-ml-mr,H-mt-mb
xmax=60; ymin,ymax=20,140
def x(a): return ml+a/xmax*pw
def y(c): return mt+(ymax-c)/(ymax-ymin)*ph
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI,Arial,sans-serif">',
   f'<rect width="{W}" height="{H}" fill="#fff"/>',
   f'<text x="{ml}" y="28" font-size="18" font-weight="bold" fill="#202124">新科技 vs 省钱：最优购买前沿</text>',
   f'<text x="{ml}" y="46" font-size="12" fill="#9aa0a6">越靠左=用的科技越新；越靠下=每月越省。红线=同等新鲜度下最省的策略</text>']
# grid
for c in range(20,141,20):
    s.append(f'<line x1="{ml}" y1="{y(c):.1f}" x2="{ml+pw}" y2="{y(c):.1f}" stroke="#e8eaed"/>')
    s.append(f'<text x="{ml-8}" y="{y(c)+4:.1f}" font-size="11" text-anchor="end" fill="#5f6368">{c}</text>')
for a in range(0,61,6):
    s.append(f'<text x="{x(a):.1f}" y="{mt+ph+20:.1f}" font-size="10" text-anchor="middle" fill="#5f6368">{a}</text>')
s.append(f'<text x="{ml+pw/2:.1f}" y="{mt+ph+42:.1f}" font-size="12" text-anchor="middle" fill="#3c4043">平均机龄(月)  越小越新</text>')
s.append(f'<text x="20" y="{mt+ph/2:.1f}" font-size="12" fill="#3c4043" transform="rotate(-90 20 {mt+ph/2:.1f})">元/月</text>')
# all strategies (grey dots)
for a,c in allp:
    s.append(f'<circle cx="{x(a):.1f}" cy="{y(c):.1f}" r="2.5" fill="#dadce0"/>')
# pareto line
dp="".join(("M" if i==0 else "L")+f"{x(a):.1f},{y(c):.1f} " for i,(a,c,_,_) in enumerate(par))
s.append(f'<path d="{dp.strip()}" fill="none" stroke="#ea4335" stroke-width="2.5"/>')
for a,c,_,_ in par:
    s.append(f'<circle cx="{x(a):.1f}" cy="{y(c):.1f}" r="3.5" fill="#ea4335"/>')
# zones
s.append(f'<rect x="{x(0):.1f}" y="{mt}" width="{x(10)-x(0):.1f}" height="{ph:.1f}" fill="#ea4335" opacity="0.07"/>')
s.append(f'<text x="{x(5):.1f}" y="{mt+18:.1f}" font-size="11" text-anchor="middle" fill="#ea4335">冤大头区</text>')
s.append(f'<text x="{x(5):.1f}" y="{mt+33:.1f}" font-size="10" text-anchor="middle" fill="#ea4335">130元/月</text>')
# sweet spot
sx,sy=15,90
s.append(f'<rect x="{x(11):.1f}" y="{y(100):.1f}" width="{x(24)-x(11):.1f}" height="{y(75)-y(100):.1f}" fill="#34a853" opacity="0.10"/>')
s.append(f'<text x="{x(17):.1f}" y="{y(102):.1f}" font-size="11" text-anchor="middle" fill="#1e8e3e">甜点区</text>')
# annotate key points
def ann(a,c,txt,dx=8,dy=-8):
    s.append(f'<text x="{x(a)+dx:.1f}" y="{y(c)+dy:.1f}" font-size="10.5" fill="#202124">{txt}</text>')
ann(6,130,"买全新+1年就卖",6,-8)
ann(18,85,"买准新(6月)+持有2年=85",6,18)
ann(48,42.5,"买3年二手+持有2年=42",-150,-8)
# user point
s.append(f'<circle cx="{x(7):.1f}" cy="{y(137):.1f}" r="5" fill="none" stroke="#202124" stroke-width="2"/>')
s.append(f'<text x="{x(7)+8:.1f}" y="{y(137)+4:.1f}" font-size="10.5" fill="#202124">你现在:137</text>')
s.append('</svg>')
open("iphone_frontier.svg","w").write("\n".join(s))
print("wrote iphone_frontier.svg")
