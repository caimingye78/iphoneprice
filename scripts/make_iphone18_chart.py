#!/usr/bin/env python3
import json
d=json.load(open("../data/iphone18_forecast.json"))
S=d["series"]; ev=d["events"]
W,H,ml,mr,mt,mb=960,540,75,40,70,80
pw,ph=W-ml-mr,H-mt-mb
xmax=48; ymax=6000
def x(t): return ml+t/xmax*pw
def y(v): return mt+(ymax-v)/ymax*ph
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI,Arial,sans-serif">',
   f'<rect width="{W}" height="{H}" fill="#fff"/>',
   f'<text x="{ml}" y="30" font-size="19" font-weight="bold" fill="#202124">iPhone 18 二手回收价预测 (国行标准款, 首发¥5999)</text>',
   f'<text x="{ml}" y="48" font-size="12" fill="#9aa0a6">基于历史折旧曲线推演, 2026-09 发布起算; 数值为预估, 仅供参考</text>']
for v in range(0,6001,1000):
    s.append(f'<line x1="{ml}" y1="{y(v):.1f}" x2="{ml+pw}" y2="{y(v):.1f}" stroke="#e8eaed"/>')
    s.append(f'<text x="{ml-8}" y="{y(v)+4:.1f}" font-size="11" text-anchor="end" fill="#5f6368">{v}</text>')
# x ticks every 6 months with calendar label
for t in range(0,49,6):
    ym=S[t]["ym"]
    s.append(f'<line x1="{x(t):.1f}" y1="{mt}" x2="{x(t):.1f}" y2="{mt+ph}" stroke="#f1f3f4"/>')
    s.append(f'<text x="{x(t):.1f}" y="{mt+ph+18:.1f}" font-size="10" text-anchor="middle" fill="#5f6368">{ym}</text>')
    s.append(f'<text x="{x(t):.1f}" y="{mt+ph+32:.1f}" font-size="9" text-anchor="middle" fill="#bdc1c6">{t}月</text>')
# main curve
dp="".join(("M" if i==0 else "L")+f"{x(p['t']):.1f},{y(p['value']):.1f} " for i,p in enumerate(S))
s.append(f'<path d="{dp.strip()}" fill="none" stroke="#ea4335" stroke-width="2.5"/>')
# dip windows (shaded bands around Sept releases & 双11)
for t,label in [(12,""),(24,"")]:
    s.append(f'<rect x="{x(t):.1f}" y="{mt}" width="{x(t+3)-x(t):.1f}" height="{ph:.1f}" fill="#34a853" opacity="0.10"/>')
# annotate events
def mark(t,txt,dy):
    p=S[t]
    s.append(f'<circle cx="{x(t):.1f}" cy="{y(p["value"]):.1f}" r="4.5" fill="#1e8e3e"/>')
    s.append(f'<text x="{x(t)+7:.1f}" y="{y(p["value"])+dy:.1f}" font-size="10.5" fill="#1e8e3e">{txt} ¥{p["value"]}</text>')
mark(12,"2027-09 抄底窗口", -8)
mark(14,"双11低点", 16)
mark(24,"2028-09 性价比顶点", -8)
# recommended sweet spot label
s.append(f'<text x="{ml+pw-360:.1f}" y="{mt+30:.1f}" font-size="12" fill="#1e8e3e" font-weight="bold">绿色区=抄底窗口(新机发布后)</text>')
s.append('</svg>')
open("../charts/iphone18_forecast.svg","w").write("\n".join(s))
print("wrote charts/iphone18_forecast.svg")
