#!/bin/bash
# Go版本RAG服务部署验证脚本

set -e

# 解析命令行参数
ENV="dev"

while [[ "$#" -gt 0 ]]; do
  case $1 in
    --env=*) ENV="${1#*=}" ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
  shift
done

echo "=== 在${ENV}环境中验证Go版RAG服务部署 ==="

# 设置API基础URL
case $ENV in
  dev)
    BASE_URL="https://dev.api.suoke.life/rag"
    ;;
  staging)
    BASE_URL="https://staging.api.suoke.life/rag"
    ;;
  prod)
    BASE_URL="https://api.suoke.life/rag"
    ;;
  *)
    echo "错误: 不支持的环境 - ${ENV}"
    exit 1
    ;;
esac

echo "API基础URL: ${BASE_URL}"

# 健康检查
echo "执行健康检查..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/health")
if [ "$HEALTH_STATUS" -eq 200 ]; then
  echo "✅ 健康检查通过"
else
  echo "❌ 健康检查失败，状态码: ${HEALTH_STATUS}"
  exit 1
fi

# 获取所有集合
echo "获取集合列表..."
COLLECTIONS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/collections")
if [ "$COLLECTIONS_STATUS" -eq 200 ]; then
  echo "✅ 获取集合列表成功"
else
  echo "❌ 获取集合列表失败，状态码: ${COLLECTIONS_STATUS}"
  exit 1
fi

# 嵌入向量测试
echo "测试嵌入向量功能..."
EMBED_RESPONSE=$(curl -s -X POST "${BASE_URL}/embed" \
  -H "Content-Type: application/json" \
  -d '{"texts":["测试嵌入向量功能"]}')

if [[ $EMBED_RESPONSE == *"embedding"* ]]; then
  echo "✅ 嵌入向量功能正常"
else
  echo "❌ 嵌入向量功能失败"
  echo "响应: ${EMBED_RESPONSE}"
  exit 1
fi

# 简单RAG查询测试
echo "测试基本RAG查询..."
QUERY_RESPONSE=$(curl -s -X POST "${BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"索克生活是什么?", "retrieval_options":{"top_k":3}}')

if [[ $QUERY_RESPONSE == *"answer"* ]]; then
  echo "✅ RAG查询功能正常"
else
  echo "❌ RAG查询功能失败"
  echo "响应: ${QUERY_RESPONSE}"
  exit 1
fi

echo "=== Go版RAG服务部署验证成功! ==="
exit 0 