#!/usr/bin/env python3
import json
import math

# 读取数据
with open("data/strategy_data.json", "r") as f:
    data = json.load(f)

# 获取残值率函数
# 使用用户提供的实际数据点校准
# iPhone 16: ¥6069 -> ¥4150 (14个月) -> 残值率 68%
# 使用指数衰减模型：rr(t) = e^{-λt}
# 已知 rr(14) = 0.68，求解 λ
lambda_val = -math.log(0.68) / 14  # 大约 0.027

def rr(t):
    """残值率函数，基于指数衰减模型"""
    return math.exp(-lambda_val * t)

# 四种情况
scenarios = [
    {"name": "买全新用1年", "a": 0, "h": 12, "color": "#ea4335"},  # 红色
    {"name": "买全新用2年", "a": 0, "h": 24, "color": "#4285f4"},  # 蓝色
    {"name": "买半年二手用2年", "a": 6, "h": 24, "color": "#34a853"},  # 绿色
    {"name": "买全新用3年", "a": 0, "h": 36, "color": "#fbbc04"},  # 黄色
]

# 设置参数
P = 5999  # iPhone 16 首发价
W, H = 900, 400
ml, mr, mt, mb = 70, 40, 80, 70
pw, ph = W - ml - mr, H - mt - mb

def x(t):
    """机龄 -> x坐标"""
    return ml + (t / 60) * pw

def y_freshness(avg_age):
    """平均机龄 -> y坐标（上部分）"""
    y_max = mt + ph / 2 - 20
    return mt + (avg_age / 60) * (ph / 2 - 40)

def y_cost(cost):
    """月成本 -> y坐标（下部分）"""
    y_min = mt + ph / 2 + 20
    y_range = ph / 2 - 40
    return y_min + (cost - 20) / (140 - 20) * y_range

# 开始生成SVG
svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI,Arial,sans-serif">',
    f'<rect width="{W}" height="{H}" fill="#fff"/>',
    # 标题
    f'<text x="{ml}" y="28" font-size="18" font-weight="bold" fill="#202124">新鲜度 vs 月成本：四种策略对比</text>',
    f'<text x="{ml}" y="48" font-size="12" fill="#9aa0a6">上：机龄随时间变化（蓝线=机龄上升，红点=平均机龄）；下：月成本（越小越省）</text>',
]

# 上部分：机龄随时间变化
svg.append(f'<rect x="{ml}" y="{mt}" width="{pw}" height="{ph/2-40}" fill="#f8f9fa" stroke="#dadce0"/>')
svg.append(f'<text x="{ml+pw/2}" y="{mt+ph/2-55}" font-size="12" text-anchor="middle" fill="#5f6368">机龄随时间上升（单位：月）</text>')

# 时间轴
for month in [0, 12, 24, 36, 48, 60]:
    svg.append(f'<line x1="{x(month):.1f}" y1="{mt}" x2="{x(month):.1f}" y2="{mt+ph/2-40}" stroke="#e8eaed" stroke-dasharray="2,2"/>')
    svg.append(f'<text x="{x(month):.1f}" y="{mt+ph/2-30}" font-size="10" text-anchor="middle" fill="#5f6368">{month}</text>')

