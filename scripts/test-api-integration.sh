#!/bin/bash

echo "🔍 开始API集成测试..."

# 检查后端服务状态
echo "检查后端服务..."
services=(
  "xiaoai-service:50053"
  "xiaoke-service:50054" 
  "laoke-service:50055"
  "soer-service:50056"
  "api-gateway:8000"
  "auth-service:8001"
  "health-data-service:8002"
)

for service in "${services[@]}"; do
  name=$(echo $service | cut -d: -f1)
  port=$(echo $service | cut -d: -f2)
  
  echo "检查 $name (端口 $port)..."
  if curl -s "http://localhost:$port/health" > /dev/null; then
    echo "✅ $name 运行正常"
  else
    echo "❌ $name 无法连接"
  fi
done

# 测试智能体API
echo "测试智能体API..."

# 测试小艾聊天API
echo "测试小艾聊天API..."
curl -X POST "http://localhost:50053/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，我想咨询健康问题",
    "messageType": "text",
    "userId": "test-user-001",
    "sessionId": "test-session-001"
  }' \
  -w "\n状态码: %{http_code}\n" || echo "❌ 小艾API测试失败"

# 测试小克服务管理API
echo "测试小克服务管理API..."
curl -X POST "http://localhost:50054/service-management" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user-001",
    "serviceType": "doctor_matching",
    "parameters": {
      "specialty": "内科",
      "location": "北京"
    }
  }' \
  -w "\n状态码: %{http_code}\n" || echo "❌ 小克API测试失败"

# 测试老克知识检索API
echo "测试老克知识检索API..."
curl -X POST "http://localhost:50055/knowledge-retrieval" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user-001",
    "serviceType": "knowledge_search",
    "parameters": {
      "query": "高血压预防",
      "category": "health_education"
    }
  }' \
  -w "\n状态码: %{http_code}\n" || echo "❌ 老克API测试失败"

# 测试索儿生活管理API
echo "测试索儿生活管理API..."
curl -X POST "http://localhost:50056/lifestyle-management" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user-001",
    "dataType": "manual",
    "data": {
      "heartRate": 72,
      "bloodPressure": {
        "systolic": 120,
        "diastolic": 80
      }
    },
    "timestamp": '$(date +%s)'
  }' \
  -w "\n状态码: %{http_code}\n" || echo "❌ 索儿API测试失败"

echo "✅ API集成测试完成" 