#!/usr/bin/env python3
"""Render all iPhone analysis charts to PNG using the dependency-free minipng."""
import os, json
from minipng import Canvas

OUT = os.path.join(os.path.dirname(__file__), "..", "charts", "png")
os.makedirs(OUT, exist_ok=True)

INK=(32,33,36); GREY=(95,99,104); LGREY=(218,220,224); GRID=(232,234,237)
BLUE=(66,133,244); RED=(234,67,53); GREEN=(52,168,83); YELLOW=(251,188,5); PURPLE=(161,66,244)

# ---------- residual model (shared) ----------
pts=[(0,1.00),(6,0.82),(12,0.74),(14,0.70),(18,0.63),(24,0.55),(30,0.48),
     (36,0.42),(48,0.32),(60,0.25),(72,0.18),(84,0.12),(96,0.08)]
def rr(t):
    if t<=pts[0][0]:return pts[0][1]
    if t>=pts[-1][0]:return pts[-1][1]
    for (a,r0),(b,r1) in zip(pts,pts[1:]):
        if a<=t<=b:return r0+(r1-r0)*(t-a)/(b-a)
    return pts[-1][1]
P=6000.0

def axes(c, ml,mt,pw,ph):
    c.line(ml,mt,ml,mt+ph,INK,2)
    c.line(ml,mt+ph,ml+pw,mt+ph,INK,2)

# ================= Chart 1: launch prices =================
def chart_launch():
    years=[2016,2017,2018,2019,2020,2021,2022,2023,2024,2025]
    series={
      "SE/E":[399,None,None,None,399,None,429,None,None,599],
      "STD":[649,699,749,699,799,799,799,799,799,799],
      "PLUS/AIR":[769,799,None,None,None,None,899,899,899,999],
      "PRO":[None,999,999,999,999,999,999,999,999,1099],
      "PRO MAX":[None,None,1099,1099,1099,1099,1099,1199,1199,1199]}
    cols={"SE/E":GREEN,"STD":BLUE,"PLUS/AIR":PURPLE,"PRO":YELLOW,"PRO MAX":RED}
    W,H=1100,640; c=Canvas(W,H)
    ml,mt,mr,mb=90,70,250,70; pw=W-ml-mr; ph=H-mt-mb
    ymin,ymax=350,1250
    c.text(ml,28,"IPHONE US LAUNCH PRICE  USD  2016-2025",INK,3)
    X=lambda yr: ml+(yr-2016)/(2025-2016)*pw
    Y=lambda v: mt+(ymax-v)/(ymax-ymin)*ph
    for v in range(400,1300,100):
        c.line(ml,Y(v),ml+pw,Y(v),GRID,1); c.text_right(ml-10,Y(v)-7,"$"+str(v),GREY,2)
    for yr in years: c.text_center(X(yr),mt+ph+12,str(yr),GREY,2)
    axes(c,ml,mt,pw,ph)
    for name,vals in series.items():
        col=cols[name]; prev=None
        for i,v in enumerate(vals):
            if v is None: prev=None; continue
            x,y=X(years[i]),Y(v)
            if prev: c.line(prev[0],prev[1],x,y,col,3)
            prev=(x,y)
        for i,v in enumerate(vals):
            if v is not None: c.disc(X(years[i]),Y(v),4,col)
    lx,ly=ml+pw+30,mt+10
    c.text(lx,ly-22,"TIER",INK,2)
    for i,(name,col) in enumerate(cols.items()):
        yy=ly+i*34; c.rect(lx,yy,26,6,col); c.text(lx+34,yy-6,name,INK,2)
    c.save(os.path.join(OUT,"iphone_price_curve.png")); print("price_curve.png")

