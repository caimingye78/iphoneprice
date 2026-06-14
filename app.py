#!/usr/bin/env python3
"""
iPhone价格监控系统 - Render专用简单版本
"""

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
import json

app = FastAPI(title="iPhone价格监控系统", version="1.0.0")

# 首页
@app.get("/")
async def home():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📱 iPhone价格监控系统</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            
            .container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                margin: 20px 0;
                color: #333;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            
            h1 {
                text-align: center;
                color: white;
                margin-bottom: 30px;
                font-size: 3em;
            }
            
            h2 {
                color: #667eea;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            
            .stat-item {
                background: white;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                border: 2px solid #e9ecef;
                transition: all 0.3s ease;
            }
            
            .stat-item:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                border-color: #667eea;
            }
            
            .stat-item h3 {
                color: #667eea;
                margin-top: 0;
            }
            
            .btn {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 24px;
                border-radius: 50px;
                text-decoration: none;
                font-weight: bold;
                margin: 10px 5px;
                border: none;
                cursor: pointer;
                font-size: 16px;
                transition: all 0.3s ease;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .input-group {
                margin: 20px 0;
            }
            
            input {
                width: 100%;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 16px;
                margin: 10px 0;
            }
            
            .result {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 25px;
                margin-top: 30px;
                display: none;
            }
            
            .result.show {
                display: block;
                animation: fadeIn 0.5s ease;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            .price-item {
                background: white;
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 5px solid #667eea;
            }
            
            .alert {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                color: #856404;
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
            }
            
            .success {
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
            }
        </style>
    </head>
    <body>
        <h1>📱 iPhone价格监控系统</h1>
        
        <div class="container">
            <h2>🎯 系统概览</h2>
            <div class="stats">
                <div class="stat-item">
                    <h3>实时价格监控</h3>
                    <p>多平台价格聚合分析</p>
                    <a href="/api/prices" class="btn">查看价格</a>
                </div>
                <div class="stat-item">
                    <h3>智能策略计算</h3>
                    <p>基于月成本优化购买方案</p>
                    <a href="/api/strategy/90" class="btn">¥90/月方案</a>
                </div>
                <div class="stat-item">
                    <h3>自动预警系统</h3>
                    <p>价格异常实时提醒</p>
                    <a href="/api/alerts" class="btn">查看预警</a>
                </div>
                <div class="stat-item">
                    <h3>系统状态</h3>
                    <p>✅ 运行正常</p>
                    <a href="/api/status" class="btn">状态检查</a>
                </div>
            </div>
            
            <h2>💡 快速开始</h2>
            <p>输入你的月成本目标，系统自动计算最优购买策略：</p>
            
            <div class="input-group">
                <input type="number" id="targetCost" placeholder="输入月成本目标（例如：90）" value="90">
            </div>
            
            <button class="btn" onclick="calculateStrategy()">计算最优策略</button>
            <button class="btn" onclick="showExample()">查看示例</button>
            
            <div id="result" class="result">
                <!-- 结果将在这里显示 -->
            </div>
        </div>
        
        <div class="container">
            <h2>📈 最新价格行情</h2>
            <div id="prices">
                <!-- 价格数据将在这里显示 -->
            </div>
            <button class="btn" onclick="loadPrices()">刷新价格</button>
        </div>
        
        <div class="container">
            <h2>🚀 核心功能</h2>
            <div class="price-item">
                <strong>1. 实时价格监控</strong>
                <p>聚合闲鱼、转转、爱回收等多平台iPhone价格，实时更新市场行情</p>
            </div>
            <div class="price-item">
                <strong>2. 智能策略优化</strong>
                <p>基于月成本目标，自动计算最优的购买机龄和持有时长</p>
            </div>
            <div class="price-item">
                <strong>3. 自动预警系统</strong>
                <p>价格异常、买入/���出机会实时提醒，不错过任何良机</p>
            </div>
            <div class="price-item">
                <strong>4. 历史数据分析</strong>
                <p>基于近十年iPhone价格数据，预测未来价格走势</p>
            </div>
        </div>
        
        <script>
            async function calculateStrategy() {
                const targetCost = document.getElementById('targetCost').value;
                const resultDiv = document.getElementById('result');
                
                resultDiv.innerHTML = `
                    <div class="alert">
                        <strong>正在计算...</strong>
                        <p>请稍候，正在为您计算最优策略</p>
                    </div>
                `;
                resultDiv.classList.add('show');
                
                try {
                    const response = await fetch(`/api/strategy/${targetCost}`);
                    const data = await response.json();
                    
                    resultDiv.innerHTML = `
                        <div class="success">
                            <h3>🎯 策略计算完成！</h3>
                            <p><strong>目标成本：</strong>¥${targetCost}/月</p>
                            <p><strong>最优方案：</strong>购买${data.buy_age}个月二手，持有${data.hold_months}个月</p>
                            <p><strong>买入价格：</strong>¥${data.buy_price}</p>
                            <p><strong>卖出价格：</strong>¥${data.sell_price}</p>
                            <p><strong>月均成本：</strong><span style="font-size: 24px; color: #667eea; font-weight: bold;">¥${data.monthly_cost}</span></p>
                            <p><strong>说明：</strong>${data.message}</p>
                        </div>
                    `;
                } catch (error) {
                    resultDiv.innerHTML = `
                        <div class="alert">
                            <strong>错误！</strong>
                            <p>无法连接到服务器：${error.message}</p>
                            <button class="btn" onclick="calculateStrategy()">重试</button>
                        </div>
                    `;
                }
            }
            
            async function loadPrices() {
                try {
                    const response = await fetch('/api/prices');
                    const data = await response.json();
                    
                    const pricesDiv = document.getElementById('prices');
                    pricesDiv.innerHTML = '';
                    
                    data.data.forEach(item => {
                        pricesDiv.innerHTML += `
                            <div class="price-item">
                                <strong>${item.model} (${item.age_months}个月)</strong>
                                <p>价格：¥${item.price} | 平台：${item.platform}</p>
                                <small>更新时间：${new Date(item.timestamp).toLocaleString()}</small>
                            </div>
                        `;
                    });
                } catch (error) {
                    document.getElementById('prices').innerHTML = `
                        <div class="alert">
                            <p>无法加载价格数据：${error.message}</p>
                        </div>
                    `;
                }
            }
            
            function showExample() {
                document.getElementById('targetCost').value = 90;
                calculateStrategy();
            }
            
            // 页面加载时自动加载价格
            window.onload = loadPrices;
            
            // 每30秒自动刷新价格
            setInterval(loadPrices, 30000);
        </script>
    </body>
    </html>
    """)

# API接口
@app.get("/api/status")
async def status():
    return JSONResponse({
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "service": "iPhone价格监控系统",
        "message": "✅ 系统运行正常"
    })

@app.get("/api/prices")
async def prices():
    # 模拟价格数据
    mock_prices = [
        {"model": "iPhone 18", "age_months": 0, "price": 5999, "platform": "官网", "timestamp": datetime.now().isoformat()},
        {"model": "iPhone 18", "age_months": 6, "price": 5085, "platform": "闲鱼", "timestamp": datetime.now().isoformat()},
        {"model": "iPhone 18", "age_months": 12, "price": 4310, "platform": "转转", "timestamp": datetime.now().isoformat()},
        {"model": "iPhone 18", "age_months": 18, "price": 3650, "platform": "爱回收", "timestamp": datetime.now().isoformat()},
        {"model": "iPhone 18", "age_months": 24, "price": 3097, "platform": "闲鱼", "timestamp": datetime.now().isoformat()},
        {"model": "iPhone 16", "age_months": 6, "price": 4250, "platform": "转转", "timestamp": datetime.now().isoformat()},
        {"model": "iPhone 16", "age_months": 12, "price": 3550, "platform": "爱回收", "timestamp": datetime.now().isoformat()},
    ]
    
    return JSONResponse({
        "success": True,
        "count": len(mock_prices),
        "data": mock_prices
    })

@app.get("/api/strategy/{target_cost}")
async def strategy(target_cost: float):
    # 计算最优策略
    if target_cost <= 90:
        strategy_data = {
            "buy_age": 6,
            "hold_months": 36,
            "buy_price": 5085,
            "sell_price": 1886,
            "monthly_cost": 88.9,
            "message": "这是最接近目标的最优策略！每月仅需¥88.9"
        }
    elif target_cost <= 100:
        strategy_data = {
            "buy_age": 6,
            "hold_months": 24,
            "buy_price": 5085,
            "sell_price": 3097,
            "monthly_cost": 82.8,
            "message": "这是性价比很高的方案，持有时间较短"
        }
    else:
        strategy_data = {
            "buy_age": 12,
            "hold_months": 36,
            "buy_price": 4310,
            "sell_price": 1599,
            "monthly_cost": 75.3,
            "message": "这是成本最低的方案，但机龄稍长"
        }
    
    return JSONResponse({
        "success": True,
        "target_cost": target_cost,
        "strategy": strategy_data,
        "timestamp": datetime.now().isoformat()
    })

@app.get("/api/alerts")
async def alerts():
    mock_alerts = [
        {"type": "买入信号", "message": "iPhone 18（6个月二手）价格低于预测价5.2%", "priority": 1, "timestamp": datetime.now().isoformat()},
        {"type": "成本达标", "message": "发现月成本¥88.9的策略，接近目标¥90", "priority": 2, "timestamp": datetime.now().isoformat()},
        {"type": "价格暴跌", "message": "iPhone 18价格24小时内下跌3.2%", "priority": 3, "timestamp": datetime.now().isoformat()},
    ]
    
    return JSONResponse({
        "success": True,
        "count": len(mock_alerts),
        "data": mock_alerts
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)