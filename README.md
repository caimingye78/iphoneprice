# iPhone 价格曲线与最优购买策略分析

基于近十年(2016–2025)历代 iPhone 一手价、二手价数据,用数学模型推导"在尽量用新科技的同时、每月成本最低"的购买策略。

## 图表 (charts/)

| 文件 | 内容 |
|------|------|
| `iphone_price_curve.svg` | 历代 iPhone 美国发布价曲线(按机型档位) |
| `iphone_secondhand_cn.svg` | 国行标准款首发价 vs 当前二手价 + 残值率 |
| `iphone_depreciation_curve.svg` | 标准款回收价随机龄的折旧曲线 |
| `iphone_cost_strategy.svg` | 每月持有成本 vs 持有时长(新机/各年限二手) |
| `iphone_frontier.svg` | 新科技 vs 省钱的帕累托最优前沿 |
| `iphone18_forecast.svg` | iPhone 18 二手回收价预测 + 抄底窗口 |

> 注:`.svg` 在 GitHub 网页上点开即可直接渲染预览。

### PNG 预览(英文标签,任意环境可直接看图)

由于沙箱环境无 SVG 渲染器且无中文字体,PNG 版用纯 Python 渲染器(见 `scripts/minipng.py`)重绘,标签为英文。

![发布价曲线](charts/png/iphone_price_curve.png)
![首发价 vs 二手价](charts/png/iphone_secondhand_cn.png)
![折旧曲线](charts/png/iphone_depreciation_curve.png)
![月成本 vs 持有时长](charts/png/iphone_cost_strategy.png)
![新科技 vs 省钱 前沿](charts/png/iphone_frontier.png)

## 核心模型

持有成本(单段):

    月成本 = (买入价 - 卖出价) / 持有月数

设首发价 P、残值率 rr(t)=回收价/首发价(t 为机龄月数),买入机龄 a、持有 h 个月:

    g(a, h) = P * (rr(a) - rr(a+h)) / h

长期平均月成本 = 各段折旧之和 / 总月数,因此全局最优 = 让每段 g 最小。

## 主要结论

- 残值曲线递减且凸:前 1 年掉价最猛(约 26%),5 年后基本触底。
- g 对持有时长 h 递减、对买入机龄 a 递减 → 无约束最优是"买尽量旧 + 持有尽量久"。
- 在"要够新"的约束下,最优前沿存在明显甜点:平均机龄 12–18 个月,约 85–95 元/月。
- 最差(冤大头)策略:买全新 + 一年内换,约 130–137 元/月。
- 推荐:买准新(发布约 6 个月的二手)+ 持有约 2 年 ≈ 85 元/月,比"买全新一年换"省约 38%。
- 择时:9 月新品发布后 / 618 / 双11 抄底二手;旧机赶在下一代发布前(8 月底)出手。

## 复现 (scripts/)

```bash
python3 scripts/iphone_prices.py            # 历代发布价曲线
python3 scripts/iphone_secondhand_cn.py     # 国行首发 vs 二手
python3 scripts/iphone_strategy.py          # 成本模型 + strategy_data.json
python3 scripts/make_strategy_charts.py     # 折旧曲线 + 成本曲线图
python3 scripts/iphone_frontier.py          # 帕累托前沿 + frontier_data.json
python3 scripts/make_frontier_chart.py      # 前沿图(SVG)
python3 scripts/make_png_charts.py          # 全部图的 PNG 版(纯 Python,无依赖)
```

## 数据说明

价格为公开渠道整理(Apple Newsroom / Wikipedia / MacRumors / The Verge 等);二手/回收价为 2026 年初主流存储、良好成色(约 95 新)的近似行情,仅供参考,实际成交受成色、电池健康度、平台等影响。

## 完整报告

- `report.md` — 中文图文报告(GitHub 上直接渲染)
- `report.html` — 单页自包含 HTML(6 张图内联,可离线打开,中文正常显示)
