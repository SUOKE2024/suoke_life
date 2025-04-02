#!/bin/bash
# 索克生活安全检查整合运行脚本
# 此脚本汇总运行所有安全检查并生成综合报告

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 配置
OUTPUT_DIR="./services/shared/security-reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${OUTPUT_DIR}/security_summary_${TIMESTAMP}.md"
LOG_FILE="${OUTPUT_DIR}/security_checks_${TIMESTAMP}.log"
SERVICE=${1:-"all"}
SEVERITY=${2:-"CRITICAL,HIGH"}

# 确保输出目录存在
mkdir -p "$OUTPUT_DIR"

# 初始化日志文件
echo "# 索克生活安全检查运行日志" > "$LOG_FILE"
echo "时间: $(date)" >> "$LOG_FILE"
echo "服务: ${SERVICE}" >> "$LOG_FILE"
echo "严重程度: ${SEVERITY}" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 写入日志函数
log() {
  echo -e "$1"
  echo -e "$1" | sed -r "s/\x1B\[([0-9]{1,3}(;[0-9]{1,3})*)?[mGK]//g" >> "$LOG_FILE"
}

# 初始化报告文件
echo "# 索克生活安全检查综合报告" > "$REPORT_FILE"
echo "生成时间: $(date)" >> "$REPORT_FILE"
echo "检查服务: ${SERVICE}" >> "$REPORT_FILE"
echo "检查严重程度: ${SEVERITY}" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 使用的脚本路径
DOCKER_SCAN_SCRIPT="./services/shared/scripts/scan-docker-image.sh"
API_SECURITY_SCRIPT="./services/shared/scripts/api-security-test.sh"
DEPENDENCY_SCAN_SCRIPT="./services/shared/scripts/dependency-vulnerability-report.sh"
HEALTH_CHECK_SCRIPT="./services/shared/scripts/microservices-health-check.sh"

# 检查脚本是否可执行
check_scripts() {
  log "${BLUE}检查脚本可执行性...${NC}"
  
  if [ ! -x "$DOCKER_SCAN_SCRIPT" ]; then
    log "${YELLOW}! 设置Docker扫描脚本可执行权限${NC}"
    chmod +x "$DOCKER_SCAN_SCRIPT"
  fi
  
  if [ ! -x "$API_SECURITY_SCRIPT" ]; then
    log "${YELLOW}! 设置API安全测试脚本可执行权限${NC}"
    chmod +x "$API_SECURITY_SCRIPT"
  fi
  
  if [ ! -x "$DEPENDENCY_SCAN_SCRIPT" ]; then
    log "${YELLOW}! 设置依赖漏洞扫描脚本可执行权限${NC}"
    chmod +x "$DEPENDENCY_SCAN_SCRIPT"
  fi
  
  if [ ! -x "$HEALTH_CHECK_SCRIPT" ]; then
    log "${YELLOW}! 设置健康检查脚本可执行权限${NC}"
    chmod +x "$HEALTH_CHECK_SCRIPT"
  fi
  
  log "${GREEN}✓ 脚本检查完成${NC}"
}

# 运行Docker镜像扫描
run_docker_scan() {
  log "\n${BLUE}======== 开始Docker镜像安全扫描 ========${NC}"
  
  echo "## Docker镜像安全扫描" >> "$REPORT_FILE"
  
  if [ "$SERVICE" == "all" ]; then
    log "${YELLOW}! Docker镜像扫描需要指定服务名称，跳过全部扫描${NC}"
    echo "未执行Docker镜像扫描，因为需要指定具体服务名称。" >> "$REPORT_FILE"
    return
  fi
  
  log "${BLUE}扫描服务 ${SERVICE} 的Docker镜像...${NC}"
  
  # 运行Docker镜像扫描脚本并捕获结果
  if $DOCKER_SCAN_SCRIPT "$SERVICE" "$SEVERITY" "json" > "${OUTPUT_DIR}/docker_scan_${SERVICE}_${TIMESTAMP}.json" 2>&1; then
    log "${GREEN}✓ Docker镜像扫描完成，未发现严重漏洞${NC}"
    echo "服务 \`${SERVICE}\` 的Docker镜像扫描完成，未发现严重漏洞。" >> "$REPORT_FILE"
  else
    log "${RED}✘ Docker镜像扫描发现严重漏洞${NC}"
    echo "服务 \`${SERVICE}\` 的Docker镜像扫描发现严重漏洞！" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
    grep -A 10 "发现.*个严重漏洞" "${OUTPUT_DIR}/docker_scan_${SERVICE}_${TIMESTAMP}.json" >> "$REPORT_FILE" 2>/dev/null || echo "无法提取漏洞详情" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
  fi
  
  echo "" >> "$REPORT_FILE"
}