# ================= Chart 2: depreciation =================
def chart_depr():
    W,H=1000,560; c=Canvas(W,H)
    ml,mt,mr,mb=90,70,40,70; pw=W-ml-mr; ph=H-mt-mb
    ymax=6000; xmax=96
    c.text(ml,28,"RESALE VALUE VS AGE  (STD IPHONE, RMB)",INK,3)
    X=lambda m: ml+m/xmax*pw; Y=lambda v: mt+(ymax-v)/ymax*ph
    for v in range(0,6001,1000):
        c.line(ml,Y(v),ml+pw,Y(v),GRID,1); c.text_right(ml-10,Y(v)-7,str(v),GREY,2)
    for m in range(0,97,12):
        c.text_center(X(m),mt+ph+12,str(m),GREY,2)
    c.text_center(ml+pw/2,mt+ph+40,"AGE (MONTHS)",GREY,2)
    axes(c,ml,mt,pw,ph)
    c.rect(X(0),mt,X(12)-X(0),ph,(252,232,230))  # highlight yr1
    ms=list(range(0,97,3)); prev=None
    for m in ms:
        v=P*rr(m); x,y=X(m),Y(v)
        if prev: c.line(prev[0],prev[1],x,y,RED,3)
        prev=(x,y)
    c.text(X(13),mt+ph-40,"YEAR 1 = STEEPEST DROP",RED,2)
    c.save(os.path.join(OUT,"iphone_depreciation_curve.png")); print("depreciation_curve.png")

# ================= Chart 3: monthly cost vs hold =================
def cost(a,h): return P*(rr(a)-rr(a+h))/h
def chart_cost():
    W,H=1050,580; c=Canvas(W,H)
    ml,mt,mr,mb=90,80,240,70; pw=W-ml-mr; ph=H-mt-mb
    ymax=160; xmax=72
    c.text(ml,28,"MONTHLY COST VS HOLD MONTHS",INK,3)
    c.text(ml,52,"LOWER + RIGHT = CHEAPER",GREY,2)
    X=lambda m: ml+m/xmax*pw; Y=lambda v: mt+(ymax-v)/ymax*ph
    for v in range(0,161,20):
        c.line(ml,Y(v),ml+pw,Y(v),GRID,1); c.text_right(ml-10,Y(v)-7,str(v),GREY,2)
    for m in range(6,73,6): c.text_center(X(m),mt+ph+12,str(m),GREY,2)
    c.text_center(ml+pw/2,mt+ph+40,"HOLD (MONTHS)",GREY,2)
    axes(c,ml,mt,pw,ph)
    holds=list(range(6,73,3))
    cfg=[(0,RED,"NEW"),(12,YELLOW,"USED 1Y"),(24,BLUE,"USED 2Y"),(36,GREEN,"USED 3Y")]
    for a,col,_ in cfg:
        prev=None
        for h in holds:
            x,y=X(h),Y(cost(a,h))
            if prev: c.line(prev[0],prev[1],x,y,col,3)
            prev=(x,y)
    # user point
    c.disc(X(14),Y(137),5,INK); c.text(X(14)+10,Y(137)-8,"YOU 137",INK,2)
    lx,ly=ml+pw+30,mt+10
    c.text(lx,ly-22,"BUY AS",INK,2)
    for i,(a,col,lab) in enumerate(cfg):
        yy=ly+i*30; c.rect(lx,yy,26,6,col); c.text(lx+34,yy-6,lab,INK,2)
    c.text(lx,ly+140,"HOLD 24MO:",GREY,2)
    for i,t in enumerate(["NEW 112","1Y 80","2Y 57","3Y 42"]):
        c.text(lx,ly+165+i*24,t,GREY,2)
    c.save(os.path.join(OUT,"iphone_cost_strategy.png")); print("cost_strategy.png")

