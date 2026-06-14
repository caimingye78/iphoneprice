# iPhone价格监控Web应用

基于FastAPI构建的iPhone价格实时监控与策略优化Web应用。

## 🚀 功能特性

### 📊 核心功能
- **实时价格监控**：多平台价格聚合（闲鱼、转转、爱回收等）
- **智能策略优化**：基于月成本目标的最优购买策略计算
- **自动预警系统**：6种预警类型，优先级1-5
- **数据可视化**：价格趋势图、统计图表、实时仪表板
- **历史数据分析**：价格历史查询、趋势分析、对比图表

### 🌐 Web界面
- **响应式设计**：支持PC、平板、手机
- **实时更新**：WebSocket实时推送价格变化和预警
- **交互式图表**：可缩放、可筛选的价格趋势图
- **用户友好**：直观的仪表板、简洁的操作界面

### 🔧 技术特性
- **后端框架**：FastAPI（高性能异步框架）
- **前端技术**：Bootstrap 5 + Chart.js + Luxon
- **数据库**：SQLite（轻量级，易于部署）
- **实时通信**：WebSocket
- **API设计**：RESTful API + OpenAPI文档

## 📋 系统要求

### 最低要求
- Python 3.8+
- 500MB可用磁盘空间
- 512MB RAM

### 推荐配置
- Python 3.10+
- 1GB可用磁盘空间
- 1GB RAM
- 现代浏览器（Chrome 90+, Firefox 88+, Safari 14+）

## 🛠️ 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/caimingye78/iphoneprice.git
cd iphoneprice/web_app
```

### 2. 一键安装运行（推荐）
```bash
# 自动安装依赖并启动
python run.py
```

### 3. 手动安装运行
```bash
# 安装依赖
pip install fastapi uvicorn sqlalchemy pydantic pyyaml aiohttp

# 启动服务器
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问应用
- 🌐 **Web界面**: http://localhost:8000
- 📚 **API文档**: http://localhost:8000/docs
- 🔌 **实时监控**: http://localhost:8000 （WebSocket连接）

## 📁 项目结构

```
web_app/
├── app.py                 # FastAPI主应用
├── run.py                # 一键启动脚本
├── config.yaml           # 配置文件
├── README.md            # 本文档
├── requirements.txt     # Python依赖
│
├── templates/           # HTML模板
│   └── index.html      # 主界面
│
├── static/             # 静态文件
│   ├── css/           # 样式表
│   ├── js/            # JavaScript
│   └── images/        # 图片资源
│
├── data/              # 数据文件
│   ├── iphone_monitor.db  # SQLite数据库
│   └── reports/      # 生成的报告
│
└── logs/             # 日志文件
    └── web_app.log   # 应用日志
```

## ⚙️ 配置说明

### 配置文件 (`config.yaml`)
```yaml
# 应用配置
app:
  name: "iPhone价格监控系统"
  port: 8000
  debug: true

# 监控配置
monitor:
  target_monthly_cost: 90.0      # 目标月成本
  target_model: "iPhone 18"      # 目标机型
  check_interval: 3600          # 检查间隔（秒）

# 数据库配置
database:
  path: "data/iphone_monitor.db"
  backup_enabled: true
```

### 环境变量
可通过环境变量覆盖配置：
```bash
export MONITOR_TARGET_COST=95
export MONITOR_TARGET_MODEL="iPhone 17"
export APP_PORT=8080
```

## 🔌 API接口

### 主要接口

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/status` | 系统状态 |
| GET | `/api/prices` | 价格数据查询 |
| GET | `/api/alerts` | 预警数据查询 |
| POST | `/api/strategy/calculate` | 计算最优策略 |
| POST | `/api/monitor/start` | 启动监控 |
| POST | `/api/monitor/stop` | 停止监控 |
| GET | `/api/stats` | 统计数据 |
| WS | `/ws` | WebSocket连接 |

### WebSocket消息类型
- `price_update`: 价格更新
- `alert`: 新预警
- `strategy_update`: 策略更新
- `status`: 监控状态

## 📈 使用示例

### 1. 查询价格数据
```bash
curl "http://localhost:8000/api/prices?model=iPhone%2018&limit=10"
```

### 2. 计算最优策略
```bash
curl -X POST "http://localhost:8000/api/strategy/calculate" \
  -H "Content-Type: application/json" \
  -d '{"target_monthly_cost": 90.0}'