# 运行API安全测试
run_api_security_test() {
  log "\n${BLUE}======== 开始API安全测试 ========${NC}"
  
  echo "## API安全测试" >> "$REPORT_FILE"
  
  # 运行API安全测试脚本
  if $API_SECURITY_SCRIPT "$SERVICE" > "${OUTPUT_DIR}/api_security_${SERVICE}_${TIMESTAMP}.log" 2>&1; then
    log "${GREEN}✓ API安全测试完成，未发现漏洞${NC}"
    echo "API安全测试完成，未发现漏洞。" >> "$REPORT_FILE"
  else
    log "${RED}✘ API安全测试发现漏洞${NC}"
    echo "API安全测试发现以下漏洞:" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
    grep -A 15 "检测到漏洞" "${OUTPUT_DIR}/api_security_${SERVICE}_${TIMESTAMP}.log" >> "$REPORT_FILE" 2>/dev/null || echo "无法提取漏洞详情" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
  fi
  
  echo "" >> "$REPORT_FILE"
}

# 运行依赖漏洞扫描
run_dependency_scan() {
  log "\n${BLUE}======== 开始依赖安全漏洞扫描 ========${NC}"
  
  echo "## 依赖安全漏洞扫描" >> "$REPORT_FILE"
  
  # 运行依赖漏洞扫描脚本
  $DEPENDENCY_SCAN_SCRIPT "$SEVERITY" > "${OUTPUT_DIR}/dependency_scan_${TIMESTAMP}.log" 2>&1
  
  # 提取扫描结果
  local total_vulns=$(grep "漏洞总数:" "${OUTPUT_DIR}/dependency_scan_${TIMESTAMP}.log" | awk '{print $2}')
  local critical=$(grep "严重漏洞:" "${OUTPUT_DIR}/dependency_scan_${TIMESTAMP}.log" | awk '{print $2}')
  local high=$(grep "高危漏洞:" "${OUTPUT_DIR}/dependency_scan_${TIMESTAMP}.log" | awk '{print $2}')
  
  if [ "$critical" -gt 0 ] || [ "$high" -gt 0 ]; then
    log "${RED}✘ 依赖扫描发现严重或高危漏洞 (严重: ${critical}, 高危: ${high})${NC}"
    echo "依赖扫描发现严重或高危漏洞！" >> "$REPORT_FILE"
    echo "- 严重漏洞: ${critical}" >> "$REPORT_FILE"
    echo "- 高危漏洞: ${high}" >> "$REPORT_FILE"
    echo "- 漏洞总数: ${total_vulns}" >> "$REPORT_FILE"
    
    # 提取漏洞最多的服务
    echo "\n### 漏洞最多的服务" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
    grep -A 5 "漏洞最多的服务:" "${OUTPUT_DIR}/dependency_scan_${TIMESTAMP}.log" | grep -v "漏洞最多的服务:" >> "$REPORT_FILE" 2>/dev/null || echo "无法提取服务漏洞信息" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
    
    # 提取最常见的漏洞
    echo "\n### 最常见的严重和高危漏洞" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
    grep -A 5 "最常见的严重和高危漏洞:" "${OUTPUT_DIR}/dependency_scan_${TIMESTAMP}.log" | grep -v "最常见的严重和高危漏洞:" >> "$REPORT_FILE" 2>/dev/null || echo "无法提取常见漏洞信息" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
  else
    log "${GREEN}✓ 依赖扫描完成，未发现严重或高危漏洞${NC}"
    echo "依赖扫描完成，未发现严重或高危漏洞。" >> "$REPORT_FILE"
  fi
  
  # 添加HTML报告链接
  local html_report=$(ls -t ${OUTPUT_DIR}/dependency_vulnerabilities_*.html 2>/dev/null | head -1)
  if [ ! -z "$html_report" ]; then
    echo "\n详细报告: [${html_report}](${html_report})" >> "$REPORT_FILE"
  fi
  
  echo "" >> "$REPORT_FILE"
}

