#!/bin/bash

echo "重置数据库..."

# 确保在backend目录下执行
cd "$(dirname "$0")"

# 设置 PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 检查是否安装了必要的PostgreSQL工具
if ! command -v psql &> /dev/null; then
    echo "错误: 未找到PostgreSQL命令行工具"
    echo "请安装 PostgreSQL 客户端工具:"
    echo "Mac: brew install postgresql"
    echo "Ubuntu: sudo apt-get install postgresql-client"
    exit 1
fi

# 检查环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "错误: 未找到 .env 文件"
    exit 1
fi

# 检查必要的环境变量
required_vars=("POSTGRES_SERVER" "POSTGRES_PORT" "POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "错误: 环境变量 $var 未设置"
        exit 1
    fi
done

echo "正在终止所有连接到数据库 $POSTGRES_DB 的会话..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_SERVER -p $POSTGRES_PORT -U $POSTGRES_USER -d postgres -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '$POSTGRES_DB' AND pid <> pg_backend_pid();"

echo "正在删除数据库 $POSTGRES_DB ..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_SERVER -p $POSTGRES_PORT -U $POSTGRES_USER -d postgres -c "DROP DATABASE IF EXISTS $POSTGRES_DB;"

echo "正在创建数据库 $POSTGRES_DB ..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_SERVER -p $POSTGRES_PORT -U $POSTGRES_USER -d postgres -c "CREATE DATABASE $POSTGRES_DB;"

echo "正在初始化数据库表..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_SERVER -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -f scripts/init.sql

echo "正在运行数据库迁移..."
alembic upgrade head

echo "正在初始化基础数据..."
python app/initial_data.py

echo "数据库重置完成!" 