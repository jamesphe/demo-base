#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 默认版本
VERSION="1.0.0"

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项] [服务名称]"
    echo
    echo "选项:"
    echo "  -h, --help             显示帮助信息"
    echo "  -v, --version VERSION  指定要部署的版本 (默认: 1.0.0)"
    echo "  -a, --all-except-db   部署除数据库外的所有服务"
    echo
    echo "服务名称可以是:"
    echo "  resume-backend"
    echo "  resume-frontend"
    echo "  resume-celery-worker"
    echo "  resume-celery-beat"
    echo
    echo "示例:"
    echo "  $0                     # 部署所有服务（默认版本）"
    echo "  $0 -v 2.0.0           # 部署所有服务（指定版本）"
    echo "  $0 -v 2.0.0 resume-backend  # 部署指定服务（指定版本）"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -a|--all-except-db)
            SERVICE_NAME="all-except-db"
            shift
            ;;
        *)
            SERVICE_NAME="$1"
            shift
            ;;
    esac
done

echo -e "${YELLOW}开始部署Resume系统 (版本: $VERSION)...${NC}"

# 检查是否需要重新部署除数据库外的所有服务
if [ "$SERVICE_NAME" = "all-except-db" ]; then
    echo -e "${YELLOW}将重新部署除数据库外的所有服务...${NC}"
    SERVICES_TO_DEPLOY=("resume-backend" "resume-celery-worker" "resume-celery-beat" "resume-frontend")
    
    # 停止并删除要重新部署的服务
    for service in "${SERVICES_TO_DEPLOY[@]}"; do
        CONTAINER_ID=$(docker compose ps -q "$service")
        if [ -n "$CONTAINER_ID" ]; then
            echo -e "${YELLOW}检测到 $service 容器正在运行，将停止并删除旧容器...${NC}"
            docker compose stop "$service"
            docker compose rm -f "$service"
        fi
    done
    
    SERVICE_NAME=""  # 清空SERVICE_NAME以便后续代码正常处理
# 检查容器是否在运行
elif [ -n "$SERVICE_NAME" ]; then
    CONTAINER_ID=$(docker compose ps -q "$SERVICE_NAME")
    if [ -n "$CONTAINER_ID" ]; then
        echo -e "${YELLOW}检测到 $SERVICE_NAME 容器正在运行，将停止并删除旧容器...${NC}"
        docker compose stop "$SERVICE_NAME"
        docker compose rm -f "$SERVICE_NAME"
    fi
else
    RUNNING_CONTAINERS=$(docker compose ps -q)
    if [ -n "$RUNNING_CONTAINERS" ]; then
        echo -e "${YELLOW}检测到有容器正在运行，将停止并删除所有容器...${NC}"
        docker compose down
    fi
fi

# 检查镜像文件是否存在
declare -A IMAGES=(
    ["resume-backend"]="resume-backend-${VERSION}.tar"
    ["resume-celery-worker"]="resume-celery-worker-${VERSION}.tar"
    ["resume-celery-beat"]="resume-celery-beat-${VERSION}.tar"
    ["resume-frontend"]="resume-frontend-${VERSION}.tar"
)

# 加载Docker镜像
echo -e "${YELLOW}加载Docker镜像...${NC}"
for service in "${!IMAGES[@]}"; do
    img="${IMAGES[$service]}"
    
    # 如果指定了服务名称，只加载对应的镜像
    if [ -n "$SERVICE_NAME" ] && [ "$SERVICE_NAME" != "all-except-db" ] && [ "$service" != "$SERVICE_NAME" ]; then
        continue
    fi
    
    if [ -f "$img" ]; then
        echo -e "正在加载 $img..."
        docker load < "$img"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}成功加载 $img${NC}"
        else
            echo -e "${RED}加载 $img 失败!${NC}"
            exit 1
        fi
    else
        echo -e "${RED}警告: $img 不存在于当前目录${NC}"
    fi
done

# 确保.env文件存在
if [ -z "$SERVICE_NAME" ] || [ "$SERVICE_NAME" = "resume-backend" ]; then
    if [ ! -f "./backend/.env" ]; then
        echo -e "警告: backend/.env 文件不存在!"
        echo -e "请创建一个 backend/.env 文件后再继续"
        exit 1
    fi
fi

if [ -z "$SERVICE_NAME" ] || [ "$SERVICE_NAME" = "resume-frontend" ]; then
    if [ ! -f "./frontend/.env" ]; then
        echo -e "警告: frontend/.env 文件不存在!"
        echo -e "请创建一个 frontend/.env 文件后再继续"
        exit 1
    fi
fi

# 确保上传文件夹存在
if [ -z "$SERVICE_NAME" ] || [ "$SERVICE_NAME" = "resume-backend" ]; then
    mkdir -p ./backend/uploads
fi

# 导出VERSION环境变量供docker-compose使用
export VERSION

# 部署服务
echo -e "${YELLOW}启动Docker容器...${NC}"
if [ "$SERVICE_NAME" = "all-except-db" ]; then
    # 启动除数据库外的所有服务
    for service in "${SERVICES_TO_DEPLOY[@]}"; do
        docker compose up -d "$service"
    done
elif [ -n "$SERVICE_NAME" ]; then
    docker compose up -d "$SERVICE_NAME"
else
    docker compose up -d
fi

# 检查容器是否正常启动
echo -e "${YELLOW}检查容器状态...${NC}"
sleep 5
docker compose ps

echo -e "${GREEN}部署完成!${NC}"
if [ -z "$SERVICE_NAME" ]; then
    echo -e "后端服务: http://localhost:8000"
    echo -e "前端服务: http://localhost:6110"
    echo -e "Celery Flower监控: http://localhost:5555"
    echo -e "PostgreSQL: localhost:5420"
    echo -e "Redis: localhost:6379"
    echo -e "已部署版本: ${VERSION}"
fi 