# 运行微服务健康检查
run_health_check() {
  log "\n${BLUE}======== 开始微服务健康检查 ========${NC}"
  
  echo "## 微服务健康状态" >> "$REPORT_FILE"
  
  # 运行健康检查脚本
  if $HEALTH_CHECK_SCRIPT "local" "table" > "${OUTPUT_DIR}/health_check_${TIMESTAMP}.log" 2>&1; then
    log "${GREEN}✓ 所有服务健康状态正常${NC}"
    echo "所有服务健康状态正常。" >> "$REPORT_FILE"
  else
    log "${RED}✘ 部分服务健康状态异常${NC}"
    echo "部分服务健康状态异常！" >> "$REPORT_FILE"
    
    # 提取故障服务
    echo "\n### 服务健康状态汇总" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
    grep -A 15 "健康检查汇总:" "${OUTPUT_DIR}/health_check_${TIMESTAMP}.log" >> "$REPORT_FILE" 2>/dev/null || echo "无法提取健康状态汇总" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
  fi
  
  echo "" >> "$REPORT_FILE"
}

# 生成安全评分
generate_security_score() {
  log "\n${BLUE}======== 生成安全评分 ========${NC}"
  
  echo "## 安全评分" >> "$REPORT_FILE"
  
  # 从各检查结果提取信息计算评分
  local docker_score=100
  local api_score=100
  local dependency_score=100
  local health_score=100
  
  # Docker镜像扫描评分
  if grep -q "发现.*个严重漏洞" "${OUTPUT_DIR}/docker_scan_${SERVICE}_${TIMESTAMP}.json" 2>/dev/null; then
    docker_score=60
    log "${RED}✘ Docker镜像安全评分: ${docker_score}/100${NC}"
  else
    log "${GREEN}✓ Docker镜像安全评分: ${docker_score}/100${NC}"
  fi
  
  # API安全测试评分
  if grep -q "检测到漏洞" "${OUTPUT_DIR}/api_security_${SERVICE}_${TIMESTAMP}.log" 2>/dev/null; then
    api_score=70
    log "${RED}✘ API安全评分: ${api_score}/100${NC}"
  else
    log "${GREEN}✓ API安全评分: ${api_score}/100${NC}"
  fi
  
  # 依赖漏洞扫描评分
  local critical=$(grep "严重漏洞:" "${OUTPUT_DIR}/dependency_scan_${TIMESTAMP}.log" 2>/dev/null | awk '{print $2}')
  local high=$(grep "高危漏洞:" "${OUTPUT_DIR}/dependency_scan_${TIMESTAMP}.log" 2>/dev/null | awk '{print $2}')
  
  if [ ! -z "$critical" ] && [ "$critical" -gt 0 ]; then
    dependency_score=$((100 - critical * 10))
    [ "$dependency_score" -lt 0 ] && dependency_score=0
    log "${RED}✘ 依赖安全评分: ${dependency_score}/100${NC}"
  elif [ ! -z "$high" ] && [ "$high" -gt 0 ]; then
    dependency_score=$((100 - high * 5))
    [ "$dependency_score" -lt 0 ] && dependency_score=0
    log "${YELLOW}! 依赖安全评分: ${dependency_score}/100${NC}"
  else
    log "${GREEN}✓ 依赖安全评分: ${dependency_score}/100${NC}"
  fi
  
  # 服务健康评分
  local down=$(grep "故障:" "${OUTPUT_DIR}/health_check_${TIMESTAMP}.log" 2>/dev/null | awk '{print $2}')
  local warning=$(grep "警告:" "${OUTPUT_DIR}/health_check_${TIMESTAMP}.log" 2>/dev/null | awk '{print $2}')
  
  if [ ! -z "$down" ] && [ "$down" -gt 0 ]; then
    health_score=$((100 - down * 20))
    [ "$health_score" -lt 0 ] && health_score=0
    log "${RED}✘ 服务健康评分: ${health_score}/100${NC}"
  elif [ ! -z "$warning" ] && [ "$warning" -gt 0 ]; then
    health_score=$((100 - warning * 10))
    [ "$health_score" -lt 0 ] && health_score=0
    log "${YELLOW}! 服务健康评分: ${health_score}/100${NC}"
  else
    log "${GREEN}✓ 服务健康评分: ${health_score}/100${NC}"
  fi
  
  # 计算总体评分
  local total_score=$(( (docker_score + api_score + dependency_score + health_score) / 4 ))
  
  # 评分等级
  local grade=""
  if [ "$total_score" -ge 90 ]; then
    grade="A+"
    log "${GREEN}✓ 总体安全评分: ${total_score}/100 (${grade})${NC}"
  elif [ "$total_score" -ge 80 ]; then
    grade="A"
    log "${GREEN}✓ 总体安全评分: ${total_score}/100 (${grade})${NC}"
  elif [ "$total_score" -ge 70 ]; then
    grade="B"
    log "${YELLOW}! 总体安全评分: ${total_score}/100 (${grade})${NC}"
  elif [ "$total_score" -ge 60 ]; then
    grade="C"
    log "${YELLOW}! 总体安全评分: ${total_score}/100 (${grade})${NC}"
  else
    grade="D"
    log "${RED}✘ 总体安全评分: ${total_score}/100 (${grade})${NC}"
  fi
  
  # 添加评分到报告
  echo "| 检查类型 | 评分 |" >> "$REPORT_FILE"
  echo "|---------|------|" >> "$REPORT_FILE"
  echo "| Docker镜像安全 | ${docker_score}/100 |" >> "$REPORT_FILE"
  echo "| API安全 | ${api_score}/100 |" >> "$REPORT_FILE"
  echo "| 依赖安全 | ${dependency_score}/100 |" >> "$REPORT_FILE"
  echo "| 服务健康 | ${health_score}/100 |" >> "$REPORT_FILE"
  echo "| **总体评分** | **${total_score}/100 (${grade})** |" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"
}