# 绘制每种情况的机龄线
for scenario in scenarios:
    a = scenario["a"]
    h = scenario["h"]
    color = scenario["color"]
    
    # 机龄线：从 a 到 a+h
    x1, y1 = x(a), y_freshness(a)
    x2, y2 = x(a + h), y_freshness(a + h)
    
    svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="3" opacity="0.7"/>')
    
    # 起点和终点标记
    svg.append(f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="4" fill="{color}"/>')
    svg.append(f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="4" fill="{color}"/>')
    
    # 平均机龄点
    avg_age = a + h / 2
    avg_x = x(avg_age)
    avg_y = y_freshness(avg_age)
    svg.append(f'<circle cx="{avg_x:.1f}" cy="{avg_y:.1f}" r="6" fill="none" stroke="{color}" stroke-width="2"/>')
    
    # 标签
    svg.append(f'<text x="{avg_x+8:.1f}" y="{avg_y+4:.1f}" font-size="11" fill="#202124" font-weight="bold">{scenario["name"]}</text>')
    svg.append(f'<text x="{avg_x+8:.1f}" y="{avg_y+18:.1f}" font-size="10" fill="#5f6368">平均机龄：{avg_age}个月</text>')

# 分隔线
svg.append(f'<line x1="{ml}" y1="{mt+ph/2}" x2="{ml+pw}" y2="{mt+ph/2}" stroke="#dadce0" stroke-width="2"/>')

# 下部分：月成本
svg.append(f'<rect x="{ml}" y="{mt+ph/2+20}" width="{pw}" height="{ph/2-40}" fill="#f8f9fa" stroke="#dadce0"/>')
svg.append(f'<text x="{ml+pw/2}" y="{mt+ph+15}" font-size="12" text-anchor="middle" fill="#5f6368">每月成本（元）</text>')

# 成本刻度
for cost in [20, 40, 60, 80, 100, 120, 140]:
    y = y_cost(cost)
    svg.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{ml+pw}" y2="{y:.1f}" stroke="#e8eaed" stroke-dasharray="2,2"/>')
    svg.append(f'<text x="{ml-8:.1f}" y="{y+4:.1f}" font-size="10" text-anchor="end" fill="#5f6368">{cost}</text>')

# 计算并显示每种情况的月成本
for scenario in scenarios:
    a = scenario["a"]
    h = scenario["h"]
    color = scenario["color"]
    
    # 计算月成本
    buy_price = P * rr(a)
    sell_price = P * rr(a + h)
    monthly_cost = (buy_price - sell_price) / h
    
    # 成本点位置
    cost_x = x(a + h/2)  # 使用平均机龄的位置
    cost_y = y_cost(monthly_cost)
    
    # 成本点
    svg.append(f'<circle cx="{cost_x:.1f}" cy="{cost_y:.1f}" r="6" fill="{color}"/>')
    
    # 连接线（从平均机龄点到成本点）
    avg_x = x(a + h/2)
    avg_y = y_freshness(a + h/2)
    svg.append(f'<line x1="{avg_x:.1f}" y1="{avg_y:.1f}" x2="{cost_x:.1f}" y2="{cost_y:.1f}" stroke="{color}" stroke-width="1" stroke-dasharray="4,2" opacity="0.5"/>')
    
    # 成本标签
    svg.append(f'<text x="{cost_x+8:.1f}" y="{cost_y+4:.1f}" font-size="10" fill="#202124" font-weight="bold">{scenario["name"]}</text>')
    svg.append(f'<text x="{cost_x+8:.1f}" y="{cost_y+18:.1f}" font-size="10" fill="#5f6368">月成本：¥{monthly_cost:.1f}/月</text>')

# 特别标注用户的情况
user_a = 0
user_h = 14
user_avg_age = user_a + user_h / 2
user_cost = 137  # 用户的实际月成本

user_cost_x = x(user_avg_age)
user_cost_y = y_cost(user_cost)

svg.append(f'<circle cx="{user_cost_x:.1f}" cy="{user_cost_y:.1f}" r="8" fill="none" stroke="#202124" stroke-width="2"/>')
svg.append(f'<text x="{user_cost_x+10:.1f}" y="{user_cost_y+4:.1f}" font-size="11" fill="#202124" font-weight="bold">你的情况</text>')
svg.append(f'<text x="{user_cost_x+10:.1f}" y="{user_cost_y+20:.1f}" font-size="10" fill="#5f6368">平均机龄：7个月，月成本：¥137/月</text>')

svg.append('</svg>')

# 写入文件
with open("freshness_demo.svg", "w") as f:
    f.write("\n".join(svg))

print("生成完毕：freshness_demo.svg")
print("\n四种策略总结：")
for scenario in scenarios:
    a = scenario["a"]
    h = scenario["h"]
    avg_age = a + h / 2
    buy_price = P * rr(a)
    sell_price = P * rr(a + h)
    monthly_cost = (buy_price - sell_price) / h
    
    print(f"{scenario['name']}:")
    print(f"  - 买入机龄: {a}个月, 持有时长: {h}个月")
    print(f"  - 平均机龄: {avg_age}个月")
    print(f"  - 买入价: ¥{buy_price:.0f}, 卖出价: ¥{sell_price:.0f}")
    print(f"  - 月成本: ¥{monthly_cost:.1f}/月")
    print()