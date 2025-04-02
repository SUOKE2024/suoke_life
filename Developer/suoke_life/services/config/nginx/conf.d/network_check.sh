#!/bin/bash
# 网络连接检查脚本
# 功能：检查主服务器与K8s集群的连接状态，并记录日志
# 版本：1.0
# 更新日期：2024-03-22

# 配置参数
LOG_FILE="/var/log/network_check.log"
K8S_ENDPOINT="120.26.161.52"
CHECK_INTERVAL=300  # 每5分钟检查一次
MAX_RETRIES=3
RETRY_INTERVAL=5
NOTIFY_EMAIL="admin@suoke.life"

# 创建日志文件（如果不存在）
touch $LOG_FILE

# 记录日志函数
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 发送通知函数（如果需要可以实现）
send_notification() {
    local subject="[$1] 服务器连接状态变更"
    local message="$2"
    
    if [ -x "$(command -v mail)" ]; then
        echo "$message" | mail -s "$subject" $NOTIFY_EMAIL
        log_message "已发送通知邮件到 $NOTIFY_EMAIL"
    else
        log_message "mail命令不可用，无法发送通知邮件"
    fi
}

# 检查网络连接函数
check_network() {
    # 检查连接状态
    for ((i=1; i<=$MAX_RETRIES; i++)); do
        if ping -c 1 -W 2 $K8S_ENDPOINT > /dev/null 2>&1; then
            log_message "连接检查成功：可以ping通K8s集群 ($K8S_ENDPOINT)"
            
            # 尝试连接健康检查端点
            if curl -s -m 5 -o /dev/null -w "%{http_code}" "http://$K8S_ENDPOINT/health" | grep -q "200"; then
                log_message "健康检查成功：K8s健康检查端点可正常访问"
                return 0
            else
                log_message "健康检查失败：K8s健康检查端点无法访问"
            fi
            
            return 1
        fi
        
        log_message "连接检查尝试 $i/$MAX_RETRIES 失败：无法ping通K8s集群"
        sleep $RETRY_INTERVAL
    done
    
    log_message "所有连接尝试均失败：无法与K8s集群建立连接"
    return 2
}

# 检查DNS解析
check_dns() {
    log_message "检查DNS解析：$K8S_ENDPOINT"
    
    # 获取当前路由信息
    local route_info=$(ip route get $K8S_ENDPOINT 2>&1)
    log_message "路由信息：$route_info"
    
    # 获取traceroute信息（如果可用）
    if [ -x "$(command -v traceroute)" ]; then
        log_message "开始执行traceroute到K8s集群..."
        local trace_info=$(traceroute -n -m 15 -w 2 $K8S_ENDPOINT 2>&1)
        log_message "Traceroute信息：\n$trace_info"
    else
        log_message "traceroute命令不可用，无法获取网络路径信息"
    fi
}

# 检查iptables规则
check_iptables() {
    log_message "检查与K8s集群相关的iptables规则..."
    
    if [ -x "$(command -v iptables)" ]; then
        local iptables_rules=$(iptables -L -n 2>&1)
        log_message "当前iptables规则摘要：$(echo "$iptables_rules" | grep -E 'Chain|ACCEPT|DROP' | head -10)"
    else
        log_message "iptables命令不可用，无法检查防火墙规则"
    fi
}

# 主函数
main() {
    log_message "开始网络连接检查..."
    check_dns
    check_iptables
    
    if check_network; then
        log_message "网络检查完成：K8s集群连接正常"
        # 之前状态如果是异常，现在恢复，则发送通知
        if [ -f "/tmp/network_status" ] && [ "$(cat /tmp/network_status)" = "error" ]; then
            send_notification "已恢复" "K8s集群连接已恢复正常"
            echo "ok" > /tmp/network_status
        fi
    else
        log_message "网络检查完成：K8s集群连接异常"
        # 如果是新的错误状态，则发送通知
        if [ ! -f "/tmp/network_status" ] || [ "$(cat /tmp/network_status)" = "ok" ]; then
            send_notification "错误" "K8s集群连接异常，请检查网络配置"
            echo "error" > /tmp/network_status
        fi
    fi
    
    log_message "本次检查完成，等待下一次检查..."
}

# 运行主函数
main

# 如果作为定时任务的一部分，只运行一次
# 如果想要持续运行，取消下面的注释
#while true; do
#    main
#    sleep $CHECK_INTERVAL
#done

exit 0 