#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取要更新的服务名称（如果有）
SERVICE_NAME=$1

echo -e "${YELLOW}开始部署Resume系统...${NC}"

# 检查容器是否在运行
if [ -n "$SERVICE_NAME" ]; then
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
IMAGES=(
    "resume-backend.tar"
    "resume-celery-worker.tar"
    "resume-celery-beat.tar"
    "resume-frontend.tar"
)

# 加载Docker镜像
echo -e "${YELLOW}加载Docker镜像...${NC}"
for img in "${IMAGES[@]}"; do
    # 如果指定了服务名称，只加载对应的镜像
    if [ -n "$SERVICE_NAME" ] && [[ ! "$img" =~ "$SERVICE_NAME" ]]; then
        continue
    fi
    
    if [ -f "$img" ]; then
        echo -e "正在加载 $img..."
        docker load < "$img"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}成功加载 $img${NC}"
        else
            echo -e "加载 $img 失败!"
            exit 1
        fi
    else
        echo -e "警告: $img 不存在于当前目录"
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

# 部署服务
echo -e "${YELLOW}启动Docker容器...${NC}"
if [ -n "$SERVICE_NAME" ]; then
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
fi 