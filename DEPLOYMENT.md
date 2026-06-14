# iPhone价格监控系统 - 部署指南

## 🚀 快速部署

### 方法1: Render（最简单，推荐）
1. **访问** https://render.com
2. **点击** "New +" → "Web Service"
3. **连接GitHub仓库** 选择你的 `caimingye78/iphoneprice` 仓库
4. **配置服务**:
   - **Name**: `iphone-price-monitor`
   - **Environment**: `Python`
   - **Region**: `Frankfurt`（或离你最近的地区）
   - **Branch**: `main`
   - **Build Command**: `pip install -r web_app/requirements.txt`
   - **Start Command**: `uvicorn web_app.app_simple:app --host 0.0.0.0 --port $PORT`
5. **点击** "Create Web Service"
6. **等待部署完成**（约5-10分钟）
7. **访问** https://iphone-price-monitor.onrender.com

### 方法2: Vercel + Render（前后端分离）
- **前端**（Vercel）: 部署静态HTML/CSS/JS
- **后端**（Render）: 部署FastAPI服务

### 方法3: Railway（备选）
1. 访问 https://railway.app
2. 点击 "New Project" → "Deploy from GitHub"
3. 选择仓库，自动检测Python应用
4. 访问生成的URL

## 📦 本地部署

### 1. 环境要求
- Python 3.8+
- SQLite3
- 500MB可用磁盘空间

### 2. 安装步骤
```bash
# 克隆仓库
git clone https://github.com/caimingye78/iphoneprice.git
cd iphoneprice

# 安装依赖
cd web_app
pip install -r requirements.txt

# 启动应用
python app_simple.py
# 或
uvicorn app_simple:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问地址
- 🌐 Web界面: http://localhost:8000
- 📚 API文档: http://localhost:8000/docs
- 📊 实时监控: http://localhost:8000

## 🐳 Docker部署

### 1. 使用Docker Compose
```bash
cd iphoneprice/web_app
docker-compose up -d
```

### 2. 构建自定义镜像
```bash
docker build -t iphone-price-monitor .
docker run -p 8000:8000 iphone-price-monitor
```

## 🔧 环境变量配置

### 生产环境推荐配置
```bash
# 应用配置
export APP_NAME="iPhone价格监控系统"
export APP_ENV="production"
export APP_DEBUG="false"

# 数据库配置
export DATABASE_URL="sqlite:///data/iphone_monitor.db"
export DATABASE_BACKUP_ENABLED="true"

# 监控配置
export MONITOR_TARGET_COST="90.0"
export MONITOR_TARGET_MODEL="iPhone 18"
export MONITOR_CHECK_INTERVAL="3600"

# 安全配置
export SECRET_KEY="your-secret-key-here"
export CORS_ORIGINS="https://your-domain.com"
```

## 📊 监控与维护

### 1. 健康检查
```bash
# 检查服务状态
curl https://iphone-price-monitor.onrender.com/api/status

# 检查数据库连接
curl https://iphone-price-monitor.onrender.com/api/stats
```

### 2. 日志查看
```bash
# Render控制台查看日志
# 或使用命令行
curl https://iphone-price-monitor.onrender.com/api/logs
```

### 3. 数据备份
```bash
# 手动备份数据库
sqlite3 data/iphone_monitor.db ".backup backup/iphone_monitor_$(date +%Y%m%d).db"
```

## 🔒 安全建议

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

### 3. HTTPS强制
确保所有部署都启用HTTPS：
- Render: 自动提供HTTPS
- Vercel: 自动提供HTTPS
- Railway: 自动提供HTTPS

## 🚨 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   lsof -i :8000
   # 或修改端口
   uvicorn app_simple:app --port 8080
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
   python app_simple.py
   ```

4. **内存不足**
   ```bash
   # 增加Swap空间
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Render特定问题

1. **部署失败**
   - 检查 `requirements.txt` 格式
   - 确保 `render.yaml` 配置正确
   - 查看Render控制台日志

2. **应用启动失败**
   - 检查启动命令中的模块路径
   - 确保 `app_simple.py` 存在
   - 查看应用日志中的Python错误

3. **内存超限**
   - 免费套餐内存限制为512MB
   - 优化应用内存使用
   - 考虑升级到付费套餐

## 📈 性能优化

### 1. 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_price_history_timestamp ON price_history(timestamp);
CREATE INDEX idx_price_history_model ON price_history(model);
CREATE INDEX idx_alert_history_timestamp ON alert_history(timestamp);
```

### 2. 缓存优化
```python
# 使用内存缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_prices(limit: int = 100):
    return get_prices(limit=limit)
```

### 3. 异步优化
```python
# 使用异步数据库操作
async def get_prices_async(limit: int = 100):
    return await asyncio.to_thread(get_prices, limit)
```

## 🔄 更新升级

### 1. 备份重要数据
```bash
# 备份数据库
cp data/iphone_monitor.db data/backup/iphone_monitor_$(date +%Y%m%d).db

# 备份配置文件
cp config.yaml config.yaml.backup
```

### 2. 更新代码
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启服务
pkill -f "uvicorn app_simple:app"
python app_simple.py
```

### 3. 验证更新
```bash
# 检查服务状态
curl http://localhost:8000/api/status

# 检查功能是否正常
curl "http://localhost:8000/api/prices?limit=5"
```

## 🌐 域名绑定

### 1. Render自定义域名
1. 进入Render Dashboard
2. 选择你的服务
3. 点击 "Settings" → "Custom Domain"
4. 添加你的域名
5. 按照指引配置DNS

### 2. Vercel自定义域名
1. 进入Vercel Dashboard
2. 选择你的项目
3. 点击 "Settings" → "Domains"
4. 添加自定义域名

## 📞 支持与帮助

### 获取帮助
- 📖 **文档**: 查看 [README.md](./README.md)
- 🐛 **Bug报告**: [GitHub Issues](https://github.com/caimingye78/iphoneprice/issues)
- 💡 **功能建议**: [GitHub Discussions](https://github.com/caimingye78/iphoneprice/discussions)
- 🚀 **部署问题**: 查看平台文档（Render, Vercel, Railway）

### 社区支持
- 💬 加入讨论: GitHub Discussions
- 🤝 贡献代码: 提交Pull Request
- 📢 分享经验: 在社区分享你的使用案例

---

**🎯 部署成功标志**
- ✅ Web界面可访问
- ✅ API接口正常响应
- ✅ 数据库连接正常
- ✅ 实时推送功能正常
- ✅ 监控系统正常运行

**🚀 最佳实践**
1. 始终使用HTTPS
2. 定期备份数据
3. 监控应用性能
4. 及时更新依赖
5. 配置适当的日志

**📊 部署状态监控**
- 使用平台提供的监控工具
- 设置警报通知
- 定期检查应用健康状态
- 分析访问日志和性能指标