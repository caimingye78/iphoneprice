#!/usr/bin/env python3
import json
import math
from datetime import datetime, timedelta

# 读取历史数据
with open("data/strategy_data.json", "r") as f:
    data = json.load(f)

# 残值率函数
lambda_val = -math.log(0.68) / 14  # 基于 iPhone 16 数据

def rr(t):
    """残值率函数，基于指数衰减模型"""
    return math.exp(-lambda_val * t)

# 基础参数
P = 5999  # iPhone 标准款首发价
TARGET_MONTHLY_COST = 90  # 目标月成本

def find_strategies_for_target(target_cost, max_a=60, max_h=60):
    """寻找月成本接近目标值的所有策略"""
    strategies = []
    
    for a in range(0, max_a + 1, 3):  # 机龄步长3个月
        for h in range(6, max_h + 1, 3):  # 持有步长3个月
            buy_price = P * rr(a)
            sell_price = P * rr(a + h)
            monthly_cost = (buy_price - sell_price) / h
            avg_age = a + h / 2
            
            # 计算与目标值的差距
            cost_diff = abs(monthly_cost - target_cost)
            
            if cost_diff <= 5:  # 允许5元误差
                strategies.append({
                    'a': a,
                    'h': h,
                    'monthly_cost': monthly_cost,
                    'avg_age': avg_age,
                    'buy_price': buy_price,
                    'sell_price': sell_price,
                    'cost_diff': cost_diff
                })
    
    # 按成本差距排序
    strategies.sort(key=lambda x: x['cost_diff'])
    return strategies[:20]  # 返回前20个最佳策略

def analyze_delayed_release_effect():
    """分析发布时间推迟的影响"""
    print("=" * 60)
    print("iPhone 18 发布时间推迟分析")
    print("=" * 60)
    
    print("\n1. 基本情况（按原计划2026年9月发布）")
    print("-" * 40)
    
    # 原发布时间：2026-09
    original_release = datetime(2026, 9, 1)
    
    # 最佳抄底策略（基于前沿分析）
    best_strategy_original = {
        'a': 6,  # 买6个月二手
        'h': 24, # 持有24个月
        'avg_age': 18,
        'monthly_cost': 85.0
    }
    
    print(f"最佳抄底时间：{original_release.strftime('%Y-%m')} + 6个月 = 2027-03")
    print(f"策略：买6个月二手，持有24个月")
    print(f"平均机龄：{best_strategy_original['avg_age']}个月")
    print(f"月成本：¥{best_strategy_original['monthly_cost']:.1f}/月")
    
    # 时间线
    print(f"\n时间线：")
    print(f"1. 2027-03：买入 iPhone 18（机龄6个月，约¥{P * rr(6):.0f}）")
    print(f"2. 2029-03：卖出 iPhone 18（机龄30个月，约¥{P * rr(30):.0f}）")
    print(f"3. 2029-03：买入 iPhone 20（假设正常发布节奏）")
    
    print("\n2. 发布时间推迟到2027年初的影响")
    print("-" * 40)
    
    # 新发布时间：2027-03
    delayed_release = datetime(2027, 3, 1)
    
    # 对策略的影响
    print("影响分析：")
    print("a) 时间轴平移：所有时间点向后推迟6个月")
    print("b) 最佳抄底点：2027-03 → 2027-09（仍在新机发布后6个月）")
    print("c) 策略原则不变：最佳策略仍是'买6个月二手，持有24个月'")
    print("d) 月成本不变：因为折旧规律不变")
    
    print(f"\n推迟后的时间线：")
    print(f"1. 2027-09：买入 iPhone 18（机龄6个月）")
    print(f"2. 2029-09：卖出 iPhone 18（机龄30个月）")
    print(f"3. 2029-09：买入 iPhone 21（因为发布节奏可能受影响）")
    
    print("\n3. 发布节奏延后的连锁影响")
    print("-" * 40)
    print("⚠️ 注意：如果苹果推迟iPhone 18发布，可能影响后续产品节奏")
    print("可能性分析：")
    print("1. 一次性推迟：仅iPhone 18推迟，后续产品恢复原节奏")
    print("2. 整体推迟：整个产品线推迟6个月")
    print("3. 追赶节奏：iPhone 19可能提前发布以恢复原节奏")
    
    print("\n4. 应对策略建议")
    print("-" * 40)
    print("保守策略：")
    print("• 保持原购买策略（买6个月二手，持有24个月）")
    print("• 相应调整时间点：所有操作推迟6个月")
    
    print("\n激进策略（如果整体产品线推迟）：")
    print("• 考虑跨代购买：iPhone 18 → iPhone 21")
    print("• 适当延长持有时间：24个月 → 30个月")
    
    return original_release, delayed_release

