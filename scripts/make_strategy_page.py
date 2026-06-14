#!/usr/bin/env python3
# 把双机策略分析 + 三张图内联成一个自包含网页 dual_phone_strategy.html
import os

def svg(name):
    p = os.path.join("charts", name)
    with open(p, "r", encoding="utf-8") as f:
        s = f.read()
    # 让内联 SVG 自适应宽度
    s = s.replace("<svg ", '<svg style="max-width:100%;height:auto" ', 1)
    return s

demo   = svg("freshness_demo.svg")
scatter= svg("freshness_vs_cost.svg")
dual   = svg("dual_phone_compare.svg")

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>双机换机策略 · iPhone 价格分析</title>
<style>
:root{{--ink:#202124;--grey:#5f6368;--line:#e8eaed;--blue:#1a73e8;--bg:#f8f9fa;}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:"Segoe UI","PingFang SC","Microsoft YaHei",Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.75}}
.wrap{{max-width:840px;margin:0 auto;padding:36px 20px 80px}}
h1{{font-size:27px;margin:0 0 6px}}
h2{{font-size:20px;margin:34px 0 10px;padding-top:10px;border-top:1px solid var(--line);color:#174ea6}}
.sub{{color:var(--grey);font-size:14px;margin-bottom:18px}}
.fig{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px;margin:18px 0;text-align:center;box-shadow:0 1px 2px rgba(0,0,0,.04)}}
.fig figcaption{{color:var(--grey);font-size:13px;margin-top:8px}}
pre{{background:#0f172a;color:#e2e8f0;border-radius:10px;padding:14px 16px;overflow:auto;font-size:13px;line-height:1.5}}
.formula{{background:#eef4ff;border-left:4px solid var(--blue);padding:10px 14px;border-radius:6px;font-family:Consolas,Menlo,monospace;font-size:14px;margin:12px 0}}
.warn{{background:#fff8e1;border-left:4px solid #f9ab00;padding:12px 16px;border-radius:6px;margin:14px 0}}
.law{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin:12px 0}}
.law b{{color:#174ea6}}
.key{{background:#e6f4ea;border-left:4px solid #1e8e3e;padding:12px 16px;border-radius:6px;margin:14px 0}}
a.back{{display:inline-block;margin-bottom:18px;color:var(--blue);text-decoration:none;font-size:14px}}
.foot{{color:#9aa0a6;font-size:12px;margin-top:36px;text-align:center}}
ul{{padding-left:22px}} li{{margin:4px 0}}
</style>
</head>
<body>
<div class="wrap">
<a class="back" href="index.html">&larr; 返回首页</a>
<h1>双机换机策略：先买后卖 vs 先卖后买 + 备用机</h1>
<div class="sub">用数学把"什么时候买、用多久、怎么过渡"讲清楚。金额为示意性测算，用于看清方向与原理。</div>

<h2>一、统一的损耗定义</h2>
<p>沿用一个核心指标——你实际"消耗"掉多少钱：</p>
<div class="formula">单段月成本 = (买入价 - 卖出价) / 持有月数</div>
<p>把它推广到"换机过渡"，用身家变化来度量：</p>
<div class="formula">累计损耗(t) = 期初身家 - 当前身家<br>身家 = 现金 + 手中所有手机的当前回收价</div>
<p>买手机本身不是损耗（现金变成等值手机资产）。真正的损耗只来自两处：<b>手机贬值</b>，以及<b>买贵了的溢价</b>。</p>

<h2>二、先理解"新鲜度" = a + h/2</h2>
<p>设买入机龄为 a、持有月数为 h（注意 h 是持有时长，不是月成本）。手中这台机的机龄从 a 匀速升到 a+h，平均值正好是中点：</p>
<div class="formula">平均机龄（新鲜度） = a + h/2 &nbsp;&nbsp;（越小代表用的科技越新）</div>
<figure class="fig">{demo}<figcaption>机龄随时间匀速上升，平均机龄即起点与终点的中点</figcaption></figure>

<h2>三、新鲜度 vs 月成本：策略空间</h2>
<p>每种买法对应一个点 (平均机龄, 月成本)。把"同样新鲜度下最便宜"的点连起来，就是帕累托最优前沿——你只该在这条线上选点。</p>
<figure class="fig">{scatter}<figcaption>红线为最优前沿；"买全新只用1年"在最贵端（冤大头区）</figcaption></figure>

<h2>四、两条换机路线</h2>
<ul>
<li><b>路线A 先买后卖（双持过渡）</b>：第0月按发布价买全新；旧机并行持有，过渡几月后卖出。隐藏成本：旧机闲置期照样贬值 + 新机吃满首发那段最陡折旧。</li>
<li><b>路线B 先卖后买 + 备用机</b>：旧机在发布前高点先卖锁定残值；地板价备用机（几乎不贬值）过渡；等新机回落到合理价（准新）再入手。避开了双持贬值，也避开了首发陡跌。</li>
</ul>

<h2>五、累计损耗对比</h2>
<figure class="fig">{dual}<figcaption>同样从"持有旧机"过渡到"持有新机"，路线B 累计损耗明显更低</figcaption></figure>
<pre>月份   路线A累计损耗   路线B累计损耗   B比A省
  0          0             0           0
  4       1140            48        1092
  6       1500            72        1428
 12       1980           552        1428
 18       2640          1212        1428</pre>
<p>到第18个月：路线A约 <b>2640</b> 元，路线B约 <b>1212</b> 元，B 比 A 省约 <b>1428</b> 元。拆开看 A 的损耗：</p>
<ul>
<li>旧机双持贬值：从高点4200拖到第4月卖只剩约3780，白掉约 420 元</li>
<li>新机吃满首发陡跌：6000买全新，到期值约4440，掉了约 1560 元</li>
</ul>
<p>差距的大头来自<b>买入价位</b>：6000买进掉到4440 = 损失1560；4920（准新）买进掉到4440 = 损失480。越过首发那段陡坡再上车，绝对折旧小得多。</p>

<h2>六、必须诚实看待的代价</h2>
<div class="warn">路线B 省钱，代价是：过渡的那几个月里你用的是旧备用机，牺牲了这段时间的"最新科技"体验。它用"晚几个月用上新机"换来更低损耗——这正是"省钱 ⇄ 尝鲜"的权衡。</div>

<h2>七、三条铁律</h2>
<div class="law"><b>铁律1 备用机要够旧。</b>必须是已经地板价、几乎不再贬值的老机。拿还值钱的机器当备用，等于换个地方承担双持成本。</div>
<div class="law"><b>铁律2 过渡期设硬上限。</b>别为了等更低价无限拖。定死线：到点不管价格如何，按目标月成本线入手。</div>
<div class="law"><b>铁律3 买卖决策独立。</b>卖旧机看"发布前高点"（每年8月底、下一代发布前是硬截止线）；买新机看"月成本是否达标"。两件事分开判断，互不迁就。</div>

<h2>八、一句话结论</h2>
<div class="key">把换机当成资产的"高抛低吸 + 零成本过渡"：在已知的跌价之前卖掉旧主力锁定残值，用一台不再贬值的备用机零成本顶过空窗，再在合理价位把新机接回来。前提就是三条铁律——备用机够旧、过渡别拖太久、买卖各自独立判断。</div>

<div class="foot">数据为公开行情整理与基于历史规律的估算，金额为示意性测算，仅供参考。</div>
</div>
</body>
</html>"""

with open("dual_phone_strategy.html", "w", encoding="utf-8") as f:
    f.write(HTML)
print("wrote dual_phone_strategy.html", len(HTML), "bytes")
