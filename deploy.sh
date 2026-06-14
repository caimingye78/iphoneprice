#!/bin/bash
# iPhone价格监控系统 - 一键部署脚本
# 支持多种部署方式：本地、Render、Docker

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印彩色消息
print_status() {
    echo -e "${BLUE}📱 [iPhone价格监控]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "命令 '$1' 未找到，请先安装"
        return 1
    fi
    return 0
}

# 显示帮助信息
show_help() {
    echo ""
    echo "📱 iPhone价格监控系统 - 部署脚本"
    echo "====================================="
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  local         本地开发环境部署"
    echo "  render        Render云端部署"
    echo "  docker        Docker容器部署"
    echo "  vercel        Vercel静态部署"
    echo "  all           ️ 部署所有环境"
    echo "  help          ️ 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 local        # 本地部署"
    echo "  $0 render       # Render云端部署"
    echo "  $0 docker       # Docker容器部署"
    echo ""
}

# 本地部署
deploy_local() {
    print_status "开始本地部署..."
    
    cd "$(dirname "$0")/web_app" || exit 1
    
    # 检查Python环境
    check_command python3 || return 1
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        print_status "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    print_status "激活虚拟环境..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        print_error "找不到虚拟环境激活脚本"
        return 1
    fi
    
    # 安装依赖
    print_status "安装Python依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # 创建必要目录
    print_status "创建数据目录..."
    mkdir -p data logs static/uploads
    
    # 初始化数据库
    print_status "初始化数据库..."
    python3 -c "
import sqlite3
import os
os.makedirs('data', exist_ok=True)
conn = sqlite3.connect('data/iphone_monitor.db')
print('✅ 数据库创建成功')
conn.close()
"
    
    # 启动服务器
    print_status "启动本地服务器..."
    echo ""
    echo "=========================================="
    echo "🚀 iPhone价格监控系统"
    echo "=========================================="
    echo "✅ 本地服务: http://localhost:8000"
    echo "📚 API文档: http://localhost:8000/docs"
    echo "📊 实时监控: WebSocket连接"
    echo "=========================================="
    echo ""
    echo "按 Ctrl+C 停止服务器"
    echo ""
    
    # 启动FastAPI服务器
    python3 app_simple.py
}

# Render部署
deploy_render() {
    print_status "开始Render云端部署..."
    
    print_status "检查Render CLI..."
    if ! command -v render &> /dev/null; then
        print_warning "Render CLI未安装，使用网页方式部署"
        echo ""
        echo "🌐 网页部署步骤:"
        echo "1. 访问 https://dashboard.render.com"
        echo "2. 点击 'New +' → 'Blueprint'"
        echo "3. 连接GitHub仓库: caimingye78/iphoneprice"
        echo "4. 选择 'web_app/render.yaml' 配置文件"
        echo "5. 点击 'Apply' 开始部署"
        echo ""
        echo "📋 部署配置详情见: web_app/render.yaml"
        echo ""
        return 0
    fi
    
    # 使用Render CLI部署
    print_status "使用Render CLI部署..."
    
    # 检查当前目录
    cd "$(dirname "$0")" || exit 1
    
    # 验证配置
    if [ ! -f "web_app/render.yaml" ]; then
        print_error "找不到 render.yaml 配置文件"
        return 1
    fi
    
    print_success "Render配置验证通过"
    echo ""
    echo "部署命令:"
    echo "  cd web_app"
    echo "  render blueprint launch"
    echo ""
    
    print_warning "注意: Render CLI可能需要登录和授权"
    print_warning "如果CLI不可用，请使用上述网页方式部署"
}

# Docker部署
deploy_docker() {
    print_status "开始Docker容器部署..."
    
    cd "$(dirname "$0")/web_app" || exit 1
    
    # 检查Docker
    check_command docker || return 1
    check_command docker-compose || {
        # 尝试使用docker compose v2
        if ! docker compose version &> /dev/null; then
            print_error "Docker Compose未安装"
            return 1
        fi
    }
    
    # 构建Docker镜像
    print_status "构建Docker镜像..."
    docker build -t iphone-price-monitor:latest .
    
    # 启动服务
    print_status "启动Docker容器..."
    
    # 检查docker-compose命令
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    # 等待服务启动
    print_status "等待服务启动..."
    sleep 5
    
    # 检查服务状态
    print_status "检查服务状态..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
    
    print_success "Docker部署完成!"
    echo ""
    echo "🌐 访问地址: http://localhost:8000"
    echo "📚 API文档: http://localhost:8000/docs"
    echo ""
    echo "管理命令:"
    echo "  cd web_app && docker-compose logs -f   # 查看日志"
    echo "  cd web_app && docker-compose stop      # 停止服务"
    echo "  cd web_app && docker-compose restart   # 重启服务"
    echo ""
}

# Vercel部署（静态前端）
deploy_vercel() {
    print_status "开始Vercel静态部署..."
    
    cd "$(dirname "$0")" || exit 1
    
    # 检查Vercel CLI
    check_command vercel || {
        print_warning "Vercel CLI未安装，使用网页方式部署"
        echo ""
        echo "🌐 网页部署步骤:"
        echo "1. 访问 https://vercel.com"
        echo "2. 导入GitHub仓库: caimingye78/iphoneprice"
        echo "3. 框架预设: Static Site"
        echo "4. 输出目录: ."
        echo "5. 点击 'Deploy'"
        echo ""
        return 0
    }
    
    # 检查vercel.json配置
    if [ ! -f "vercel.json" ]; then
        print_status "创建vercel.json配置文件..."
        cat > vercel.json << EOF
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "buildCommand": "echo 'Building static site...'",
  "outputDirectory": ".",
  "framework": "static"
}
EOF
    fi
    
    # 部署到Vercel
    print_status "部署到Vercel..."
    vercel --prod
    
    print_success "Vercel部署完成!"
    echo ""
    echo "📋 注意: Vercel仅部署静态文件"
    echo "🌐 后端API需单独部署到Render"
    echo ""
}

# 部署状态检查
check_deployment_status() {
    print_status "检查部署状态..."
    
    # 检查本地服务
    if curl -s http://localhost:8000/api/status &> /dev/null; then
        print_success "本地服务运行正常"
    else
        print_warning "本地服务未运行"
    fi
    
    echo ""
    echo "📊 部署完成!"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "📱 iPhone价格监控系统 - 一键部署"
    echo "=========================================="
    echo ""
    
    case "${1:-help}" in
        "local")
            deploy_local
            ;;
        "render")
            deploy_render
            ;;
        "docker")
            deploy_docker
            ;;
        "vercel")
            deploy_vercel
            ;;
        "all")
            echo "🚀 部署所有环境..."
            deploy_docker
            echo ""
            deploy_render
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"