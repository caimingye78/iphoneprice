#!/usr/bin/env python3
# 双机换机两条路线的"累计损耗"对比图
# 路线A：先买后卖（买新机时旧机并行持有，过渡期旧机闲置贬值）
# 路线B：先卖后买 + 备用机（旧机高点先卖，地板价备用机过渡，等新机合理价再入手）
#
# 损耗定义（与用户的方法一致）：
#   累计损耗(t) = 期初身家 - 当前身家
#   身家 = 现金 + 手中所有手机的当前回收价
# 即"为了从拥有旧机过渡到拥有新机，到目前为止一共消耗掉多少钱"。

import json

# 残值率曲线（与 iphone_frontier.py 一致：锚点线性插值）
pts = [(0,1.00),(6,0.82),(12,0.74),(14,0.70),(18,0.63),(24,0.55),
       (30,0.48),(36,0.42),(48,0.32),(60,0.25),(72,0.18),(84,0.12),(96,0.08)]
def rr(t):
    if t <= pts[0][0]: return pts[0][1]
    if t >= pts[-1][0]: return pts[-1][1]
    for (t0,r0),(t1,r1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            return r0 + (r1-r0)*(t-t0)/(t1-t0)
    return pts[-1][1]

# ---- 场景参数（示意性，单位：元 / 月）----
P        = 6000.0   # 机型基准价（标准款），残值=P*rr(机龄)
OLD_AGE0 = 14       # 旧主力机在第0个月时的机龄（约满一年多，正处发布前高点）
PL       = 6000.0   # 新一代发布价（A 路线按发布价买全新）
DA       = 4        # A 路线双持过渡月数（买新后多久卖掉旧机）
DB       = 6        # B 路线过渡月数（备用机顶多久后买入准新新机）
BACKUP0  = 700.0    # 备用机（地板价老机）初始回收价
BACKUP_DROP = 12.0  # 备用机每月贬值（地板价机贬得极慢）
USED_AGE = 6        # B 路线买入新机时的"准新"机龄（价格已回落到合理位）
MONTHS   = 18       # 观察窗口

def old_val(t):     # 旧主力机第 t 月回收价
    return P * rr(OLD_AGE0 + t)
def newA_val(t):    # A 的新机：第0月买全新，机龄=t
    return PL * rr(t)
def backup_val(t):  # 备用机
    return max(0.0, BACKUP0 - BACKUP_DROP * t)
def newB_val(t):    # B 的新机：第DB月买入准新(机龄USED_AGE)，之后随历法月继续变老
    age = USED_AGE + (t - DB)
    return P * rr(age)
USED_BUY_PRICE = P * rr(USED_AGE)   # B 买入准新新机的价格（合理价）

W0 = old_val(0)     # 期初身家基准 = 旧机当前价

def lossA(t):
    # 现金流：第0月付 PL 买全新；第DA月卖旧机收 old_val(DA)
    cash = -PL + (old_val(DA) if t >= DA else 0.0)
    if t < DA:
        phones = old_val(t) + newA_val(t)
    else:
        phones = newA_val(t)
    return W0 - (cash + phones)

def lossB(t):
    # 第0月：卖旧机收 old_val(0)，买备用机付 BACKUP0
    cash = old_val(0) - BACKUP0
    if t < DB:
        phones = backup_val(t)
    else:
        # 第DB月：买准新新机付 USED_BUY_PRICE，卖备用机收 backup_val(DB)
        cash += -USED_BUY_PRICE + backup_val(DB)
        phones = newB_val(t)
    return W0 - (cash + phones)

A = [(t, lossA(t)) for t in range(MONTHS+1)]
B = [(t, lossB(t)) for t in range(MONTHS+1)]

# ---- 控制台输出（核对）----
print("月份  路线A累计损耗  路线B累计损耗  B比A省")
for t in range(0, MONTHS+1, 2):
    a = lossA(t); b = lossB(t)
    print(f"{t:>3}   {a:>10.0f}    {b:>10.0f}    {a-b:>8.0f}")
print(f"\nB 买入准新新机价(合理价) = {USED_BUY_PRICE:.0f}  (vs A 发布价 {PL:.0f})")
print(f"窗口末({MONTHS}月) A损耗={lossA(MONTHS):.0f}  B损耗={lossB(MONTHS):.0f}  省={lossA(MONTHS)-lossB(MONTHS):.0f}")

# ---- 画 SVG ----
Wd, Hd = 920, 540
ml, mr, mt, mb = 75, 220, 70, 70
pw, ph = Wd-ml-mr, Hd-mt-mb
xmax = MONTHS
ymax = max(max(v for _,v in A), max(v for _,v in B)) * 1.12
ymax = (int(ymax/200)+1)*200

def X(t): return ml + t/xmax*pw
def Y(v): return mt + (ymax-v)/ymax*ph

s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd}" height="{Hd}" font-family="Segoe UI,PingFang SC,Microsoft YaHei,Arial,sans-serif">',
   f'<rect width="{Wd}" height="{Hd}" fill="#ffffff"/>',
   f'<text x="{ml}" y="30" font-size="18" font-weight="bold" fill="#202124">换机两条路线的累计损耗对比</text>',
   f'<text x="{ml}" y="50" font-size="12" fill="#9aa0a6">同样从“持有旧机”过渡到“持有新机”，谁更省 — 数值为示意性测算</text>']