# ================= Chart 4: frontier =================
def chart_frontier():
    strats=[]
    for a in range(0,37,6):
        for h in range(12,49,6):
            strats.append((a+h/2.0,cost(a,h),a,h))
    def dom(p):
        for o in strats:
            if o is p: continue
            if o[0]<=p[0] and o[1]<=p[1] and (o[0]<p[0] or o[1]<p[1]): return True
        return False
    par=sorted([p for p in strats if not dom(p)])
    W,H=1050,600; c=Canvas(W,H)
    ml,mt,mr,mb=90,80,40,80; pw=W-ml-mr; ph=H-mt-mb
    xmax=60; ymin,ymax=20,140
    c.text(ml,28,"NEW TECH VS SAVING : FRONTIER",INK,3)
    c.text(ml,52,"LEFT=NEWER   DOWN=CHEAPER   RED=BEST",GREY,2)
    X=lambda a: ml+a/xmax*pw; Y=lambda v: mt+(ymax-v)/(ymax-ymin)*ph
    for v in range(20,141,20):
        c.line(ml,Y(v),ml+pw,Y(v),GRID,1); c.text_right(ml-10,Y(v)-7,str(v),GREY,2)
    for a in range(0,61,6): c.text_center(X(a),mt+ph+12,str(a),GREY,2)
    c.text_center(ml+pw/2,mt+ph+40,"AVG PHONE AGE (MONTHS)",GREY,2)
    axes(c,ml,mt,pw,ph)
    c.rect(X(0),mt,X(10)-X(0),ph,(252,232,230))
    c.text(X(0.5),mt+12,"SUCKER ZONE 130",RED,2)
    c.rect(X(11),Y(100),X(24)-X(11),Y(75)-Y(100),(230,244,234))
    c.text(X(12),Y(78),"SWEET SPOT",GREEN,2)
    for a,v,_,_ in strats: c.disc(X(a),Y(v),3,LGREY)
    prev=None
    for a,v,_,_ in par:
        x,y=X(a),Y(v)
        if prev: c.line(prev[0],prev[1],x,y,RED,3)
        prev=(x,y)
    for a,v,_,_ in par: c.disc(X(a),Y(v),4,RED)
    c.disc(X(7),Y(137),5,INK); c.text(X(7)+10,Y(137)+2,"YOU 137",INK,2)
    c.text(X(18)+6,Y(85)+14,"USED 6MO + HOLD 2Y = 85",INK,2)
    c.save(os.path.join(OUT,"iphone_frontier.png")); print("frontier.png")

# ================= Chart 5: launch vs used (RMB) =================
def chart_used():
    models=["7","8","X","XR","11","12","13","14","15","16"]
    yrs=[2016,2017,2017,2018,2019,2020,2021,2022,2023,2024]
    launch=[5388,5888,8388,6499,5499,6299,5999,5999,5999,5999]
    used=[350,600,950,1000,1450,2050,2950,3550,4250,5050]
    W,H=1050,600; c=Canvas(W,H)
    ml,mt,mr,mb=90,80,210,80; pw=W-ml-mr; ph=H-mt-mb
    ymax=9000; n=len(models)
    c.text(ml,28,"LAUNCH VS USED PRICE  (CN, RMB)",INK,3)
    c.text(ml,52,"USED = EARLY 2026 APPROX",GREY,2)
    X=lambda i: ml+i/(n-1)*pw; Y=lambda v: mt+(ymax-v)/ymax*ph
    for v in range(0,9001,1000):
        c.line(ml,Y(v),ml+pw,Y(v),GRID,1); c.text_right(ml-10,Y(v)-7,str(v),GREY,2)
    for i,m in enumerate(models):
        c.text_center(X(i),mt+ph+12,m,INK,2); c.text_center(X(i),mt+ph+30,str(yrs[i]),GREY,2)
    axes(c,ml,mt,pw,ph)
    def plot(vals,col):
        prev=None
        for i,v in enumerate(vals):
            x,y=X(i),Y(v)
            if prev: c.line(prev[0],prev[1],x,y,col,3)
            prev=(x,y)
        for i,v in enumerate(vals): c.disc(X(i),Y(v),4,col)
    plot(launch,BLUE); plot(used,RED)
    lx,ly=ml+pw+30,mt+10
    c.rect(lx,ly,26,6,BLUE); c.text(lx+34,ly-6,"LAUNCH",INK,2)
    c.rect(lx,ly+30,26,6,RED); c.text(lx+34,ly+24,"USED NOW",INK,2)
    c.text(lx,ly+80,"RESIDUAL:",GREY,2)
    for i,m in enumerate(models):
        c.text(lx,ly+105+i*22,m+": "+str(round(used[i]/launch[i]*100))+"%",GREY,2)
    c.save(os.path.join(OUT,"iphone_secondhand_cn.png")); print("secondhand_cn.png")

