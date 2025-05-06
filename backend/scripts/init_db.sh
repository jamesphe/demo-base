#!/bin/bash

# 加载环境变量
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
else
    echo "错误: 未找到 .env 文件"
    exit 1
fi

echo "正在初始化数据库..."

# 执行SQL脚本
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_SERVER -p $POSTGRES_PORT -U $POSTGRES_USER -f init.sql
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_SERVER -p $POSTGRES_PORT -U $POSTGRES_USER -f init_permissions.sql

echo "数据库初始化完成!" 