# 网格 + Y 轴刻度
for v in range(0, int(ymax)+1, 400):
    s.append(f'<line x1="{ml}" y1="{Y(v):.1f}" x2="{ml+pw}" y2="{Y(v):.1f}" stroke="#eef0f2"/>')
    s.append(f'<text x="{ml-8}" y="{Y(v)+4:.1f}" font-size="11" text-anchor="end" fill="#5f6368">{v}</text>')
# X 轴刻度
for t in range(0, xmax+1, 2):
    s.append(f'<text x="{X(t):.1f}" y="{mt+ph+20:.1f}" font-size="10" text-anchor="middle" fill="#5f6368">{t}</text>')
s.append(f'<text x="{ml+pw/2:.1f}" y="{mt+ph+44:.1f}" font-size="12" text-anchor="middle" fill="#3c4043">过渡开始后的月份</text>')
s.append(f'<text x="22" y="{mt+ph/2:.1f}" font-size="12" fill="#3c4043" transform="rotate(-90 22 {mt+ph/2:.1f})">累计损耗（元）</text>')

# 关键时间竖线：A 卖旧机(DA)、B 买新机(DB)
s.append(f'<line x1="{X(DA):.1f}" y1="{mt}" x2="{X(DA):.1f}" y2="{mt+ph}" stroke="#ea4335" stroke-dasharray="4 4" opacity="0.5"/>')
s.append(f'<text x="{X(DA)+4:.1f}" y="{mt+14:.1f}" font-size="9.5" fill="#ea4335">A:第{DA}月卖旧机</text>')
s.append(f'<line x1="{X(DB):.1f}" y1="{mt}" x2="{X(DB):.1f}" y2="{mt+ph}" stroke="#34a853" stroke-dasharray="4 4" opacity="0.5"/>')
s.append(f'<text x="{X(DB)+4:.1f}" y="{mt+28:.1f}" font-size="9.5" fill="#34a853">B:第{DB}月买准新</text>')

def path(data):
    d=[]
    for i,(t,v) in enumerate(data):
        d.append(("M" if i==0 else "L")+f"{X(t):.1f},{Y(v):.1f}")
    return " ".join(d)

# 路线A（红）、路线B（绿）
s.append(f'<path d="{path(A)}" fill="none" stroke="#ea4335" stroke-width="3"/>')
s.append(f'<path d="{path(B)}" fill="none" stroke="#34a853" stroke-width="3"/>')