if __name__=="__main__":
    chart_launch(); chart_depr(); chart_cost(); chart_frontier(); chart_used()
    print("All PNGs ->", os.path.abspath(OUT))


# ================= Chart 6: iPhone 18 forecast =================
def chart_iphone18():
    """iPhone 18价格预测图"""
    W,H=1050,580; c=Canvas(W,H)
    ml,mt,mr,mb=90,80,200,80; pw=W-ml-mr; ph=H-mt-mb
    
    # 时间点数据
    dates = ["2026-09", "2027-03", "2027-09", "2027-11", "2028-09", "2030-09"]
    ages = [0, 6, 12, 14, 24, 48]
    prices = [5999, 4919, 4439, 4199, 3299, 1920]
    residuals = [100, 82, 74, 70, 55, 32]
    
    n = len(dates)
    ymax = 7000
    xmax = 48  # 48个月
    
    c.text(ml,28,"IPHONE 18 PRICE FORECAST 2026-2030",INK,3)
    c.text(ml,52,"PREDICTED RESALE VALUE OVER TIME",GREY,2)
    
    X=lambda m: ml+m/xmax*pw
    Y=lambda v: mt+(ymax-v)/ymax*ph
    
    # 网格
    for v in range(0,7001,1000):
        c.line(ml,Y(v),ml+pw,Y(v),GRID,1)
        c.text_right(ml-10,Y(v)-7,str(v),GREY,2)
    
    for i, age in enumerate(ages):
        c.text_center(X(age),mt+ph+12,str(age),GREY,2)
        if i < len(dates):
            c.text_center(X(age),mt+ph+30,dates[i],GREY,2)
    
    axes(c,ml,mt,pw,ph)
    
    # 绘制价格曲线
    prev = None
    for i in range(n):
        x = X(ages[i])
        y = Y(prices[i])
        if prev:
            c.line(prev[0], prev[1], x, y, RED, 3)
        prev = (x, y)
        c.disc(x, y, 6, RED)
    
    # 标注关键点
    key_points = [
        (0, "LAUNCH ¥5999"),
        (6, "6MO ¥4919"),
        (12, "1Y ¥4439"),
        (14, "¥4199"),
        (24, "2Y ¥3299"),
        (48, "4Y ¥1920")
    ]
    
    for age, label in key_points:
        x = X(age)
        y = Y(P * rr(age))
        c.text(x+8, y-8, label, INK, 2)
    
    # 推荐购买点
    buy_age = 6
    sell_age = 42  # 6+36
    buy_x = X(buy_age)
    buy_y = Y(P * rr(buy_age))
    sell_x = X(sell_age)
    sell_y = Y(P * rr(sell_age))
    
    c.disc(buy_x, buy_y, 8, GREEN)
    c.disc(sell_x, sell_y, 8, BLUE)
    
    # 图例
    lx, ly = ml+pw+30, mt+10
    c.text(lx, ly-22, "KEY POINTS", INK, 2)
    c.rect(lx, ly, 26, 6, RED); c.text(lx+34, ly-6, "PRICE CURVE", INK, 2)
    c.rect(lx, ly+30, 26, 6, GREEN); c.text(lx+34, ly+24, "BUY POINT", INK, 2)
    c.rect(lx, ly+60, 26, 6, BLUE); c.text(lx+34, ly+54, "SELL POINT", INK, 2)
    
    # 策略信息
    monthly_cost = (P*rr(buy_age) - P*rr(sell_age)) / (sell_age - buy_age)
    c.text(lx, ly+100, "RECOMMENDED:", GREY, 2)
    c.text(lx, ly+120, f"BUY: {buy_age}MO", GREY, 2)
    c.text(lx, ly+140, f"HOLD: 36MO", GREY, 2)
    c.text(lx, ly+160, f"COST: ¥{monthly_cost:.1f}/MO", GREY, 2)
    
    c.save(os.path.join(OUT,"iphone18_forecast.png"))
    print("iphone18_forecast.png")

