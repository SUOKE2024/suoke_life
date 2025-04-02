#!/bin/bash
#
# RAG服务安全审计脚本
# 执行基本的安全渗透测试和配置检查
#

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$SERVICE_DIR/config"
LOG_FILE="$SCRIPT_DIR/security_audit_$(date +%Y%m%d).log"
REPORT_FILE="$SCRIPT_DIR/security_audit_report_$(date +%Y%m%d).html"
ENDPOINT="https://suoke.life/ai"
SEVERITY_THRESHOLD=7  # 高于此分值的问题将触发警告

# 颜色代码
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 全局变量
ISSUES_FOUND=0
HIGH_SEVERITY_ISSUES=0
MEDIUM_SEVERITY_ISSUES=0
LOW_SEVERITY_ISSUES=0
TOTAL_CHECKS=0
PASSED_CHECKS=0
ISSUES=()

# 日志函数
log() {
  local level=$1
  local message=$2
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  
  case $level in
    "INFO")
      local color=$GREEN
      ;;
    "WARN")
      local color=$YELLOW
      ;;
    "ERROR")
      local color=$RED
      ;;
    *)
      local color=$NC
      ;;
  esac
  
  echo -e "${color}[$timestamp] [$level] $message${NC}" | tee -a "$LOG_FILE"
}

# 添加安全问题
add_issue() {
  local severity=$1
  local category=$2
  local title=$3
  local description=$4
  local recommendation=$5
  
  ISSUES_FOUND=$((ISSUES_FOUND + 1))
  
  case $severity in
    "HIGH")
      HIGH_SEVERITY_ISSUES=$((HIGH_SEVERITY_ISSUES + 1))
      local severity_score=9
      ;;
    "MEDIUM")
      MEDIUM_SEVERITY_ISSUES=$((MEDIUM_SEVERITY_ISSUES + 1))
      local severity_score=5
      ;;
    "LOW")
      LOW_SEVERITY_ISSUES=$((LOW_SEVERITY_ISSUES + 1))
      local severity_score=2
      ;;
    *)
      local severity_score=1
      ;;
  esac
  
  ISSUES+=("$severity|$severity_score|$category|$title|$description|$recommendation")
  
  if [ $severity_score -ge $SEVERITY_THRESHOLD ]; then
    log "ERROR" "[$severity] $title"
  else
    log "WARN" "[$severity] $title"
  fi
}

# 记录检查结果
record_check() {
  local category=$1
  local title=$2
  local result=$3
  local description=$4
  
  TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
  
  if [ "$result" == "PASS" ]; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    log "INFO" "[PASS] $title"
  else
    local severity=$5
    local recommendation=$6
    add_issue "$severity" "$category" "$title" "$description" "$recommendation"
  fi
}

