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
