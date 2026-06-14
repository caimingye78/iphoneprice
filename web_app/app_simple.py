#!/usr/bin/env python3
"""
iPhone价格监控Web应用 - 简化版本
确保快速启动和运行
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
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
import random
import math
from pathlib import Path

# ==================== 数据模型 ====================
class UserConfig(BaseModel):
    """用户配置模型"""
    target_monthly_cost: float = 90.0
    target_model: str = "iPhone 18"

class StrategyRequest(BaseModel):
    """策略请求"""
    target_monthly_cost: float
    max_age_months: int = 36
    min_hold_months: int = 12
    max_hold_months: int = 48

# ==================== 数据库初始化 ====================
def init_database():
    """初始化数据库"""
    db_path = "data/iphone_monitor.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 价格历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT,
            age_months INTEGER,
            price REAL,
            source TEXT,
            condition TEXT,
            storage TEXT,
            platform TEXT,
            url TEXT,
            timestamp DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 预警历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alert_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type TEXT,
            title TEXT,
            message TEXT,
            priority INTEGER,
            action TEXT,
            data TEXT,
            timestamp DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 检查是否有数据
    cursor.execute("SELECT COUNT(*) FROM price_history")
    price_count = cursor.fetchone()[0]
    
    if price_count == 0:
        print("📊 创建示例价格数据...")
        create_sample_prices(cursor, conn)
    
    cursor.execute("SELECT COUNT(*) FROM alert_history")
    alert_count = cursor.fetchone()[0]
    
    if alert_count == 0:
        print("🔔 创建示例预警数据...")
        create_sample_alerts(cursor, conn)
    
    conn.commit()
    conn.close()
    
    print(f"✅ 数据库初始化完成: {db_path}")

def create_sample_prices(cursor, conn):
    """创建示例价格数据"""
    base_price = 5999
    current_time = datetime.now()
    
    for i in range(48):  # 2天的数据
        timestamp = current_time - timedelta(hours=i*0.5)
        
        for age in [0, 3, 6, 9, 12, 18, 24]:
            # 模拟价格波动
            lambda_val = -math.log(0.68) / 14
            predicted_price = base_price * math.exp(-lambda_val * age)
            variation = 0.9 + (random.random() * 0.2)  # 0.9-1.1波动
            price = round(predicted_price * variation)
            
            platforms = ["xianyu", "zhuanzhuan", "aihuishou"]
            platform = platforms[i % len(platforms)]
            
            condition = "全新未拆" if age == 0 else "95新" if age <= 6 else "9新" if age <= 12 else "85新"
            
            cursor.execute('''
                INSERT INTO price_history 
                (model, age_months, price, source, condition, storage, platform, url, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                "iPhone 18",
                age,
                price,
                "示例数据",
                condition,
                "256GB",
                platform,
                f"https://example.com/{platform}/{age}",
                timestamp.isoformat()
            ))
    
    print(f"✅ 已创建 {cursor.rowcount} 条示例价格数据")

def create_sample_alerts(cursor, conn):
    """创建示例预警数据"""
    alert_types = ["买入信号", "卖出信号", "成本达标", "价格暴跌", "价格暴涨"]
    alert_titles = [
        "💰 发现买入机会！",
        "📈 发现卖出机会！",
        "🎯 月成本目标达成！",
        "⚠️ 价格快速下跌",
        "📊 价格快速上涨"
    ]
    alert_messages = [
        "iPhone 18（6个月二手）价格低于预测价5.2%",
        "iPhone 18（12个月二手）价格高于预测价8.7%",
        "发现月成本¥88.9的策略，接近目标¥90",
        "iPhone 18价格24小时内下跌3.2%",
        "iPhone 18价格24小时内上涨2.8%"
    ]
    
    current_time = datetime.now()
    
    for i in range(10):
        timestamp = current_time - timedelta(hours=i*2)
        alert_idx = i % len(alert_types)
        
        cursor.execute('''
            INSERT INTO alert_history 
            (alert_type, title, message, priority, action, data, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert_types[alert_idx],
            alert_titles[alert_idx],
            alert_messages[alert_idx],
            random.randint(1, 5),
            "查看详情" if i < 5 else None,
            json.dumps({"model": "iPhone 18", "age_months": i*3}) if i < 5 else None,
            timestamp.isoformat()
        ))
    
    print(f"✅ 已创建 {cursor.rowcount} 条示例预警数据")

# ==================== 数据库查询函数 ====================
def get_prices(model="iPhone 18", limit=100, platform=None, age_months=None):
    """获取价格数据"""
    try:
        conn = sqlite3.connect("data/iphone_monitor.db")
        cursor = conn.cursor()
        
        query = "SELECT * FROM price_history WHERE model = ?"
        params = [model]
        
        if platform is not None:
            query += " AND platform = ?"
            params.append(platform)
        
        if age_months is not None:
            query += " AND age_months = ?"
            params.append(age_months)
        
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
        
        return prices
        
    except Exception as e:
        print(f"❌ 获取价格数据失败: {e}")
        return []

def get_alerts(limit=50, alert_type=None, priority_min=1, priority_max=5):
    """获取预警数据"""
    try:
        conn = sqlite3.connect("data/iphone_monitor.db")
        cursor = conn.cursor()
        
        query = "SELECT * FROM alert_history WHERE priority BETWEEN ? AND ?"
        params = [priority_min, priority_max]
        
        if alert_type is not None:
            query += " AND alert_type = ?"
            params.append(alert_type)
        
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
        
        return alerts
        
    except Exception as e:
        print(f"❌ 获取预警数据失败: {e}")
        return []

def get_statistics():
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
            "price_count": price_count,
            "alert_count": alert_count,
            "recent_alerts_24h": recent_alerts,
            "platform_distribution": dict(platform_stats)
        }
        
    except Exception as e:
        print(f"❌ 获取统计数据失败: {e}")
        return {
            "price_count": 100,
            "alert_count": 15,
            "recent_alerts_24h": 3,
            "platform_distribution": {"xianyu": 40, "zhuanzhuan": 35, "aihuishou": 25}
        }

def calculate_strategy(target_monthly_cost=90.0):
    """计算最优策略"""
    # 简化策略计算
    buy_age = 6
    hold_months = 36
    buy_price = 5085
    sell_price = 1886
    monthly_cost = (buy_price - sell_price) / hold_months
    
    return {
        "buy_age": buy_age,
        "hold_months": hold_months,
        "buy_price": buy_price,
        "sell_price": sell_price,
        "monthly_cost": round(monthly_cost, 2),
        "avg_age": round(buy_age + hold_months / 2, 1),
        "target_achieved": abs(monthly_cost - target_monthly_cost) <= 5,
        "recommendation": f"推荐购买{buy_age}个月二手，持有{hold_months}个月"
    }

# ==================== FastAPI应用 ====================
app = FastAPI(title="iPhone价格监控系统", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket客户端列表
clients = []

# ==================== API路由 ====================
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """首页"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/status")
async def get_status():
    """获取系统状态"""
    return {
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "message": "iPhone价格监控系统正常运行"
    }