# 检查TLS配置
check_tls() {
  log "INFO" "检查TLS/SSL配置..."
  
  # 检查是否使用TLS
  local uses_tls=$(curl -sI $ENDPOINT/health | grep -i "Server:" | grep -i "nginx")
  if [ -z "$uses_tls" ]; then
    record_check "传输安全" "HTTPS启用状态" "PASS" "服务正确启用了HTTPS"
  else
    record_check "传输安全" "HTTPS启用状态" "FAIL" "服务未使用HTTPS" "HIGH" "配置Nginx强制使用HTTPS，并添加适当的重定向"
  fi
  
  # 检查TLS版本
  local tls_version=$(nmap --script ssl-enum-ciphers -p 443 suoke.life | grep -i "TLSv1.0\|TLSv1.1\|SSLv3\|SSLv2" || echo "")
  if [ -z "$tls_version" ]; then
    record_check "传输安全" "TLS版本" "PASS" "服务仅使用TLS 1.2或更高版本"
  else
    record_check "传输安全" "TLS版本" "FAIL" "服务使用过时的TLS/SSL版本" "HIGH" "配置Nginx仅使用TLS 1.2和TLS 1.3"
  fi
  
  # 检查安全响应头
  local headers=$(curl -sI $ENDPOINT/health)
  
  # 检查HSTS头
  if echo "$headers" | grep -q "Strict-Transport-Security"; then
    record_check "传输安全" "HTTP严格传输安全(HSTS)" "PASS" "已配置HSTS头"
  else
    record_check "传输安全" "HTTP严格传输安全(HSTS)" "FAIL" "未配置HSTS头" "MEDIUM" "添加'Strict-Transport-Security'头以强制HTTPS连接"
  fi
  
  # 检查Content-Security-Policy头
  if echo "$headers" | grep -q "Content-Security-Policy"; then
    record_check "传输安全" "内容安全策略(CSP)" "PASS" "已配置CSP头"
  else
    record_check "传输安全" "内容安全策略(CSP)" "FAIL" "未配置CSP头" "MEDIUM" "添加'Content-Security-Policy'头以防止XSS攻击"
  fi
  
  # 检查X-Content-Type-Options头
  if echo "$headers" | grep -q "X-Content-Type-Options"; then
    record_check "传输安全" "X-Content-Type-Options" "PASS" "已配置X-Content-Type-Options头"
  else
    record_check "传输安全" "X-Content-Type-Options" "FAIL" "未配置X-Content-Type-Options头" "LOW" "添加'X-Content-Type-Options: nosniff'头"
  fi
}

# 检查访问控制
check_access_control() {
  log "INFO" "检查访问控制..."
  
  # 尝试访问指标端点
  local metrics_access=$(curl -s -o /dev/null -w "%{http_code}" $ENDPOINT/metrics)
  if [ "$metrics_access" == "401" ] || [ "$metrics_access" == "403" ]; then
    record_check "访问控制" "指标端点保护" "PASS" "指标端点已正确限制访问"
  else
    record_check "访问控制" "指标端点保护" "FAIL" "指标端点未受到保护，返回状态码: $metrics_access" "HIGH" "为/metrics端点配置基本身份验证和IP限制"
  fi
  
  # 尝试无API密钥访问RAG端点
  local no_key_access=$(curl -s -o /dev/null -w "%{http_code}" -H "Content-Type: application/json" -d '{"query":"test"}' $ENDPOINT/rag)
  if [ "$no_key_access" == "401" ] || [ "$no_key_access" == "403" ]; then
    record_check "访问控制" "API密钥验证" "PASS" "API密钥验证正确配置"
  else
    record_check "访问控制" "API密钥验证" "FAIL" "未进行API密钥验证，返回状态码: $no_key_access" "HIGH" "确保所有API端点要求有效的API密钥"
  fi
  
  # 检查CORS配置
  local cors_headers=$(curl -sI -X OPTIONS $ENDPOINT/rag -H "Origin: http://example.com" -H "Access-Control-Request-Method: POST")
  
  if echo "$cors_headers" | grep -q "Access-Control-Allow-Origin: \*"; then
    record_check "访问控制" "CORS策略" "FAIL" "CORS配置过于宽松，允许所有来源" "MEDIUM" "限制CORS允许的来源，避免使用通配符"
  elif echo "$cors_headers" | grep -q "Access-Control-Allow-Origin:"; then
    record_check "访问控制" "CORS策略" "PASS" "CORS配置正确受限"
  else
    record_check "访问控制" "CORS策略" "PASS" "CORS响应头配置恰当"
  fi
}

# 检查速率限制
check_rate_limiting() {
  log "INFO" "检查速率限制..."
  
  # 快速发送多个请求以测试速率限制
  local request_count=10
  local rate_limit_reached=0
  
  for i in $(seq 1 $request_count); do
    local status=$(curl -s -o /dev/null -w "%{http_code}" $ENDPOINT/health)
    if [ "$status" == "429" ]; then
      rate_limit_reached=1
      break
    fi
    sleep 0.1
  done
  
  if [ $rate_limit_reached -eq 1 ]; then
    record_check "DoS防护" "速率限制" "PASS" "速率限制已正确配置"
  else
    record_check "DoS防护" "速率限制" "FAIL" "未检测到速率限制" "MEDIUM" "配置Nginx速率限制以防止DoS攻击"
  fi
}

