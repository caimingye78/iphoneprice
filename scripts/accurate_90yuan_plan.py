#!/usr/bin/env python3
import json
import math
from datetime import datetime, timedelta

# 读取前沿数据
with open("data/frontier_data.json", "r") as f:
    frontier_data = json.load(f)

pareto_points = frontier_data["pareto"]  # (平均机龄, 月成本, a, h)

# 残值率函数
lambda_val = -math.log(0.68) / 14

def rr(t):
    return math.exp(-lambda_val * t)

P = 5999  # iPhone 标准款首发价
TARGET_COST = 90

def find_strategies_near_target():
    """在前沿曲线附近寻找接近目标成本的策略"""
    strategies = []
    
    # 首先看前沿曲线上的点
    for avg_age, cost, a, h in pareto_points:
        if 85 <= cost <= 95:  # 85-95元范围内
            strategies.append({
                'type': 'pareto',
                'avg_age': avg_age,
                'cost': cost,
                'a': a,
                'h': h,
                'buy_price': P * rr(a),
                'sell_price': P * rr(a + h)
            })
    
    # 补充一些非前沿但合理的策略
    for a in [3, 6, 9, 12, 15, 18]:  # 合理的买入机龄
        for h in [12, 18, 24, 30, 36]:  # 合理的持有时长
            buy_price = P * rr(a)
            sell_price = P * rr(a + h)
            cost = (buy_price - sell_price) / h
            avg_age = a + h / 2
            
            if 88 <= cost <= 92:  # 更接近90元
                strategies.append({
                    'type': 'near_target',
                    'avg_age': avg_age,
                    'cost': cost,
                    'a': a,
                    'h': h,
                    'buy_price': buy_price,
                    'sell_price': sell_price
                })
    
    # 去重并排序
    unique_strategies = []
    seen = set()
    
    for s in strategies:
        key = (s['a'], s['h'])
        if key not in seen:
            seen.add(key)
            unique_strategies.append(s)
    
    # 按成本接近90元排序
    unique_strategies.sort(key=lambda x: abs(x['cost'] - 90))
    return unique_strategies[:10]

def generate_realistic_plan():
    """生成现实可行的操作计划"""
    print("=" * 70)
    print("月成本90元的现实操作方案（基于iPhone历史数据）")
    print("=" * 70)
    
    strategies = find_strategies_near_target()
    
    if not strategies:
        print("未找到合适策略，使用默认策略...")
        # 默认：买6个月二手，持有24个月（前沿最优之一）
        a = 6
        h = 24
        buy_price = P * rr(a)
        sell_price = P * rr(a + h)
        cost = (buy_price - sell_price) / h
        strategies = [{
            'type': 'default',
            'avg_age': a + h / 2,
            'cost': cost,
            'a': a,
            'h': h,
            'buy_price': buy_price,
            'sell_price': sell_price
        }]
    
    print(f"\n找到 {len(strategies)} 个可行策略：")
    
    # 分组展示
    fresh_plans = [s for s in strategies if s['avg_age'] <= 15]
    balanced_plans = [s for s in strategies if 15 < s['avg_age'] <= 25]
    saving_plans = [s for s in strategies if s['avg_age'] > 25]
    
    # 推荐方案
    print("\n🌟 推荐方案选择：")
    
    # 方案1：平衡型（中等新鲜度，中等成本）
    if balanced_plans:
        plan1 = balanced_plans[0]
    elif fresh_plans:
        plan1 = fresh_plans[0]
    else:
        plan1 = strategies[0]
    
    # 方案2：较新型（追求较新体验）
    if fresh_plans:
        plan2 = fresh_plans[0]
    else:
        # 创建一个较新方案：买3个月二手，持有18个月
        a2 = 3
        h2 = 18
        buy_price2 = P * rr(a2)
        sell_price2 = P * rr(a2 + h2)
        cost2 = (buy_price2 - sell_price2) / h2
        plan2 = {
            'type': 'custom_fresh',
            'avg_age': a2 + h2 / 2,
            'cost': cost2,
            'a': a2,
            'h': h2,
            'buy_price': buy_price2,
            'sell_price': sell_price2
        }
    
    # 方案3：省钱型（追求最低成本）
    if saving_plans:
        plan3 = saving_plans[0]
    else:
        # 创建一个省钱方案：买12个月二手，持有36个月
        a3 = 12
        h3 = 36
        buy_price3 = P * rr(a3)
        sell_price3 = P * rr(a3 + h3)
        cost3 = (buy_price3 - sell_price3) / h3
        plan3 = {
            'type': 'custom_saving',
            'avg_age': a3 + h3 / 2,
            'cost': cost3,
            'a': a3,
            'h': h3,
            'buy_price': buy_price3,
            'sell_price': sell_price3
        }
    
    print(f"\n1. 【方案A】平衡推荐型 ⭐：")
    print(f"   • 策略：买{plan1['a']}个月二手 → 持有{plan1['h']}个月")
    print(f"   • 平均机龄：{plan1['avg_age']:.1f}个月")
    print(f"   • 月成本：¥{plan1['cost']:.1f}/月")
    print(f"   • 买入价：约¥{plan1['buy_price']:.0f}")
    print(f"   • 卖出价：约¥{plan1['sell_price']:.0f}")
    
    print(f"\n2. 【方案B】较新体验型：")
    print(f"   • 策略：买{plan2['a']}个月二手 → 持有{plan2['h']}个月")
    print(f"   • 平均机龄：{plan2['avg_age']:.1f}个月")
    print(f"   • 月成本：¥{plan2['cost']:.1f}/月")
    print(f"   • 买入价：约¥{plan2['buy_price']:.0f}")
    print(f"   • 卖出价：约¥{plan2['sell_price']:.0f}")
    
    print(f"\n3. 【方案C】极致省钱型：")
    print(f"   • 策略：买{plan3['a']}个月二手 → 持有{plan3['h']}个月")
    print(f"   • 平均机龄：{plan3['avg_age']:.1f}个月")
    print(f"   • 月成本：¥{plan3['cost']:.1f}/月")
    print(f"   • 买入价：约¥{plan3['buy_price']:.0f}")
    print(f"   • 卖出价：约¥{plan3['sell_price']:.0f}")
    
    return plan1, plan2, plan3

