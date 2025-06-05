#!/bin/bash

# 索克生活 API 网关 - 自动化运维脚本
# Automated Operations Scripts for Suoke Life API Gateway

set -euo pipefail

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs"
CONFIG_DIR="${PROJECT_ROOT}/config"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

# 创建必要目录
mkdir -p "${LOG_DIR}"

# 健康检查函数
health_check() {
    log_info "执行API网关健康检查..."
    
    local health_url="${API_GATEWAY_URL:-http://localhost:8080}/health"
    local max_retries=3
    local retry_delay=5
    
    for ((i=1; i<=max_retries; i++)); do
        if curl -f -s "${health_url}" > /dev/null; then
            log_success "健康检查通过"
            return 0
        else
            log_warn "健康检查失败 (尝试 ${i}/${max_retries})"
            if [[ $i -lt $max_retries ]]; then
                sleep $retry_delay
            fi
        fi
    done
    
    log_error "健康检查失败，服务可能不可用"
    return 1
}

# 性能监控函数
performance_monitor() {
    log_info "执行性能监控检查..."
    
    local metrics_url="${API_GATEWAY_URL:-http://localhost:8080}/metrics"
    local output_file="${LOG_DIR}/performance_$(date +%Y%m%d_%H%M%S).log"
    
    # 获取指标数据
    if curl -s "${metrics_url}" > "${output_file}"; then
        log_success "性能指标已保存到 ${output_file}"
        
        # 分析关键指标
        local cpu_usage=$(grep "process_cpu_seconds_total" "${output_file}" | tail -1 | awk '{print $2}')
        local memory_usage=$(grep "process_resident_memory_bytes" "${output_file}" | tail -1 | awk '{print $2}')
        local request_rate=$(grep "http_requests_total" "${output_file}" | grep -v "#" | wc -l)
        
        log_info "CPU使用时间: ${cpu_usage:-N/A} 秒"
        log_info "内存使用: $((${memory_usage:-0} / 1024 / 1024)) MB"
        log_info "请求指标数量: ${request_rate}"
        
        # 检查阈值
        if [[ ${memory_usage:-0} -gt 1073741824 ]]; then  # 1GB
            log_warn "内存使用超过1GB，建议检查内存泄漏"
        fi
    else
        log_error "无法获取性能指标"
        return 1
    fi
}

# 日志清理函数
log_cleanup() {
    log_info "执行日志清理..."
    
    local log_retention_days=${LOG_RETENTION_DAYS:-7}
    local cleaned_files=0
    
    # 清理应用日志
    if [[ -d "${LOG_DIR}" ]]; then
        while IFS= read -r -d '' file; do
            rm -f "$file"
            ((cleaned_files++))
        done < <(find "${LOG_DIR}" -name "*.log" -type f -mtime +${log_retention_days} -print0)
    fi
    
    # 清理系统日志（如果有权限）
    if [[ -w /var/log ]]; then
        while IFS= read -r -d '' file; do
            rm -f "$file"
            ((cleaned_files++))
        done < <(find /var/log -name "*api-gateway*" -type f -mtime +${log_retention_days} -print0 2>/dev/null)
    fi
    
    log_success "已清理 ${cleaned_files} 个过期日志文件"
}

