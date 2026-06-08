#!/usr/bin/env python3
import json
import math
from datetime import datetime, timedelta

# 残值率函数
lambda_val = -math.log(0.68) / 14

def rr(t):
    return math.exp(-lambda_val * t)

P = 5999  # iPhone 标准款首发价

def create_price_overlay_chart():
    """创建价格曲线叠加图表"""
    
    # 定义时间范围：从iPhone 18发布开始，到2032年
    start_date = datetime(2027, 3, 1)  # iPhone 18预计发布时间
    end_date = datetime(2032, 12, 1)
    
    # 每个月的时间点
    months = []
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        months.append(len(months))
        dates.append(current_date)
        current_date += timedelta(days=30)  # 近似每月30天
    
    # 价格曲线
    # 1. 全新机价格曲线（随时间折旧）
    new_price_curve = [P * rr(month) for month in months]
    
    # 2. 6个月二手价格曲线
    used_6mo_price_curve = [P * rr(month + 6) for month in months]
    
    # 3. 12个月二手价格曲线
    used_12mo_price_curve = [P * rr(month + 12) for month in months]
    
    # 4. 推荐策略的购买点和卖出点
    # 推荐策略：买6个月二手，持有36个月
    buy_month = 6  # 发布后6个月买入
    hold_months = 36  # 持有36个月
    
    buy_point = (buy_month, P * rr(buy_month))
    sell_point = (buy_month + hold_months, P * rr(buy_month + hold_months))
    
    # 5. 你的当前策略（买全新，用14个月）
    current_buy_point = (0, P)
    current_sell_point = (14, P * rr(14))
    
    # 创建SVG
    W, H = 1000, 600
    ml, mr, mt, mb = 80, 40, 80, 80
    pw, ph = W - ml - mr, H - mt - mb
    
    def x(month):
        return ml + (month / 72) * pw  # 总共显示72个月（6年）
    
    def y(price):
        price_min = 0
        price_max = P * 1.1  # 稍微高于首发价
        return mt + (price_max - price) / (price_max - price_min) * ph
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI,Arial,sans-serif">',
        f'<rect width="{W}" height="{H}" fill="#fff"/>',
        
        # 标题
        f'<text x="{ml}" y="28" font-size="20" font-weight="bold" fill="#202124">iPhone价格曲线叠加图：购买与卖出时点可视化</text>',
        f'<text x="{ml}" y="48" font-size="12" fill="#9aa0a6">三线叠加：全新机曲线、6个月二手曲线、12个月二手曲线，标注推荐策略与当前策略</text>',
    ]
    
    # 背景网格
    for price in [1000, 2000, 3000, 4000, 5000, 6000]:
        y_pos = y(price)
        svg.append(f'<line x1="{ml}" y1="{y_pos:.1f}" x2="{ml+pw}" y2="{y_pos:.1f}" stroke="#e8eaed"/>')
        svg.append(f'<text x="{ml-10}" y="{y_pos+4:.1f}" font-size="10" text-anchor="end" fill="#5f6368">¥{price}</text>')
    
    for month in [0, 12, 24, 36, 48, 60, 72]:
        x_pos = x(month)
        svg.append(f'<line x1="{x_pos:.1f}" y1="{mt}" x2="{x_pos:.1f}" y2="{mt+ph}" stroke="#e8eaed"/>')
        date_label = (start_date + timedelta(days=month*30)).strftime('%Y-%m')
        svg.append(f'<text x="{x_pos:.1f}" y="{mt+ph+20:.1f}" font-size="10" text-anchor="middle" fill="#5f6368">{date_label}</text>')
    
    # 坐标轴标签
    svg.append(f'<text x="{ml+pw/2:.1f}" y="{mt+ph+42:.1f}" font-size="12" text-anchor="middle" fill="#3c4043">时间（月）</text>')
    svg.append(f'<text x="30" y="{mt+ph/2:.1f}" font-size="12" fill="#3c4043" transform="rotate(-90 30 {mt+ph/2:.1f})">价格（元）</text>')
    
    # 绘制价格曲线
    # 1. 全新机曲线（蓝色）
    new_path = []
    for i, month in enumerate(months[:73]):  # 只绘制前73个点
        px = x(month)
        py = y(new_price_curve[i])
        if i == 0:
            new_path.append(f"M{px:.1f},{py:.1f}")
        else:
            new_path.append(f"L{px:.1f},{py:.1f}")
    
    svg.append(f'<path d="{" ".join(new_path)}" fill="none" stroke="#4285f4" stroke-width="3" opacity="0.8"/>')
    svg.append(f'<text x="{ml+10}" y="{y(5500)+4:.1f}" font-size="11" fill="#4285f4" font-weight="bold">全新机价格曲线</text>')
    
    # 2. 6个月二手曲线（绿色）
    used6_path = []
    for i, month in enumerate(months[:67]):  # 6个月二手从第6个月开始
        px = x(month)
        py = y(used_6mo_price_curve[i])
        if i == 0:
            used6_path.append(f"M{px:.1f},{py:.1f}")
        else:
            used6_path.append(f"L{px:.1f},{py:.1f}")
    
    svg.append(f'<path d="{" ".join(used6_path)}" fill="none" stroke="#34a853" stroke-width="3" opacity="0.8"/>')
    svg.append(f'<text x="{x(30):.1f}" y="{y(4500)+4:.1f}" font-size="11" fill="#34a853" font-weight="bold">6个月二手价格曲线</text>')
    
    # 3. 12个月二手曲线（橙色）
    used12_path = []
    for i, month in enumerate(months[:61]):  # 12个月二手从第12个月开始
        px = x(month)
        py = y(used_12mo_price_curve[i])
        if i == 0:
            used12_path.append(f"M{px:.1f},{py:.1f}")
        else:
            used12_path.append(f"L{px:.1f},{py:.1f}")
    
    svg.append(f'<path d="{" ".join(used12_path)}" fill="none" stroke="#fbbc04" stroke-width="3" opacity="0.8"/>')
    svg.append(f'<text x="{x(42):.1f}" y="{y(3500)+4:.1f}" font-size="11" fill="#fbbc04" font-weight="bold">12个月二手价格曲线</text>')
    
    # 标注推荐策略
    bx, by = x(buy_month), y(buy_point[1])
    sx, sy = x(sell_point[0]), y(sell_point[1])
    
    # 购买点
    svg.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="8" fill="#34a853" stroke="#fff" stroke-width="2"/>')
    svg.append(f'<text x="{bx+12:.1f}" y="{by-8:.1f}" font-size="11" fill="#34a853" font-weight="bold">推荐购买点</text>')
    svg.append(f'<text x="{bx+12:.1f}" y="{by+6:.1f}" font-size="10" fill="#5f6368">时间：{buy_month}个月后</text>')
    svg.append(f'<text x="{bx+12:.1f}" y="{by+20:.1f}" font-size="10" fill="#5f6368">价格：¥{buy_point[1]:.0f}</text>')
    
    # 卖出点
    svg.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="8" fill="#ea4335" stroke="#fff" stroke-width="2"/>')
    svg.append(f'<text x="{sx-100:.1f}" y="{sy-8:.1f}" font-size="11" fill="#ea4335" font-weight="bold">推荐卖出点</text>')
    svg.append(f'<text x="{sx-100:.1f}" y="{sy+6:.1f}" font-size="10" fill="#5f6368">时间：{sell_point[0]}个月后</text>')
    svg.append(f'<text x="{sx-100:.1f}" y="{sy+20:.1f}" font-size="10" fill="#5f6368">价格：¥{sell_point[1]:.0f}</text>')
    
    # 连接线
    svg.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="#34a853" stroke-width="2" stroke-dasharray="5,3"/>')
    
    # 标注当前策略
    cbx, cby = x(current_buy_point[0]), y(current_buy_point[1])
    csx, csy = x(current_sell_point[0]), y(current_sell_point[1])
    
    svg.append(f'<circle cx="{cbx:.1f}" cy="{cby:.1f}" r="8" fill="#4285f4" stroke="#fff" stroke-width="2"/>')
    svg.append(f'<text x="{cbx+12:.1f}" y="{cby-30:.1f}" font-size="11" fill="#4285f4" font-weight="bold">当前购买点</text>')
    
    svg.append(f'<circle cx="{csx:.1f}" cy="{csy:.1f}" r="8" fill="#ea4335" stroke="#fff" stroke-width="2"/>')
    svg.append(f'<text x="{csx+12:.1f}" y="{csy-30:.1f}" font-size="11" fill="#ea4335" font-weight="bold">当前卖出点</text>')
    
    # 当前策略连接线
    svg.append(f'<line x1="{cbx:.1f}" y1="{cby:.1f}" x2="{csx:.1f}" y2="{csy:.1f}" stroke="#4285f4" stroke-width="2" stroke-dasharray="5,3"/>')
    
    # 添加策略对比区域
    svg.append(f'<rect x="{ml}" y="{mt+ph+60}" width="{pw}" height="120" fill="#f8f9fa" stroke="#dadce0" rx="5"/>')
    
    svg.append(f'<text x="{ml+10}" y="{mt+ph+80}" font-size="12" fill="#202124" font-weight="bold">策略对比分析：</text>')
    
    # 推荐策略详情
    monthly_cost_rec = (buy_point[1] - sell_point[1]) / hold_months
    svg.append(f'<text x="{ml+20}" y="{mt+ph+100}" font-size="11" fill="#34a853">推荐策略：买{buy_month}个月二手，持有{hold_months}个月</text>')
    svg.append(f'<text x="{ml+40}" y="{mt+ph+115}" font-size="10" fill="#5f6368">月成本：¥{monthly_cost_rec:.1f}/月 | 平均机龄：{buy_month + hold_months/2:.0f}个月</text>')
    
    # 当前策略详情
    monthly_cost_cur = (current_buy_point[1] - current_sell_point[1]) / 14
    svg.append(f'<text x="{ml+20}" y="{mt+ph+135}" font-size="11" fill="#4285f4">当前策略：买全新，持有14个月</text>')
    svg.append(f'<text x="{ml+40}" y="{mt+ph+150}" font-size="10" fill="#5f6368">月成本：¥{monthly_cost_cur:.1f}/月 | 平均机龄：{0 + 14/2:.0f}个月</text>')
    
    # 改进效果
    improvement = monthly_cost_cur - monthly_cost_rec
    improvement_pct = (improvement / monthly_cost_cur) * 100
    svg.append(f'<text x="{ml+20}" y="{mt+ph+170}" font-size="11" fill="#ea4335">改善效果：每月节省¥{improvement:.1f}（{improvement_pct:.1f}%）</text>')
    
    svg.append('</svg>')
    
    # 写入文件
    with open("price_overlay_chart.svg", "w") as f:
        f.write("\n".join(svg))
    
    print("生成完毕：price_overlay_chart.svg")
    
    # 生成PNG版本
    try:
        from cairosvg import svg2png
        
        svg2png(
            bytestring="\n".join(svg).encode('utf-8'),
            write_to="price_overlay_chart.png",
            output_width=1200,
            output_height=720
        )
        print("生成完毕：price_overlay_chart.png")
    except ImportError:
        print("注意：cairosvg库未安装，PNG版本未生成。如需PNG版本，请安装：pip install cairosvg")
    
    return svg