# 末端节点 + 数值
ta,va=A[-1]; tb,vb=B[-1]
s.append(f'<circle cx="{X(ta):.1f}" cy="{Y(va):.1f}" r="4" fill="#ea4335"/>')
s.append(f'<text x="{X(ta)+6:.1f}" y="{Y(va)+4:.1f}" font-size="11" fill="#ea4335" font-weight="bold">A ¥{va:.0f}</text>')
s.append(f'<circle cx="{X(tb):.1f}" cy="{Y(vb):.1f}" r="4" fill="#34a853"/>')
s.append(f'<text x="{X(tb)+6:.1f}" y="{Y(vb)+4:.1f}" font-size="11" fill="#34a853" font-weight="bold">B ¥{vb:.0f}</text>')

# 差额（省了多少）用竖直双箭头在末端标注
gx = X(ta) - 30
s.append(f'<line x1="{gx:.1f}" y1="{Y(va):.1f}" x2="{gx:.1f}" y2="{Y(vb):.1f}" stroke="#1a73e8" stroke-width="1.5"/>')
s.append(f'<text x="{gx-6:.1f}" y="{(Y(va)+Y(vb))/2:.1f}" font-size="11" text-anchor="end" fill="#1a73e8" font-weight="bold">B省¥{va-vb:.0f}</text>')

# 右侧说明框
lx = ml+pw+18
s.append(f'<rect x="{lx-8}" y="{mt}" width="200" height="{ph}" fill="#f8f9fa" stroke="#dadce0" rx="6"/>')
yy=mt+22
s.append(f'<rect x="{lx}" y="{yy-11}" width="14" height="4" fill="#ea4335"/>')
s.append(f'<text x="{lx+20}" y="{yy-4}" font-size="11.5" font-weight="bold" fill="#ea4335">路线A 先买后卖</text>')
for line in ["第0月按发布价买全新","旧机并行持有,第%d月卖出"%DA,"→ 旧机闲置期照样贬值","→ 新机吃满首发高位折旧"]:
    yy+=17; s.append(f'<text x="{lx}" y="{yy}" font-size="10" fill="#5f6368">{line}</text>')
yy+=24
s.append(f'<rect x="{lx}" y="{yy-11}" width="14" height="4" fill="#34a853"/>')
s.append(f'<text x="{lx+20}" y="{yy-4}" font-size="11.5" font-weight="bold" fill="#34a853">路线B 先卖+备用机</text>')
for line in ["旧机发布前高点先卖","地板价备用机顶 %d 个月"%DB,"等新机回落到合理价(准新)","→ 避开双持贬值","→ 避开首发价那段陡跌"]:
    yy+=17; s.append(f'<text x="{lx}" y="{yy}" font-size="10" fill="#5f6368">{line}</text>')
yy+=26
s.append(f'<rect x="{lx-2}" y="{yy-12}" width="194" height="86" fill="#fff8e1" stroke="#f9ab00" rx="4"/>')
s.append(f'<text x="{lx+4}" y="{yy+2}" font-size="10.5" font-weight="bold" fill="#b06000">代价（要诚实看）</text>')
for line in ["B 在过渡的 %d 个月里"%DB,"用的是旧备用机，","牺牲了这段时间的","“最新科技”体验。","省钱 ⇄ 尝鲜，需自己权衡。"]:
    yy+=15; s.append(f'<text x="{lx+4}" y="{yy}" font-size="9.5" fill="#7a5300">{line}</text>')

s.append('</svg>')
open("charts/dual_phone_compare.svg","w").write("\n".join(s))
print("\nwrote charts/dual_phone_compare.svg")

# 同时存一份数据
json.dump({
  "assumptions":{"P":P,"old_age0":OLD_AGE0,"launch_price":PL,"overlapA":DA,
                 "bridgeB":DB,"backup0":BACKUP0,"backup_drop":BACKUP_DROP,
                 "used_age":USED_AGE,"used_buy_price":USED_BUY_PRICE,"months":MONTHS},
  "lossA":[[t,round(v,1)] for t,v in A],
  "lossB":[[t,round(v,1)] for t,v in B],
}, open("data/dual_phone_compare.json","w"), ensure_ascii=False, indent=1)
print("wrote data/dual_phone_compare.json")