# 检查服务器信息泄露
check_info_disclosure() {
  log "INFO" "检查信息泄露..."
  
  # 检查服务器版本头
  local server_header=$(curl -sI $ENDPOINT/health | grep -i "Server:" || echo "")
  if echo "$server_header" | grep -q -E "Server: nginx/[0-9]"; then
    record_check "信息泄露" "服务器版本头" "FAIL" "服务器泄露详细版本信息" "LOW" "配置Nginx隐藏详细版本信息"
  else
    record_check "信息泄露" "服务器版本头" "PASS" "服务器未泄露详细版本信息"
  fi
  
  # 检查错误页面是否泄露信息
  local error_page=$(curl -s $ENDPOINT/nonexistent_endpoint)
  if echo "$error_page" | grep -q -i "nginx\|python\|traceback\|error"; then
    record_check "信息泄露" "错误页面" "FAIL" "错误页面可能泄露系统信息" "MEDIUM" "自定义错误页面，避免泄露技术栈详情"
  else
    record_check "信息泄露" "错误页面" "PASS" "错误页面未泄露系统信息"
  fi
}

# 检查配置文件安全
check_config_security() {
  log "INFO" "检查配置文件安全..."
  
  # 检查RAG配置文件
  if [ -f "$CONFIG_DIR/rag-config.json" ]; then
    # 检查API密钥是否直接存储在配置中
    if grep -q "\"api_key\":" "$CONFIG_DIR/rag-config.json"; then
      record_check "配置安全" "API密钥存储" "FAIL" "API密钥直接存储在配置文件中" "HIGH" "使用环境变量或专用的密钥存储服务"
    else
      record_check "配置安全" "API密钥存储" "PASS" "API密钥未直接存储在配置文件中"
    fi
    
    # 检查不安全的Redis配置
    if grep -q "\"redis\":" "$CONFIG_DIR/rag-config.json"; then
      local redis_config=$(grep -A 10 "\"redis\":" "$CONFIG_DIR/rag-config.json")
      if echo "$redis_config" | grep -q "\"password\":" && ! echo "$redis_config" | grep -q "\"password\": \"\""; then
        record_check "配置安全" "Redis密码保护" "PASS" "Redis连接已配置密码"
      else
        record_check "配置安全" "Redis密码保护" "FAIL" "Redis连接未配置密码" "MEDIUM" "为Redis配置强密码"
      fi
    fi
  else
    log "WARN" "找不到RAG配置文件: $CONFIG_DIR/rag-config.json"
  fi
  
  # 检查Nginx配置文件
  if [ -f "$CONFIG_DIR/nginx.conf" ]; then
    # 检查是否启用了安全响应头
    if grep -q "add_header Strict-Transport-Security" "$CONFIG_DIR/nginx.conf"; then
      record_check "配置安全" "Nginx HSTS配置" "PASS" "Nginx已配置HSTS头"
    else
      record_check "配置安全" "Nginx HSTS配置" "FAIL" "Nginx未配置HSTS头" "MEDIUM" "在Nginx配置中添加HSTS响应头"
    fi
    
    # 检查是否限制了敏感文件访问
    if grep -q "location ~ \.(git|py|json|env|ini|conf)$" "$CONFIG_DIR/nginx.conf"; then
      record_check "配置安全" "敏感文件访问限制" "PASS" "Nginx已限制敏感文件访问"
    else
      record_check "配置安全" "敏感文件访问限制" "FAIL" "Nginx未限制敏感文件访问" "MEDIUM" "配置Nginx限制敏感文件和目录的访问"
    fi
  else
    log "WARN" "找不到Nginx配置文件: $CONFIG_DIR/nginx.conf"
  fi
}

