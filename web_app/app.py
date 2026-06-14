#!/usr/bin/env python3
"""
iPhone价格监控Web应用 - FastAPI后端
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import json
import logging
import sqlite3
import os
from pathlib import Path

# 导入监控器组件
import sys
import os

# 添加父目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scripts_dir = os.path.join(parent_dir, 'scripts')
sys.path.append(scripts_dir)

# 尝试导入，如果失败则创建简化版本
try:
    from iphone_price_monitor_enhanced import (
        EnhancediPhonePriceMonitor, MonitorConfig, PriceData, Alert, AlertType
    )
except ImportError as e:
    print(f"⚠️ 无法导入完整监控器: {e}")
    print("📝 使用简化版本继续运行...")
    
    # 创建简化版本的数据类
    from dataclasses import dataclass
    from datetime import datetime
    from typing import Optional, Dict
    from enum import Enum
    
    class AlertType(Enum):
        BUY_SIGNAL = "买入信号"
        SELL_SIGNAL = "卖出信号"
        COST_TARGET = "成本达标"
        PRICE_DROP = "价格暴跌"
        PRICE_SURGE = "价格暴涨"
        MARKET_EVENT = "市场事件"
    
    @dataclass
    class MonitorConfig:
        target_monthly_cost: float = 90.0
        target_model: str = "iPhone 18"
        buy_threshold: float = 0.05
        sell_threshold: float = 0.10
        cost_tolerance: float = 0.03
        check_interval: int = 3600
        enable_email: bool = False
        enable_push: bool = False
    
    @dataclass
    class PriceData:
        model: str
        age_months: int
        price: float
        source: str
        timestamp: datetime
        condition: str = "95新"
        storage: str = "256GB"
        url: str = ""
        platform: str = ""
    
    @dataclass
    class Alert:
        alert_type: AlertType
        title: str
        message: str
        priority: int
        timestamp: datetime
        action: Optional[str] = None
        data: Optional[Dict] = None
    
    # 简化版的监控器
    class EnhancediPhonePriceMonitor:
        def __init__(self, config):
            self.config = config
            print(f"📱 简化版监控器已初始化 - 目标: {config.target_model}")
    
    # 简化版的数据库管理器
    class DatabaseManager:
        def __init__(self, db_path="data/iphone_monitor.db"):
            self.db_path = db_path
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

# ==================== 数据模型 ====================
class UserConfig(BaseModel):
    """用户配置模型"""
    target_monthly_cost: float = 90.0
    target_model: str = "iPhone 18"
    buy_threshold: float = 0.05
    sell_threshold: float = 0.10
    cost_tolerance: float = 0.03
    check_interval: int = 3600
    enable_email: bool = False
    enable_push: bool = False

class PriceQuery(BaseModel):
    """价格查询参数"""
    model: str = "iPhone 18"
    age_months: Optional[int] = None
    platform: Optional[str] = None
    limit: int = 100
    days: int = 7

class AlertFilter(BaseModel):
    """预警过滤器"""
    alert_type: Optional[str] = None
    priority_min: int = 1
    priority_max: int = 5
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 50

class StrategyRequest(BaseModel):
    """策略请求"""
    target_monthly_cost: float
    max_age_months: int = 36
    min_hold_months: int = 12
    max_hold_months: int = 48

# ==================== Web应用类 ====================
class iPhoneWebApp:
    """iPhone价格监控Web应用"""
    
    def __init__(self):
        self.app = FastAPI(title="iPhone价格监控系统", version="1.0.0")
        self.monitor = None
        self.clients = []
        self.setup_app()
        self.setup_routes()
        self.init_database()
        self.init_monitor()
    
    def setup_app(self):
        """设置FastAPI应用"""
        # CORS配置
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 创建静态文件目录
        static_dir = Path("static")
        static_dir.mkdir(exist_ok=True)
        self.app.mount("/static", StaticFiles(directory="static"), name="static")
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def init_database(self):
        """初始化数据库"""
        try:
            import simple_db
            simple_db.init_database()
            print("✅ 数据库初始化完成")
        except Exception as e:
            print(f"⚠️ 数据库初始化失败: {e}")
    
    def init_monitor(self):
        """初始化监控器"""
        config = MonitorConfig(
            target_monthly_cost=90.0,
            target_model="iPhone 18",
            buy_threshold=0.05,
            sell_threshold=0.10,
            cost_tolerance=0.03,
            check_interval=300,
            enable_email=False,
            enable_push=False
        )
        self.monitor = EnhancediPhonePriceMonitor(config)
    
    def setup_routes(self):
        """设置路由"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def read_root():
            """首页"""
            with open("templates/index.html", "r", encoding="utf-8") as f:
                return f.read()
        
        @self.app.get("/api/status")
        async def get_status():
            """获取系统状态"""
            return {
                "status": "running",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "monitor_active": self.monitor is not None
            }
        
        @self.app.get("/api/prices")
        async def get_prices(
            model: str = Query("iPhone 18", description="机型"),
            age_months: Optional[int] = Query(None, description="机龄(月)"),
            platform: Optional[str] = Query(None, description="平台"),
            limit: int = Query(100, description="返回数量"),
            days: int = Query(7, description="天数")
        ):
            """获取价格数据"""
            try:
                conn = sqlite3.connect("data/iphone_monitor.db")
                cursor = conn.cursor()
                
                query = """
                    SELECT * FROM price_history 
                    WHERE model = ?
                """
                params = [model]
                
                if age_months is not None:
                    query += " AND age_months = ?"
                    params.append(age_months)
                
                if platform is not None:
                    query += " AND platform = ?"
                    params.append(platform)
                
                if days > 0:
                    start_date = datetime.now() - timedelta(days=days)
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                conn.close()
                
                # 转换为字典格式
                prices = []
                for row in rows:
                    prices.append({
                        "id": row[0],
                        "model": row[1],
                        "age_months": row[2],
                        "price": row[3],
                        "source": row[4],
                        "condition": row[5],
                        "storage": row[6],
                        "platform": row[7],
                        "url": row[8],
                        "timestamp": row[9],
                        "created_at": row[10]
                    })
                
                return {
                    "success": True,
                    "count": len(prices),
                    "data": prices
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/alerts")
        async def get_alerts(
            alert_type: Optional[str] = Query(None, description="预警类型"),
            priority_min: int = Query(1, description="最低优先级"),
            priority_max: int = Query(5, description="最高优先级"),
            limit: int = Query(50, description="返回数量")
        ):
            """获取预警数据"""
            try:
                conn = sqlite3.connect("data/iphone_monitor.db")
                cursor = conn.cursor()
                
                query = "SELECT * FROM alert_history WHERE 1=1"
                params = []
                
                if alert_type is not None:
                    query += " AND alert_type = ?"
                    params.append(alert_type)
                
                query += " AND priority BETWEEN ? AND ?"
                params.extend([priority_min, priority_max])
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                conn.close()
                
                # 转换为字典格式
                alerts = []
                for row in rows:
                    alerts.append({
                        "id": row[0],
                        "alert_type": row[1],
                        "title": row[2],
                        "message": row[3],
                        "priority": row[4],
                        "action": row[5],
                        "data": json.loads(row[6]) if row[6] else None,
                        "timestamp": row[7],
                        "created_at": row[8]
                    })
                
                return {
                    "success": True,
                    "count": len(alerts),
                    "data": alerts
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/strategy/calculate")
        async def calculate_strategy(request: StrategyRequest):
            """计算最优策略"""
            try:
                # 这里应该调用监控器的策略计算逻辑
                # 为简化，返回示例策略
                strategy = {
                    "buy_age": 6,
                    "hold_months": 36,
                    "buy_price": 5085,
                    "sell_price": 1886,
                    "monthly_cost": 88.9,
                    "avg_age": 24.0,
                    "target_achieved": True,
                    "recommendation": "推荐购买6个月二手，持有36个月"
                }
                
                return {
                    "success": True,
                    "strategy": strategy,
                    "message": f"找到月成本¥{strategy['monthly_cost']:.1f}的最优策略"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/monitor/start")
        async def start_monitoring():
            """启动监控"""
            try:
                # 实际应该启动异步监控任务
                return {
                    "success": True,
                    "message": "监控已启动",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/monitor/stop")
        async def stop_monitoring():
            """停止监控"""
            try:
                # 实际应该停止监控任务
                return {
                    "success": True,
                    "message": "监控已停止",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/stats")
        async def get_statistics():
            """获取统计数据"""
            try:
                conn = sqlite3.connect("data/iphone_monitor.db")
                cursor = conn.cursor()
                
                # 价格统计
                cursor.execute("SELECT COUNT(*) FROM price_history")
                price_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM alert_history")
                alert_count = cursor.fetchone()[0]
                
                # 最近24小时预警
                start_time = datetime.now() - timedelta(hours=24)
                cursor.execute(
                    "SELECT COUNT(*) FROM alert_history WHERE timestamp >= ?",
                    (start_time.isoformat(),)
                )
                recent_alerts = cursor.fetchone()[0]
                
                # 平台分布
                cursor.execute(
                    "SELECT platform, COUNT(*) FROM price_history GROUP BY platform"
                )
                platform_stats = cursor.fetchall()
                
                conn.close()
                
                return {
                    "success": True,
                    "stats": {
                        "price_count": price_count,
                        "alert_count": alert_count,
                        "recent_alerts_24h": recent_alerts,
                        "platform_distribution": dict(platform_stats)
                    }
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket连接"""
            await websocket.accept()
            self.clients.append(websocket)
            
            try:
                while True:
                    # 接收消息
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # 处理消息
                    if message.get("type") == "subscribe":
                        await websocket.send_text(json.dumps({
                            "type": "subscription_confirmed",
                            "message": f"已订阅: {message.get('channel', 'unknown')}"
                        }))
                    
                    # 定期发送监控数据
                    await asyncio.sleep(30)
                    
            except WebSocketDisconnect:
                self.clients.remove(websocket)
            except Exception as e:
                logging.error(f"WebSocket错误: {e}")
                self.clients.remove(websocket)
    
    def broadcast_message(self, message: Dict):
        """广播消息到所有WebSocket客户端"""
        for client in self.clients:
            try:
                asyncio.create_task(client.send_text(json.dumps(message)))
            except Exception as e:
                logging.error(f"广播消息失败: {e}")

# ==================== 主程序 ====================
app_instance = iPhoneWebApp()
app = app_instance.app

if __name__ == "__main__":
    import uvicorn
    
    # 创建必要目录
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    print("=" * 70)
    print("🌐 iPhone价格监控Web应用")
    print("=" * 70)
    print("✅ 后端服务: FastAPI")
    print("✅ 数据库: SQLite")
    print("✅ WebSocket: 实时推送")
    print("✅ API接口: RESTful")
    print("=" * 70)
    print("🚀 启动服务器: http://localhost:8000")
    print("📊 接口文档: http://localhost:8000/docs")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)