# ================= Chart 7: freshness demo =================
def chart_freshness():
    """新鲜度演示图"""
    W,H=1000,600; c=Canvas(W,H)
    ml,mt,mr,mb=80,80,40,80; pw=W-ml-mr; ph=H-mt-mb
    
    c.text(ml,28,"FRESHNESS DEMO: 4 STRATEGIES",INK,3)
    c.text(ml,52,"UPPER: AGE OVER TIME | LOWER: MONTHLY COST",GREY,2)
    
    # 四种策略
    strategies = [
        {"name": "NEW+1Y", "a": 0, "h": 12, "color": RED},
        {"name": "NEW+2Y", "a": 0, "h": 24, "color": BLUE},
        {"name": "6MO+2Y", "a": 6, "h": 24, "color": GREEN},
        {"name": "NEW+3Y", "a": 0, "h": 36, "color": YELLOW}
    ]
    
    # 上部分：机龄随时间变化
    top_h = ph/2 - 40
    X=lambda month: ml + (month/60) * pw
    Y_top=lambda age: mt + (age/60) * top_h
    
    c.rect(ml, mt, pw, top_h, (248,249,250))
    c.text(ml, mt-10, "AGE OVER TIME (MONTHS)", GREY, 2)
    
    # 时间轴
    for month in [0, 12, 24, 36, 48, 60]:
        x = X(month)
        c.line(x, mt, x, mt+top_h, LGREY, 1)
        c.text_center(x, mt+top_h+12, str(month), GREY, 2)
    
    # 绘制每种策略
    for s in strategies:
        col = s["color"]
        x1 = X(s["a"])
        y1 = Y_top(s["a"])
        x2 = X(s["a"] + s["h"])
        y2 = Y_top(s["a"] + s["h"])
        
        c.line(x1, y1, x2, y2, col, 3)
        c.disc(x1, y1, 4, col)
        c.disc(x2, y2, 4, col)
        
        # 平均机龄点
        avg_age = s["a"] + s["h"]/2
        avg_x = X(avg_age)
        avg_y = Y_top(avg_age)
        c.disc(avg_x, avg_y, 6, col)
        
        c.text(avg_x+8, avg_y-8, s["name"], INK, 2)
    
    # 分隔线
    sep_y = mt + ph/2
    c.line(ml, sep_y, ml+pw, sep_y, INK, 2)
    
    # 下部分：月成本
    bottom_h = ph/2 - 40
    bottom_y = sep_y + 20
    Y_cost=lambda cost: bottom_y + (cost-20)/(140-20) * bottom_h
    
    c.rect(ml, bottom_y, pw, bottom_h, (248,249,250))
    c.text(ml, bottom_y-10, "MONTHLY COST (RMB)", GREY, 2)
    
    # 成本刻度
    for cost in [20, 40, 60, 80, 100, 120, 140]:
        y = Y_cost(cost)
        c.line(ml, y, ml+pw, y, LGREY, 1)
        c.text_right(ml-10, y-7, str(cost), GREY, 2)
    
    # 计算并绘制成本点
    for s in strategies:
        col = s["color"]
        cost = cost(s["a"], s["h"])
        x = X(s["a"] + s["h"]/2)
        y = Y_cost(cost)
        
        c.disc(x, y, 6, col)
        c.text(x+8, y-8, f"{s['name']} ¥{cost:.1f}", INK, 2)
    
    # 图例
    lx, ly = ml+20, bottom_y + bottom_h + 20
    c.text(lx, ly-10, "STRATEGIES:", GREY, 2)
    for i, s in enumerate(strategies):
        yy = ly + i*24
        c.rect(lx, yy, 20, 6, s["color"])
        c.text(lx+30, yy-6, f"{s['name']}: a={s['a']}, h={s['h']}, avg={s['a']+s['h']/2}mo", GREY, 2)
    
    c.save(os.path.join(OUT,"freshness_demo.png"))
    print("freshness_demo.png")

