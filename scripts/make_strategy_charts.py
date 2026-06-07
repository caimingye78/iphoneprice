#!/usr/bin/env python3
import json
d = json.load(open("strategy_data.json"))

# ---------- Chart 1: recycle residual value curve ----------
months, resid = d["months"], d["resid"]
W,H,ml,mr,mt,mb = 880,480,70,40,55,55
pw,ph = W-ml-mr, H-mt-mb
xmax=96; ymax=6000
def x(m): return ml+m/xmax*pw
def y(v): return mt+(ymax-v)/ymax*ph
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI,Arial,sans-serif">',
   f'<rect width="{W}" height="{H}" fill="#fff"/>',
   f'<text x="{ml}" y="30" font-size="18" font-weight="bold" fill="#202124">标准款 iPhone 回收价随机龄的折旧曲线 (首发约6000元)</text>']
for v in range(0,6001,1000):
    s.append(f'<line x1="{ml}" y1="{y(v):.1f}" x2="{ml+pw}" y2="{y(v):.1f}" stroke="#e8eaed"/>')
    s.append(f'<text x="{ml-8}" y="{y(v)+4:.1f}" font-size="11" text-anchor="end" fill="#5f6368">{v}</text>')
for m in range(0,97,12):
    s.append(f'<text x="{x(m):.1f}" y="{mt+ph+20:.1f}" font-size="11" text-anchor="middle" fill="#5f6368">{m}月</text>')
dpath="".join(("M" if i==0 else "L")+f"{x(m):.1f},{y(v):.1f} " for i,(m,v) in enumerate(zip(months,resid)))
s.append(f'<path d="{dpath.strip()}" fill="none" stroke="#ea4335" stroke-width="2.5"/>')
# annotate steep first year
s.append(f'<rect x="{x(0):.1f}" y="{mt}" width="{x(12)-x(0):.1f}" height="{ph:.1f}" fill="#ea4335" opacity="0.06"/>')
s.append(f'<text x="{x(6):.1f}" y="{mt+ph-8:.1f}" font-size="11" text-anchor="middle" fill="#ea4335">第1年掉价最猛</text>')
s.append(f'<text x="{ml}" y="{H-15}" font-size="11" fill="#9aa0a6">越往后越平缓：前1年掉约26%，第5年后基本触底</text>')
s.append('</svg>')
open("iphone_depreciation_curve.svg","w").write("\n".join(s))
print("wrote iphone_depreciation_curve.svg")

# ---------- Chart 2: monthly cost vs holding period ----------
holds=d["holds"]; curves=d["curves"]
W,H,ml,mr,mt,mb=900,500,70,210,55,55
pw,ph=W-ml-mr,H-mt-mb
xmax=72; ymax=160
def x2(m): return ml+m/xmax*pw
def y2(v): return mt+(ymax-v)/ymax*ph
colors={"0":"#ea4335","12":"#fbbc05","24":"#4285f4","36":"#34a853"}
labels={"0":"买全新机","12":"买1年二手","24":"买2年二手","36":"买3年二手"}
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI,Arial,sans-serif">',
   f'<rect width="{W}" height="{H}" fill="#fff"/>',
   f'<text x="{ml}" y="30" font-size="18" font-weight="bold" fill="#202124">每月持有成本 vs 持有时长</text>',
   f'<text x="{ml}" y="48" font-size="12" fill="#9aa0a6">越往右下越省钱：持有越久、买得越旧，每月成本越低</text>']
for v in range(0,161,20):
    s.append(f'<line x1="{ml}" y1="{y2(v):.1f}" x2="{ml+pw}" y2="{y2(v):.1f}" stroke="#e8eaed"/>')
    s.append(f'<text x="{ml-8}" y="{y2(v)+4:.1f}" font-size="11" text-anchor="end" fill="#5f6368">{v}</text>')
for m in range(6,73,6):
    s.append(f'<text x="{x2(m):.1f}" y="{mt+ph+20:.1f}" font-size="10" text-anchor="middle" fill="#5f6368">{m}</text>')
s.append(f'<text x="{ml+pw/2:.1f}" y="{mt+ph+40:.1f}" font-size="12" text-anchor="middle" fill="#3c4043">持有月数</text>')
s.append(f'<text x="20" y="{mt+ph/2:.1f}" font-size="12" fill="#3c4043" transform="rotate(-90 20 {mt+ph/2:.1f})">元/月</text>')
for key in ["0","12","24","36"]:
    c=colors[key]; vals=curves[key]
    dp="".join(("M" if i==0 else "L")+f"{x2(h):.1f},{y2(v):.1f} " for i,(h,v) in enumerate(zip(holds,vals)))
    s.append(f'<path d="{dp.strip()}" fill="none" stroke="{c}" stroke-width="2.5"/>')
# user's point: 137/mo at 14 mo new
s.append(f'<circle cx="{x2(14):.1f}" cy="{y2(137):.1f}" r="5" fill="none" stroke="#202124" stroke-width="2"/>')
s.append(f'<text x="{x2(14)+8:.1f}" y="{y2(137)-6:.1f}" font-size="11" fill="#202124">你: 16用14月=137</text>')
lx=ml+pw+25; ly=mt+20
s.append(f'<text x="{lx}" y="{ly-12}" font-size="13" font-weight="bold" fill="#202124">买入方式</text>')
for i,key in enumerate(["0","12","24","36"]):
    yy=ly+i*26
    s.append(f'<line x1="{lx}" y1="{yy}" x2="{lx+22}" y2="{yy}" stroke="{colors[key]}" stroke-width="3"/>')
    s.append(f'<text x="{lx+30}" y="{yy+4}" font-size="12" fill="#3c4043">{labels[key]}</text>')
s.append(f'<text x="{lx}" y="{ly+130}" font-size="11" fill="#5f6368">结论(持有24个月):</text>')
notes=["全新机: 112元/月","1年二手: 80元/月","2年二手: 57元/月","3年二手: 42元/月"]
for i,t in enumerate(notes):
    s.append(f'<text x="{lx}" y="{ly+152+i*18}" font-size="11" fill="#5f6368">{t}</text>')
s.append('</svg>')
open("iphone_cost_strategy.svg","w").write("\n".join(s))
print("wrote iphone_cost_strategy.svg")
