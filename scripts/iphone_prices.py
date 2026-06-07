#!/usr/bin/env python3
# Generate an SVG line chart of iPhone US launch prices (base storage) 2016-2025.

# Data: US launch price in USD for base storage of each tier, by year.
# None = no model in that tier that year.
years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

series = {
    "SE / e (budget)":      [399, None, None, None, 399, None, 429, None, None, 599],
    "Standard":             [649, 699, 749, 699, 799, 799, 799, 799, 799, 799],
    "Plus / Air (big std)": [769, 799, None, None, None, None, 899, 899, 899, 999],
    "Pro":                  [None, 999, 999, 999, 999, 999, 999, 999, 999, 1099],
    "Pro Max":              [None, None, 1099, 1099, 1099, 1099, 1099, 1199, 1199, 1199],
}

colors = {
    "SE / e (budget)":      "#34a853",
    "Standard":             "#4285f4",
    "Plus / Air (big std)": "#a142f4",
    "Pro":                  "#fbbc05",
    "Pro Max":              "#ea4335",
}

# Chart geometry
W, H = 920, 560
ml, mr, mt, mb = 70, 230, 50, 60
pw = W - ml - mr
ph = H - mt - mb

ymin, ymax = 350, 1250
xmin, xmax = years[0], years[-1]

def x(yr): return ml + (yr - xmin) / (xmax - xmin) * pw
def y(v):  return mt + (ymax - v) / (ymax - ymin) * ph

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI, Arial, sans-serif">')
svg.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
svg.append(f'<text x="{ml}" y="28" font-size="20" font-weight="bold" fill="#202124">iPhone 美国发布价曲线 (2016-2025, 基础存储, 美元)</text>')

# Y gridlines
for v in range(400, 1300, 100):
    yy = y(v)
    svg.append(f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml+pw}" y2="{yy:.1f}" stroke="#e8eaed" stroke-width="1"/>')
    svg.append(f'<text x="{ml-10}" y="{yy+4:.1f}" font-size="12" text-anchor="end" fill="#5f6368">${v}</text>')

# X labels
for yr in years:
    xx = x(yr)
    svg.append(f'<line x1="{xx:.1f}" y1="{mt}" x2="{xx:.1f}" y2="{mt+ph}" stroke="#f1f3f4" stroke-width="1"/>')
    svg.append(f'<text x="{xx:.1f}" y="{mt+ph+22}" font-size="12" text-anchor="middle" fill="#5f6368">{yr}</text>')

# Plot each series (skip None gaps, connecting available points)
for name, vals in series.items():
    c = colors[name]
    pts = [(years[i], v) for i, v in enumerate(vals) if v is not None]
    # build path
    d = ""
    for i, (yr, v) in enumerate(pts):
        cmd = "M" if i == 0 else "L"
        d += f"{cmd}{x(yr):.1f},{y(v):.1f} "
    svg.append(f'<path d="{d.strip()}" fill="none" stroke="{c}" stroke-width="2.5"/>')
    for yr, v in pts:
        svg.append(f'<circle cx="{x(yr):.1f}" cy="{y(v):.1f}" r="3.5" fill="{c}"/>')

# Legend
lx = ml + pw + 25
ly = mt + 10
svg.append(f'<text x="{lx}" y="{ly-12}" font-size="13" font-weight="bold" fill="#202124">机型档位</text>')
for i, (name, c) in enumerate(colors.items()):
    yy = ly + i * 26
    svg.append(f'<line x1="{lx}" y1="{yy}" x2="{lx+24}" y2="{yy}" stroke="{c}" stroke-width="3"/>')
    svg.append(f'<circle cx="{lx+12}" cy="{yy}" r="3.5" fill="{c}"/>')
    svg.append(f'<text x="{lx+32}" y="{yy+4}" font-size="12" fill="#3c4043">{name}</text>')

svg.append(f'<text x="{ml}" y="{H-15}" font-size="11" fill="#9aa0a6">数据来源: Apple Newsroom / Wikipedia / MacRumors / The Verge 等公开发布价 (美国, 不含税)</text>')
svg.append('</svg>')

with open("iphone_price_curve.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(svg))
print("wrote iphone_price_curve.svg")
