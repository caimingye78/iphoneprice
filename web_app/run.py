#!/usr/bin/env python3
"""
iPhone价格监控Web应用 - 启动脚本
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    print("🔍 检查系统依赖...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 8:
        print(f"❌ 需要Python 3.8+，当前版本: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version}")
    
    # 检查必要目录
    required_dirs = ["templates", "static", "data", "logs"]
    for dir_name in required_dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ 目录已创建: {dir_name}")
    
    return True

def install_requirements():
    """安装Python依赖"""
    print("\n📦 安装Python依赖...")
    
    requirements = [
        "fastapi",
        "uvicorn[standard]",
        "sqlalchemy",
        "pydantic",
        "pyyaml",
        "aiohttp",
        "aiosqlite",
        "python-multipart",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "email-validator",
        "pytest",
        "pytest-asyncio"
    ]
    
    try:
        import importlib
        for package in requirements:
            try:
                importlib.import_module(package.replace("-", "_").split("[")[0])
                print(f"✅ {package} 已安装")
            except ImportError:
                print(f"📥 正在安装 {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} 安装完成")
    except Exception as e:
        print(f"❌ 安装依赖失败: {e}")
        return False
    
    return True

def init_database():
    """初始化数据库"""
    print("\n🗄️ 初始化数据库...")
    
    try:
        # 导入数据库管理模块
        sys.path.append('../scripts')
        from iphone_price_monitor_enhanced import DatabaseManager
        
        db_manager = DatabaseManager()
        print("✅ 数据库初始化完成")
        
        # 创建示例数据（可选）
        print("📊 创建示例数据...")
        create_sample_data()
        
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def create_sample_data():
    """创建示例数据"""
    try:
        import sqlite3
        from datetime import datetime, timedelta
        
        conn = sqlite3.connect("data/iphone_monitor.db")
        cursor = conn.cursor()
        
        # 检查是否有数据
        cursor.execute("SELECT COUNT(*) FROM price_history")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("  创建示例价格数据...")
            
            # 添加一些示例价格数据
            base_price = 5999
            current_time = datetime.now()
            
            for i in range(24):  # 24小时的数据
                timestamp = current_time - timedelta(hours=i)
                
                # 不同机龄的价格
                for age in [0, 3, 6, 9, 12, 18, 24]:
                    # 模拟价格波动
                    import math
                    import random
                    
                    lambda_val = -math.log(0.68) / 14
                    predicted_price = base_price * math.exp(-lambda_val * age)
                    variation = 0.9 + (random.random() * 0.2)  # 0.9-1.1波动
                    price = round(predicted_price * variation)
                    
                    platforms = ["xianyu", "zhuanzhuan", "aihuishou"]
                    platform = platforms[i % len(platforms)]
                    
                    condition = "全新未拆" if age == 0 else "95新" if age <= 6 else "9新" if age <= 12 else "85新"
                    
                    cursor.execute("""
                        INSERT INTO price_history 
                        (model, age_months, price, source, condition, storage, platform, url, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
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
            
            conn.commit()
            print(f"✅ 已创建 {cursor.rowcount} 条示例价格数据")
        
        # 检查预警数据
        cursor.execute("SELECT COUNT(*) FROM alert_history")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("  创建示例预警数据...")
            
            # 添加一些示例预警
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
            
            for i in range(10):
                timestamp = current_time - timedelta(hours=i*2)
                alert_idx = i % len(alert_types)
                
                cursor.execute("""
                    INSERT INTO alert_history 
                    (alert_type, title, message, priority, action, data, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert_types[alert_idx],
                    alert_titles[alert_idx],
                    alert_messages[alert_idx],
                    random.randint(1, 5),
                    "查看详情" if i < 5 else None,
                    json.dumps({"model": "iPhone 18", "age_months": i*3}) if i < 5 else None,
                    timestamp.isoformat()
                ))
            
            conn.commit()
            print(f"✅ 已创建 {cursor.rowcount} 条示例预警数据")
        
        conn.close()
        
    except Exception as e:
        print(f"⚠️ 创建示例数据时出错: {e}")

def start_server():
    """启动Web服务器"""
    print("\n🚀 启动Web服务器...")
    print("=" * 70)
    print("🌐 iPhone价格监控Web应用")
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
    
    try:
        import uvicorn
        uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")

def create_config_file():
    """创建配置文件"""
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        print("\n⚙️ 创建配置文件...")
        
        config_content = """# iPhone价格监控Web应用配置

# 应用配置
app:
  name: "iPhone价格监控系统"
  version: "1.0.0"
  debug: true
  host: "0.0.0.0"
  port: 8000

# 监控配置
monitor:
  target_monthly_cost: 90.0
  target_model: "iPhone 18"
  buy_threshold: 0.05
  sell_threshold: 0.10
  cost_tolerance: 0.03
  check_interval: 3600

# 数据库配置
database:
  path: "data/iphone_monitor.db"
  backup_enabled: true

# 日志配置
logging:
  level: "INFO"
  file: "logs/web_app.log"
"""
        
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config_content)
        
        print(f"✅ 配置文件已创建: {config_path}")

def main():
    """主函数"""
    print("=" * 70)
    print("📱 iPhone价格监控Web应用 - 安装与启动")
    print("=" * 70)
    
    # 切换到脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 执行步骤
    steps = [
        ("检查系统依赖", check_dependencies),
        ("安装Python依赖", install_requirements),
        ("创建配置文件", create_config_file),
        ("初始化数据库", init_database),
        ("启动Web服务器", start_server)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*50}")
        print(f"步骤: {step_name}")
        print(f"{'='*50}")
        
        try:
            if not step_func():
                print(f"❌ {step_name} 失败")
                print("请手动检查并解决问题后重试")
                return
        except KeyboardInterrupt:
            print(f"\n🛑 用户中断: {step_name}")
            return
        except Exception as e:
            print(f"❌ {step_name} 出错: {e}")
            return

if __name__ == "__main__":
    import json
    import random
    
    main()