#!/bin/bash

# 确保脚本在出错时停止执行
set -e

# 更灵活的参数处理
PLATFORM="linux/amd64"  # 默认平台
VERSION="latest"        # 默认版本

# 处理参数
if [ $# -ge 1 ]; then
    if [ "$1" = "mac" ] || [[ "$1" == linux/* ]]; then
        # 第一个参数是平台
        PLATFORM=$([[ "$1" = "mac" ]] && echo "linux/arm64" || echo "$1")
        # 如果有第二个参数，则作为版本号
        if [ $# -ge 2 ]; then
            # 去掉版本号中的v前缀（如果存在）
            VERSION=$(echo "$2" | sed 's/^v//')
        fi
    else
        # 第一个参数作为版本号，去掉v前缀（如果存在）
        VERSION=$(echo "$1" | sed 's/^v//')
    fi
fi

echo -e "${YELLOW}构建信息:${NC}"
echo -e "${YELLOW}平台: ${PLATFORM}${NC}"
echo -e "${YELLOW}版本: ${VERSION}${NC}"
echo -e ""

# 定义颜色用于输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 拉取基础镜像
echo -e "${YELLOW}拉取基础镜像...${NC}"
# 提取Dockerfile中的基础镜像
echo -e "${YELLOW}拉取前端基础镜像...${NC}"
docker pull --platform ${PLATFORM} node:18-alpine
echo -e "${YELLOW}拉取后端基础镜像...${NC}"
docker pull --platform ${PLATFORM} python:3.10.16-slim
echo -e "${YELLOW}拉取nginx镜像...${NC}"
docker pull --platform ${PLATFORM} nginx:stable-alpine
echo -e "${GREEN}基础镜像拉取完成!${NC}"

echo -e "${YELLOW}开始构建前端镜像...${NC}"
echo -e "${YELLOW}目标平台: ${PLATFORM}${NC}"
echo -e "${YELLOW}版本号: ${VERSION}${NC}"
# 进入frontend目录并构建镜像
cd ../frontend
docker build --platform ${PLATFORM} -t "resume-frontend:${VERSION}" .
echo -e "${GREEN}前端镜像构建成功!${NC}"

# 保存前端镜像
echo -e "${YELLOW}保存前端镜像...${NC}"
docker save "resume-frontend:${VERSION}" -o "../docker/resume-frontend-${VERSION}.tar"
echo -e "${GREEN}前端镜像保存成功!${NC}"

# 返回到项目根目录
cd ..

echo -e "${YELLOW}开始构建后端镜像...${NC}"
# 进入backend目录并构建镜像
cd backend
docker build --platform ${PLATFORM} -t "resume-backend:${VERSION}" .
echo -e "${GREEN}后端镜像构建成功!${NC}"

# 保存后端镜像
echo -e "${YELLOW}保存后端镜像...${NC}"
docker save "resume-backend:${VERSION}" -o "../docker/resume-backend-${VERSION}.tar"
echo -e "${GREEN}后端镜像保存成功!${NC}"

# 构建 Celery Worker 镜像
echo -e "${YELLOW}开始构建 Celery Worker 镜像...${NC}"
docker build --platform ${PLATFORM} -t "resume-celery-worker:${VERSION}" -f Dockerfile.celery .
echo -e "${GREEN}Celery Worker 镜像构建成功!${NC}"

# 保存 Celery Worker 镜像
echo -e "${YELLOW}保存 Celery Worker 镜像...${NC}"
docker save "resume-celery-worker:${VERSION}" -o "../docker/resume-celery-worker-${VERSION}.tar"
echo -e "${GREEN}Celery Worker 镜像保存成功!${NC}"

# 构建 Celery Beat 镜像
echo -e "${YELLOW}开始构建 Celery Beat 镜像...${NC}"
docker build --platform ${PLATFORM} -t "resume-celery-beat:${VERSION}" -f Dockerfile.celerybeat .
echo -e "${GREEN}Celery Beat 镜像构建成功!${NC}"

# 保存 Celery Beat 镜像
echo -e "${YELLOW}保存 Celery Beat 镜像...${NC}"
docker save "resume-celery-beat:${VERSION}" -o "../docker/resume-celery-beat-${VERSION}.tar"
echo -e "${GREEN}Celery Beat 镜像保存成功!${NC}"

# 返回到 docker 目录
cd ../docker

echo -e "${GREEN}所有操作已完成! 镜像已保存至docker目录${NC}"
echo -e "${YELLOW}提示: 您可以使用以下命令加载镜像:${NC}"
echo -e "  docker load -i resume-frontend-${VERSION}.tar"
echo -e "  docker load -i resume-backend-${VERSION}.tar"
echo -e "  docker load -i resume-celery-worker-${VERSION}.tar"
echo -e "  docker load -i resume-celery-beat-${VERSION}.tar"
echo -e "${YELLOW}然后可以使用 docker-compose 启动服务或性能测试:${NC}"
echo -e "  docker-compose up -d             # 启动正常服务"
echo -e "  docker-compose -f docker-compose.test.yml up # 启动性能测试"