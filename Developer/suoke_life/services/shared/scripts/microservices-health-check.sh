#!/bin/bash
# 索克生活微服务健康检查脚本
# 此脚本检查所有微服务的健康状态和依赖关系

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 配置
OUTPUT_FORMAT=${1:-"table"} # table, json
ENVIRONMENT=${2:-"local"}   # local, dev, prod
TIMEOUT=5                   # 超时时间(秒)
OUTPUT_DIR="./services/shared/health-reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="${OUTPUT_DIR}/health_check_${ENVIRONMENT}_${TIMESTAMP}.json"

# 确保输出目录存在
mkdir -p "$OUTPUT_DIR"

# 服务配置
declare -A SERVICES
SERVICES["api-gateway"]="8000"
SERVICES["auth-service"]="8001"
SERVICES["user-service"]="8002"
SERVICES["knowledge-base-service"]="8010"
SERVICES["knowledge-graph-service"]="8020"
SERVICES["xiaoke-service"]="8030"
SERVICES["xiaoai-service"]="8040"
SERVICES["rag-service"]="8050"
SERVICES["inquiry-diagnosis-service"]="8060"
SERVICES["looking-diagnosis-service"]="8061"
SERVICES["smell-diagnosis-service"]="8062"
SERVICES["touch-diagnosis-service"]="8063"
SERVICES["four-diagnosis-coordinator"]="8070"
SERVICES["soer-service"]="8080"
SERVICES["laoke-service"]="8090"
SERVICES["agent-coordinator-service"]="8100"

# 环境配置
declare -A ENV_URLS
ENV_URLS["local"]="http://localhost"
ENV_URLS["dev"]="http://dev-api.suoke.life"
ENV_URLS["prod"]="http://api.suoke.life"

# 初始化结果JSON
echo "{\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"environment\":\"${ENVIRONMENT}\",\"services\":{}}" > "$OUTPUT_FILE"

# 依赖关系定义
declare -A DEPENDENCIES
DEPENDENCIES["api-gateway"]="auth-service"
DEPENDENCIES["auth-service"]="user-service"
DEPENDENCIES["rag-service"]="knowledge-base-service,knowledge-graph-service"
DEPENDENCIES["xiaoai-service"]="rag-service"
DEPENDENCIES["xiaoke-service"]="rag-service"
DEPENDENCIES["laoke-service"]="rag-service"
DEPENDENCIES["four-diagnosis-coordinator"]="inquiry-diagnosis-service,looking-diagnosis-service,smell-diagnosis-service,touch-diagnosis-service"
DEPENDENCIES["agent-coordinator-service"]="xiaoai-service,xiaoke-service,laoke-service,soer-service"

# 检查单个服务健康状态
check_service_health() {
  local service=$1
  local port=${SERVICES[$service]}
  local base_url=${ENV_URLS[$ENVIRONMENT]}
  local url="${base_url}:${port}/health"
  
  if [ "$ENVIRONMENT" != "local" ]; then
    # 非本地环境使用域名而非端口
    url="${base_url}/${service}/health"
  fi
  
  echo -e "${BLUE}检查服务健康状态: ${service} (${url})${NC}"
  
  # 初始化服务状态为未知
  jq ".services[\"$service\"] = {\"name\":\"$service\",\"status\":\"UNKNOWN\",\"response_time\":null,\"details\":null,\"dependencies\":[]}" "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
  
  # 检查服务健康
  local start_time=$(date +%s.%N)
  local response=$(curl -s -o response.tmp -w "%{http_code}" -m $TIMEOUT "$url" 2>/dev/null || echo "TIMEOUT")
  local end_time=$(date +%s.%N)
  local response_time=$(echo "$end_time - $start_time" | bc)
  
  local status=""
  local details=""
  
  if [ "$response" == "TIMEOUT" ]; then
    status="DOWN"
    details="连接超时 (${TIMEOUT}s)"
    echo -e "${RED}✘ ${service}: 连接超时${NC}"
  elif [ "$response" == "000" ]; then
    status="DOWN"
    details="连接失败"
    echo -e "${RED}✘ ${service}: 连接失败${NC}"
  elif [ "$response" == "200" ]; then
    status="UP"
    details=$(cat response.tmp)
    echo -e "${GREEN}✓ ${service}: 正常 (${response_time}s)${NC}"
  else
    status="WARNING"
    details=$(cat response.tmp)
    echo -e "${YELLOW}! ${service}: 状态码 ${response} (${response_time}s)${NC}"
  fi
  
  # 添加依赖关系
  local deps=${DEPENDENCIES[$service]}
  local deps_json="[]"
  
  if [ ! -z "$deps" ]; then
    deps_json="["
    IFS=',' read -ra DEP_ARRAY <<< "$deps"
    for i in "${!DEP_ARRAY[@]}"; do
      if [ "$i" -gt 0 ]; then
        deps_json="${deps_json},"
      fi
      deps_json="${deps_json}\"${DEP_ARRAY[$i]}\""
    done
    deps_json="${deps_json}]"
  fi
  
  # 更新服务状态
  local details_escaped=$(echo "$details" | sed 's/"/\\"/g')
  jq ".services[\"$service\"] = {\"name\":\"$service\",\"status\":\"$status\",\"response_time\":$response_time,\"details\":\"$details_escaped\",\"dependencies\":$deps_json}" "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
  
  # 清理临时文件
  rm -f response.tmp
}

