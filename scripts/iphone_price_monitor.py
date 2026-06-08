#!/usr/bin/env python3
"""
iPhone价格实时监控与预警系统
支持月成本目标跟踪、实时价格监控、自动预警功能
"""

import json
import math
import time
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional, Tuple
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dataclasses import dataclass
from enum import Enum

# ==================== 配置部分 ====================
class AlertType(Enum):
    """预警类型"""
    BUY_SIGNAL = "买入信号"          # 价格达到目标买入点
    SELL_SIGNAL = "卖出信号"         # 价格达到目标卖出点  
    COST_TARGET = "成本达标"         # 月成本达到目标值
    PRICE_DROP = "价格暴跌"          # 价格快速下跌
    PRICE_SURGE = "价格暴涨"         # 价格快速上涨
    MARKET_EVENT = "市场事件"        # 重要市场事件（发布会等）

@dataclass
class MonitorConfig:
    """监控配置"""
    # 目标月成本
    target_monthly_cost: float = 90.0
    
    # 监控机型
    target_model: str = "iPhone 18"
    
    # 预警阈值
    buy_threshold: float = 0.05      # 低于预测价5%触发买入
    sell_threshold: float = 0.10     # 高于预测价10%触发卖出
    cost_tolerance: float = 0.03     # 月成本误差3%内视为达标
    
    # 监控频率（秒）
    check_interval: int = 3600       # 默认1小时
    
    # 预警方式
    enable_email: bool = False
    enable_push: bool = False
    enable_log: bool = True
    
    # 价格数据源配置
    data_sources: List[str] = None
    
    def __post_init__(self):
        if self.data_sources is None:
            self.data_sources = [
                "闲鱼", "转转", "爱回收", "京东二手", "淘宝二手"
            ]

@dataclass  
class PriceData:
    """价格数据"""
    model: str
    age_months: int
    price: float
    source: str
    timestamp: datetime
    condition: str = "95新"  # 成色：95新、9新、85新等
    storage: str = "256GB"  # 存储容量

@dataclass
class Alert:
    """预警信息"""
    alert_type: AlertType
    title: str
    message: str
    priority: int  # 1-5，5为最高
    timestamp: datetime
    action: Optional[str] = None