# 执行常见漏洞测试
test_common_vulnerabilities() {
  log "INFO" "测试常见漏洞..."
  
  # 测试SQL注入
  local sql_injection_payload='{"query":"x\' OR 1=1; --"}'
  local sql_response=$(curl -s -H "Content-Type: application/json" -d "$sql_injection_payload" $ENDPOINT/rag || echo "")
  
  if echo "$sql_response" | grep -q -i "sql\|syntax\|error\|exception"; then
    record_check "常见漏洞" "SQL注入" "FAIL" "可能存在SQL注入漏洞" "HIGH" "使用参数化查询，验证和清理所有用户输入"
  else
    record_check "常见漏洞" "SQL注入" "PASS" "未检测到SQL注入漏洞"
  fi
  
  # 测试XSS
  local xss_payload='{"query":"<script>alert(1)</script>"}'
  local xss_response=$(curl -s -H "Content-Type: application/json" -d "$xss_payload" $ENDPOINT/rag || echo "")
  
  if echo "$xss_response" | grep -q "<script>alert(1)</script>"; then
    record_check "常见漏洞" "跨站脚本(XSS)" "FAIL" "可能存在XSS漏洞" "HIGH" "对所有输出进行HTML编码，实施内容安全策略"
  else
    record_check "常见漏洞" "跨站脚本(XSS)" "PASS" "未检测到XSS漏洞"
  fi
  
  # 测试命令注入
  local cmd_injection_payload='{"query":"& cat /etc/passwd"}'
  local cmd_response=$(curl -s -H "Content-Type: application/json" -d "$cmd_injection_payload" $ENDPOINT/rag || echo "")
  
  if echo "$cmd_response" | grep -q "root:"; then
    record_check "常见漏洞" "命令注入" "FAIL" "可能存在命令注入漏洞" "HIGH" "避免使用shell命令，验证并清理所有用户输入"
  else
    record_check "常见漏洞" "命令注入" "PASS" "未检测到命令注入漏洞"
  fi
  
  # 测试不安全的反序列化
  local deserial_payload='{"query":"payload", "__class__": "subprocess.Popen", "args": ["cat", "/etc/passwd"]}'
  local deserial_response=$(curl -s -H "Content-Type: application/json" -d "$deserial_payload" $ENDPOINT/rag || echo "")
  
  if echo "$deserial_response" | grep -q "root:"; then
    record_check "常见漏洞" "不安全的反序列化" "FAIL" "可能存在不安全的反序列化漏洞" "HIGH" "使用安全的序列化库，避免直接反序列化不可信数据"
  else
    record_check "常见漏洞" "不安全的反序列化" "PASS" "未检测到不安全的反序列化漏洞"
  fi
}

# 新增安全检查项：
check_fail2ban() {
  systemctl is-active --quiet fail2ban || echo "fail2ban未运行"
}

check_ports() {
  netstat -tuln | grep -E ':80 |:443 ' || echo "关键端口未加密"
}

check_updates() {
  yum check-update | grep 'security' || echo "有可用安全更新"
}