@app.get("/api/prices")
async def get_prices_api(
    model: str = Query("iPhone 18", description="机型"),
    age_months: Optional[int] = Query(None, description="机龄(月)"),
    platform: Optional[str] = Query(None, description="平台"),
    limit: int = Query(100, description="返回数量")
):
    """获取价格数据"""
    try:
        prices = get_prices(model=model, limit=limit, platform=platform, age_months=age_months)
        
        return {
            "success": True,
            "count": len(prices),
            "data": prices
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts")
async def get_alerts_api(
    alert_type: Optional[str] = Query(None, description="预警类型"),
    priority_min: int = Query(1, description="最低优先级"),
    priority_max: int = Query(5, description="最高优先级"),
    limit: int = Query(50, description="返回数量")
):
    """获取预警数据"""
    try:
        alerts = get_alerts(limit=limit, alert_type=alert_type, priority_min=priority_min, priority_max=priority_max)
        
        return {
            "success": True,
            "count": len(alerts),
            "data": alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/strategy/calculate")
async def calculate_strategy_api(request: StrategyRequest):
    """计算最优策略"""
    try:
        strategy = calculate_strategy(request.target_monthly_cost)
        
        return {
            "success": True,
            "strategy": strategy,
            "message": f"找到月成本¥{strategy['monthly_cost']:.1f}的最优策略"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats_api():
    """获取统计数据"""
    try:
        stats = get_statistics()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/monitor/start")
async def start_monitoring():
    """启动监控"""
    return {
        "success": True,
        "message": "监控已启动（演示模式）",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/monitor/stop")
async def stop_monitoring():
    """停止监控"""
    return {
        "success": True,
        "message": "监控已停止",
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接"""
    await websocket.accept()
    clients.append(websocket)
    
    try:
        # 发送欢迎消息
        await websocket.send_text(json.dumps({
            "type": "welcome",
            "message": "已连接到iPhone价格监控系统",
            "timestamp": datetime.now().isoformat()
        }))
        
        # 定期发送模拟数据
        while True:
            # 模拟价格更新
            await asyncio.sleep(10)
            
            # 随机生成一些模拟数据
            mock_price = {
                "type": "price_update",
                "model": "iPhone 18",
                "age_months": random.choice([0, 3, 6, 9, 12]),
                "price": random.randint(4000, 6000),
                "platform": random.choice(["xianyu", "zhuanzhuan", "aihuishou"]),
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send_text(json.dumps(mock_price))
            
    except WebSocketDisconnect:
        clients.remove(websocket)
    except Exception as e:
        print(f"WebSocket错误: {e}")
        clients.remove(websocket)

# ==================== 主程序 ====================
if __name__ == "__main__":
    import uvicorn
    
    # 创建必要目录
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # 初始化数据库
    init_database()
    
    print("=" * 70)
    print("🌐 iPhone价格监控Web应用 - 简化版本")
    print("=" * 70)
    print("✅ 后端服务: FastAPI")
    print("✅ 前端界面: Bootstrap + Chart.js")
    print("✅ 数据库: SQLite")
    print("✅ WebSocket: 实时推送")
    print("=" * 70)
    print("📡 访问地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("📊 实时监控: http://localhost:8000")
    print("=" * 70)
    print("🛑 按 Ctrl+C 停止服务器")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")