# 检查依赖健康状态
check_dependencies() {
  # 从JSON文件生成依赖健康状态
  local service_statuses=$(jq -r '.services | to_entries[] | "\(.key)|\(.value.status)"' "$OUTPUT_FILE")
  
  echo -e "\n${BLUE}检查依赖关系:${NC}"
  
  while IFS='|' read -r service status; do
    local deps=${DEPENDENCIES[$service]}
    
    if [ ! -z "$deps" ]; then
      local all_deps_healthy=true
      local unhealthy_deps=""
      
      IFS=',' read -ra DEP_ARRAY <<< "$deps"
      for dep in "${DEP_ARRAY[@]}"; do
        local dep_status=$(jq -r ".services[\"$dep\"].status" "$OUTPUT_FILE")
        
        if [ "$dep_status" != "UP" ]; then
          all_deps_healthy=false
          unhealthy_deps="${unhealthy_deps}${dep}(${dep_status}), "
        fi
      done
      
      if [ "$all_deps_healthy" = true ]; then
        echo -e "${GREEN}✓ ${service}: 所有依赖正常${NC}"
      else
        unhealthy_deps=${unhealthy_deps%, }
        echo -e "${YELLOW}! ${service}: 依赖异常 - ${unhealthy_deps}${NC}"
        
        # 如果服务本身是UP但依赖有问题，将状态修改为WARNING
        if [ "$status" == "UP" ]; then
          jq ".services[\"$service\"].status = \"WARNING\"" "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
          jq ".services[\"$service\"].details = \"服务正常但依赖异常: ${unhealthy_deps}\"" "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
        fi
      fi
    fi
  done <<< "$service_statuses"
}

# 生成汇总报告
generate_summary() {
  local total=$(jq -r '.services | length' "$OUTPUT_FILE")
  local up=$(jq -r '.services | to_entries[] | select(.value.status=="UP") | .key' "$OUTPUT_FILE" | wc -l)
  local warning=$(jq -r '.services | to_entries[] | select(.value.status=="WARNING") | .key' "$OUTPUT_FILE" | wc -l)
  local down=$(jq -r '.services | to_entries[] | select(.value.status=="DOWN") | .key' "$OUTPUT_FILE" | wc -l)
  local unknown=$(jq -r '.services | to_entries[] | select(.value.status=="UNKNOWN") | .key' "$OUTPUT_FILE" | wc -l)
  
  echo -e "\n${BLUE}健康检查汇总:${NC}"
  echo -e "环境: ${ENVIRONMENT}"
  echo -e "总服务数: ${total}"
  echo -e "${GREEN}正常: ${up}${NC}"
  echo -e "${YELLOW}警告: ${warning}${NC}"
  echo -e "${RED}故障: ${down}${NC}"
  echo -e "未知: ${unknown}"
  
  # 更新JSON结果
  jq ".summary = {\"total\":$total,\"up\":$up,\"warning\":$warning,\"down\":$down,\"unknown\":$unknown}" "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
  
  # 如果有问题的服务，列出它们
  if [ "$warning" -gt 0 ] || [ "$down" -gt 0 ]; then
    echo -e "\n${YELLOW}需要关注的服务:${NC}"
    
    if [ "$down" -gt 0 ]; then
      echo -e "${RED}故障服务:${NC}"
      jq -r '.services | to_entries[] | select(.value.status=="DOWN") | "  - \(.key)"' "$OUTPUT_FILE"
    fi
    
    if [ "$warning" -gt 0 ]; then
      echo -e "${YELLOW}警告服务:${NC}"
      jq -r '.services | to_entries[] | select(.value.status=="WARNING") | "  - \(.key)"' "$OUTPUT_FILE"
    fi
  fi
}

# 主函数
main() {
  echo "🔍 开始索克生活微服务健康检查 (环境: ${ENVIRONMENT})"
  
  # 检查每个服务的健康状态
  for service in "${!SERVICES[@]}"; do
    check_service_health "$service"
  done
  
  # 检查依赖关系
  check_dependencies
  
  # 生成汇总报告
  generate_summary
  
  echo -e "\n✅ 健康检查完成！结果已保存至: $OUTPUT_FILE"
  
  # 如果非table格式，输出JSON结果
  if [ "$OUTPUT_FORMAT" != "table" ]; then
    cat "$OUTPUT_FILE"
  fi
  
  # 返回状态码：如果有DOWN的服务则返回1
  local down_count=$(jq -r '.summary.down' "$OUTPUT_FILE")
  if [ "$down_count" -gt 0 ]; then
    return 1
  fi
  
  return 0
}

# 执行主函数
main