```

### 3. 获取统计数据
```bash
curl "http://localhost:8000/api/stats"
```

## 🐳 Docker部署

### 构建镜像
```bash
docker build -t iphone-price-monitor .
```

### 运行容器
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --name iphone-monitor \
  iphone-price-monitor
```

### Docker Compose
```yaml
version: '3.8'
services:
  iphone-monitor:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

## 🔒 安全配置

### 1. 启用认证（可选）
在 `config.yaml` 中配置：
```yaml
security:
  api_key_auth:
    enabled: true
    api_keys:
      - "your-secret-api-key"
```

### 2. 限制访问
```yaml
security:
  cors:
    allow_origins: ["https://your-domain.com"]
  rate_limit:
    enabled: true
    requests_per_minute: 60
```

## 🧪 测试

### 运行测试
```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行测试
pytest tests/
```

### API测试示例
```python
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
```

## 📊 监控与维护

### 查看日志
```bash
# 实时查看日志
tail -f logs/web_app.log

# 查看错误日志
grep "ERROR" logs/web_app.log
```

### 数据库维护
```bash
# 备份数据库
cp data/iphone_monitor.db data/backup/iphone_monitor_$(date +%Y%m%d).db

# 清理旧数据（保留30天）
sqlite3 data/iphone_monitor.db "DELETE FROM price_history WHERE timestamp < datetime('now', '-30 days')"
```

### 性能监控
```bash
# 查看系统状态
curl "http://localhost:8000/api/status"

# 查看数据库大小
ls -lh data/iphone_monitor.db
```

## 🚨 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查看占用8000端口的进程
   lsof -i :8000
   
   # 修改端口
   uvicorn app:app --port 8080
   ```

2. **依赖安装失败**
   ```bash
   # 使用虚拟环境
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **数据库错误**
   ```bash
   # 重新初始化数据库
   rm -f data/iphone_monitor.db
   python run.py
   ```

4. **WebSocket连接失败**
   - 检查防火墙设置
   - 确保使用正确的协议（ws://或wss://）
   - 查看浏览器控制台错误信息

### 日志级别
在 `config.yaml` 中调整日志级别：
```yaml
logging:
  level: "DEBUG"  # 更详细的日志
```

## 🔄 更新升级

### 备份配置和数据
```bash
# 备份配置
cp config.yaml config.yaml.backup

# 备份数据库
cp data/iphone_monitor.db data/iphone_monitor.db.backup
```

### 更新代码
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启服务
pkill -f "uvicorn app:app"
python run.py
```

## 🤝 贡献指南

### 开发环境设置
```bash
# 1. 克隆仓库
git clone https://github.com/caimingye78/iphoneprice.git

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 3. 安装开发依赖
pip install -r requirements-dev.txt

# 4. 启动开发服务器
uvicorn app:app --reload
```

### 代码规范
- 使用Black格式化代码
- 遵循PEP 8编码规范
- 添加类型注解
- 编写单元测试

### 提交规范
- 提交信息使用英文
- 描述清晰的提交信息
- 关联Issue编号（如: Fix #123）

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情。

## 📞 支持与联系

### 问题反馈
- 🐛 **Bug报告**: [GitHub Issues](https://github.com/caimingye78/iphoneprice/issues)
- 💡 **功能建议**: [GitHub Discussions](https://github.com/caimingye78/iphoneprice/discussions)
- ❓ **使用问题**: 查看 [FAQ](../FAQ.md)

### 贡献者
- [caimingye78](https://github.com/caimingye78) - 项目创建者
- 欢迎贡献代码、文档或测试！

## 📈 路线图

### 近期计划
- [ ] 集成更多价格数据源
- [ ] 添加移动端应用
- [ ] 实现用户账户系统
- [ ] 添加更多分析图表

### 长期目标
- [ ] 机器学习价格预测
- [ ] 社区功能
- [ ] 多语言支持
- [ ] API市场

---

**🎯 目标**: 帮助用户以最低成本享受最新iPhone技术

**📊 核心理念**: 数据驱动决策，智能优化成本

**🚀 愿景**: 成为最专业的手机购买优化平台