# 生成修复建议
generate_recommendations() {
  log "\n${BLUE}======== 生成修复建议 ========${NC}"
  
  echo "## 安全修复建议" >> "$REPORT_FILE"
  
  local has_recommendations=false
  
  # Docker镜像漏洞修复建议
  if grep -q "发现.*个严重漏洞" "${OUTPUT_DIR}/docker_scan_${SERVICE}_${TIMESTAMP}.json" 2>/dev/null; then
    has_recommendations=true
    echo "### Docker镜像漏洞修复" >> "$REPORT_FILE"
    echo "1. 更新基础镜像到最新版本" >> "$REPORT_FILE"
    echo "2. 使用多阶段构建减少不必要的依赖" >> "$REPORT_FILE"
    echo "3. 删除不必要的系统包和开发工具" >> "$REPORT_FILE"
    echo "4. 考虑使用轻量级基础镜像，如Alpine或distroless" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
  fi
  
  # API安全漏洞修复建议
  if grep -q "检测到漏洞" "${OUTPUT_DIR}/api_security_${SERVICE}_${TIMESTAMP}.log" 2>/dev/null; then
    has_recommendations=true
    echo "### API安全漏洞修复" >> "$REPORT_FILE"
    
    if grep -q "SQL注入" "${OUTPUT_DIR}/api_security_${SERVICE}_${TIMESTAMP}.log" 2>/dev/null; then
      echo "1. 对所有查询使用参数化SQL语句" >> "$REPORT_FILE"
      echo "2. 实现ORM或查询构建器来防止SQL注入" >> "$REPORT_FILE"
    fi
    
    if grep -q "XSS" "${OUTPUT_DIR}/api_security_${SERVICE}_${TIMESTAMP}.log" 2>/dev/null; then
      echo "3. 实施内容安全策略(CSP)防止XSS攻击" >> "$REPORT_FILE"
      echo "4. 对输出进行HTML编码，特别是用户提供的内容" >> "$REPORT_FILE"
    fi
    
    if grep -q "路径遍历" "${OUTPUT_DIR}/api_security_${SERVICE}_${TIMESTAMP}.log" 2>/dev/null; then
      echo "5. 验证和净化所有文件路径参数" >> "$REPORT_FILE"
      echo "6. 使用安全的路径操作库，如path.resolve()" >> "$REPORT_FILE"
    fi
    
    echo "7. 实现API请求速率限制防止暴力攻击" >> "$REPORT_FILE"
    echo "8. 审查所有错误处理，确保不泄露敏感信息" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
  fi
  
  # 依赖漏洞修复建议
  local critical=$(grep "严重漏洞:" "${OUTPUT_DIR}/dependency_scan_${TIMESTAMP}.log" 2>/dev/null | awk '{print $2}')
  local high=$(grep "高危漏洞:" "${OUTPUT_DIR}/dependency_scan_${TIMESTAMP}.log" 2>/dev/null | awk '{print $2}')
  
  if [ ! -z "$critical" ] && [ "$critical" -gt 0 ] || [ ! -z "$high" ] && [ "$high" -gt 0 ]; then
    has_recommendations=true
    echo "### 依赖漏洞修复" >> "$REPORT_FILE"
    echo "1. 立即更新以下有严重漏洞的依赖:" >> "$REPORT_FILE"
    
    # 提取常见漏洞
    grep -A 5 "最常见的严重和高危漏洞:" "${OUTPUT_DIR}/dependency_scan_${TIMESTAMP}.log" | grep -v "最常见的严重和高危漏洞:" | sed 's/^/   - /' >> "$REPORT_FILE" 2>/dev/null
    
    echo "2. 运行 \`npm audit fix\` 或 \`pip install -U\` 自动更新有漏洞的依赖" >> "$REPORT_FILE"
    echo "3. 考虑替代具有长期未修复漏洞的库" >> "$REPORT_FILE"
    echo "4. 实施依赖更新自动化流程" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
  fi
  
  # 服务健康修复建议
  local down=$(grep "故障:" "${OUTPUT_DIR}/health_check_${TIMESTAMP}.log" 2>/dev/null | awk '{print $2}')
  local warning=$(grep "警告:" "${OUTPUT_DIR}/health_check_${TIMESTAMP}.log" 2>/dev/null | awk '{print $2}')
  
  if [ ! -z "$down" ] && [ "$down" -gt 0 ] || [ ! -z "$warning" ] && [ "$warning" -gt 0 ]; then
    has_recommendations=true
    echo "### 服务健康问题修复" >> "$REPORT_FILE"
    echo "1. 检查以下服务的连接问题:" >> "$REPORT_FILE"
    
    # 提取故障服务
    grep -A 10 "故障服务:" "${OUTPUT_DIR}/health_check_${TIMESTAMP}.log" 2>/dev/null | grep "^ " | sed 's/^/   /' >> "$REPORT_FILE" 2>/dev/null
    
    # 提取警告服务
    grep -A 10 "警告服务:" "${OUTPUT_DIR}/health_check_${TIMESTAMP}.log" 2>/dev/null | grep "^ " | sed 's/^/   /' >> "$REPORT_FILE" 2>/dev/null
    
    echo "2. 检查依赖服务的可用性和连接配置" >> "$REPORT_FILE"
    echo "3. 审查服务日志以识别潜在故障原因" >> "$REPORT_FILE"
    echo "4. 考虑实施服务自动恢复策略" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
  fi
  
  if [ "$has_recommendations" = false ]; then
    echo "恭喜！未发现需要修复的安全问题。持续保持良好的安全实践！" >> "$REPORT_FILE"
  fi
}

# 主函数
main() {
  log "${BLUE}开始索克生活安全检查 (服务: ${SERVICE}, 严重程度: ${SEVERITY})${NC}"
  
  # 检查脚本可执行性
  check_scripts
  
  # 运行Docker镜像扫描
  run_docker_scan
  
  # 运行API安全测试
  run_api_security_test
  
  # 运行依赖漏洞扫描
  run_dependency_scan
  
  # 运行微服务健康检查
  run_health_check
  
  # 生成安全评分
  generate_security_score
  
  # 生成修复建议
  generate_recommendations
  
  log "\n${GREEN}✅ 所有安全检查完成！${NC}"
  log "详细报告已保存至: ${REPORT_FILE}"
  log "运行日志已保存至: ${LOG_FILE}"
}

# 执行主函数
main