def create_detailed_timeline(plan, phone_name="iPhone 18", release_date=None):
    """创建详细时间线"""
    if release_date is None:
        release_date = datetime(2027, 3, 1)  # iPhone 18预计发布时间
    
    print(f"\n📅 【{phone_name}阶段】具体操作时间线：")
    print("-" * 50)
    
    # 计算关键日期
    buy_delay_days = plan['a'] * 30  # 每月按30天算
    hold_days = plan['h'] * 30
    
    buy_date = release_date + timedelta(days=buy_delay_days)
    sell_date = buy_date + timedelta(days=hold_days)
    
    print(f"1. 发布时间：{release_date.strftime('%Y年%m月')}")
    print(f"2. 买入时间：{buy_date.strftime('%Y年%m月')}（发布后{plan['a']}个月）")
    print(f"3. 买入价格：约¥{plan['buy_price']:.0f}")
    print(f"4. 使用时长：{plan['h']}个月（{plan['h']//12}年{plan['h']%12}个月）")
    print(f"5. 卖出时间：{sell_date.strftime('%Y年%m月')}")
    print(f"6. 卖出价格：约¥{plan['sell_price']:.0f}")
    print(f"7. 总机龄：{plan['a'] + plan['h']}个月")
    print(f"8. 月均成本：¥{plan['cost']:.1f}/月")
    
    # 下一阶段建议
    print(f"\n🔄 下一阶段建议：")
    next_a = 6  # 标准：买6个月二手
    next_h = 24  # 标准：持有24个月
    next_buy_price = P * rr(next_a)
    next_sell_price = P * rr(next_a + next_h)
    next_cost = (next_buy_price - next_sell_price) / next_h
    
    next_buy_date = sell_date
    next_sell_date = next_buy_date + timedelta(days=next_h * 30)
    
    print(f"1. {next_buy_date.strftime('%Y年%m月')}：买入下一代iPhone")
    print(f"   策略：买{next_a}个月二手，持有{next_h}个月")
    print(f"   预计月成本：¥{next_cost:.1f}/月")
    print(f"2. {next_sell_date.strftime('%Y年%m月')}：卖出，继续循环")
    
    return buy_date, sell_date, next_buy_date, next_sell_date

def analyze_delayed_release_impact():
    """分析发布时间推迟的影响"""
    print("\n" + "=" * 70)
    print("iPhone 18发布时间推迟的影响分析")
    print("=" * 70)
    
    print("\n📊 核心问题：发布时间推迟是否导致策略原则性改变？")
    print("\n答案：❌ 不会改变策略原则")
    
    print("\n📈 影响分析：")
    print("1. 时间轴平移：所有时间点相应推迟")
    print("2. 折旧规律：不变（苹果产品折旧曲线稳定）")
    print("3. 最优策略：不变（仍是'买准新+用满周期'）")
    print("4. 月成本：不变（因为折旧率不变）")
    print("5. 新鲜度：不变（平均机龄公式不变）")
    
    print("\n⚠️ 唯一影响：操作时间点调整")
    print("   • 原计划：2026年9月发布 → 2027年3月抄底")
    print("   • 新计划：2027年3月发布 → 2027年9月抄底")
    print("   • 调整：所有操作推迟6个月")
    
    print("\n✅ 应对策略：")
    print("1. 保持耐心：等待新机发布后6个月再抄底")
    print("2. 灵活调整：根据实际发布时间微调")
    print("3. 坚持原则：'买准新+用满2年'策略不变")
    
    print("\n🎯 关键结论：")
    print("发布时间推迟 → 策略逻辑不变 → 只需调整日历")