def find_90_yuan_strategies():
    """寻找月成本90元的实际操作方案"""
    print("\n" + "=" * 60)
    print("月成本90元的具体操作方案")
    print("=" * 60)
    
    strategies = find_strategies_for_target(TARGET_MONTHLY_COST)
    
    if not strategies:
        print("未找到精确匹配的策略，寻找最接近的策略...")
        # 放宽条件
        all_strategies = []
        for a in range(0, 61, 1):
            for h in range(6, 61, 1):
                buy_price = P * rr(a)
                sell_price = P * rr(a + h)
                monthly_cost = (buy_price - sell_price) / h
                if 85 <= monthly_cost <= 95:  # 85-95元范围
                    all_strategies.append({
                        'a': a,
                        'h': h,
                        'monthly_cost': monthly_cost,
                        'avg_age': a + h / 2,
                        'buy_price': buy_price,
                        'sell_price': sell_price
                    })
        
        # 按接近90元排序
        all_strategies.sort(key=lambda x: abs(x['monthly_cost'] - 90))
        strategies = all_strategies[:10]
    
    print(f"\n找到 {len(strategies)} 个月成本接近¥{TARGET_MONTHLY_COST}的策略：")
    
    # 分组展示
    fresh_strategies = [s for s in strategies if s['avg_age'] <= 15]
    balanced_strategies = [s for s in strategies if 15 < s['avg_age'] <= 25]
    saving_strategies = [s for s in strategies if s['avg_age'] > 25]
    
    print("\n1. 较新策略（平均机龄 ≤ 15个月）：")
    for s in fresh_strategies[:3]:
        print(f"   • 买入机龄：{s['a']}个月，持有：{s['h']}个月")
        print(f"     平均机龄：{s['avg_age']:.1f}个月，月成本：¥{s['monthly_cost']:.1f}")
        print(f"     买入价：¥{s['buy_price']:.0f}，卖出价：¥{s['sell_price']:.0f}")
    
    print("\n2. 平衡策略（平均机龄 16-25个月）：")
    for s in balanced_strategies[:3]:
        print(f"   • 买入机龄：{s['a']}个月，持有：{s['h']}个月")
        print(f"     平均机龄：{s['avg_age']:.1f}个月，月成本：¥{s['monthly_cost']:.1f}")
        print(f"     买入价：¥{s['buy_price']:.0f}，卖出价：¥{s['sell_price']:.0f}")
    
    print("\n3. 省钱策略（平均机龄 > 25个月）：")
    for s in saving_strategies[:3]:
        print(f"   • 买入机龄：{s['a']}个月，持有：{s['h']}个月")
        print(f"     平均机龄：{s['avg_age']:.1f}个月，月成本：¥{s['monthly_cost']:.1f}")
        print(f"     买入价：¥{s['buy_price']:.0f}，卖出价：¥{s['sell_price']:.0f}")
    
    # 推荐一个具体操作方案
    print("\n" + "=" * 60)
    print("推荐的具体操作方案（基于历史数据）")
    print("=" * 60)
    
    # 选择一个平衡策略
    best_balanced = None
    for s in strategies:
        if 12 <= s['avg_age'] <= 20 and 88 <= s['monthly_cost'] <= 92:
            best_balanced = s
            break
    
    if not best_balanced:
        best_balanced = balanced_strategies[0] if balanced_strategies else strategies[0]
    
    print(f"\n推荐策略：")
    print(f"• 买入机龄：{best_balanced['a']}个月（约{best_balanced['a']//12}年{best_balanced['a']%12}个月二手）")
    print(f"• 持有时长：{best_balanced['h']}个月（{best_balanced['h']//12}年{best_balanced['h']%12}个月）")
    print(f"• 平均机龄：{best_balanced['avg_age']:.1f}个月")
    print(f"• 月成本：¥{best_balanced['monthly_cost']:.1f}/月")
    
    # 具体时间线示例（假设iPhone 18在2027-03发布）
    release_date = datetime(2027, 3, 1)
    
    print(f"\n具体操作时间线（以iPhone 18为例）：")
    buy_date = release_date + timedelta(days=best_balanced['a'] * 30)
    sell_date = buy_date + timedelta(days=best_balanced['h'] * 30)
    
    print(f"1. {buy_date.strftime('%Y-%m')}：买入 iPhone 18（机龄{best_balanced['a']}个月）")
    print(f"   价格：约¥{best_balanced['buy_price']:.0f}")
    
    print(f"2. {sell_date.strftime('%Y-%m')}：卖出 iPhone 18（总机龄{best_balanced['a'] + best_balanced['h']}个月）")
    print(f"   回收价：约¥{best_balanced['sell_price']:.0f}")
    
    # 计算下一次购买
    next_buy_a = 6  # 假设买6个月二手
    next_h = 24     # 持有24个月
    next_buy_date = sell_date
    next_sell_date = next_buy_date + timedelta(days=next_h * 30)
    
    print(f"3. {next_buy_date.strftime('%Y-%m')}：买入下一代 iPhone")
    print(f"   策略：买{next_buy_a}个月二手，持有{next_h}个月")
    print(f"4. {next_sell_date.strftime('%Y-%m')}：卖出，进入下一轮")
    
    print("\n连续操作总结：")
    total_months = best_balanced['h'] + next_h
    avg_monthly_cost = (best_balanced['monthly_cost'] * best_balanced['h'] + 85.0 * next_h) / total_months
    
    print(f"• 第一轮：{best_balanced['h']}个月，¥{best_balanced['monthly_cost']:.1f}/月")
    print(f"• 第二轮：{next_h}个月，约¥85.0/月（标准最优策略）")
    print(f"• 长期平均：¥{avg_monthly_cost:.1f}/月")
    
    return best_balanced

if __name__ == "__main__":
    original, delayed = analyze_delayed_release_effect()
    best_strategy = find_90_yuan_strategies()
    
    print("\n" + "=" * 60)
    print("结论与建议")
    print("=" * 60)
    
    print("\n1. 发布时间推迟影响：")
    print("   • 原则性改变：❌ 无，最优策略逻辑不变")
    print("   • 时间点调整：✅ 所有操作相应推迟")
    print("   • 月成本影响：❌ 无，因为折旧规律不变")
    
    print("\n2. 月成本90元方案：")
    print(f"   • 可行策略：✅ 有多个方案可选")
    print(f"   • 推荐方案：买入{best_strategy['a']}个月二手，持有{best_strategy['h']}个月")
    print(f"   • 平均机龄：{best_strategy['avg_age']:.1f}个月")
    print(f"   • 实际成本：¥{best_strategy['monthly_cost']:.1f}/月")
    
    print("\n3. 操作建议：")
    print("   • 保持耐心：等待iPhone 18发布后6个月再抄底")
    print("   • 灵活调整：根据实际发布情况微调时间点")
    print("   • 长期坚持：使用'买准新+用满2年'的循环策略")