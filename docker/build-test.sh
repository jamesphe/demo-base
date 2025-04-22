#!/bin/bash

# 确保脚本在出错时停止执行
set -e

# 定义平台参数，默认为linux/amd64
if [ "$1" = "mac" ]; then
  PLATFORM="linux/arm64"
else
  PLATFORM=${1:-linux/amd64}
fi

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
# 进入frontend目录并构建镜像
cd ../frontend
docker build --platform ${PLATFORM} -t resume-frontend:latest .
echo -e "${GREEN}前端镜像构建成功!${NC}"

# 保存前端镜像
echo -e "${YELLOW}保存前端镜像...${NC}"
docker save -o ../docker/resume-frontend.tar resume-frontend:latest
echo -e "${GREEN}前端镜像保存成功!${NC}"

# 返回到项目根目录
cd ..

echo -e "${YELLOW}开始构建后端镜像...${NC}"
# 进入backend目录并构建镜像
cd backend
docker build --platform ${PLATFORM} -t resume-backend:latest .
echo -e "${GREEN}后端镜像构建成功!${NC}"

# 保存后端镜像
echo -e "${YELLOW}保存后端镜像...${NC}"
docker save -o ../docker/resume-backend.tar resume-backend:latest
echo -e "${GREEN}后端镜像保存成功!${NC}"

# 构建 Celery Worker 镜像
echo -e "${YELLOW}开始构建 Celery Worker 镜像...${NC}"
docker build --platform ${PLATFORM} -t resume-celery-worker:latest -f Dockerfile.celery .
echo -e "${GREEN}Celery Worker 镜像构建成功!${NC}"

# 保存 Celery Worker 镜像
echo -e "${YELLOW}保存 Celery Worker 镜像...${NC}"
docker save -o ../docker/resume-celery-worker.tar resume-celery-worker:latest
echo -e "${GREEN}Celery Worker 镜像保存成功!${NC}"

# 构建 Celery Beat 镜像
echo -e "${YELLOW}开始构建 Celery Beat 镜像...${NC}"
docker build --platform ${PLATFORM} -t resume-celery-beat:latest -f Dockerfile.celerybeat .
echo -e "${GREEN}Celery Beat 镜像构建成功!${NC}"

# 保存 Celery Beat 镜像
echo -e "${YELLOW}保存 Celery Beat 镜像...${NC}"
docker save -o ../docker/resume-celery-beat.tar resume-celery-beat:latest
echo -e "${GREEN}Celery Beat 镜像保存成功!${NC}"

# 返回到 docker 目录
cd ../docker

echo -e "${GREEN}所有操作已完成! 自定义镜像已保存至docker目录${NC}"
echo -e "${YELLOW}提示: 您可以使用以下命令加载镜像:${NC}"
echo -e "  docker load -i resume-frontend.tar"
echo -e "  docker load -i resume-backend.tar"
echo -e "  docker load -i resume-celery-worker.tar"
echo -e "  docker load -i resume-celery-beat.tar"
echo -e "${YELLOW}标准镜像(如k6)将在服务器上自动拉取${NC}"
echo -e "${YELLOW}然后可以使用 docker-compose 启动服务或性能测试:${NC}"
echo -e "  docker-compose up -d             # 启动正常服务"
echo -e "  docker-compose -f docker-compose.test.yml up # 启动性能测试" 