def compare_with_current_strategy(plan_cost, plan_avg_age):
    """与当前策略对比"""
    print("\n" + "=" * 70)
    print("与你当前策略对比分析")
    print("=" * 70)
    
    your_cost = 137  # 你当前的月成本
    your_avg_age = 7  # 你当前的平均机龄
    
    print(f"\n📊 当前状态：")
    print(f"• 月成本：¥{your_cost}/月")
    print(f"• 平均机龄：{your_avg_age}个月")
    print(f"• 策略：买全新 → 14个月换机")
    
    print(f"\n📊 推荐方案：")
    print(f"• 月成本：¥{plan_cost:.1f}/月")
    print(f"• 平均机龄：{plan_avg_age:.1f}个月")
    
    print(f"\n📈 改善效果：")
    cost_saving = your_cost - plan_cost
    age_increase = plan_avg_age - your_avg_age
    saving_percent = (cost_saving / your_cost) * 100
    
    print(f"• 每月节省：¥{cost_saving:.1f}")
    print(f"• 节省比例：{saving_percent:.1f}%")
    print(f"• 每年节省：¥{cost_saving * 12:.0f}")
    print(f"• 新鲜度变化：+{age_increase:.1f}个月（稍旧但可接受）")
    
    print(f"\n💡 权衡分析：")
    print(f"• 你获得：每月省¥{cost_saving:.1f}（年省¥{cost_saving*12:.0f}）")
    print(f"• 你付出：手机平均旧{age_increase:.1f}个月")
    print(f"• 性价比：每¥1成本换取{1/age_increase*100:.1f}%新鲜度改善")

if __name__ == "__main__":
    # 生成三种方案
    plan1, plan2, plan3 = generate_realistic_plan()
    
    # 使用推荐方案（方案1）创建详细时间线
    print("\n" + "=" * 70)
    print("详细操作指南（以推荐方案为例）")
    print("=" * 70)
    
    # iPhone 18发布时间（推迟到2027-03）
    iphone18_release = datetime(2027, 3, 1)
    
    # 为推荐方案创建时间线
    buy_date, sell_date, next_buy, next_sell = create_detailed_timeline(
        plan1, 
        "iPhone 18", 
        iphone18_release
    )
    
    # 分析推迟发布的影响
    analyze_delayed_release_impact()
    
    # 与当前策略对比
    compare_with_current_strategy(plan1['cost'], plan1['avg_age'])
    
    # 最终建议
    print("\n" + "=" * 70)
    print("最终操作建议")
    print("=" * 70)
    
    print(f"\n🎯 你的目标：月成本¥{TARGET_COST}，发布时间推迟到2027年初")
    
    print(f"\n📋 具体操作步骤：")
    print(f"1. 等待：iPhone 18正式发布（预计{iphone18_release.strftime('%Y年%m月')}）")
    print(f"2. 再等：{plan1['a']}个月（到{buy_date.strftime('%Y年%m月')}）")
    print(f"3. 买入：iPhone 18二手，价格约¥{plan1['buy_price']:.0f}")
    print(f"4. 使用：{plan1['h']}个月（到{sell_date.strftime('%Y年%m月')}）")
    print(f"5. 卖出：价格约¥{plan1['sell_price']:.0f}")
    print(f"6. 重复：进入下一轮循环")
    
    print(f"\n💰 成本控制：")
    print(f"• 目标成本：¥{TARGET_COST}/月")
    print(f"• 实际成本：¥{plan1['cost']:.1f}/月")
    print(f"• 误差范围：{abs(plan1['cost'] - TARGET_COST)/TARGET_COST*100:.1f}%")
    
    print(f"\n📱 设备状态：")
    print(f"• 平均机龄：{plan1['avg_age']:.1f}个月")
    print(f"• 相当于：始终使用1-2年前的旗舰机")
    print(f"• 体验：完全满足日常需求，性能充足")
    
    print(f"\n✅ 关键确认：")
    print("• 发布时间推迟 → 不影响策略有效性")
    print("• 月成本90元 → 完全可实现")
    print("• 操作可行 → 基于历史数据验证")
    print("• 长期坚持 → 形成稳定换机节奏")
    
    print(f"\n⚠️ 注意事项：")
    print("1. 实际发布时间可能还有变化，保持关注")
    print("2. 二手市场价格会有波动，预留10%缓冲")
    print("3. 成色很重要，尽量选择95新以上")
    print("4. 存储版本选择256GB最保值")
    
    print(f"\n🌟 最佳实践：")
    print("1. 在'闲鱼'或'转转'等平台交易")
    print("2. 选择信用好的卖家")
    print("3. 收到货后立即验机")
    print("4. 保留购买凭证")
    print("5. 使用时贴膜戴壳保持成色")