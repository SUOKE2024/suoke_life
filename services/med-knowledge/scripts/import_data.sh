#!/bin/bash

# 确保脚本在错误时退出
set -e

NEO4J_URI=${NEO4J_URI:-bolt://localhost:7687}
NEO4J_USERNAME=${NEO4J_USERNAME:-neo4j}
NEO4J_PASSWORD=${NEO4J_PASSWORD:-suoke_password}

echo "连接Neo4j: $NEO4J_URI"

# 创建数据目录（如果不存在）
mkdir -p data

# 下载示例数据（如果不存在）
if [ ! -f data/constitutions.json ]; then
  echo "下载体质数据..."
  curl -o data/constitutions.json https://suoke-sample-data.s3.amazonaws.com/constitutions.json
fi

if [ ! -f data/symptoms.json ]; then
  echo "下载症状数据..."
  curl -o data/symptoms.json https://suoke-sample-data.s3.amazonaws.com/symptoms.json
fi

if [ ! -f data/acupoints.json ]; then
  echo "下载穴位数据..."
  curl -o data/acupoints.json https://suoke-sample-data.s3.amazonaws.com/acupoints.json
fi

if [ ! -f data/herbs.json ]; then
  echo "下载中药数据..."
  curl -o data/herbs.json https://suoke-sample-data.s3.amazonaws.com/herbs.json
fi

if [ ! -f data/syndromes.json ]; then
  echo "下载证型数据..."
  curl -o data/syndromes.json https://suoke-sample-data.s3.amazonaws.com/syndromes.json
fi

# 导入数据
echo "导入数据到Neo4j..."
go run cmd/tools/import_data.go \
  --uri="$NEO4J_URI" \
  --username="$NEO4J_USERNAME" \
  --password="$NEO4J_PASSWORD" \
  --constitutions=data/constitutions.json \
  --symptoms=data/symptoms.json \
  --acupoints=data/acupoints.json \
  --herbs=data/herbs.json \
  --syndromes=data/syndromes.json

echo "数据导入完成"