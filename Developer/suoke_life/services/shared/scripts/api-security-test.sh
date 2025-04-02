#!/bin/bash
# 索克生活微服务API安全测试脚本

set -e

# 检查必要命令
command -v jq >/dev/null 2>&1 || { echo "❌ 需要安装jq工具才能解析JSON响应"; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "❌ 需要安装curl工具"; exit 1; }

# 默认配置
SERVICE_NAME=${1:-"all"}
BASE_URL=${2:-"http://localhost"}
OUTPUT_DIR="./services/shared/security-reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${OUTPUT_DIR}/api_security_${SERVICE_NAME}_${TIMESTAMP}.json"

# 确保输出目录存在
mkdir -p "$OUTPUT_DIR"

# 服务端口映射
declare -A SERVICE_PORTS
SERVICE_PORTS["xiaoai-service"]=8040
SERVICE_PORTS["knowledge-base-service"]=8010
SERVICE_PORTS["knowledge-graph-service"]=8020
SERVICE_PORTS["rag-service"]=8050

# 测试端点数组
declare -A ENDPOINTS
ENDPOINTS["xiaoai-service"]="/health,/api/v1/chat,/api/v1/health-recommendations,/metrics"
ENDPOINTS["knowledge-base-service"]="/health,/api/v1/documents,/api/v1/search,/metrics"
ENDPOINTS["knowledge-graph-service"]="/health,/api/v1/entities,/api/v1/relationships,/metrics"
ENDPOINTS["rag-service"]="/health,/api/v1/query,/api/v1/vector-search,/metrics"

# 安全测试集
declare -A SECURITY_TESTS
SECURITY_TESTS["sql_injection"]="' OR 1=1 --"
SECURITY_TESTS["xss"]="<script>alert(1)</script>"
SECURITY_TESTS["nosql_injection"]="{\"$gt\":\"\"}"
SECURITY_TESTS["jwt_none_alg"]="{\"alg\":\"none\",\"typ\":\"JWT\"}"
SECURITY_TESTS["path_traversal"]="../../../etc/passwd"
SECURITY_TESTS["command_injection"]="; cat /etc/passwd"

# 初始化报告
echo "{\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"results\":{}}" > "$REPORT_FILE"

# 测试单个服务API安全
test_service_security() {
    local service=$1
    local port=${SERVICE_PORTS[$service]}
    local service_url="${BASE_URL}:${port}"
    
    echo "🔍 测试服务: $service ($service_url)"
    
    # 初始化服务结果
    jq ".results[\"$service\"] = {}" "$REPORT_FILE" > "${REPORT_FILE}.tmp" && mv "${REPORT_FILE}.tmp" "$REPORT_FILE"
    
    IFS=',' read -ra ENDPOINT_ARRAY <<< "${ENDPOINTS[$service]}"
    
    for endpoint in "${ENDPOINT_ARRAY[@]}"; do
        echo "  📡 测试端点: $endpoint"
        
        # 初始化端点结果
        jq ".results[\"$service\"][\"$endpoint\"] = {}" "$REPORT_FILE" > "${REPORT_FILE}.tmp" && mv "${REPORT_FILE}.tmp" "$REPORT_FILE"
        
        # 检查端点是否需要认证
        AUTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$service_url$endpoint")
        NEEDS_AUTH=false
        
        if [ "$AUTH_STATUS" == "401" ] || [ "$AUTH_STATUS" == "403" ]; then
            NEEDS_AUTH=true
            echo "  🔒 端点需要认证"
        fi
        
        # 为不同的安全测试执行请求
        for test_name in "${!SECURITY_TESTS[@]}"; do
            test_payload=${SECURITY_TESTS[$test_name]}
            
            echo "    🧪 执行测试: $test_name"
            
            # 构建测试请求
            if [[ "$endpoint" == *"query"* || "$endpoint" == *"chat"* || "$endpoint" == *"search"* ]]; then
                # 对查询类端点使用POST请求
                RESPONSE=$(curl -s -X POST \
                    -H "Content-Type: application/json" \
                    -d "{\"query\":\"$test_payload\"}" \
                    "$service_url$endpoint" 2>&1)
                CODE=$?
            else
                # 对其他端点使用GET请求附加参数
                RESPONSE=$(curl -s "$service_url$endpoint?q=$test_payload" 2>&1)
                CODE=$?
            fi
            
            # 分析响应
            if [ "$CODE" -ne 0 ]; then
                RESULT="CONNECTION_ERROR"
                DETAILS="连接错误: $RESPONSE"
            elif [[ "$RESPONSE" == *"error"* && "$RESPONSE" == *"sql"* ]]; then
                RESULT="VULNERABLE"
                DETAILS="可能的SQL注入漏洞"
            elif [[ "$RESPONSE" == *"error"* && "$RESPONSE" == *"syntax"* ]]; then
                RESULT="SUSPICIOUS"
                DETAILS="可疑的错误信息泄露"
            elif [[ "$RESPONSE" == *"/etc/passwd"* ]]; then
                RESULT="VULNERABLE"
                DETAILS="路径遍历漏洞"
            elif [[ "$RESPONSE" == *"<script>"* ]]; then
                RESULT="VULNERABLE"
                DETAILS="XSS漏洞"
            else
                RESULT="PASSED"
                DETAILS="未检测到漏洞"
            fi
            
            # 存储结果
            jq ".results[\"$service\"][\"$endpoint\"][\"$test_name\"] = {\"result\":\"$RESULT\",\"details\":\"$DETAILS\"}" "$REPORT_FILE" > "${REPORT_FILE}.tmp" && mv "${REPORT_FILE}.tmp" "$REPORT_FILE"
        done
    done
}

# 主测试逻辑
echo "🚀 开始API安全测试..."

if [ "$SERVICE_NAME" == "all" ]; then
    for service in "${!SERVICE_PORTS[@]}"; do
        test_service_security "$service"
    done
else
    if [[ -z "${SERVICE_PORTS[$SERVICE_NAME]}" ]]; then
        echo "❌ 未知服务: $SERVICE_NAME"
        exit 1
    fi
    test_service_security "$SERVICE_NAME"
fi

echo "✅ 安全测试完成！报告已保存至: $REPORT_FILE"

# 总结结果
VULN_COUNT=$(jq -r '.results | to_entries[] | .value | to_entries[] | .value | to_entries[] | select(.value.result=="VULNERABLE") | .value.result' "$REPORT_FILE" | wc -l | tr -d ' ')
SUSPICIOUS_COUNT=$(jq -r '.results | to_entries[] | .value | to_entries[] | .value | to_entries[] | select(.value.result=="SUSPICIOUS") | .value.result' "$REPORT_FILE" | wc -l | tr -d ' ')

echo "📊 测试结果总结:"
echo "  - 发现漏洞: $VULN_COUNT"
echo "  - 可疑问题: $SUSPICIOUS_COUNT"

if [ "$VULN_COUNT" -gt 0 ]; then
    echo "⚠️ 检测到漏洞，请查看报告详情进行修复！"
    jq -r '.results | to_entries[] | .key as $service | .value | to_entries[] | .key as $endpoint | .value | to_entries[] | select(.value.result=="VULNERABLE") | "  ❌ \($service) - \($endpoint) - \(.key): \(.value.details)"' "$REPORT_FILE"
    exit 1
fi

exit 0