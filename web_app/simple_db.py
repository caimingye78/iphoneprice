#!/usr/bin/env python3
"""
简化版数据库管理 - 用于Web应用演示
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
import random

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
    
    for i in range(72):  # 3天的数据
        timestamp = current_time - timedelta(hours=i)
        
        for age in [0, 3, 6, 9, 12, 18, 24]:
            # 模拟价格波动
            import math
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
    
    for i in range(15):
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

def get_prices(model="iPhone 18", limit=100):
    """获取价格数据"""
    try:
        conn = sqlite3.connect("data/iphone_monitor.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM price_history 
            WHERE model = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (model, limit))
        
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

def get_alerts(limit=50):
    """获取预警数据"""
    try:
        conn = sqlite3.connect("data/iphone_monitor.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM alert_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
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
            "price_count": 0,
            "alert_count": 0,
            "recent_alerts_24h": 0,
            "platform_distribution": {}
        }

if __name__ == "__main__":
    print("=" * 70)
    print("📊 简化版数据库管理器")
    print("=" * 70)
    
    init_database()
    
    # 测试查询
    print("\n🔍 测试查询...")
    prices = get_prices(limit=5)
    print(f"最近5条价格记录: {len(prices)} 条")
    
    alerts = get_alerts(limit=5)
    print(f"最近5条预警记录: {len(alerts)} 条")
    
    stats = get_statistics()
    print(f"统计数据: {stats}")
    
    print("\n✅ 数据库测试完成")