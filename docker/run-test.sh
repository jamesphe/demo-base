#!/bin/bash

# 确保脚本在出错时停止执行
set -e

# 定义颜色用于输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否已经加载所有需要的镜像
echo -e "${YELLOW}检查镜像是否已加载...${NC}"

# 加载必要的镜像文件（如果尚未加载）
load_image() {
  local image_name=$1
  local tar_file=$2
  
  if ! docker image inspect $image_name > /dev/null 2>&1; then
    echo -e "${YELLOW}正在加载镜像: $image_name${NC}"
    docker load -i $tar_file
    echo -e "${GREEN}镜像加载成功: $image_name${NC}"
  else
    echo -e "${GREEN}镜像已存在: $image_name${NC}"
  fi
}

# 加载所有必需的镜像
load_image "resume-backend:latest" "resume-backend.tar"
load_image "resume-frontend:latest" "resume-frontend.tar"
load_image "resume-celery-worker:latest" "resume-celery-worker.tar" 
load_image "resume-celery-beat:latest" "resume-celery-beat.tar"

# 检查标准镜像
echo -e "${YELLOW}检查标准镜像...${NC}"
if ! docker image inspect grafana/k6:latest > /dev/null 2>&1; then
  echo -e "${YELLOW}正在拉取 k6 镜像...${NC}"
  docker pull grafana/k6:latest
  echo -e "${GREEN}k6 镜像拉取成功${NC}"
else
  echo -e "${GREEN}k6 镜像已存在${NC}"
fi

# 准备运行测试
echo -e "${YELLOW}准备启动性能测试...${NC}"

# 停止并移除可能存在的旧容器
echo -e "${YELLOW}清理已有的测试容器...${NC}"
docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true

# 启动测试环境
echo -e "${YELLOW}启动测试环境...${NC}"
docker-compose -f docker-compose.test.yml up -d

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 15

# 运行性能测试
echo -e "${YELLOW}开始执行性能测试...${NC}"
docker-compose -f docker-compose.test.yml logs -f k6

# 测试结束后提示
echo -e "${GREEN}性能测试完成!${NC}"
echo -e "${YELLOW}您可以使用以下命令查看详细的服务日志:${NC}"
echo -e "  docker-compose -f docker-compose.test.yml logs -f resume-backend"

# 询问是否要关闭测试环境
read -p "是否需要关闭测试环境? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  docker-compose -f docker-compose.test.yml down -v
  echo -e "${GREEN}测试环境已关闭!${NC}"
fi 