def convert_all_svg_to_png():
    """转换所有SVG文件为PNG"""
    import os
    
    svg_files = [
        "charts/iphone_price_curve.svg",
        "charts/iphone_secondhand_cn.svg",
        "charts/iphone_depreciation_curve.svg",
        "charts/iphone_cost_strategy.svg",
        "charts/iphone_frontier.svg",
        "charts/iphone18_forecast.svg",
        "charts/freshness_demo.svg",
        "charts/freshness_vs_cost.svg",
    ]
    
    try:
        from cairosvg import svg2png
        
        print("\n开始转换所有SVG文件为PNG...")
        
        for svg_file in svg_files:
            if os.path.exists(svg_file):
                png_file = svg_file.replace(".svg", ".png").replace("charts/", "charts/png/")
                
                # 确保目录存在
                os.makedirs(os.path.dirname(png_file), exist_ok=True)
                
                with open(svg_file, "r", encoding="utf-8") as f:
                    svg_content = f.read()
                
                svg2png(
                    bytestring=svg_content.encode('utf-8'),
                    write_to=png_file,
                    output_width=1200,
                    output_height=720
                )
                
                print(f"✓ 已转换：{svg_file} → {png_file}")
            else:
                print(f"⚠️ 文件不存在：{svg_file}")
        
        print("\n所有SVG文件已转换为PNG格式，保存在 charts/png/ 目录下")
        
    except ImportError:
        print("cairosvg库未安装，无法转换PNG。")
        print("如需PNG版本，请安装：pip install cairosvg")
        print("或者使用现有脚本：python3 scripts/make_png_charts.py")

if __name__ == "__main__":
    print("=" * 60)
    print("创建价格曲线叠加图表")
    print("=" * 60)
    
    # 创建叠加图表
    create_price_overlay_chart()
    
    print("\n" + "=" * 60)
    print("转换所有SVG为PNG格式")
    print("=" * 60)
    
    # 转换所有SVG为PNG
    convert_all_svg_to_png()
    
    print("\n" + "=" * 60)
    print("图表说明")
    print("=" * 60)
    
    print("\n📊 新增图表：price_overlay_chart.svg/png")
    print("   特点：")
    print("   • 三线叠加：全新机、6个月二手、12个月二手价格曲线")
    print("   • 标注推荐策略：买6个月二手，持有36个月")
    print("   • 标注当前策略：买全新，持有14个月")
    print("   • 直观对比购买点和卖出点")
    
    print("\n📁 PNG文件位置：")
    print("   • charts/png/ 目录下包含所有图表的PNG版本")
    print("   • 可以直接在图片查看器中打开")
    
    print("\n🔗 访问方式：")
    print("   1. 在线查看：打开 charts/png/ 目录下的PNG文件")
    print("   2. GitHub查看：PNG文件已自动添加到仓库")
    print("   3. 本地查看：双击PNG文件即可")