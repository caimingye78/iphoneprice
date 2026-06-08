#!/usr/bin/env python3
import json
import math
from datetime import datetime, timedelta

# 读取历史数据和前沿数据
with open("data/frontier_data.json", "r") as f:
    frontier_data = json.load(f)

pareto_points = frontier_data["pareto"]  # 前沿点 (平均机龄, 月成本, a, h)

# 残值率函数
lambda_val = -math.log(0.68) / 14

def rr(t):
    return math.exp(-lambda_val * t)

P = 5999  # iPhone 标准款首发价
TARGET_COST = 90

def find_best_strategy_on_frontier(target_cost):
    """在前沿曲线上找到最接近目标月成本的策略"""
    best_point = None
    min_diff = float('inf')
    
    for avg_age, cost, a, h in pareto_points:
        diff = abs(cost - target_cost)
        if diff < min_diff:
            min_diff = diff
            best_point = (avg_age, cost, a, h)
    
    return best_point

def generate_concrete_plan():
    """生成具体操作计划"""
    print("=" * 60)
    print("月成本90元的具体操作方案（基于历史数据优化）")
    print("=" * 60)
    
    # 在前沿曲线上找到最佳点
    best_on_frontier = find_best_strategy_on_frontier(TARGET_COST)
    
    if best_on_frontier:
        avg_age, cost, a, h = best_on_frontier
        print(f"\n1. 前沿曲线上的最佳匹配点：")
        print(f"   • 平均机龄：{avg_age}个月")
        print(f"   • 月成本：¥{cost:.1f}/月")
        print(f"   • 策略：买{a}个月二手，持有{h}个月")
        print(f"   • 距离目标：相差¥{abs(cost - TARGET_COST):.1f}")
    
    # 寻找更多可选方案
    print("\n2. 其他可行方案（月成本85-95元）：")
    
    strategies = []
    for a_test in range(0, 37, 3):  # 机龄0-36个月
        for h_test in range(12, 61, 3):  # 持有12-60个月
            buy_price = P * rr(a_test)
            sell_price = P * rr(a_test + h_test)
            monthly_cost = (buy_price - sell_price) / h_test
            avg_age_test = a_test + h_test / 2
            
            if 85 <= monthly_cost <= 95:
                strategies.append({
                    'a': a_test,
                    'h': h_test,
                    'cost': monthly_cost,
                    'avg_age': avg_age_test,
                    'buy_price': buy_price,
                    'sell_price': sell_price
                })
    
    # 按新鲜度分组
    fresh = [s for s in strategies if s['avg_age'] <= 18]
    balanced = [s for s in strategies if 18 < s['avg_age'] <= 30]
    saving = [s for s in strategies if s['avg_age'] > 30]
    
    print("\n   A. 较新方案（平均机龄≤18个月）：")
    for s in fresh[:2]:
        print(f"      • 买{s['a']}个月二手，持有{s['h']}个月")
        print(f"        平均机龄：{s['avg_age']:.1f}个月，成本：¥{s['cost']:.1f}/月")
    
    print("\n   B. 平衡方案（平均机龄19-30个月）：")
    for s in balanced[:2]:
        print(f"      • 买{s['a']}个月二手，持有{s['h']}个月")
        print(f"        平均机龄：{s['avg_age']:.1f}个月，成本：¥{s['cost']:.1f}/月")
    
    print("\n   C. 省钱方案（平均机龄>30个月）：")
    for s in saving[:2]:
        print(f"      • 买{s['a']}个月二手，持有{s['h']}个月")
        print(f"        平均机龄：{s['avg_age']:.1f}个月，成本：¥{s['cost']:.1f}/月")
    
    # 推荐综合方案
    print("\n3. 推荐的综合操作方案：")
    print("-" * 40)
    
    # 方案A：较新体验型
    plan_a = fresh[0] if fresh else strategies[0]
    
    # 方案B：平衡型（推荐）
    plan_b = None
    for s in strategies:
        if 20 <= s['avg_age'] <= 25 and 88 <= s['cost'] <= 92:
            plan_b = s
            break
    
    if not plan_b:
        plan_b = balanced[0] if balanced else strategies[len(strategies)//2]
    
    print(f"\n   【方案A】较新体验型：")
    print(f"   • 买入：iPhone发布后{plan_a['a']}个月（约{plan_a['a']//12}年{plan_a['a']%12}个月二手）")
    print(f"   • 持有：{plan_a['h']}个月（{plan_a['h']//12}年{plan_a['h']%12}个月）")
    print(f"   • 月成本：¥{plan_a['cost']:.1f}/月")
    print(f"   • 平均机龄：{plan_a['avg_age']:.1f}个月")
    
    print(f"\n   【方案B】平衡推荐型（⭐推荐）：")
    print(f"   • 买入：iPhone发布后{plan_b['a']}个月（约{plan_b['a']//12}年{plan_b['a']%12}个月二手）")
    print(f"   • 持有：{plan_b['h']}个月（{plan_b['h']//12}年{plan_b['h']%12}个月）")
    print(f"   • 月成本：¥{plan_b['cost']:.1f}/月")
    print(f"   • 平均机龄：{plan_b['avg_age']:.1f}个月")
    
    # 具体时间线（考虑iPhone 18推迟到2027-03发布）
    print("\n4. 具体时间线操作（以iPhone 18为例）：")
    print("-" * 40)
    
    release_date = datetime(2027, 3, 1)  # iPhone 18预计2027-03发布
    
    print(f"\n   📱 iPhone 18 阶段：")
    buy_date_18 = release_date + timedelta(days=plan_b['a'] * 30)
    sell_date_18 = buy_date_18 + timedelta(days=plan_b['h'] * 30)
    
    print(f"   1. {buy_date_18.strftime('%Y-%m')}：买入 iPhone 18")
    print(f"      机龄：{plan_b['a']}个月，价格：约¥{plan_b['buy_price']:.0f}")
    
    print(f"   2. {sell_date_18.strftime('%Y-%m')}：卖出 iPhone 18")
    print(f"      总机龄：{plan_b['a'] + plan_b['h']}个月，回收价：约¥{plan_b['sell_price']:.0f}")
    
    # 下一阶段
    print(f"\n   📱 下一代 iPhone 阶段：")
    # 使用标准最优策略：买6个月二手，持有24个月
    next_a = 6
    next_h = 24
    next_buy_price = P * rr(next_a)
    next_sell_price = P * rr(next_a + next_h)
    next_cost = (next_buy_price - next_sell_price) / next_h
    
    buy_date_next = sell_date_18
    sell_date_next = buy_date_next + timedelta(days=next_h * 30)
    
    print(f"   3. {buy_date_next.strftime('%Y-%m')}：买入下一代 iPhone")
    print(f"      策略：买{next_a}个月二手，持有{next_h}个月")
    print(f"      月成本：约¥{next_cost:.1f}/月")
    
    print(f"   4. {sell_date_next.strftime('%Y-%m')}：卖出，进入下一轮")
    
    # 长期统计
    print(f"\n5. 长期成本统计：")
    print("-" * 40)
    
    total_months = plan_b['h'] + next_h
    total_cost = (plan_b['cost'] * plan_b['h']) + (next_cost * next_h)
    avg_cost = total_cost / total_months
    
    print(f"   • 第一阶段（iPhone 18）：{plan_b['h']}个月，¥{plan_b['cost']:.1f}/月")
    print(f"   • 第二阶段（下一代）：{next_h}个月，¥{next_cost:.1f}/月")
    print(f"   • 两阶段平均：¥{avg_cost:.1f}/月")
    print(f"   • 总时长：{total_months}个月（{total_months//12}年{total_months%12}个月）")
    
    # 与传统策略对比
    print(f"\n6. 与你当前策略对比：")
    print("-" * 40)
    
    your_current_cost = 137  # 你的当前月成本
    your_avg_age = 7         # 你的平均机龄
    
    print(f"   • 你当前：平均机龄{your_avg_age}个月，月成本¥{your_current_cost}/月")
    print(f"   • 推荐方案：平均机龄{plan_b['avg_age']:.1f}个月，月成本¥{plan_b['cost']:.1f}/月")
    print(f"   • 改善：新鲜度 -{(plan_b['avg_age'] - your_avg_age):.1f}个月，成本 -¥{(your_current_cost - plan_b['cost']):.1f}/月")
    print(f"   • 节省比例：{(your_current_cost - plan_b['cost']) / your_current_cost * 100:.1f}%")
    
    return plan_b

def analyze_delayed_impact_on_strategy(plan):
    """分析发布时间推迟对具体策略的影响"""
    print("\n" + "=" * 60)
    print("iPhone 18推迟发布对策略的影响分析")
    print("=" * 60)
    
    print(f"\n假设原计划发布时间：2026-09")
    print(f"实际预计发布时间：2027-03（推迟6个月）")
    print(f"\n你的目标策略：买{plan['a']}个月二手，持有{plan['h']}个月")
    
    print(f"\n影响分析：")
    print("1. 时间点平移：所有操作相应推迟6个月")
    print("2. 策略有效性：✅ 完全有效（折旧规律不变）")
    print("3. 月成本：✅ 不变（仍为¥{plan['cost']:.1f}/月）")
    print("4. 新鲜度：✅ 不变（平均机龄仍为{plan['avg_age']:.1f}个月）")
    
    print(f"\n具体调整：")
    print(f"• 原计划抄底时间：2026-09 + {plan['a']}个月 = 2026-{(9+plan['a']//12)%12:02d}")
    print(f"• 调整后抄底时间：2027-03 + {plan['a']}个月 = 2027-{(3+plan['a']//12)%12:02d}")
    print(f"• 持有结束时间：相应推迟6个月")
    
    print(f"\n⚠️ 注意事项：")
    print("1. 后续产品发布节奏可能受影响")
    print("2. 如果整体产品线推迟，可能需要跨代购买")
    print("3. 保持策略灵活性，根据实际发布情况微调")
    
    print(f"\n✅ 核心结论：")
    print("发布时间推迟不影响策略原则，只需调整时间点。")
    print("'买准新机+用满周期'的策略逻辑依然有效。")

if __name__ == "__main__":
    best_plan = generate_concrete_plan()
    analyze_delayed_impact_on_strategy(best_plan)
    
    print("\n" + "=" * 60)
    print("最终操作指南")
    print("=" * 60)
    
    print(f"\n📋 你的具体操作步骤：")
    print(f"1. 等待 iPhone 18 正式发布（预计2027-03）")
    print(f"2. 发布后等待 {best_plan['a']} 个月（约到2027-{(3+best_plan['a']//12)%12:02d}）")
    print(f"3. 以约¥{best_plan['buy_price']:.0f} 买入 iPhone 18（{best_plan['a']}个月二手）")
    print(f"4. 使用 {best_plan['h']} 个月（到2027-{(3+(best_plan['a']+best_plan['h'])//12)%12:02d}）")
    print(f"5. 以约¥{best_plan['sell_price']:.0f} 卖出 iPhone 18")
    print(f"6. 重复步骤1-5，进入下一轮")
    
    print(f"\n💰 成本预期：")
    print(f"• 目标月成本：¥{TARGET_COST}/月")
    print(f"• 实际月成本：¥{best_plan['cost']:.1f}/月")
    print(f"• 与你当前对比：节省 ¥{137 - best_plan['cost']:.1f}/月")
    print(f"• 年节省：¥{(137 - best_plan['cost']) * 12:.0f}元")
    
    print(f"\n📱 设备新鲜度：")
    print(f"• 平均机龄：{best_plan['avg_age']:.1f}个月")
    print(f"• 与你当前对比：+{best_plan['avg_age'] - 7:.1f}个月（稍微旧一点）")
    print(f"• 但仍然使用现代旗舰（仅差1-2代）")
    
    print(f"\n✅ 关键要点：")
    print("• 发布时间推迟 → 策略不变，时间点顺延")
    print("• 月成本90元 → 完全可行，有多个方案")
    print("• 最佳平衡 → 稍微牺牲新鲜度，大幅降低成本")
    print("• 长期坚持 → 形成'买准新+用满周期'的习惯")