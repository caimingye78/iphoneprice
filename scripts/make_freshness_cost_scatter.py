#!/usr/bin/env python3
import json
import math

# 读取前沿数据
with open("data/frontier_data.json", "r") as f:
    data = json.load(f)

all_points = data["all"]  # 所有策略点 (平均机龄, 月成本)
pareto_points = data["pareto"]  # 前沿点 (平均机龄, 月成本, a, h)

# 四种需要标注的情况
highlight_cases = [
    {"name": "买全新用1年", "a": 0, "h": 12, "color": "#ea4335", "symbol": "○"},
    {"name": "买全新用2年", "a": 0, "h": 24, "color": "#4285f4", "symbol": "△"},
    {"name": "买半年二手用2年", "a": 6, "h": 24, "color": "#34a853", "symbol": "□"},
    {"name": "买全新用3年", "a": 0, "h": 36, "color": "#fbbc04", "symbol": "◇"},
]

# 计算每种情况的平均机龄和月成本
def rr(t):
    """残值率函数"""
    lambda_val = -math.log(0.68) / 14  # 基于 iPhone 16 数据
    return math.exp(-lambda_val * t)

P = 5999  # iPhone 16 首发价

cases_data = []
for case in highlight_cases:
    a = case["a"]
    h = case["h"]
    avg_age = a + h / 2
    buy_price = P * rr(a)
    sell_price = P * rr(a + h)
    monthly_cost = (buy_price - sell_price) / h
    
    case["avg_age"] = avg_age
    case["monthly_cost"] = monthly_cost
    cases_data.append(case)

# SVG 参数
W, H = 900, 520
ml, mr, mt, mb = 70, 40, 60, 70
pw, ph = W - ml - mr, H - mt - mb

xmax = 60  # 平均机龄最大 60 个月
ymin, ymax = 20, 140  # 月成本范围

def x(a):
    return ml + (a / xmax) * pw

def y(c):
    return mt + (ymax - c) / (ymax - ymin) * ph

# 开始生成SVG
svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI,Arial,sans-serif">',
    f'<rect width="{W}" height="{H}" fill="#fff"/>',
    # 标题
    f'<text x="{ml}" y="28" font-size="18" font-weight="bold" fill="#202124">新鲜度 vs 月成本：策略空间散点图</text>',
    f'<text x="{ml}" y="46" font-size="12" fill="#9aa0a6">四种典型策略在前沿曲线上对照比较（越小越新越省）</text>',
]

# 网格线
for c in range(20, 141, 20):
    svg.append(f'<line x1="{ml}" y1="{y(c):.1f}" x2="{ml+pw}" y2="{y(c):.1f}" stroke="#e8eaed"/>')
    svg.append(f'<text x="{ml-8}" y="{y(c)+4:.1f}" font-size="11" text-anchor="end" fill="#5f6368">{c}</text>')

for a in range(0, 61, 6):
    svg.append(f'<text x="{x(a):.1f}" y="{mt+ph+20:.1f}" font-size="10" text-anchor="middle" fill="#5f6368">{a}</text>')

# 坐标轴标签
svg.append(f'<text x="{ml+pw/2:.1f}" y="{mt+ph+42:.1f}" font-size="12" text-anchor="middle" fill="#3c4043">平均机龄（月） 越小越新</text>')
svg.append(f'<text x="20" y="{mt+ph/2:.1f}" font-size="12" fill="#3c4043" transform="rotate(-90 20 {mt+ph/2:.1f})">元/月</text>')

# 绘制所有策略点（灰色）
for a, c in all_points:
    svg.append(f'<circle cx="{x(a):.1f}" cy="{y(c):.1f}" r="2" fill="#dadce0" opacity="0.6"/>')

# 绘制前沿曲线
pareto_path = []
for i, (a, c, _, _) in enumerate(pareto_points):
    px = x(a)
    py = y(c)
    if i == 0:
        pareto_path.append(f"M{px:.1f},{py:.1f}")
    else:
        pareto_path.append(f"L{px:.1f},{py:.1f}")

svg.append(f'<path d="{" ".join(pareto_path)}" fill="none" stroke="#ea4335" stroke-width="2.5"/>')

# 标注前沿点
for a, c, _, _ in pareto_points:
    svg.append(f'<circle cx="{x(a):.1f}" cy="{y(c):.1f}" r="3" fill="#ea4335"/>')

# 标注四种情况
symbols_def = {
    "○": '<circle r="7" fill="none" stroke-width="2"/>',
    "△": '<polygon points="0,-8 7,6 -7,6" fill="none" stroke-width="2"/>',
    "□": '<rect x="-6" y="-6" width="12" height="12" fill="none" stroke-width="2"/>',
    "◇": '<polygon points="0,-8 6,0 0,8 -6,0" fill="none" stroke-width="2"/>',
}

