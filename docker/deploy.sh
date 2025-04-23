#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}开始部署Resume系统...${NC}"

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
if [ ! -f "./backend/.env" ]; then
    echo -e "警告: backend/.env 文件不存在!"
    echo -e "请创建一个 backend/.env 文件后再继续"
    exit 1
fi

if [ ! -f "./frontend/.env" ]; then
    echo -e "警告: frontend/.env 文件不存在!"
    echo -e "请创建一个 frontend/.env 文件后再继续"
    exit 1
fi

# 确保上传文件夹存在
mkdir -p ./backend/uploads

# 部署服务
echo -e "${YELLOW}启动Docker容器...${NC}"
docker compose up -d

# 检查容器是否正常启动
echo -e "${YELLOW}检查容器状态...${NC}"
sleep 5
docker compose ps

echo -e "${GREEN}部署完成!${NC}"
echo -e "后端服务: http://localhost:8000"
echo -e "前端服务: http://localhost:6110"
echo -e "Celery Flower监控: http://localhost:5555"
echo -e "PostgreSQL: localhost:5420"
echo -e "Redis: localhost:6379" 