# 生成安全审计报告
generate_report() {
  log "INFO" "生成安全审计报告..."
  
  cat > $REPORT_FILE << EOF
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>索克生活RAG服务安全审计报告</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
    h1 { color: #35BB78; border-bottom: 2px solid #35BB78; padding-bottom: 10px; }
    h2 { color: #35BB78; margin-top: 30px; }
    .summary { display: flex; margin: 20px 0; }
    .summary-box { flex: 1; padding: 20px; border-radius: 5px; margin-right: 10px; text-align: center; }
    .summary-total { background-color: #f2f2f2; }
    .summary-passed { background-color: #d4edda; }
    .summary-issues { background-color: #f8d7da; }
    .severity-high { background-color: #f8d7da; }
    .severity-medium { background-color: #fff3cd; }
    .severity-low { background-color: #d1ecf1; }
    .table-container { margin-top: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
    th { background-color: #f2f2f2; }
    tr:nth-child(even) { background-color: #f9f9f9; }
    .severity-column { text-align: center; font-weight: bold; }
    .HIGH { color: #721c24; }
    .MEDIUM { color: #856404; }
    .LOW { color: #0c5460; }
    .timestamp { color: #666; font-size: 0.8em; margin-top: 5px; }
    .chart-container { display: flex; margin: 20px 0; }
    .chart { flex: 1; height: 200px; margin-right: 10px; }
    .recommendations { margin-top: 30px; background-color: #f9f9f9; padding: 20px; border-radius: 5px; }
  </style>
</head>
<body>
  <h1>索克生活RAG服务安全审计报告</h1>
  <p class="timestamp">生成时间: $(date '+%Y-%m-%d %H:%M:%S')</p>
  
  <div class="summary">
    <div class="summary-box summary-total">
      <h3>总检查项</h3>
      <div style="font-size: 24px; font-weight: bold;">$TOTAL_CHECKS</div>
    </div>
    <div class="summary-box summary-passed">
      <h3>通过检查</h3>
      <div style="font-size: 24px; font-weight: bold;">$PASSED_CHECKS</div>
    </div>
    <div class="summary-box summary-issues">
      <h3>发现问题</h3>
      <div style="font-size: 24px; font-weight: bold;">$ISSUES_FOUND</div>
    </div>
  </div>
  
  <div class="summary">
    <div class="summary-box severity-high">
      <h3>高危问题</h3>
      <div style="font-size: 24px; font-weight: bold;">$HIGH_SEVERITY_ISSUES</div>
    </div>
    <div class="summary-box severity-medium">
      <h3>中危问题</h3>
      <div style="font-size: 24px; font-weight: bold;">$MEDIUM_SEVERITY_ISSUES</div>
    </div>
    <div class="summary-box severity-low">
      <h3>低危问题</h3>
      <div style="font-size: 24px; font-weight: bold;">$LOW_SEVERITY_ISSUES</div>
    </div>
  </div>
  
  <h2>安全问题详情</h2>
  
  <div class="table-container">
    <table>
      <tr>
        <th>严重性</th>
        <th>类别</th>
        <th>问题</th>
        <th>描述</th>
        <th>建议</th>
      </tr>
EOF

  # 按严重性排序问题
  # 使用临时文件替代命令替换，以避免语法错误
  local temp_file=$(mktemp)
  for issue in "${ISSUES[@]}"; do
    echo "$issue" >> "$temp_file"
  done
  
  # 使用sort命令排序并读取结果
  local sorted_issues=()
  while IFS= read -r line; do
    sorted_issues+=("$line")
  done < <(sort -t'|' -k2,2nr -k3,3 "$temp_file")
  
  # 删除临时文件
  rm -f "$temp_file"

  for issue in "${sorted_issues[@]}"; do
    local severity="" 
    local severity_score=""
    local category=""
    local title=""
    local description=""
    local recommendation=""
    IFS='|' read -r severity severity_score category title description recommendation <<< "$issue"
    
    cat >> $REPORT_FILE << EOF
      <tr>
        <td class="severity-column $severity">$severity</td>
        <td>$category</td>
        <td>$title</td>
        <td>$description</td>
        <td>$recommendation</td>
      </tr>
EOF
  done

  cat >> $REPORT_FILE << EOF
    </table>
  </div>
  
  <h2>安全建议摘要</h2>
  
  <div class="recommendations">
    <h3>高优先级建议</h3>
    <ul>
EOF

  # 添加高优先级建议
  for issue in "${sorted_issues[@]}"; do
    local severity="" 
    local severity_score=""
    local category=""
    local title=""
    local description=""
    local recommendation=""
    IFS='|' read -r severity severity_score category title description recommendation <<< "$issue"
    if [ "$severity" == "HIGH" ]; then
      echo "      <li><strong>$title</strong>: $recommendation</li>" >> $REPORT_FILE
    fi
  done

  cat >> $REPORT_FILE << EOF
    </ul>
    
    <h3>中优先级建议</h3>
    <ul>
EOF

  # 添加中优先级建议
  for issue in "${sorted_issues[@]}"; do
    local severity="" 
    local severity_score=""
    local category=""
    local title=""
    local description=""
    local recommendation=""
    IFS='|' read -r severity severity_score category title description recommendation <<< "$issue"
    if [ "$severity" == "MEDIUM" ]; then
      echo "      <li><strong>$title</strong>: $recommendation</li>" >> $REPORT_FILE
    fi
  done

  cat >> $REPORT_FILE << EOF
    </ul>
    
    <h3>低优先级建议</h3>
    <ul>
EOF

  # 添加低优先级建议
  for issue in "${sorted_issues[@]}"; do
    local severity="" 
    local severity_score=""
    local category=""
    local title=""
    local description=""
    local recommendation=""
    IFS='|' read -r severity severity_score category title description recommendation <<< "$issue"
    if [ "$severity" == "LOW" ]; then
      echo "      <li><strong>$title</strong>: $recommendation</li>" >> $REPORT_FILE
    fi
  done

  cat >> $REPORT_FILE << EOF
    </ul>
  </div>
  
  <h2>结论</h2>
  <p>
    此安全审计在$(date '+%Y-%m-%d')执行，共检查了$TOTAL_CHECKS个安全项目，其中$PASSED_CHECKS个检查通过，发现$ISSUES_FOUND个安全问题
    （$HIGH_SEVERITY_ISSUES个高危问题，$MEDIUM_SEVERITY_ISSUES个中危问题，$LOW_SEVERITY_ISSUES个低危问题）。
  </p>
  
  <p>
    高风险评估: 
    如果发现高危安全问题，应立即采取措施修复，以防止潜在的安全漏洞被利用；
    如果发现中危问题，建议在下一个维护周期内修复；
    如果仅有低危问题，系统安全状况良好，可在方便时处理以进一步增强安全性。
  </p>
  
  <p>
    建议定期进行安全审计和渗透测试，以确保系统的持续安全。
  </p>
</body>
</html>
EOF

  log "INFO" "报告已生成: $REPORT_FILE"
}

# 主函数
main() {
  log "INFO" "==== 开始RAG服务安全审计 ===="
  
  # 初始化日志文件
  : > "$LOG_FILE"
  
  # 检查TLS配置
  check_tls
  
  # 检查访问控制
  check_access_control
  
  # 检查速率限制
  check_rate_limiting
  
  # 检查信息泄露
  check_info_disclosure
  
  # 检查配置文件安全
  check_config_security
  
  # 测试常见漏洞
  test_common_vulnerabilities
  
  # 新增安全检查项
  check_fail2ban
  check_ports
  check_updates
  
  # 生成报告
  generate_report
  
  log "INFO" "==== 安全审计完成 ===="
  log "INFO" "总检查项: $TOTAL_CHECKS"
  log "INFO" "通过检查: $PASSED_CHECKS"
  log "INFO" "发现问题: $ISSUES_FOUND (高危: $HIGH_SEVERITY_ISSUES, 中危: $MEDIUM_SEVERITY_ISSUES, 低危: $LOW_SEVERITY_ISSUES)"
  log "INFO" "审计报告: $REPORT_FILE"
  
  # 根据安全问题的严重性决定退出代码
  if [ $HIGH_SEVERITY_ISSUES -gt 0 ]; then
    return 2  # 发现高危问题
  elif [ $MEDIUM_SEVERITY_ISSUES -gt 0 ]; then
    return 1  # 发现中危问题
  else
    return 0  # 未发现中高危问题
  fi
}

# 脚本入口
main "$@" 