for case in cases_data:
    px = x(case["avg_age"])
    py = y(case["monthly_cost"])
    color = case["color"]
    symbol = case["symbol"]
    
    # 创建符号定义
    symbol_id = f"symbol-{case['name']}"
    svg.append(f'<defs><g id="{symbol_id}">{symbols_def[symbol]}</g></defs>')
    
    # 使用符号
    svg.append(f'<use href="#{symbol_id}" x="{px}" y="{py}" stroke="{color}" fill="none"/>')
    svg.append(f'<circle cx="{px}" cy="{py}" r="3" fill="{color}"/>')
    
    # 标签
    dx = 8 if case["name"] != "买全新用3年" else -120
    dy = -8 if case["name"] != "买半年二手用2年" else 20
    
    svg.append(f'<text x="{px+dx:.1f}" y="{py+dy:.1f}" font-size="10.5" fill="{color}" font-weight="bold">{case["name"]}</text>')
    
    # 详细信息
    if case["name"] == "买全新用3年":
        svg.append(f'<text x="{px+dx:.1f}" y="{py+dy+14:.1f}" font-size="9.5" fill="#5f6368">平均机龄: {case["avg_age"]}个月</text>')
        svg.append(f'<text x="{px+dx:.1f}" y="{py+dy+28:.1f}" font-size="9.5" fill="#5f6368">月成本: ¥{case["monthly_cost"]:.1f}/月</text>')
        svg.append(f'<text x="{px+dx:.1f}" y="{py+dy+42:.1f}" font-size="9.5" fill="#5f6368">买入机龄: {case["a"]}个月, 持有: {case["h"]}个月</text>')
    else:
        svg.append(f'<text x="{px+dx:.1f}" y="{py+dy+14:.1f}" font-size="9.5" fill="#5f6368">平均机龄: {case["avg_age"]}个月 | 月成本: ¥{case["monthly_cost"]:.1f}/月</text>')

# 添加用户点（你的情况）
user_avg_age = 7  # 你的平均机龄
user_cost = 137   # 你的月成本
user_px = x(user_avg_age)
user_py = y(user_cost)

svg.append(f'<circle cx="{user_px:.1f}" cy="{user_py:.1f}" r="8" fill="none" stroke="#202124" stroke-width="2"/>')
svg.append(f'<text x="{user_px+10:.1f}" y="{user_py+4:.1f}" font-size="10.5" fill="#202124" font-weight="bold">你的情况</text>')
svg.append(f'<text x="{user_px+10:.1f}" y="{user_py+18:.1f}" font-size="9.5" fill="#5f6368">平均机龄: 7个月, 月成本: ¥137/月</text>')

# 添加图例
legend_x = ml + pw - 180
legend_y = mt + 20

svg.append(f'<rect x="{legend_x-10}" y="{legend_y-15}" width="190" height="150" fill="#f8f9fa" stroke="#dadce0" rx="5"/>')
svg.append(f'<text x="{legend_x}" y="{legend_y}" font-size="11" fill="#202124" font-weight="bold">四种策略说明：</text>')

for i, case in enumerate(cases_data):
    symbol_y = legend_y + 20 + i * 25
    # 符号
    symbol_id = f"legend-symbol-{i}"
    svg.append(f'<defs><g id="{symbol_id}">{symbols_def[case["symbol"]]}</g></defs>')
    svg.append(f'<use href="#{symbol_id}" x="{legend_x}" y="{symbol_y}" stroke="{case["color"]}" fill="none"/>')
    
    # 文本
    svg.append(f'<text x="{legend_x+15}" y="{symbol_y+4}" font-size="10" fill="#202124">{case["name"]}</text>')
    svg.append(f'<text x="{legend_x+15}" y="{symbol_y+16}" font-size="9" fill="#5f6368">平均机龄: {case["avg_age"]}个月, 月成本: ¥{case["monthly_cost"]:.1f}</text>')

# 重要发现注释
note_x = ml + 20
note_y = mt + 30

svg.append(f'<rect x="{note_x-10}" y="{note_y-10}" width="250" height="80" fill="#f0f7ff" stroke="#4285f4" stroke-width="1" rx="5" opacity="0.9"/>')
svg.append(f'<text x="{note_x}" y="{note_y}" font-size="11" fill="#4285f4" font-weight="bold">关键发现：</text>')
svg.append(f'<text x="{note_x}" y="{note_y+15}" font-size="10" fill="#202124">• "买全新用3年" 与 "买半年二手用2年"</text>')
svg.append(f'<text x="{note_x+10}" y="{note_y+30}" font-size="9.5" fill="#5f6368">平均机龄相同(18个月)，新鲜度等价！</text>')
svg.append(f'<text x="{note_x}" y="{note_y+45}" font-size="10" fill="#202124">• 但后者月成本 ¥102.5 vs 前者 ¥104.8</text>')
svg.append(f'<text x="{note_x+10}" y="{note_y+60}" font-size="9.5" fill="#5f6368">提前体验半年二手，每月省¥2.3</text>')

svg.append('</svg>')

# 写入文件
with open("freshness_vs_cost.svg", "w") as f:
    f.write("\n".join(svg))

print("生成完毕：freshness_vs_cost.svg")
print("\n四种策略在前沿上的位置：")
for case in cases_data:
    print(f"{case['name']}:")
    print(f"  - 平均机龄: {case['avg_age']}个月")
    print(f"  - 月成本: ¥{case['monthly_cost']:.1f}/月")
    print(f"  - 距离前沿: 需要计算...")
    
# 计算距离前沿的距离
print("\n前沿曲线最近点分析：")
for case in cases_data:
    min_dist = float('inf')
    closest_point = None
    
    for pa, pc, _, _ in pareto_points:
        dist = math.sqrt((pa - case['avg_age'])**2 + (pc - case['monthly_cost'])**2)
        if dist < min_dist:
            min_dist = dist
            closest_point = (pa, pc)
    
    if closest_point:
        print(f"{case['name']}:")
        print(f"  - 距离最近前沿点: {min_dist:.2f} 单位")
        print(f"  - 前沿点位置: 平均机龄={closest_point[0]}个月, 月成本=¥{closest_point[1]}/月")
        if min_dist < 5:
            print(f"  - ✅ 策略接近帕累托最优")
        else:
            print(f"  - ⚠️ 策略有优化空间")