# ================= Chart 8: freshness vs cost scatter =================
def chart_freshness_scatter():
    """新鲜度vs月成本散点图"""
    W,H=1050,600; c=Canvas(W,H)
    ml,mt,mr,mb=90,80,200,80; pw=W-ml-mr; ph=H-mt-mb
    
    # 生成策略点
    strats = []
    for a in range(0, 37, 3):
        for h in range(6, 49, 3):
            avg_age = a + h/2
            monthly_cost = cost(a, h)
            if monthly_cost <= 150:  # 只显示合理的成本
                strats.append((avg_age, monthly_cost, a, h))
    
    # 前沿点（简化计算）
    pareto = []
    for target_age in range(6, 61, 6):
        best_cost = 200
        best_point = None
        for age, cost_val, a, h in strats:
            if abs(age - target_age) <= 3 and cost_val < best_cost:
                best_cost = cost_val
                best_point = (age, cost_val, a, h)
        if best_point:
            pareto.append(best_point)
    
    # 排序
    pareto.sort(key=lambda x: x[0])
    
    xmax = 60
    ymin, ymax = 20, 140
    
    c.text(ml,28,"FRESHNESS VS MONTHLY COST SCATTER",INK,3)
    c.text(ml,52,"4 STRATEGIES MARKED ON FRONTIER",GREY,2)
    
    X=lambda a: ml+a/xmax*pw
    Y=lambda v: mt+(ymax-v)/(ymax-ymin)*ph
    
    # 网格
    for v in range(20,141,20):
        c.line(ml,Y(v),ml+pw,Y(v),GRID,1)
        c.text_right(ml-10,Y(v)-7,str(v),GREY,2)
    
    for a in range(0,61,6):
        c.text_center(X(a),mt+ph+12,str(a),GREY,2)
    
    c.text_center(ml+pw/2,mt+ph+40,"AVG PHONE AGE (MONTHS)",GREY,2)
    axes(c,ml,mt,pw,ph)
    
    # 所有策略点
    for age, cost_val, _, _ in strats:
        c.disc(X(age), Y(cost_val), 2, LGREY)
    
    # 前沿曲线
    prev = None
    for age, cost_val, _, _ in pareto:
        x, y = X(age), Y(cost_val)
        if prev:
            c.line(prev[0], prev[1], x, y, RED, 3)
        prev = (x, y)
        c.disc(x, y, 4, RED)
    
    # 四种策略标注
    highlight = [
        (0, 12, RED, "NEW+1Y", "○"),
        (0, 24, BLUE, "NEW+2Y", "△"),
        (6, 24, GREEN, "6MO+2Y", "□"),
        (0, 36, YELLOW, "NEW+3Y", "◇")
    ]
    
    for a, h, col, name, symbol in highlight:
        avg_age = a + h/2
        cost_val = cost(a, h)
        x, y = X(avg_age), Y(cost_val)
        
        # 符号
        if symbol == "○":
            c.circle(x, y, 7, col, 2)
        elif symbol == "△":
            c.triangle(x, y-7, x+6, y+5, x-6, y+5, col, 2)
        elif symbol == "□":
            c.rect(x-6, y-6, 12, 12, col, 2)
        elif symbol == "◇":
            c.diamond(x, y, 8, col, 2)
        
        c.disc(x, y, 3, col)
        c.text(x+10, y-8, name, INK, 2)
        c.text(x+10, y+6, f"¥{cost_val:.1f}", GREY, 2)
    
    # 用户点
    user_age = 7
    user_cost = 137
    c.disc(X(user_age), Y(user_cost), 8, INK)
    c.text(X(user_age)+10, Y(user_cost), "YOU ¥137", INK, 2)
    
    # 图例
    lx, ly = ml+pw+30, mt+10
    c.text(lx, ly-22, "4 STRATEGIES", INK, 2)
    
    symbols = [
        (RED, "○", "NEW+1Y", "¥140.7"),
        (BLUE, "△", "NEW+2Y", "¥120.9"),
        (GREEN, "□", "6MO+2Y", "¥102.5"),
        (YELLOW, "◇", "NEW+3Y", "¥104.8")
    ]
    
    for i, (col, sym, name, price) in enumerate(symbols):
        yy = ly + i*30
        if sym == "○":
            c.circle(lx+10, yy, 5, col, 2)
        elif sym == "△":
            c.triangle(lx+10, yy-5, lx+16, yy+3, lx+4, yy+3, col, 2)
        elif sym == "□":
            c.rect(lx+4, yy-5, 12, 10, col, 2)
        elif sym == "◇":
            c.diamond(lx+10, yy, 5, col, 2)
        
        c.text(lx+25, yy-6, name, INK, 2)
        c.text(lx+25, yy+6, price, GREY, 2)
    
    c.save(os.path.join(OUT,"freshness_vs_cost.png"))
    print("freshness_vs_cost.png")

