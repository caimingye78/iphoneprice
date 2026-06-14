# 🚀 iPhone价格监控系统 - 一键部署指南

> **5分钟内完成部署，立即开始使用！**

## 📋 部署前准备

### 1. 系统要求
- **操作系统**: macOS / Linux / Windows (WSL2)
- **Python**: 3.8+ (本地部署需要)
- **Node.js**: 14+ (可选)
- **Docker**: 20.10+ (可选)
- **Git**: 任意版本

### 2. 克隆仓库
```bash
git clone https://github.com/caimingye78/iphoneprice.git
cd iphoneprice
```

## 🎯 推荐部署方案

### 方案A：🌐 **Render云部署** (最简单，适合生产环境)
**✅ 优点**: 免费、自动HTTPS、无需维护服务器  
**⏰ 时间**: 3-5分钟  
**💵 费用**: 免费

```bash
# 一键部署到Render
./deploy.sh render

# 或手动部署步骤:
# 1. 访问 https://dashboard.render.com
# 2. 点击 'New +' → 'Blueprint'
# 3. 连接GitHub仓库: caimingye78/iphoneprice
# 4. 选择配置文件: web_app/render.yaml
# 5. 点击 'Apply' 开始部署
```

**部署完成后的URL**: `https://iphone-price-monitor-xxxx.onrender.com`

### 方案B：💻 **本地开发部署** (适合开发测试)
**✅ 优点**: 快速启动、易于调试  
**⏰ 时间**: 2分钟  
**💵 费用**: 免费

```bash
# 一键本地部署
./deploy.sh local

# 启动后访问: http://localhost:8000
```

### 方案C：🐳 **Docker容器部署** (适合技术用户)
**✅ 优点**: 环境隔离、易于迁移  
**⏰ 时间**: 3分钟  
**💵 费用**: 免费

```bash
# 确保已安装Docker和Docker Compose
./deploy.sh docker

# 启动后访问: http://localhost:8000
```

## 📝 详细部署步骤

### Render云部署详细步骤

#### 步骤1：访问Render控制台
1. 打开 https://dashboard.render.com
2. 注册/登录账号（支持GitHub登录）

#### 步骤2：创建新服务
1. 点击右上角 **"New +"** 按钮
2. 选择 **"Blueprint"**

#### 步骤3：连接GitHub仓库
1. 在Blueprint页面，点击 **"Connect GitHub Repository"**
2. 搜索仓库: **caimingye78/iphoneprice**
3. 点击 **"Connect"**

#### 步骤4：配置部署
1. Render会自动检测 `web_app/render.yaml` 配置
2. 确认以下配置：
   - **Service Name**: iphone-price-monitor
   - **Plan**: Free
   - **Region**: Singapore (推荐亚洲用户)
   - **Branch**: main

#### 步骤5：开始部署
1. 点击 **"Apply"** 按钮
2. 等待部署完成（约3-5分钟）

#### 步骤6：获取访问地址
部署完成后，在服务页面找到 **"URL"** 字段：
```
https://iphone-price-monitor-xxxx.onrender.com
```

### 本地部署详细步骤

#### 步骤1：安装Python依赖
```bash
cd web_app
python3 -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

#### 步骤2：初始化数据库
```bash
mkdir -p data
python3 -c "
import sqlite3
conn = sqlite3.connect('data/iphone_monitor.db')
print('✅ 数据库创建成功')
conn.close()
"
```

#### 步骤3：启动服务器
```bash
python3 app_simple.py
```

#### 步骤4：访问应用
打开浏览器访问：http://localhost:8000

### Docker部署详细步骤

#### 步骤1：确保Docker已安装
```bash
docker --version
docker-compose --version  # 或 docker compose version
```

#### 步骤2：构建并启动
```bash
cd web_app

# 构建镜像
docker build -t iphone-price-monitor:latest .

# 启动服务
docker-compose up -d
```

#### 步骤3：查看运行状态
```bash
docker-compose ps
docker-compose logs -f  # 查看实时日志
```

## 🔧 环境变量配置

### Render环境变量设置
在Render控制台中添加以下环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `APP_ENV` | `production` | 生产环境 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `DATABASE_URL` | `data/iphone_monitor.db` | 数据库路径 |
| `API_KEY` | (可选) | API密钥 |

### 本地环境变量设置
创建 `.env` 文件：
```bash
cd web_app
cat > .env << EOF
APP_ENV=development
LOG_LEVEL=DEBUG
DATABASE_URL=data/iphone_monitor.db
EOF
```

## 🚨 故障排除

### 常见问题1：Render部署失败
**症状**: 构建失败或启动失败

**解决方案**:
1. 检查 `web_app/requirements.txt` 文件
2. 查看Render构建日志
3. 确保Python版本兼容性

```bash
# 本地测试构建
cd web_app
pip install -r requirements.txt
python3 app_simple.py
```

### 常见问题2：数据库连接错误
**症状**: 无法创建或连接数据库

**解决方案**:
```bash
# 检查文件权限
ls -la data/

# 重新创建数据库
rm -f data/iphone_monitor.db
python3 -c "
import sqlite3
conn = sqlite3.connect('data/iphone_monitor.db')
conn.close()
"
```

### 常见问题3：端口占用
**症状**: 无法启动服务器

**解决方案**:
```bash
# 查看占用端口的进程
sudo lsof -i :8000

# 停止占用进程
sudo kill -9 <PID>
```

### 常见问题4：依赖安装失败
**症状**: pip安装报错

**解决方案**:
```bash
# 升级pip
pip install --upgrade pip

# 使用清华镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📊 部署验证

### 健康检查
```bash
# 检查API状态
curl https://iphone-price-monitor-xxxx.onrender.com/api/status

# 期望响应:
{
  "status": "running",
  "version": "1.0.0",
  "timestamp": "..."
}
```

### 功能测试
1. **主页**: 访问 `/`
2. **API文档**: 访问 `/docs`
3. **价格数据**: 访问 `/api/prices`
4. **预警数据**: 访问 `/api/alerts`

## 🔄 更新部署

### Render更新
```bash
# 更新代码后推送
git push origin main

# Render会自动重新部署
```

### 手动重新部署
1. 访问Render控制台
2. 找到服务
3. 点击 **"Manual Deploy"** → **"Clear Cache & Deploy"**

## 📞 技术支持

### 获取帮助
- **GitHub Issues**: https://github.com/caimingye78/iphoneprice/issues
- **Render文档**: https://render.com/docs
- **Docker文档**: https://docs.docker.com

### 紧急联系
如果部署遇到问题，可以通过以下方式获取帮助：
1. 查看日志文件: `web_app/logs/app.log`
2. 检查系统状态: `/api/status`
3. 提交GitHub Issue

---

**🎯 部署成功提示**: 看到 "🚀 iPhone价格监控系统" 页面即表示部署成功！

**💡 小贴士**: 建议先本地测试，再部署到Render生产环境

**⏰ 预计时间**: 
- 本地部署: 2分钟
- Render部署: 5分钟
- Docker部署: 3分钟