# 缓存清理函数
cache_cleanup() {
    log_info "执行缓存清理..."
    
    local redis_host="${REDIS_HOST:-localhost}"
    local redis_port="${REDIS_PORT:-6379}"
    local redis_db="${REDIS_DB:-0}"
    
    # 检查Redis连接
    if command -v redis-cli >/dev/null 2>&1; then
        if redis-cli -h "${redis_host}" -p "${redis_port}" -n "${redis_db}" ping >/dev/null 2>&1; then
            # 获取缓存统计
            local cache_keys=$(redis-cli -h "${redis_host}" -p "${redis_port}" -n "${redis_db}" dbsize)
            log_info "当前缓存键数量: ${cache_keys}"
            
            # 清理过期键
            local expired_keys=$(redis-cli -h "${redis_host}" -p "${redis_port}" -n "${redis_db}" eval "
                local keys = redis.call('keys', 'suoke:gateway:cache:*')
                local expired = 0
                for i=1,#keys do
                    local ttl = redis.call('ttl', keys[i])
                    if ttl == -1 then
                        redis.call('expire', keys[i], 3600)
                        expired = expired + 1
                    end
                end
                return expired
            " 0)
            
            log_success "已处理 ${expired_keys} 个无过期时间的缓存键"
        else
            log_warn "无法连接到Redis服务器"
        fi
    else
        log_warn "redis-cli 未安装，跳过缓存清理"
    fi
}

# 配置备份函数
config_backup() {
    log_info "执行配置备份..."
    
    local backup_dir="${PROJECT_ROOT}/backups/config"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${backup_dir}/config_backup_${timestamp}.tar.gz"
    
    mkdir -p "${backup_dir}"
    
    # 备份配置文件
    if tar -czf "${backup_file}" -C "${PROJECT_ROOT}" config/ 2>/dev/null; then
        log_success "配置已备份到 ${backup_file}"
        
        # 清理旧备份（保留最近10个）
        local old_backups=$(ls -1t "${backup_dir}"/config_backup_*.tar.gz 2>/dev/null | tail -n +11)
        if [[ -n "${old_backups}" ]]; then
            echo "${old_backups}" | xargs rm -f
            log_info "已清理旧备份文件"
        fi
    else
        log_error "配置备份失败"
        return 1
    fi
}

# 数据库连接检查函数
database_check() {
    log_info "执行数据库连接检查..."
    
    local db_url="${DATABASE_URL:-}"
    
    if [[ -z "${db_url}" ]]; then
        log_warn "DATABASE_URL 未设置，跳过数据库检查"
        return 0
    fi
    
    # 使用Python检查数据库连接
    python3 -c "
import os
import sys
try:
    import psycopg2
    from urllib.parse import urlparse
    
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url:
        print('数据库URL未配置')
        sys.exit(1)
    
    parsed = urlparse(db_url)
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path[1:],
        user=parsed.username,
        password=parsed.password
    )
    
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    
    if result and result[0] == 1:
        print('数据库连接正常')
    else:
        print('数据库连接异常')
        sys.exit(1)
        
    cursor.close()
    conn.close()
    
except ImportError:
    print('psycopg2 未安装，跳过数据库检查')
except Exception as e:
    print(f'数据库连接失败: {e}')
    sys.exit(1)
" && log_success "数据库连接检查通过" || log_error "数据库连接检查失败"
}

# 服务重启函数
service_restart() {
    log_info "执行服务重启..."
    
    local service_name="${SERVICE_NAME:-suoke-api-gateway}"
    local restart_method="${RESTART_METHOD:-docker}"
    
    case "${restart_method}" in
        "docker")
            if command -v docker >/dev/null 2>&1; then
                if docker ps --format "table {{.Names}}" | grep -q "${service_name}"; then
                    docker restart "${service_name}"
                    log_success "Docker容器 ${service_name} 已重启"
                else
                    log_warn "Docker容器 ${service_name} 未运行"
                fi
            else
                log_error "Docker 未安装"
                return 1
            fi
            ;;
        "kubernetes")
            if command -v kubectl >/dev/null 2>&1; then
                kubectl rollout restart deployment/"${service_name}" -n suoke-services
                kubectl rollout status deployment/"${service_name}" -n suoke-services --timeout=300s
                log_success "Kubernetes部署 ${service_name} 已重启"
            else
                log_error "kubectl 未安装"
                return 1
            fi
            ;;
        "systemd")
            if command -v systemctl >/dev/null 2>&1; then
                sudo systemctl restart "${service_name}"
                sudo systemctl is-active --quiet "${service_name}"
                log_success "Systemd服务 ${service_name} 已重启"
            else
                log_error "systemctl 未可用"
                return 1
            fi
            ;;
        *)
            log_error "不支持的重启方法: ${restart_method}"
            return 1
            ;;
    esac
    
    # 等待服务启动
    sleep 10
    health_check
}

# 安全扫描函数
security_scan() {
    log_info "执行安全扫描..."
    
    local scan_report="${LOG_DIR}/security_scan_$(date +%Y%m%d_%H%M%S).json"
    
    # 依赖漏洞扫描
    if command -v safety >/dev/null 2>&1; then
        log_info "执行依赖漏洞扫描..."
        if safety check --json > "${scan_report}" 2>/dev/null; then
            local vulnerabilities=$(jq length "${scan_report}" 2>/dev/null || echo "0")
            if [[ ${vulnerabilities} -eq 0 ]]; then
                log_success "未发现依赖漏洞"
            else
                log_warn "发现 ${vulnerabilities} 个依赖漏洞，详情请查看 ${scan_report}"
            fi
        else
            log_warn "依赖漏洞扫描失败"
        fi
    else
        log_warn "safety 未安装，跳过依赖漏洞扫描"
    fi
    
    # 端口扫描
    if command -v nmap >/dev/null 2>&1; then
        log_info "执行端口扫描..."
        local gateway_host="${API_GATEWAY_HOST:-localhost}"
        nmap -p 8080,50051,9090 "${gateway_host}" > "${LOG_DIR}/port_scan_$(date +%Y%m%d_%H%M%S).txt"
        log_success "端口扫描完成"
    else
        log_warn "nmap 未安装，跳过端口扫描"
    fi
}