# ================= Chart 9: price overlay chart =================
def chart_price_overlay():
    """价格曲线叠加图"""
    W,H=1100,700; c=Canvas(W,H)
    ml,mt,mr,mb=100,90,250,90; pw=W-ml-mr; ph=H-mt-mb
    
    c.text(ml,28,"PRICE CURVE OVERLAY: BUY & SELL POINTS",INK,3)
    c.text(ml,52,"3 LINES: NEW, 6MO USED, 12MO USED",GREY,2)
    
    # 时间范围：0-72个月（6年）
    xmax = 72
    ymax = 7000
    
    X=lambda month: ml + (month/xmax) * pw
    Y=lambda price: mt + (ymax-price)/ymax * ph
    
    # 网格
    for price in [1000,2000,3000,4000,5000,6000]:
        y = Y(price)
        c.line(ml, y, ml+pw, y, GRID, 1)
        c.text_right(ml-10, y-7, str(price), GREY, 2)
    
    for month in [0,12,24,36,48,60,72]:
        x = X(month)
        c.line(x, mt, x, mt+ph, LGREY, 1)
        c.text_center(x, mt+ph+12, str(month), GREY, 2)
        # 日期标签
        year = 2027 + month//12
        month_name = (3 + month%12) % 12
        if month_name == 0: month_name = 12
        date_label = f"{year}-{month_name:02d}"
        c.text_center(x, mt+ph+30, date_label, GREY, 2)
    
    axes(c,ml,mt,pw,ph)
    
    # 三条价格曲线
    months = list(range(0, 73, 3))
    
    # 全新机曲线（蓝色）
    new_prev = None
    for m in months:
        price = P * rr(m)
        x, y = X(m), Y(price)
        if new_prev:
            c.line(new_prev[0], new_prev[1], x, y, BLUE, 3)
        new_prev = (x, y)
    c.text(ml+10, Y(5500), "NEW PHONE", BLUE, 2)
    
    # 6个月二手曲线（绿色）- 从第6个月开始
    used6_prev = None
    for m in months:
        if m >= 6:
            price = P * rr(m)
            x, y = X(m), Y(price)
            if used6_prev:
                c.line(used6_prev[0], used6_prev[1], x, y, GREEN, 3)
            used6_prev = (x, y)
    c.text(X(30), Y(4500), "6MO USED", GREEN, 2)
    
    # 12个月二手曲线（橙色）- 从第12个月开始
    used12_prev = None
    for m in months:
        if m >= 12:
            price = P * rr(m)
            x, y = X(m), Y(price)
            if used12_prev:
                c.line(used12_prev[0], used12_prev[1], x, y, YELLOW, 3)
            used12_prev = (x, y)
    c.text(X(42), Y(3500), "12MO USED", YELLOW, 2)
    
    # 推荐策略点
    buy_age = 6
    hold_months = 36
    buy_price = P * rr(buy_age)
    sell_price = P * rr(buy_age + hold_months)
    
    buy_x, buy_y = X(buy_age), Y(buy_price)
    sell_x, sell_y = X(buy_age + hold_months), Y(sell_price)
    
    # 购买点（绿色）
    c.disc(buy_x, buy_y, 8, GREEN)
    c.text(buy_x+12, buy_y-20, "REC BUY", GREEN, 2)
    c.text(buy_x+12, buy_y-8, f"¥{buy_price:.0f}", GREY, 2)
    
    # 卖出点（红色）
    c.disc(sell_x, sell_y, 8, RED)
    c.text(sell_x-60, sell_y-20, "REC SELL", RED, 2)
    c.text(sell_x-60, sell_y-8, f"¥{sell_price:.0f}", GREY, 2)
    
    # 连接线
    c.line(buy_x, buy_y, sell_x, sell_y, GREEN, 2, dash=[5,3])
    
    # 当前策略点
    current_buy_x, current_buy_y = X(0), Y(P)
    current_sell_x, current_sell_y = X(14), Y(P * rr(14))
    
    c.disc(current_buy_x, current_buy_y, 8, BLUE)
    c.text(current_buy_x+12, current_buy_y-30, "CUR BUY", BLUE, 2)
    
    c.disc(current_sell_x, current_sell_y, 8, RED)
    c.text(current_sell_x+12, current_sell_y-30, "CUR SELL", RED, 2)
    
    c.line(current_buy_x, current_buy_y, current_sell_x, current_sell_y, BLUE, 2, dash=[5,3])
    
    # 策略对比区域
    info_y = mt+ph+60
    info_h = 120
    c.rect(ml, info_y, pw, info_h, (248,249,250))
    
    c.text(ml+10, info_y+20, "STRATEGY COMPARISON:", INK, 2)
    
    # 推荐策略
    rec_cost = (buy_price - sell_price) / hold_months
    c.text(ml+20, info_y+45, "RECOMMENDED: BUY 6MO USED, HOLD 36MO", GREEN, 2)
    c.text(ml+40, info_y+60, f"MONTHLY COST: ¥{rec_cost:.1f} | AVG AGE: {buy_age+hold_months/2:.0f}MO", GREY, 2)
    
    # 当前策略
    cur_cost = (P - P*rr(14)) / 14
    c.text(ml+20, info_y+85, "CURRENT: BUY NEW, HOLD 14MO", BLUE, 2)
    c.text(ml+40, info_y+100, f"MONTHLY COST: ¥{cur_cost:.1f} | AVG AGE: {0+14/2:.0f}MO", GREY, 2)
    
    # 改进效果
    improvement = cur_cost - rec_cost
    improvement_pct = (improvement / cur_cost) * 100
    c.text(ml+20, info_y+125, f"IMPROVEMENT: SAVE ¥{improvement:.1f}/MO ({improvement_pct:.1f}%)", RED, 2)
    
    # 图例
    lx, ly = ml+pw+30, mt+10
    c.text(lx, ly-22, "LEGEND", INK, 2)
    
    legends = [
        (BLUE, "NEW CURVE"),
        (GREEN, "6MO USED"),
        (YELLOW, "12MO USED"),
        (GREEN, "REC BUY POINT"),
        (RED, "SELL POINT"),
        (BLUE, "CUR BUY POINT")
    ]
    
    for i, (col, text) in enumerate(legends):
        yy = ly + i*25
        c.rect(lx, yy, 20, 6, col)
        c.text(lx+30, yy-6, text, INK, 2)
    
    c.save(os.path.join(OUT,"price_overlay_chart.png"))
    print("price_overlay_chart.png")

# ================= 主函数 =================
if __name__=="__main__":
    chart_launch()
    chart_depr()
    chart_cost()
    chart_frontier()
    chart_used()
    chart_iphone18()
    chart_freshness()
    chart_freshness_scatter()
    chart_price_overlay()
    print("All PNGs ->", os.path.abspath(OUT))