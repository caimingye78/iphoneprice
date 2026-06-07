#!/usr/bin/env python3
"""Build a single self-contained HTML report with all SVG charts inlined."""
import os
BASE=os.path.join(os.path.dirname(__file__),"..")
CH=os.path.join(BASE,"charts")

def svg(name):
    with open(os.path.join(CH,name),encoding="utf-8") as f:
        return f.read()

charts={n:svg(n+".svg") for n in
        ["iphone_price_curve","iphone_secondhand_cn","iphone_depreciation_curve",
         "iphone_cost_strategy","iphone_frontier","iphone18_forecast"]}

html=f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>iPhone 价格曲线与最优购买策略分析</title>
<style>
:root{{--ink:#202124;--grey:#5f6368;--line:#e8eaed;--blue:#1a73e8;--bg:#f8f9fa;}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:"Segoe UI","PingFang SC","Microsoft YaHei",Arial,sans-serif;
color:var(--ink);background:var(--bg);line-height:1.7}}
.wrap{{max-width:960px;margin:0 auto;padding:32px 20px 80px;background:#fff}}
h1{{font-size:28px;margin:.2em 0 .1em}}
h2{{font-size:21px;margin:1.6em 0 .5em;padding-bottom:.3em;border-bottom:2px solid var(--line)}}
h3{{font-size:16px;color:var(--grey);margin:1.2em 0 .4em}}
.sub{{color:var(--grey);font-size:14px;margin-bottom:1.5em}}
.fig{{margin:18px 0;text-align:center}}
.fig svg{{max-width:100%;height:auto;border:1px solid var(--line);border-radius:8px}}
table{{border-collapse:collapse;width:100%;margin:14px 0;font-size:14px}}
th,td{{border:1px solid var(--line);padding:7px 10px;text-align:left}}
th{{background:var(--bg)}}
tr:nth-child(even) td{{background:#fcfcfd}}
code,pre{{font-family:"SF Mono",Consolas,monospace}}
pre{{background:#f1f3f4;padding:14px 16px;border-radius:8px;overflow-x:auto;font-size:13px}}
.tip{{background:#e8f0fe;border-left:4px solid var(--blue);padding:12px 16px;border-radius:0 8px 8px 0;margin:16px 0}}
.hl{{background:#fef7e0;border-left:4px solid #f9ab00;padding:12px 16px;border-radius:0 8px 8px 0;margin:16px 0}}
.footer{{color:#9aa0a6;font-size:12px;margin-top:40px;border-top:1px solid var(--line);padding-top:16px}}
</style>
</head>
<body>
<div class="wrap">
<h1>iPhone 价格曲线与最优购买策略分析</h1>
<div class="sub">基于近十年(2016–2025)历代 iPhone 一手价/二手价,用数学方法回答:什么时候买、买哪一款、用多久再换最划算。</div>

<h2>1. 历代发布价(美国, 美元, 基础存储)</h2>
<div class="fig">{charts['iphone_price_curve']}</div>
<ul>
<li>标准款自 2020 年起长期锁定 <b>799 美元</b>,非常稳定。</li>
<li>Pro 档连续 8 年(2017–2024)守住 999 美元,2025 年 iPhone 17 Pro 才涨到 1099。</li>
<li>Pro Max 名义价从 1099 涨到 1199,但 Apple 常以"涨价同时翻倍存储"维持同存储价格不变。</li>
<li>入门档涨幅最明显:399 一路抬到 16e 的 599。</li>
</ul>

<h2>2. 国行二手价与折旧曲线</h2>
<div class="fig">{charts['iphone_secondhand_cn']}</div>
<div class="fig">{charts['iphone_depreciation_curve']}</div>
<p>折旧近似指数衰减:<b>前 1 年掉得最猛(约 26%)</b>,之后趋缓,5 年后基本触底。大致规律:满 1 年残值约 80%、满 2 年约 60%、满 3 年约 50%、满 4 年约 33%。</p>

<h2>3. 数学模型</h2>
<p>把"每月真实损耗"形式化。单段持有成本:</p>
<pre>月成本 = (买入价 - 卖出价) / 持有月数

设首发价 P、残值率 rr(t)=回收价/首发价(t 为机龄月数),
买入机龄 a、持有 h 个月:
    g(a, h) = P * (rr(a) - rr(a+h)) / h</pre>
<p>多部手机连续使用时,长期平均月成本 = 各段折旧之和 / 总月数。因此全局最优 = 让每段 g 最小。</p>
<div class="tip"><b>你的案例验证:</b> iPhone 16 买入 6069,14 个月回收 4150 → g = (6069 − 4150) / 14 = <b>137 元/月</b>。</div>

<h2>4. 策略空间与最优前沿</h2>
<div class="fig">{charts['iphone_cost_strategy']}</div>
<p>g 有两条单调性:<b>持有越久越省</b>(陡降被摊薄)、<b>买得越旧越省</b>(绝对折旧变小)。</p>
<div class="fig">{charts['iphone_frontier']}</div>
<table>
<tr><th>平均机龄(月)</th><th>月成本(¥)</th><th>最优策略</th></tr>
<tr><td>6</td><td>130</td><td>买全新, 持有 12 月(冤大头区)</td></tr>
<tr><td>12</td><td>95</td><td>买 6 月二手, 持有 12 月</td></tr>
<tr><td>18</td><td>85</td><td>买 6 月二手, 持有 24 月(甜点)</td></tr>
<tr><td>24</td><td>75</td><td>买 6 月二手, 持有 36 月</td></tr>
<tr><td>48</td><td>42</td><td>买 36 月二手, 持有 24 月</td></tr>
</table>
<p>前沿拐点在<b>平均机龄 12~18 个月</b>:从 6→18 个月月成本由 130 暴跌到 85,再往后只缓慢下降。</p>

<h2>5. iPhone 18 二手价预测与抄底时点</h2>
<div class="sub">假设 2026-09 发布、国行标准款首发 ¥5999,沿用历史折旧曲线推演。</div>
<div class="fig">{charts['iphone18_forecast']}</div>
<table>
<tr><th>时间</th><th>机龄</th><th>预测回收价</th><th>残值</th><th>说明</th></tr>
<tr><td>2026-09</td><td>0</td><td>¥5999</td><td>100%</td><td>首发</td></tr>
<tr><td>2027-03</td><td>6月</td><td>¥4919</td><td>82%</td><td>第一波价稳</td></tr>
<tr><td>2027-09</td><td>12月</td><td>¥4439</td><td>74%</td><td>iPhone19 发布,台阶下跌</td></tr>
<tr><td>2027 双11</td><td>14月</td><td>¥4199</td><td>70%</td><td><b>促销低点</b></td></tr>
<tr><td>2028-09</td><td>24月</td><td>¥3299</td><td>55%</td><td><b>性价比顶点</b></td></tr>
<tr><td>2030-09</td><td>48月</td><td>¥1920</td><td>32%</td><td>趋于触底</td></tr>
</table>
<div class="hl"><b>抄底结论:</b><br>
• 想买二手 18 自用最划算 → <b>2027-09(iPhone19 发布后)到 2027 双11</b> 抄底,价约 ¥4200、是 1 代差的现代旗舰,买后持有 2 年月成本约 74 元;<br>
• 若更看重省钱、不在意代差 → <b>2028-09</b> 买入(约 ¥3300),持有 2 年月成本低至 <b>57 元/月</b>;<br>
• 要首发尝鲜 → 2026-09 全新买,但务必持有 ≥ 2 年再换,别一年一换。</div>

<h2>6. 结论:给你的最优策略</h2>
<table>
<tr><th>需求</th><th>策略</th><th>月成本</th></tr>
<tr><td>省钱优先</td><td>买 2–3 年二手标准款, 用 2–3 年</td><td>42–57</td></tr>
<tr><td>均衡(推荐)</td><td>买准新(约 6 月二手), 持有约 2 年</td><td>≈85</td></tr>
<tr><td>必须尝鲜</td><td>买全新, 持有 ≥ 2–3 年再换</td><td>97–112</td></tr>
</table>
<p><b>择时:</b>收二手在 9 月新机发布后 / 618 / 双11 抄底;旧机赶在下一代发布前(8 月底)出手。</p>
<div class="tip"><b>一句话:</b>不必降低"用新科技"的标准,只需把"买全新+一年换"改成"买准新+用满两年",月成本从 137 → 约 85,长期每年省约 600 元,手上始终是一台够新的旗舰。</div>

<div class="footer">
数据来源:Apple Newsroom / Wikipedia / MacRumors / The Verge 等公开发布价;二手价为 2026 年初主流存储、良好成色近似行情,仅供参考。iPhone 18 相关为基于历史规律的预测,非官方数据。内容经整理改写以符合引用规范。
</div>
</div>
</body>
</html>"""

out=os.path.join(BASE,"report.html")
with open(out,"w",encoding="utf-8") as f:
    f.write(html)
print("wrote report.html ({} KB)".format(round(len(html)/1024)))
