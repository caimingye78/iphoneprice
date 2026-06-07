#!/usr/bin/env python3
# Generate an SVG chart: China iPhone launch price (RMB) vs current second-hand
# market value (approx, early 2026) for the STANDARD model line. Also computes
# residual value ratio.
#
# NOTE: second-hand numbers are approximate market estimates for mainstream
# storage, good condition (~95新), as of early 2026. They are indicative, not exact.

models = ["7", "8", "X", "XR", "11", "12", "13", "14", "15", "16"]
launch_year = [2016, 2017, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

# China launch price (RMB), base storage tier
launch_cn = [5388, 5888, 8388, 6499, 5499, 6299, 5999, 5999, 5999, 5999]

# Current second-hand market value (RMB), good condition, mainstream storage (approx, early 2026)
used_now = [350, 600, 950, 1000, 1450, 2050, 2950, 3550, 4250, 5050]

W, H = 960, 560
ml, mr, mt, mb = 70, 200, 60, 60
pw = W - ml - mr
ph = H - mt - mb

ymin, ymax = 0, 9000
n = len(models)

def x(i): return ml + i / (n - 1) * pw
def y(v): return mt + (ymax - v) / (ymax - ymin) * ph

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI, Arial, sans-serif">')
svg.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
svg.append(f'<text x="{ml}" y="28" font-size="19" font-weight="bold" fill="#202124">国行标准款 iPhone：首发价 vs 当前二手价 (人民币)</text>')
svg.append(f'<text x="{ml}" y="46" font-size="12" fill="#9aa0a6">二手价为 2026 年初主流存储、良好成色近似行情，仅供参考</text>')

# Y grid
for v in range(0, 9001, 1000):
    yy = y(v)
    svg.append(f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml+pw}" y2="{yy:.1f}" stroke="#e8eaed" stroke-width="1"/>')
    svg.append(f'<text x="{ml-10}" y="{yy+4:.1f}" font-size="11" text-anchor="end" fill="#5f6368">{v}</text>')

# X labels
for i, m in enumerate(models):
    xx = x(i)
    svg.append(f'<text x="{xx:.1f}" y="{mt+ph+20}" font-size="12" text-anchor="middle" fill="#3c4043">{m}</text>')
    svg.append(f'<text x="{xx:.1f}" y="{mt+ph+36}" font-size="10" text-anchor="middle" fill="#9aa0a6">{launch_year[i]}</text>')

def path(vals):
    d = ""
    for i, v in enumerate(vals):
        d += ("M" if i == 0 else "L") + f"{x(i):.1f},{y(v):.1f} "
    return d.strip()

# Launch price line (blue)
svg.append(f'<path d="{path(launch_cn)}" fill="none" stroke="#4285f4" stroke-width="2.5"/>')
for i, v in enumerate(launch_cn):
    svg.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="3.5" fill="#4285f4"/>')

# Used now line (red)
svg.append(f'<path d="{path(used_now)}" fill="none" stroke="#ea4335" stroke-width="2.5"/>')
for i, v in enumerate(used_now):
    svg.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="3.5" fill="#ea4335"/>')
    svg.append(f'<text x="{x(i):.1f}" y="{y(v)-8:.1f}" font-size="9" text-anchor="middle" fill="#ea4335">{v}</text>')

# Legend
lx = ml + pw + 25
ly = mt + 10
items = [("首发价(国行)", "#4285f4"), ("当前二手价", "#ea4335")]
for i, (name, c) in enumerate(items):
    yy = ly + i * 26
    svg.append(f'<line x1="{lx}" y1="{yy}" x2="{lx+24}" y2="{yy}" stroke="{c}" stroke-width="3"/>')
    svg.append(f'<text x="{lx+32}" y="{yy+4}" font-size="12" fill="#3c4043">{name}</text>')

# residual ratio note
svg.append(f'<text x="{lx}" y="{ly+70}" font-size="12" font-weight="bold" fill="#202124">残值率(约)</text>')
for i, m in enumerate(models):
    ratio = used_now[i] / launch_cn[i] * 100
    yy = ly + 92 + i * 18
    svg.append(f'<text x="{lx}" y="{yy}" font-size="10.5" fill="#5f6368">iPhone {m}: {ratio:.0f}%</text>')

svg.append('</svg>')

with open("iphone_secondhand_cn.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(svg))
print("wrote iphone_secondhand_cn.svg")
for i, m in enumerate(models):
    print(f"iPhone {m}: 首发 {launch_cn[i]}  二手 {used_now[i]}  残值 {used_now[i]/launch_cn[i]*100:.0f}%")