# 性能调优函数
performance_tuning() {
    log_info "执行性能调优..."
    
    # 系统参数调优
    if [[ -w /proc/sys ]]; then
        # 增加文件描述符限制
        echo 65536 > /proc/sys/fs/file-max 2>/dev/null || true
        
        # 调整网络参数
        echo 1 > /proc/sys/net/ipv4/tcp_tw_reuse 2>/dev/null || true
        echo 1 > /proc/sys/net/ipv4/tcp_fin_timeout 2>/dev/null || true
        
        log_success "系统参数调优完成"
    else
        log_warn "无权限修改系统参数"
    fi
    
    # 应用参数调优
    local tuning_config="${CONFIG_DIR}/performance-tuning.yaml"
    if [[ -f "${tuning_config}" ]]; then
        log_info "应用性能调优配置已存在: ${tuning_config}"
    else
        cat > "${tuning_config}" << EOF
# 性能调优配置
performance:
  worker_processes: auto
  worker_connections: 1024
  keepalive_timeout: 65
  client_max_body_size: 10m
  
  # 缓存配置
  cache:
    max_size: 100m
    inactive: 60m
    
  # 连接池配置
  connection_pool:
    max_connections: 100
    min_connections: 10
    max_idle_time: 300
EOF
        log_success "已创建性能调优配置: ${tuning_config}"
    fi
}

# 故障排查函数
troubleshoot() {
    log_info "执行故障排查..."
    
    local troubleshoot_report="${LOG_DIR}/troubleshoot_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "=== API网关故障排查报告 ==="
        echo "时间: $(date)"
        echo ""
        
        echo "=== 服务状态 ==="
        health_check || echo "健康检查失败"
        echo ""
        
        echo "=== 系统资源 ==="
        echo "CPU使用率:"
        top -bn1 | grep "Cpu(s)" || echo "无法获取CPU信息"
        echo ""
        echo "内存使用:"
        free -h || echo "无法获取内存信息"
        echo ""
        echo "磁盘使用:"
        df -h || echo "无法获取磁盘信息"
        echo ""
        
        echo "=== 网络连接 ==="
        echo "监听端口:"
        netstat -tlnp | grep -E ":8080|:50051|:9090" || echo "无法获取端口信息"
        echo ""
        
        echo "=== 进程信息 ==="
        ps aux | grep -E "api.gateway|uvicorn|gunicorn" | grep -v grep || echo "未找到相关进程"
        echo ""
        
        echo "=== 最近日志 ==="
        if [[ -f "${LOG_DIR}/api-gateway.log" ]]; then
            tail -50 "${LOG_DIR}/api-gateway.log"
        else
            echo "日志文件不存在"
        fi
        
    } > "${troubleshoot_report}"
    
    log_success "故障排查报告已生成: ${troubleshoot_report}"
}

# 主函数
main() {
    local operation="${1:-help}"
    
    case "${operation}" in
        "health")
            health_check
            ;;
        "monitor")
            performance_monitor
            ;;
        "cleanup")
            log_cleanup
            cache_cleanup
            ;;
        "backup")
            config_backup
            ;;
        "check")
            health_check
            database_check
            performance_monitor
            ;;
        "restart")
            service_restart
            ;;
        "security")
            security_scan
            ;;
        "tune")
            performance_tuning
            ;;
        "troubleshoot")
            troubleshoot
            ;;
        "full")
            log_info "执行完整运维检查..."
            health_check
            database_check
            performance_monitor
            log_cleanup
            cache_cleanup
            config_backup
            security_scan
            log_success "完整运维检查完成"
            ;;
        "help"|*)
            echo "索克生活 API 网关 - 自动化运维脚本"
            echo ""
            echo "用法: $0 <operation>"
            echo ""
            echo "可用操作:"
            echo "  health      - 健康检查"
            echo "  monitor     - 性能监控"
            echo "  cleanup     - 清理日志和缓存"
            echo "  backup      - 配置备份"
            echo "  check       - 综合检查（健康+数据库+性能）"
            echo "  restart     - 服务重启"
            echo "  security    - 安全扫描"
            echo "  tune        - 性能调优"
            echo "  troubleshoot- 故障排查"
            echo "  full        - 完整运维检查"
            echo "  help        - 显示帮助信息"
            echo ""
            echo "环境变量:"
            echo "  API_GATEWAY_URL    - API网关URL (默认: http://localhost:8080)"
            echo "  REDIS_HOST         - Redis主机 (默认: localhost)"
            echo "  REDIS_PORT         - Redis端口 (默认: 6379)"
            echo "  DATABASE_URL       - 数据库连接URL"
            echo "  SERVICE_NAME       - 服务名称 (默认: suoke-api-gateway)"
            echo "  RESTART_METHOD     - 重启方法 (docker/kubernetes/systemd)"
            echo "  LOG_RETENTION_DAYS - 日志保留天数 (默认: 7)"
            ;;
    esac
}

# 执行主函数
main "$@" 