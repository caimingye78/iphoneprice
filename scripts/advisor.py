#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iPhone 购买策略顾问 (零依赖, 纯标准库)

根据折旧模型,输入参数即输出最省的买法、预计月成本与抄底时点。

用法:
  # 命令行参数模式
  python3 advisor.py --price 5999 --max-age 12 --years 2 --new-ok yes
  python3 advisor.py -p 5999 -a 6 -y 3

  # 交互问答模式 (不带参数直接运行)
  python3 advisor.py

参数:
  --price/-p     机型首发价 (元),默认 5999 (标准款)
  --max-age/-a   你能接受买入时手机的最大机龄 (月);0=只买全新,默认 12
  --years/-y     你打算用几年,默认 2 (年)。也可用 --months 指定月数
  --months/-m    打算用几个月 (覆盖 --years)
  --new-ok       是否愿意买全新 (yes/no),默认 yes
  --launch       该机型发布年月 YYYY-MM,用于推算抄底日历日期,默认 2026-09
"""
import sys, argparse

# ---- 残值曲线 rr(t): 回收价/首发价, t=机龄(月) ----
PTS = [(0,1.00),(6,0.82),(12,0.74),(14,0.70),(18,0.63),(24,0.55),
       (30,0.48),(36,0.42),(48,0.32),(60,0.25),(72,0.18),(84,0.12),(96,0.08)]

def rr(t):
    if t <= PTS[0][0]: return PTS[0][1]
    if t >= PTS[-1][0]: return PTS[-1][1]
    for (a,r0),(b,r1) in zip(PTS, PTS[1:]):
        if a <= t <= b:
            return r0 + (r1-r0)*(t-a)/(b-a)
    return PTS[-1][1]

def monthly_cost(P, buy_age, hold):
    """买入机龄 buy_age、持有 hold 个月的每月持有成本(元/月)"""
    return P*(rr(buy_age) - rr(buy_age+hold)) / hold

def cal(launch_ym, t):
    """launch_ym=(y,m), 返回机龄 t 个月时的日历 (年, 月)"""
    y, m = launch_ym
    idx = (m-1) + t
    return (y + idx//12, idx%12 + 1)

def fmt_ym(ym): return f"{ym[0]}-{ym[1]:02d}"

# ---------------- 核心建议 ----------------
def advise(P, max_age, hold_months, new_ok, launch_ym):
    lo_age = 0 if new_ok else 1
    # 候选买入机龄: 0..max_age, 步长1; 在该约束下找月成本最低
    best = None
    table = []
    step_ages = sorted(set([0,3,6,9,12,14,18,24,30,36] + [max_age]))
    for a in range(lo_age, max_age+1):
        c = monthly_cost(P, a, hold_months)
        if best is None or c < best[1]:
            best = (a, c)
    # 展示用的稀疏表
    for a in step_ages:
        if a < lo_age or a > max_age: continue
        table.append((a, P*rr(a), monthly_cost(P, a, hold_months)))

    buy_age, cost = best
    buy_price = P*rr(buy_age)
    sell_age = buy_age + hold_months
    sell_price = P*rr(sell_age)
    total_loss = buy_price - sell_price

    # 抄底日历点: 买入机龄对应的发布后日期, 并贴近最近的"新机发布后/双11"窗口
    buy_ym = cal(launch_ym, buy_age)

    # 与"买全新+只用12个月"基准对比
    base = monthly_cost(P, 0, 12)

    return {
        "buy_age": buy_age, "buy_price": buy_price,
        "hold": hold_months, "sell_age": sell_age, "sell_price": sell_price,
        "total_loss": total_loss, "cost": cost, "buy_ym": buy_ym,
        "base": base, "table": table,
    }

def dip_windows(launch_ym):
    """给出未来两年的抄底窗口(每年9月新机发布后 + 双11)"""
    wins = []
    for k in [12, 24]:  # 发布后第1、2个9月
        ym = cal(launch_ym, k)
        wins.append((k, fmt_ym(ym), "新一代发布后(价格台阶下跌)"))
        ym2 = cal(launch_ym, k+2)
        wins.append((k+2, fmt_ym(ym2), "双11促销低点"))
    return wins

def bar(v, vmax=140, width=30):
    n = int(round(v/vmax*width))
    return "#"*max(0,min(width,n))

def render(P, max_age, hold_months, new_ok, launch_ym, r):
    L = []
    yrs = hold_months/12
    L.append("="*52)
    L.append("           iPhone 购买策略建议")
    L.append("="*52)
    L.append(f"输入: 首发价¥{P:.0f} | 可接受最旧机龄{max_age}月 | "
             f"打算用{hold_months}月(≈{yrs:.1f}年) | 买全新:{'是' if new_ok else '否'}")
    L.append("")
    L.append("【最优买法】")
    if r["buy_age"] == 0:
        L.append(f"  买【全新】(¥{r['buy_price']:.0f})")
    else:
        L.append(f"  买【机龄约{r['buy_age']}月的二手】(¥{r['buy_price']:.0f}),"
                 f"约对应 {fmt_ym(r['buy_ym'])} 入手")
    L.append(f"  持有 {hold_months} 个月后,机龄{r['sell_age']}月,"
             f"预计回收 ¥{r['sell_price']:.0f}")
    L.append(f"  期间净损耗 ¥{r['total_loss']:.0f}")
    L.append("")
    L.append(f"  >> 每月真实成本 ≈ ¥{r['cost']:.1f}/月 <<")
    save = (1 - r['cost']/r['base'])*100
    L.append(f"     (相比'买全新只用1年'的¥{r['base']:.0f}/月,省 {save:.0f}%)")
    L.append("")
    L.append("【不同买入机龄的月成本对比】(持有时长固定为你的设定)")
    for a, bp, c in r["table"]:
        tag = "  <== 推荐" if a == r["buy_age"] else ""
        label = "全新" if a==0 else f"{a:>2}月二手"
        L.append(f"  {label}  买¥{bp:>4.0f}  {c:6.1f}元/月 |{bar(c)}{tag}")
    L.append("")
    L.append("【抄底时点】(基于每年9月发布会规律)")
    for t, yms, why in dip_windows(launch_ym):
        L.append(f"  {yms}  (机龄{t}月)  {why}")
    L.append("  提示: 旧机要在下一代发布前(8月底)出手,避免发布会后跳价。")
    L.append("")
    L.append("【一句话】")
    if r["cost"] <= 60:
        msg = "极致省钱档:用上一代/上两代准新机,持有期拉长,体验仍在线。"
    elif r["cost"] <= 90:
        msg = "性价比甜点:买准新、用满约2年,够新又省一大截。"
    else:
        msg = "偏尝鲜档:若想再省,把持有期延长到2-3年,或改买准新二手。"
    L.append(f"  {msg}")
    L.append("="*52)
    return "\n".join(L)

# ---------------- 输入解析 ----------------
def parse_launch(s):
    try:
        y, m = s.split("-"); return (int(y), int(m))
    except Exception:
        return (2026, 9)

def interactive():
    print("\n--- iPhone 购买策略顾问 (交互模式, 直接回车用默认值) ---\n")
    def ask(q, default, cast=float):
        s = input(f"{q} [默认 {default}]: ").strip()
        if not s: return default
        try: return cast(s)
        except Exception: return default
    P = ask("机型首发价(元)", 5999.0, float)
    new_ok_s = input("愿意买全新吗? (y/n) [默认 y]: ").strip().lower()
    new_ok = not new_ok_s.startswith("n")
    max_age = int(ask("能接受买入时最大机龄(月), 0=只买全新", 12, float))
    if not new_ok and max_age < 1: max_age = 1
    months = int(ask("打算用多少个月", 24, float))
    ls = input("该机型发布年月 YYYY-MM [默认 2026-09]: ").strip() or "2026-09"
    launch = parse_launch(ls)
    r = advise(P, max_age, months, new_ok, launch)
    print("\n" + render(P, max_age, months, new_ok, launch, r))

def main(argv):
    ap = argparse.ArgumentParser(add_help=True, description="iPhone 购买策略顾问")
    ap.add_argument("-p","--price", type=float, default=5999.0)
    ap.add_argument("-a","--max-age", type=int, default=12)
    ap.add_argument("-y","--years", type=float, default=2.0)
    ap.add_argument("-m","--months", type=int, default=None)
    ap.add_argument("--new-ok", choices=["yes","no"], default="yes")
    ap.add_argument("--launch", type=str, default="2026-09")
    ap.add_argument("-i","--interactive", action="store_true")
    args = ap.parse_args(argv)

    # 无参数 -> 交互模式
    if args.interactive or len(argv) == 0:
        interactive(); return

    months = args.months if args.months is not None else int(round(args.years*12))
    new_ok = (args.new_ok == "yes")
    max_age = args.max_age
    if not new_ok and max_age < 1: max_age = 1
    launch = parse_launch(args.launch)
    r = advise(args.price, max_age, months, new_ok, launch)
    print(render(args.price, max_age, months, new_ok, launch, r))

if __name__ == "__main__":
    main(sys.argv[1:])