# ==================== 核心监控类 ====================
class iPhonePriceMonitor:
    """iPhone价格监控器"""
    
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.price_history: Dict[str, List[PriceData]] = {}
        self.alerts: List[Alert] = []
        self.is_running = False
        
        # 加载预测模型
        self.prediction_model = self._load_prediction_model()
        
        # 初始化价格数据源
        self.data_sources = self._init_data_sources()
        
        print(f"✅ iPhone价格监控器已初始化")
        print(f"   目标机型: {config.target_model}")
        print(f"   目标月成本: ¥{config.target_monthly_cost}/月")
        print(f"   监控频率: 每{config.check_interval//3600}小时")
        print(f"   数据源: {', '.join(config.data_sources)}")
    
    def _load_prediction_model(self) -> Dict:
        """加载价格预测模型"""
        # 使用历史数据中的残值率模型
        lambda_val = -math.log(0.68) / 14
        
        model = {
            "base_price": 5999,  # iPhone标准款首发价
            "lambda": lambda_val,
            "launch_date": datetime(2027, 3, 1),  # iPhone 18预计发布时间
            "prediction_formula": "P(t) = P0 * exp(-λ*t)"
        }
        
        return model
    
    def _init_data_sources(self) -> Dict:
        """初始化数据源（模拟实现）"""
        # 实际应用中这里会连接真实API
        return {
            "闲鱼": {"type": "crawler", "url": "https://2.taobao.com"},
            "转转": {"type": "crawler", "url": "https://www.zhuanzhuan.com"},
            "爱回收": {"type": "api", "url": "https://www.aihuishou.com"},
            "京东二手": {"type": "api", "url": "https://paipai.jd.com"},
            "淘宝二手": {"type": "crawler", "url": "https://2.taobao.com"}
        }
    
    def fetch_market_prices(self) -> List[PriceData]:
        """从市场获取实时价格（模拟实现）"""
        # 模拟实际市场数据
        current_time = datetime.now()
        base_price = self.prediction_model["base_price"]
        lambda_val = self.prediction_model["lambda"]
        
        # 模拟不同机龄的价格
        prices = []
        
        # 模拟全新机价格（可能有波动）
        new_price_variation = 0.95 + (time.time() % 100) / 500  # ±5%波动
        new_price = base_price * new_price_variation
        
        prices.append(PriceData(
            model=self.config.target_model,
            age_months=0,
            price=new_price,
            source="模拟市场",
            timestamp=current_time,
            condition="全新未拆",
            storage="256GB"
        ))
        
        # 模拟二手价格
        for age in [3, 6, 9, 12, 18, 24]:
            # 基于残值率模型，加上市场波动
            base_value = base_price * math.exp(-lambda_val * age)
            market_variation = 0.90 + (time.time() % 100 + age) / 400  # ±10%波动
            market_price = base_value * market_variation
            
            condition = "95新" if age <= 6 else "9新" if age <= 12 else "85新"
            
            prices.append(PriceData(
                model=self.config.target_model,
                age_months=age,
                price=market_price,
                source="模拟市场",
                timestamp=current_time,
                condition=condition,
                storage="256GB"
            ))
        
        return prices
    
    def calculate_monthly_cost(self, buy_price: float, sell_price: float, hold_months: int) -> float:
        """计算月成本"""
        if hold_months <= 0:
            return float('inf')
        return (buy_price - sell_price) / hold_months
    
    def find_optimal_strategy(self, current_prices: List[PriceData]) -> Dict:
        """寻找最优购买策略"""
        best_strategy = None
        best_cost = float('inf')
        
        base_price = self.prediction_model["base_price"]
        lambda_val = self.prediction_model["lambda"]
        
        # 遍历可能的买入机龄和持有时长
        for buy_age in range(0, 37, 3):  # 0-36个月
            # 找到对应机龄的市场价格
            buy_price = None
            for price_data in current_prices:
                if price_data.age_months == buy_age:
                    buy_price = price_data.price
                    break
            
            if buy_price is None:
                # 使用预测模型估算
                buy_price = base_price * math.exp(-lambda_val * buy_age)
            
            # 遍历可能的持有时长
            for hold_months in range(12, 49, 3):  # 12-48个月
                sell_age = buy_age + hold_months
                # 预测卖出价格
                sell_price = base_price * math.exp(-lambda_val * sell_age)
                
                # 计算月成本
                monthly_cost = self.calculate_monthly_cost(buy_price, sell_price, hold_months)
                
                # 计算新鲜度（平均机龄）
                avg_age = buy_age + hold_months / 2
                
                # 检查是否优于当前最优
                if monthly_cost < best_cost:
                    best_cost = monthly_cost
                    best_strategy = {
                        "buy_age": buy_age,
                        "hold_months": hold_months,
                        "buy_price": buy_price,
                        "sell_price": sell_price,
                        "monthly_cost": monthly_cost,
                        "avg_age": avg_age,
                        "deviation": abs(monthly_cost - self.config.target_monthly_cost) / self.config.target_monthly_cost
                    }
        
        return best_strategy
    
    def check_alerts(self, current_prices: List[PriceData], optimal_strategy: Dict) -> List[Alert]:
        """检查是否需要触发预警"""
        alerts = []
        current_time = datetime.now()
        
        # 1. 检查成本达标预警
        if optimal_strategy["deviation"] <= self.config.cost_tolerance:
            alerts.append(Alert(
                alert_type=AlertType.COST_TARGET,
                title="🎯 月成本目标达成！",
                message=f"发现月成本¥{optimal_strategy['monthly_cost']:.1f}的策略，接近目标¥{self.config.target_monthly_cost}",
                priority=4,
                timestamp=current_time,
                action=f"买入机龄：{optimal_strategy['buy_age']}个月，持有：{optimal_strategy['hold_months']}个月"
            ))
        
        # 2. 检查买入信号
        base_price = self.prediction_model["base_price"]
        lambda_val = self.prediction_model["lambda"]
        
        for price_data in current_prices:
            predicted_price = base_price * math.exp(-lambda_val * price_data.age_months)
            price_ratio = price_data.price / predicted_price
            
            if price_ratio <= (1 - self.config.buy_threshold):
                alerts.append(Alert(
                    alert_type=AlertType.BUY_SIGNAL,
                    title="💰 发现买入机会！",
                    message=f"{price_data.model}（{price_data.age_months}个月，{price_data.condition}）价格¥{price_data.price:.0f}，低于预测价{((1-price_ratio)*100):.1f}%",
                    priority=5,
                    timestamp=current_time,
                    action=f"立即购买：机龄{price_data.age_months}个月，价格¥{price_data.price:.0f}"
                ))
            
            if price_ratio >= (1 + self.config.sell_threshold):
                alerts.append(Alert(
                    alert_type=AlertType.SELL_SIGNAL,
                    title="📈 发现卖出机会！",
                    message=f"{price_data.model}（{price_data.age_months}个月，{price_data.condition}）价格¥{price_data.price:.0f}，高于预测价{((price_ratio-1)*100):.1f}%",
                    priority=4,
                    timestamp=current_time,
                    action=f"考虑卖出：机龄{price_data.age_months}个月，价格¥{price_data.price:.0f}"
                ))
        
        # 3. 检查价格异常波动（需要价格历史）
        if hasattr(self, 'last_prices'):
            for price_data in current_prices:
                last_price = self._find_last_price(price_data.age_months)
                if last_price:
                    change_rate = (price_data.price - last_price) / last_price
                    if change_rate <= -0.05:  # 下跌5%以上
                        alerts.append(Alert(
                            alert_type=AlertType.PRICE_DROP,
                            title="⚠️ 价格快速下跌",
                            message=f"{price_data.model}（{price_data.age_months}个月）价格下跌{(change_rate*100):.1f}%，当前¥{price_data.price:.0f}",
                            priority=3,
                            timestamp=current_time
                        ))
                    elif change_rate >= 0.05:  # 上涨5%以上
                        alerts.append(Alert(
                            alert_type=AlertType.PRICE_SURGE,
                            title="📊 价格快速上涨",
                            message=f"{price_data.model}（{price_data.age_months}个月）价格上涨{(change_rate*100):.1f}%，当前¥{price_data.price:.0f}",
                            priority=3,
                            timestamp=current_time
                        ))
        
        # 保存当前价格供下次比较
        self.last_prices = {p.age_months: p.price for p in current_prices}
        
        return alerts
    
    def _find_last_price(self, age_months: int) -> Optional[float]:
        """查找上次价格"""
        if hasattr(self, 'last_prices'):
            return self.last_prices.get(age_months)
        return None
    
    def send_alert(self, alert: Alert):
        """发送预警（模拟实现）"""
        if self.config.enable_log:
            print(f"\n{'='*60}")
            print(f"🔔 预警 [{alert.alert_type.value}] - 优先级：{alert.priority}")
            print(f"时间：{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"标题：{alert.title}")
            print(f"内容：{alert.message}")
            if alert.action:
                print(f"建议操作：{alert.action}")
            print(f"{'='*60}")
        
        # 实际应用中这里可以发送邮件、推送通知等
        if self.config.enable_email:
            self._send_email_alert(alert)
        
        if self.config.enable_push:
            self._send_push_alert(alert)
    
    def _send_email_alert(self, alert: Alert):
        """发送邮件预警（占位实现）"""
        # 实际实现需要配置SMTP服务器
        pass
    
    def _send_push_alert(self, alert: Alert):
        """发送推送通知（占位实现）"""
        # 实际实现需要集成推送服务
        pass
    
    def generate_report(self, current_prices: List[PriceData], optimal_strategy: Dict, alerts: List[Alert]) -> Dict:
        """生成监控报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "target_model": self.config.target_model,
            "target_monthly_cost": self.config.target_monthly_cost,
            "market_prices": [
                {
                    "age_months": p.age_months,
                    "price": p.price,
                    "condition": p.condition,
                    "source": p.source,
                    "timestamp": p.timestamp.isoformat()
                }
                for p in current_prices
            ],
            "optimal_strategy": optimal_strategy,
            "alerts_count": len(alerts),
            "alerts": [
                {
                    "type": a.alert_type.value,
                    "title": a.title,
                    "message": a.message,
                    "priority": a.priority,
                    "action": a.action
                }
                for a in alerts
            ],
            "summary": self._generate_summary(optimal_strategy, alerts)
        }
        
        return report
    
    def _generate_summary(self, optimal_strategy: Dict, alerts: List[Alert]) -> str:
        """生成摘要"""
        summary_parts = []
        
        # 策略摘要
        if optimal_strategy["deviation"] <= 0.05:
            status = "✅ 目标达成"
        elif optimal_strategy["deviation"] <= 0.10:
            status = "⚠️ 接近目标"
        else:
            status = "⏳ 仍需等待"
        
        summary_parts.append(f"策略状态：{status}")
        summary_parts.append(f"最佳月成本：¥{optimal_strategy['monthly_cost']:.1f}/月（目标¥{self.config.target_monthly_cost}）")
        summary_parts.append(f"推荐策略：买{optimal_strategy['buy_age']}个月二手，持有{optimal_strategy['hold_months']}个月")
        
        # 预警摘要
        if alerts:
            high_priority = [a for a in alerts if a.priority >= 4]
            if high_priority:
                summary_parts.append(f"高优先级预警：{len(high_priority)}个")
        
        return "\n".join(summary_parts)
    
    def run_once(self):
        """执行一次完整的监控检查"""
        print(f"\n⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始监控检查...")
        
        # 1. 获取市场价格
        current_prices = self.fetch_market_prices()
        print(f"   获取到 {len(current_prices)} 个价格数据点")
        
        # 2. 寻找最优策略
        optimal_strategy = self.find_optimal_strategy(current_prices)
        print(f"   最优策略：买{optimal_strategy['buy_age']}个月二手，持有{optimal_strategy['hold_months']}个月")
        print(f"   预计月成本：¥{optimal_strategy['monthly_cost']:.1f}/月")
        
        # 3. 检查预警
        alerts = self.check_alerts(current_prices, optimal_strategy)
        print(f"   发现 {len(alerts)} 个预警信号")
        
        # 4. 发送预警
        for alert in alerts:
            self.send_alert(alert)
        
        # 5. 生成报告
        report = self.generate_report(current_prices, optimal_strategy, alerts)
        
        # 6. 保存报告
        self._save_report(report)
        
        return report
    
    def _save_report(self, report: Dict):
        """保存报告到文件"""
        reports_dir = "data/monitor_reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = f"{reports_dir}/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"   报告已保存：{filename}")
    
    def start_monitoring(self):
        """启动持续监控"""
        self.is_running = True
        print(f"\n🚀 启动iPhone价格持续监控")
        print(f"   按 Ctrl+C 停止监控")
        
        try:
            while self.is_running:
                self.run_once()
                
                # 等待下一次检查
                print(f"   下次检查：{self.config.check_interval//60}分钟后")
                time.sleep(self.config.check_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 监控已停止")
            self.is_running = False
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        print("🛑 监控停止命令已发送")

# ==================== 工具函数 ====================
def create_dashboard(report: Dict):
    """创建监控仪表板（控制台版本）"""
    print("\n" + "="*70)
    print("📊 iPhone价格监控仪表板")
    print("="*70)
    
    # 基本信息
    print(f"\n📱 目标机型：{report['target_model']}")
    print(f"💰 目标月成本：¥{report['target_monthly_cost']}/月")
    print(f"🕐 报告时间：{report['timestamp']}")
    
    # 最优策略
    strategy = report['optimal_strategy']
    print(f"\n🎯 最优购买策略：")
    print(f"   • 买入机龄：{strategy['buy_age']}个月")
    print(f"   • 持有时长：{strategy['hold_months']}个月")
    print(f"   • 预计月成本：¥{strategy['monthly_cost']:.1f}/月")
    print(f"   • 平均机龄：{strategy['avg_age']:.1f}个月")
    print(f"   • 与目标偏差：{strategy['deviation']*100:.1f}%")
    
    # 市场价格快照
    print(f"\n📈 市场价格快照：")
    for price in report['market_prices'][:5]:  # 显示前5个
        age_label = "全新" if price['age_months'] == 0 else f"{price['age_months']}个月"
        print(f"   • {age_label} {price['condition']}：¥{price['price']:.0f}")
    
    # 预警状态
    print(f"\n🔔 预警状态：")
    if report['alerts_count'] > 0:
        high_alerts = [a for a in report['alerts'] if a['priority'] >= 4]
        print(f"   ⚠️ 发现 {report['alerts_count']} 个预警信号")
        print(f"   🔴 高优先级：{len(high_alerts)} 个")
        
        # 显示高优先级预警
        for alert in high_alerts[:3]:  # 最多显示3个
            print(f"      • [{alert['type']}] {alert['title']}")
    else:
        print(f"   ✅ 无预警信号，市场稳定")
    
    print(f"\n📋 摘要：")
    for line in report['summary'].split('\n'):
        print(f"   {line}")
    
    print(f"\n" + "="*70)

# ==================== 主程序 ====================
def main():
    """主函数"""
    print("="*70)
    print("📱 iPhone价格实时监控与预警系统")
    print("="*70)
    
    # 配置监控器
    config = MonitorConfig(
        target_monthly_cost=90.0,
        target_model="iPhone 18",
        buy_threshold=0.05,
        sell_threshold=0.10,
        cost_tolerance=0.03,
        check_interval=300,  # 5分钟（演示用，实际可以更长）
        enable_log=True,
        enable_email=False,
        enable_push=False
    )
    
    # 创建监控器
    monitor = iPhonePriceMonitor(config)
    
    # 运行模式选择
    print("\n请选择运行模式：")
    print("1. 单次检查（生成报告）")
    print("2. 持续监控（后台运行）")
    print("3. 自定义检查")
    
    choice = input("\n请输入选择（1-3）：").strip()
    
    if choice == "1":
        # 单次检查
        print("\n执行单次监控检查...")
        report = monitor.run_once()
        create_dashboard(report)
        
    elif choice == "2":
        # 持续监控
        print("\n启动持续监控...")
        monitor.start_monitoring()
        
    elif choice == "3":
        # 自定义检查
        print("\n自定义监控设置：")
        custom_target = float(input("目标月成本（默认90）：") or "90")
        custom_interval = int(input("检查间隔秒数（默认300）：") or "300")
        
        config.target_monthly_cost = custom_target
        config.check_interval = custom_interval
        
        monitor = iPhonePriceMonitor(config)
        report = monitor.run_once()
        create_dashboard(report)
        
    else:
        print("无效选择，退出程序")

if __name__ == "__main__":
    main()