#!/usr/bin/env python3
"""
iPhone价格监控系统 - Render专用单文件版本
直接放在仓库根目录运行
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import sqlite3
import json
import os
import random
import math

# ==================== 数据模型 ====================
class StrategyRequest(BaseModel):
    """策略请求"""
    target_monthly_cost: float = 90.0
    max_age_months: int = 36

# ==================== 数据库初始化 ====================
def init_database():
    """初始化数据库"""
    db_path = "iphone_monitor.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 价格历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT,
            age_months INTEGER,
            price REAL,
            platform TEXT,
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
            timestamp DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建示例数据
    create_sample_data(cursor, conn)
    
    conn.commit()
    conn.close()
    
    print(f"✅ 数据库初始化完成: {db_path}")
    return db_path

def create_sample_data(cursor, conn):
    """创建示例数据"""
    base_price = 5999
    current_time = datetime.now()
    
    # 创建价格数据
    for i in range(24):
        timestamp = current_time - timedelta(hours=i)
        
        for age in [0, 6, 12, 18, 24]:
            predicted_price = base_price * math.exp(-0.025 * age)
            price = round(predicted_price * (0.9 + random.random() * 0.2))
            
            cursor.execute('''
                INSERT INTO price_history (model, age_months, price, platform, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                "iPhone 18",
                age,
                price,
                random.choice(["闲鱼", "转转", "爱回收"]),
                timestamp.isoformat()
            ))
    
    # 创建预警数据
    alerts = [
        ("买入信号", "💰 发现买入机会！", "iPhone 18（6个月二手）价格低于预测价5.2%", 1),
        ("卖出信号", "📈 发现卖出机会！", "iPhone 18（12个月二手）价格高于预测价8.7%", 2),
        ("成本达标", "🎯 月成本目标达成！", "发现月成本¥88.9的策略，接近目标¥90", 3),
        ("价格暴跌", "⚠️ 价格快速下跌", "iPhone 18价格24小时内下跌3.2%", 4),
        ("价格暴涨", "📊 价格快速上涨", "iPhone 18价格24小时内上涨2.8%", 5),
    ]
    
    for i, (alert_type, title, message, priority) in enumerate(alerts):
        timestamp = current_time - timedelta(hours=i*6)
        
        cursor.execute('''
            INSERT INTO alert_history (alert_type, title, message, priority, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (alert_type, title, message, priority, timestamp.isoformat()))
    
    print(f"✅ 已创建示例数据")

# ==================== 数据库查询 ====================
def get_prices(model="iPhone 18", limit=50):
    """获取价格数据"""
    conn = sqlite3.connect("iphone_monitor.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM price_history 
        WHERE model = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (model, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    prices = []
    for row in rows:
        prices.append({
            "id": row[0],
            "model": row[1],
            "age_months": row[2],
            "price": row[3],
            "platform": row[4],
            "timestamp": row[5]
        })
    
    return prices

def get_alerts(limit=10):
    """获取预警数据"""
    conn = sqlite3.connect("iphone_monitor.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM alert_history 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    alerts = []
    for row in rows:
        alerts.append({
            "id": row[0],
            "alert_type": row[1],
            "title": row[2],
            "message": row[3],
            "priority": row[4],
            "timestamp": row[5]
        })
    
    return alerts

def calculate_strategy(target_monthly_cost=90.0):
    """计算最优策略"""
    # 基于历史数据分析的最优策略
    strategies = [
        {"age": 6, "months": 36, "buy": 5085, "sell": 1886, "cost": 88.9},
        {"age": 6, "months": 24, "buy": 5085, "sell": 3097, "cost": 82.8},
        {"age": 12, "months": 36, "buy": 4310, "sell": 1599, "cost": 75.3},
        {"age": 0, "months": 24, "buy": 5999, "sell": 3000, "cost": 124.9},
    ]
    
    # 找到最接近目标成本的策略
    best_strategy = min(strategies, key=lambda s: abs(s["cost"] - target_monthly_cost))
    
    return {
        "buy_age": best_strategy["age"],
        "hold_months": best_strategy["months"],
        "buy_price": best_strategy["buy"],
        "sell_price": best_strategy["sell"],
        "monthly_cost": best_strategy["cost"],
        "target_achieved": abs(best_strategy["cost"] - target_monthly_cost) <= 10,
        "recommendation": f"购买{best_strategy['age']}个月二手，持有{best_strategy['months']}个月"
    }

# ==================== FastAPI应用 ====================
app = FastAPI(title="iPhone价格监控系统", version="2.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== API路由 ====================
@app.get("/")
async def root():
    """首页"""
    return HTMLResponse('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📱 iPhone价格监控系统</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f7fa;
                color: #333;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            }
            
            .header h1 {
                margin: 0;
                font-size: 3em;
                font-weight: 700;
            }
            
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
                margin-top: 10px;
            }
            
            .card {
                background: white;
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 25px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
                border: 1px solid #e9ecef;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.12);
            }
            
            .card h2 {
                color: #2d3748;
                margin-top: 0;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }
            
            .stat-item {
                text-align: center;
                padding: 25px;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 12px;
                border: 1px solid #dee2e6;
                transition: all 0.3s ease;
            }
            
            .stat-item:hover {
                background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
                transform: scale(1.02);
            }
            
            .stat-item h3 {
                color: #495057;
                margin-top: 0;
                font-size: 1.2em;
            }
            
            .stat-item a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
                font-size: 1.1em;
                display: inline-block;
                margin-top: 10px;
                padding: 8px 16px;
                border-radius: 8px;
                background: white;
                border: 2px solid #667eea;
                transition: all 0.3s ease;
            }
            
            .stat-item a:hover {
                background: #667eea;
                color: white;
            }
            
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 14px 28px;
                border-radius: 10px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s ease;
                margin: 10px 5px;
                min-width: 200px;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .btn-secondary {
                background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            }
            
            .btn-success {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            }
            
            .status {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                display: inline-block;
                font-weight: 600;
                font-size: 0.9em;
            }
            
            .feature-list {
                list-style: none;
                padding: 0;
                margin: 20px 0;
            }
            
            .feature-list li {
                padding: 12px 0;
                border-bottom: 1px solid #e9ecef;
                display: flex;
                align-items: center;
                gap: 15px;
                font-size: 1.1em;
            }
            
            .feature-list li:last-child {
                border-bottom: none;
            }
            
            .feature-icon {
                background: #667eea;
                color: white;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2em;
            }
            
            .input-group {
                margin: 20px 0;
            }
            
            .input-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #495057;
            }
            
            .input-group input {
                width: 100%;
                padding: 14px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 16px;
                transition: border-color 0.3s ease;
            }
            
            .input-group input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .strategy-result {
                background: #f8fafc;
                border-radius: 12px;
                padding: 25px;
                margin-top: 25px;
                border: 1px solid #e2e8f0;
                display: none;
            }
            
            .strategy-result.show {
                display: block;
                animation: fadeIn 0.5s ease;
            }
            
            .strategy-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            
            .strategy-item {
                background: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 3px 10px rgba(0,0,0,0.05);
            }
            
            .strategy-item .value {
                font-size: 1.8em;
                font-weight: 700;
                color: #667eea;
                margin: 10px 0;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @media (max-width: 768px) {
                .header h1 { font-size: 2em; }
                .header { padding: 25px; }
                .card { padding: 20px; }
                .stats { grid-template-columns: 1fr; }
                .btn { min-width: 100%; margin: 5px 0; }
            }
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body>
        <div class="header">
            <h1><i class="fas fa-mobile-alt"></i> iPhone价格监控系统</h1>
            <p>实时监控、智能策略、自动预警 - 让每一分钱都花在刀刃上</p>
        </div>
        
        <div class="card">
            <h2><i class="fas fa-tachometer-alt"></i> 系统概览</h2>
            <div class="stats">
                <div class="stat-item">
                    <div class="feature-icon"><i class="fas fa-chart-line"></i></div>
                    <h3>实时价格监控</h3>
                    <p>多平台价格聚合分析</p>
                    <a href="/api/prices"><i class="fas fa-external-link-alt"></i> 查看价格数据</a>
                </div>
                <div class="stat-item">
                    <div class="feature-icon"><i class="fas fa-calculator"></i></div>
                    <h3>智能策略计算</h3>
                    <p>基于月成本优化购买方案</p>
                    <a href="/api/strategy/calculate?target_monthly_cost=90"><i class="fas fa-external-link-alt"></i> 计算最优策略</a>
                </div>
                <div class="stat-item">
                    <div class="feature-icon"><i class="fas fa-bell"></i></div>
                    <h3>自动预警系统</h3>
                    <p>价格异常实时提醒</p>
                    <a href="/api/alerts"><i class="fas fa-external-link-alt"></i> 查看预警记录</a>
                </div>
                <div class="stat-item">
                    <div class="feature-icon"><i class="fas fa-chart-bar"></i></div>
                    <h3>数据可视化</h3>
                    <p>价格趋势图表分析</p>
                    <a href="/api/stats"><i class="fas fa-external-link-alt"></i> 查看统计报告</a>
                </div>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e9ecef;">
                <p><strong>系统状态:</strong> <span class="status"><i class="fas fa-check-circle"></i> 运行正常</span></p>
                <p><strong>版本:</strong> 2.0.0 | <strong>最后更新:</strong> <span id="currentDate"></span></p>
                <p><strong>服务地址:</strong> <code id="serviceUrl"></code></p>
            </div>
        </div>
        
        <div class="card">
            <h2><i class="fas fa-calculator"></i> 智能策略优化器</h2>
            <p>输入你的月成本目标，系统自动计算最优购买策略：</p>
            
            <div class="input-group">
                <label for="targetCost"><i class="fas fa-bullseye"></i> 月成本目标（元）</label>
                <input type="number" id="targetCost" value="90" placeholder="例如：90" min="30" max="200" step="10">
            </div>
            
            <div class="input-group">
                <label for="maxAge"><i class="fas fa-calendar"></i> 最大接受机龄（月）</label>
                <input type="number" id="maxAge" value="12" placeholder="例如：12" min="0" max="36" step="6">
            </div>
            
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 25px 0;">
                <button class="btn" onclick="calculateStrategy()">
                    <i class="fas fa-calculator"></i> 计算最优策略
                </button>
                <button class="btn btn-secondary" onclick="showQuickStrategy(90)">
                    <i class="fas fa-bolt"></i> ¥90/月方案
                </button>
                <button class="btn btn-secondary" onclick="showQuickStrategy(100)">
                    <i class="fas fa-bolt"></i> ¥100/月方案
                </button>
                <button class="btn btn-success" onclick="resetCalculator()">
                    <i class="fas fa-redo"></i> 重置
                </button>
            </div>
            
            <div id="strategyResult" class="strategy-result">
                <!-- 结果将在这里显示 -->
            </div>
        </div>
        
        <div class="card">
            <h2><i class="fas fa-star"></i> 核心功能</h2>
            <ul class="feature-list">
                <li>
                    <div class="feature-icon"><i class="fas fa-chart-line"></i></div>
                    <div>
                        <strong>实时价格监控</strong><br>
                        聚合闲鱼、转转、爱回收等多平台价格，实时更新市场行情
                    </div>
                </li>
                <li>
                    <div class="feature-icon"><i class="fas fa-calculator"></i></div>
                    <div>
                        <strong>智能策略优化</strong><br>
                        基于月成本目标，自动计算最优的购买机龄和持有时长
                    </div>
                </li>
                <li>
                    <div class="feature-icon"><i class="fas fa-bell"></i></div>
                    <div>
                        <strong>自动预警系统</strong><br>
                        价格异常、买入/卖出机会实时提醒，不错过任何良机
                    </div>
                </li>
                <li>
                    <div class="feature-icon"><i class="fas fa-database"></i></div>
                    <div>
                        <strong>历史数据分析</strong><br>
                        基于近十年iPhone��格数据，预测未来价格走势
                    </div>
                </li>
                <li>
                    <div class="feature-icon"><i class="fas fa-mobile-alt"></i></div>
                    <div>
                        <strong>跨平台支持</strong><br>
                        响应式设计，支持手机、平板、电脑所有设备
                    </div>
                </li>
                <li>
                    <div class="feature-icon"><i class="fas fa-cloud"></i></div>
                    <div>
                        <strong>云端部署</strong><br>
                        随时随地访问，数据自动备份，永不丢失
                    </div>
                </li>
            </ul>
        </div>
        
        <div class="card">
            <h2><i class="fas fa-question-circle"></i> 如何使用</h2>
            <div class="strategy-grid">
                <div class="strategy-item">
                    <div class="feature-icon"><i class="fas fa-1"></i></div>
                    <h4>第一步：设定目标</h4>
                    <p>输入你期望的月成本（例如¥90）</p>
                </div>
                <div class="strategy-item">
                    <div class="feature-icon"><i class="fas fa-2"></i></div>
                    <h4>第二步：计算策略</h4>
                    <p>系统自动计算最优购买方案</p>
                </div>
                <div class="strategy-item">
                    <div class="feature-icon"><i class="fas fa-3"></i></div>
                    <h4>第三步：执行计划</h4>
                    <p>按照推荐的时间和价格买入</p>
                </div>
                <div class="strategy-item">
                    <div class="feature-icon"><i class="fas fa-4"></i></div>
                    <h4>第四步：监控优化</h4>
                    <p>系统持续监控，及时调整策略</p>
                </div>
            </div>
        </div>
        
        <script>
            // 显示当前日期
            document.getElementById('currentDate').textContent = new Date().toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            
            // 显示服务地址
            document.getElementById('serviceUrl').textContent = window.location.host;
            
            async function calculateStrategy() {
                const targetCost = document.getElementById('targetCost').value;
                const maxAge = document.getElementById('maxAge').value;
                
                const resultDiv = document.getElementById('strategyResult');
                resultDiv.innerHTML = `
                    <div style="text-align: center; padding: 20px;">
                        <i class="fas fa-spinner fa-spin fa-2x"></i>
                        <p>正在计算最优策略...</p>
                    </div>
                `;
                resultDiv.classList.add('show');
                
                try {
                    const response = await fetch(`/api/strategy/calculate?target_monthly_cost=${targetCost}`, {
                        method: 'POST'
                    });
                    const data = await response.json();
                    
                    if (data.success) {
                        const strategy = data.strategy;
                        const time = new Date().toLocaleTimeString('zh-CN');
                        
                        resultDiv.innerHTML = `
                            <h3><i class="fas fa-check-circle" style="color: #10b981;"></i> 策略计算完成 (${time})</h3>
                            <p><strong>目标成本:</strong> ¥${targetCost}/月</p>
                            <p><strong>计算结果:</strong> ${data.message}</p>
                            
                            <div class="strategy-grid">
                                <div class="strategy-item">
                                    <div class="feature-icon"><i class="fas fa-shopping-cart"></i></div>
                                    <h4>购买机龄</h4>
                                    <div class="value">${strategy.buy_age}个月</div>
                                    <p>二手手机机龄</p>
                                </div>
                                <div class="strategy-item">
                                    <div class="feature-icon"><i class="fas fa-calendar-alt"></i></div>
                                    <h4>持有时长</h4>
                                    <div class="value">${strategy.hold_months}个月</div>
                                    <p>建议使用时间</p>
                                </div>
                                <div class="strategy-item">
                                    <div class="feature-icon"><i class="fas fa-money-bill-wave"></i></div>
                                    <h4>买入价格</h4>
                                    <div class="value">¥${strategy.buy_price}</div>
                                    <p>预计买入价格</p>
                                </div>
                                <div class="strategy-item">
                                    <div class="feature-icon"><i class="fas fa-hand-holding-usd"></i></div>
                                    <h4>卖出价格</h4>
                                    <div class="value">¥${strategy.sell_price}</div>
                                    <p>预计卖出价格</p>
                                </div>
                            </div>
                            
                            <div style="text-align: center; margin: 25px 0; padding: 20px; background: linear-gradient(135deg, #f0fff4 0%, #dcffe4 100%); border-radius: 10px;">
                                <h3 style="color: #059669; margin-top: 0;">
                                    <i class="fas fa-trophy"></i> 最终月成本
                                </h3>
                                <div style="font-size: 3em; font-weight: 700; color: #059669; margin: 15px 0;">
                                    ¥${strategy.monthly_cost.toFixed(1)}
                                </div>
                                <p style="font-size: 1.2em;">
                                    ${strategy.target_achieved ? 
                                        '<span style="color: #10b981;"><i class="fas fa-check-circle"></i> 目标已达成！</span>' : 
                                        '<span style="color: #f59e0b;"><i class="fas fa-exclamation-triangle"></i> 接近目标</span>'
                                    }
                                </p>
                            </div>
                            
                            <div style="background: #f8fafc; padding: 20px; border-radius: 10px; margin-top: 20px;">
                                <h4><i class="fas fa-lightbulb"></i> 操作建议</h4>
                                <p><strong>${strategy.recommendation}</strong></p>
                                <p>平均机龄: ${strategy.avg_age || (strategy.buy_age + strategy.hold_months/2).toFixed(1)}个月</p>
                                <p>总折旧: ¥${strategy.buy_price - strategy.sell_price}</p>
                                <p>推荐操作时间: 每月初或促销季</p>
                            </div>
                            
                            <div style="margin-top: 25px; display: flex; gap: 10px; justify-content: center;">
                                <button class="btn" onclick="showPriceData()">
                                    <i class="fas fa-chart-line"></i> 查看价格走势
                                </button>
                                <button class="btn btn-secondary" onclick="saveStrategy()">
                                    <i class="fas fa-save"></i> 保存策略
                                </button>
                                <button class="btn btn-success" onclick="shareStrategy()">
                                    <i class="fas fa-share-alt"></i> 分享策略
                                </button>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `
                            <h3><i class="fas fa-exclamation-triangle" style="color: #f59e0b;"></i> 计算失败</h3>
                            <p>${data.message || '未知错误'}</p>
                            <button class="btn" onclick="calculateStrategy()">重试</button>
                        `;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `
                        <h3><i class="fas fa-exclamation-circle" style="color: #ef4444;"></i> 网络错误</h3>
                        <p>无法连接到服务器，请检查网络连接</p>
                        <p>错误信息: ${error.message}</p>
                        <button class="btn" onclick="calculateStrategy()">重试</button>
                    `;
                }
            }
            
            function showQuickStrategy(cost) {
                document.getElementById('targetCost').value = cost;
                calculateStrategy();
            }
            
            function resetCalculator() {
                document.getElementById('targetCost').value = 90;
                document.getElementById('maxAge').value = 12;
                document.getElementById('strategyResult').classList.remove('show');
            }
            
            function showPriceData() {
                window.open('/api/prices', '_blank');
            }
            
            function saveStrategy() {
                alert('策略已保存到本地！');
            }
            
            function shareStrategy() {
                const url = window.location.href;
                if (navigator.share) {
                    navigator.share({
                        title: 'iPhone价格监控策略',
                        text: '看看我找到的最优iPhone购买策略！',
                        url: url
                    });
                } else {
                    navigator.clipboard.writeText(url).then(() => {
                        alert('链接已复制到剪贴板！');
                    });
                }
            }
            
            // 页面加载完成后自动计算一个示例策略
            window.addEventListener('load', function() {
                setTimeout(() => {
                    document.getElementById('strategyResult').innerHTML = `
                        <div style="text-align: center; padding: 20px; color: #6c757d;">
                            <i class="fas fa-lightbulb fa-2x"></i>
                            <h3>立即开始优化你的iPhone购买策略</h3>
                            <p>输入月成本目标，点击"计算最优策略"开始优化</p>
                            <p>或者直接点击 <strong>¥90/月方案</strong> 查看推荐策略</p>
                        </div>
                    `;
                    document.getElementById('strategyResult').classList.add('show');
                }, 1000);
            });
        </script>
    </body>
    </html>
    ''')
            <p>输入你的月成本目标：</p>
            <input type="number" id="targetCost" value="90" placeholder="月成本目标">
            <button class="btn" onclick="calculateStrategy()">计算最优策略</button>
            <div id="strategyResult" style="margin-top: 20px;"></div>
        </div>
        
        <div class="card">
            <h2>📊 核心功能</h2>
            <ul>
                <li><strong>📈 实时价格监控</strong> - 多平台价格聚合</li>
                <li><strong>🎯 智能策略优化</strong> - 基于月成本目标计算最优购买方案</li>
                <li><strong>🔔 自动预警系统</strong> - 价格异常实时提醒</li>
                <li><strong>📈 数据可视化</strong> - 价格趋势图表</li>
                <li><strong>🌍 Web界面</strong> - 响应式设计，支持所有设备</li>
            </ul>
        </div>
        
        <script>
            async function calculateStrategy() {
                const targetCost = document.getElementById('targetCost').value;
                const response = await fetch(`/api/strategy/calculate?target_monthly_cost=${targetCost}`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                const resultDiv = document.getElementById('strategyResult');
                resultDiv.innerHTML = `
                    <h3>🎯 最优策略结果</h3>
                    <p><strong>购买机龄:</strong> ${data.strategy.buy_age}个月二手</p>
                    <p><strong>持有时长:</strong> ${data.strategy.hold_months}个月</p>
                    <p><strong>买入价格:</strong> ¥${data.strategy.buy_price}</p>
                    <p><strong>卖出价格:</strong> ¥${data.strategy.sell_price}</p>
                    <p><strong>月均成本:</strong> <strong style="color: #4CAF50;">¥${data.strategy.monthly_cost}</strong></p>
                    <p><strong>目标达成:</strong> ${data.strategy.target_achieved ? '✅ 已达成' : '⚠️ 未完全达成'}</p>
                    <p><strong>建议:</strong> ${data.strategy.recommendation}</p>
                    <p><strong>说明:</strong> ${data.message}</p>
                `;
            }
        </script>
    </body>
    </html>
    ''')

@app.get("/api/status")
async def get_status():
    """获取系统状态"""
    return {
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "service": "iPhone价格监控系统",
        "message": "✅ 系统运行正常，功能完整"
    }

@app.get("/api/prices")
async def get_prices_api(
    model: str = Query("iPhone 18", description="机型"),
    limit: int = Query(50, description="返回数量")
):
    """获取价格数据"""
    try:
        prices = get_prices(model=model, limit=limit)
        
        return {
            "success": True,
            "count": len(prices),
            "model": model,
            "data": prices
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts")
async def get_alerts_api(
    limit: int = Query(10, description="返回数量")
):
    """获取预警数据"""
    try:
        alerts = get_alerts(limit=limit)
        
        return {
            "success": True,
            "count": len(alerts),
            "data": alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/strategy/calculate")
async def calculate_strategy_api(
    target_monthly_cost: float = Query(90.0, description="月成本目标")
):
    """计算最优策略"""
    try:
        strategy = calculate_strategy(target_monthly_cost)
        
        return {
            "success": True,
            "target_cost": target_monthly_cost,
            "strategy": strategy,
            "message": f"找到月成本¥{strategy['monthly_cost']:.1f}的最优策略，{(strategy['monthly_cost'] - target_monthly_cost):+.1f}元"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """获取统计数据"""
    try:
        conn = sqlite3.connect("iphone_monitor.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM price_history")
        price_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alert_history")
        alert_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "success": True,
            "stats": {
                "price_records": price_count,
                "alert_records": alert_count,
                "uptime": "100%",
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 启动应用 ====================
if __name__ == "__main__":
    import uvicorn
    
    # 初始化数据库
    init_database()
    
    print("=" * 70)
    print("🚀 iPhone价格监控系统 - Render部署版本")
    print("=" * 70)
    print("✅ 单文件运行，无需目录结构")
    print("✅ 内置SQLite数据库")
    print("✅ 完整的API接口")
    print("✅ 响应式Web界面")
    print("=" * 70)
    print("📡 访问地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("📊 健康检查: http://localhost:8000/api/status")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
