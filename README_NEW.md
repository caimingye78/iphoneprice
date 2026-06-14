# 📱 iPhone价格监控与策略优化系统

> **实时监控、智能策略、自动预警** - 基于历史数据的iPhone购买优化平台
> 🌐 **Web应用**: 实时价格监控仪表板 + 智能策略计算器 + 自动预警系统

## 🚀 快速开始

### 一键部署
```bash
# 克隆项目
git clone https://github.com/caimingye78/iphoneprice.git
cd iphoneprice

# 运行部署脚本（选择部署方式）
./deploy.sh
```

### 在线访问
- 🌐 **Web应用**: [本地运行](http://localhost:8000) 
- ☁️ **在线演示**: [Render部署](https://iphone-price-monitor.onrender.com) (可能需要几分钟启动)
- 📚 **API文档**: `/docs` 端点
- 📊 **实时监控**: WebSocket连接

### 主要功能
1. **📈 实时价格监控** - 多平台价格聚合（闲鱼、转转、爱回收）
2. **🎯 智能策略优化** - 基于月成本目标的最优购买策略
3. **🔔 自动预警系统** - 价格异常、买入/卖出机会实时预警
4. **📊 数据可视化** - 价格趋势图表、统计分析报告
5. **🌍 Web界面** - 响应式设计，支持PC/平板/手机

## 📋 部署选项

### 1. 📍 本地部署（开发测试）
```bash
cd web_app
pip install -r requirements.txt
python app_simple.py
# 访问 http://localhost:8000
```

### 2. ☁️ Render部署（生产环境，推荐）
1. 访问 https://render.com
2. 点击 "New +" → "Web Service"
3. 连接GitHub仓库
4. 配置服务（已提供 `render.yaml`）
5. 等待部署完成

### 3. 🐳 Docker部署
```bash
cd web_app
docker-compose up -d
# 访问 http://localhost:8000
```

### 4. 🚀 其他平台
- **Vercel**: 适合静态前端
- **Railway**: 简单易用
- **Fly.io**: 全球部署
- **Heroku**: 传统平台

## 🏗️ 项目结构

```
📁 iphoneprice/
├── 🚀 部署和配置
│   ├── deploy.sh          # 一键部署脚本
│   ├── DEPLOYMENT.md      # 详细部署指南
│   ├── .github/workflows/ # CI/CD自动化
│   └── web_app/           # Web应用目录
│       ├── app_simple.py  # FastAPI后端（简化版）
│       ├── templates/     # HTML前端模板
│       ├── requirements.txt # Python依赖
│       ├── render.yaml    # Render部署配置
│       └── Dockerfile     # Docker镜像配置
├── 📈 数据分析和图表
│   ├── charts/            # SVG/PNG价格图表
│   ├── report.html        # 交互式分析报告
│   ├── dashboard_prototype.html # 监控仪表板
│   └── scripts/           # Python分析脚本
├── 📄 文档和设计
│   ├── iphone_app_design.md # iOS应用设计文档
│   └── iphone18_price_predictions.html # iPhone18预测报告
└── 📊 核心功能模块
    ├── 实时价格监控
    ├── 策略优化引擎
    ├── 预警管理系统
    └── 数据持久化存储
```

## 🔧 技术架构

### 后端架构
- **框架**: FastAPI（高性能异步框架）
- **数据库**: SQLite（轻量级，易于部署）
- **实时通信**: WebSocket
- **API设计**: RESTful + OpenAPI文档
- **数据采集**: 多平台价格聚合

### 前端架构
- **UI框架**: Bootstrap 5
- **图表库**: Chart.js
- **时间处理**: Luxon
- **实时更新**: WebSocket
- **响应式设计**: 支持所有设备

### 部署架构
- **平台**: Render（主要）、Vercel、Railway
- **容器**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **监控**: 健康检查 + 日志系统

## 📊 核心算法

### 1. 月成本优化模型
```
月成本 = (买入价 - 卖出价) / 持有月数
目标: 在满足"新鲜度"约束下最小化月成本
```

### 2. 新鲜度计算
```
新鲜度 = 买入机龄 + 持有月数/2
越小代表用的科技越新
```

### 3. 最优策略搜索
- **搜索空间**: 买入机龄(0-36月) × 持有时长(12-48月)
- **优化目标**: 最小化月成本
- **约束条件**: 新鲜度阈值、价格可行性

### 4. 预警算法
- **买入信号**: 价格低于预测值5%以上
- **卖出信号**: 价格高于预测值10%以上
- **价格异常**: 24小时内涨跌超过8%
- **成本达标**: 月成本达到目标值±3%

## 🔄 开发路线图

### ✅ 已完成
- [x] 基础价格分析模型
- [x] Web应用框架
- [x] 实时监控系统
- [x] 预警机制
- [x] 部署配置

### 🚧 进行中
- [ ] 更多数据源集成
- [ ] 用户认证系统
- [ ] 移动端应用
- [ ] 高级分析功能

### 📅 计划中
- [ ] 机器学习价格预测
- [ ] 社区分享功能
- [ ] API市场
- [ ] 多语言支持

## 🤝 贡献指南

### 开发环境设置
```bash
# 1. 克隆仓库
git clone https://github.com/caimingye78/iphoneprice.git
cd iphoneprice

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 3. 安装开发依赖
pip install -r web_app/requirements.txt
pip install pytest black flake8

# 4. 启动开发服务器
cd web_app
uvicorn app_simple:app --reload
```

### 代码规范
- 使用Black格式化代码
- 遵循PEP 8编码规范
- 添加类型注解
- 编写单元测试

### 提交规范
- 提交信息使用英文
- 描述清晰的提交信息
- 关联Issue编号

## 📞 支持与联系

### 问题反馈
- 🐛 **Bug报告**: [GitHub Issues](https://github.com/caimingye78/iphoneprice/issues)
- 💡 **功能建议**: [GitHub Discussions](https://github.com/caimingye78/iphoneprice/discussions)
- ❓ **使用问题**: 查看文档或提问

### 社区支持
- 💬 加入讨论: GitHub Discussions
- 🤝 贡献代码: 提交Pull Request
- 📢 分享经验: 在社区分享使用案例

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**🎯 项目愿景**: 帮助用户以最低成本享受最新iPhone技术  
**📊 核心理念**: 数据驱动决策，智能优化成本  
**🚀 最终目标**: 成为最专业的手机购买优化平台

> 💡 **提示**: 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 获取详细部署指南  
> 📚 **文档**: 所有API接口文档可在 `/docs` 端点查看  
> 🐛 **问题**: 遇到问题请查看故障排除部分或提交Issue