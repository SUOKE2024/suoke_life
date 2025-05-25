#!/bin/bash

# 索克生活 - 触诊服务数据备份脚本
# 用于定期备份数据库、配置文件和重要数据

set -e

# 配置变量
BACKUP_DIR="/app/backups"
DATA_DIR="/app/data"
CONFIG_DIR="/app/config"
LOGS_DIR="/app/logs"
MODELS_DIR="/app/models"
REPORTS_DIR="/app/reports"

# 时间戳
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="palpation_backup_${TIMESTAMP}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 创建备份目录
create_backup_directory() {
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        log_info "创建备份目录: $BACKUP_DIR"
    fi
    
    # 创建当前备份的子目录
    CURRENT_BACKUP_DIR="$BACKUP_DIR/$BACKUP_NAME"
    mkdir -p "$CURRENT_BACKUP_DIR"
    log_info "创建当前备份目录: $CURRENT_BACKUP_DIR"
}

# 备份数据库
backup_database() {
    log_info "开始备份数据库..."
    
    if [ -f "$DATA_DIR/palpation.db" ]; then
        # 创建数据库备份目录
        mkdir -p "$CURRENT_BACKUP_DIR/database"
        
        # 使用SQLite的.backup命令进行热备份
        sqlite3 "$DATA_DIR/palpation.db" ".backup '$CURRENT_BACKUP_DIR/database/palpation_${TIMESTAMP}.db'"
        
        # 验证备份文件
        if [ -f "$CURRENT_BACKUP_DIR/database/palpation_${TIMESTAMP}.db" ]; then
            # 检查备份文件完整性
            sqlite3 "$CURRENT_BACKUP_DIR/database/palpation_${TIMESTAMP}.db" "PRAGMA integrity_check;" > /dev/null
            
            # 获取文件大小
            ORIGINAL_SIZE=$(stat -f%z "$DATA_DIR/palpation.db" 2>/dev/null || stat -c%s "$DATA_DIR/palpation.db")
            BACKUP_SIZE=$(stat -f%z "$CURRENT_BACKUP_DIR/database/palpation_${TIMESTAMP}.db" 2>/dev/null || stat -c%s "$CURRENT_BACKUP_DIR/database/palpation_${TIMESTAMP}.db")
            
            log_success "数据库备份完成 (原始: ${ORIGINAL_SIZE} bytes, 备份: ${BACKUP_SIZE} bytes)"
            
            # 压缩数据库备份
            gzip "$CURRENT_BACKUP_DIR/database/palpation_${TIMESTAMP}.db"
            log_info "数据库备份已压缩"
        else
            log_error "数据库备份失败"
            return 1
        fi
    else
        log_warning "数据库文件不存在: $DATA_DIR/palpation.db"
    fi
}

# 备份配置文件
backup_configuration() {
    log_info "开始备份配置文件..."
    
    if [ -d "$CONFIG_DIR" ]; then
        mkdir -p "$CURRENT_BACKUP_DIR/config"
        
        # 复制所有配置文件
        cp -r "$CONFIG_DIR"/* "$CURRENT_BACKUP_DIR/config/" 2>/dev/null || true
        
        # 备份环境变量文件
        if [ -f "/app/.env" ]; then
            cp "/app/.env" "$CURRENT_BACKUP_DIR/config/"
        fi
        
        # 创建配置文件清单
        find "$CURRENT_BACKUP_DIR/config" -type f > "$CURRENT_BACKUP_DIR/config/file_list.txt"
        
        log_success "配置文件备份完成"
    else
        log_warning "配置目录不存在: $CONFIG_DIR"
    fi
}

# 备份模型文件
backup_models() {
    log_info "开始备份模型文件..."
    
    if [ -d "$MODELS_DIR" ] && [ "$(ls -A $MODELS_DIR)" ]; then
        mkdir -p "$CURRENT_BACKUP_DIR/models"
        
        # 复制模型文件（排除临时文件）
        find "$MODELS_DIR" -type f \( -name "*.pkl" -o -name "*.joblib" -o -name "*.h5" -o -name "*.pt" -o -name "*.pth" \) \
            -exec cp {} "$CURRENT_BACKUP_DIR/models/" \;
        
        # 创建模型文件清单
        find "$CURRENT_BACKUP_DIR/models" -type f > "$CURRENT_BACKUP_DIR/models/model_list.txt"
        
        log_success "模型文件备份完成"
    else
        log_warning "模型目录为空或不存在: $MODELS_DIR"
    fi
}

# 备份重要日志
backup_logs() {
    log_info "开始备份重要日志..."
    
    if [ -d "$LOGS_DIR" ]; then
        mkdir -p "$CURRENT_BACKUP_DIR/logs"
        
        # 备份最近7天的日志文件
        find "$LOGS_DIR" -name "*.log" -mtime -7 -exec cp {} "$CURRENT_BACKUP_DIR/logs/" \;
        
        # 备份错误日志
        find "$LOGS_DIR" -name "*error*" -mtime -30 -exec cp {} "$CURRENT_BACKUP_DIR/logs/" \;
        
        # 压缩日志文件
        if [ "$(ls -A $CURRENT_BACKUP_DIR/logs)" ]; then
            tar -czf "$CURRENT_BACKUP_DIR/logs_${TIMESTAMP}.tar.gz" -C "$CURRENT_BACKUP_DIR" logs/
            rm -rf "$CURRENT_BACKUP_DIR/logs"
            log_success "日志文件备份并压缩完成"
        else
            log_warning "没有找到需要备份的日志文件"
        fi
    else
        log_warning "日志目录不存在: $LOGS_DIR"
    fi
}

# 备份报告文件
backup_reports() {
    log_info "开始备份报告文件..."
    
    if [ -d "$REPORTS_DIR" ] && [ "$(ls -A $REPORTS_DIR)" ]; then
        mkdir -p "$CURRENT_BACKUP_DIR/reports"
        
        # 备份最近30天的报告文件
        find "$REPORTS_DIR" -type f -mtime -30 -exec cp {} "$CURRENT_BACKUP_DIR/reports/" \;
        
        # 压缩报告文件
        if [ "$(ls -A $CURRENT_BACKUP_DIR/reports)" ]; then
            tar -czf "$CURRENT_BACKUP_DIR/reports_${TIMESTAMP}.tar.gz" -C "$CURRENT_BACKUP_DIR" reports/
            rm -rf "$CURRENT_BACKUP_DIR/reports"
            log_success "报告文件备份并压缩完成"
        else
            log_warning "没有找到需要备份的报告文件"
        fi
    else
        log_warning "报告目录为空或不存在: $REPORTS_DIR"
    fi
}

# 创建备份元数据
create_backup_metadata() {
    log_info "创建备份元数据..."
    
    cat > "$CURRENT_BACKUP_DIR/backup_info.json" << EOF
{
    "backup_name": "$BACKUP_NAME",
    "timestamp": "$TIMESTAMP",
    "date": "$(date -Iseconds)",
    "hostname": "$(hostname)",
    "backup_type": "full",
    "service": "palpation-service",
    "version": "1.0.0",
    "components": {
        "database": $([ -f "$CURRENT_BACKUP_DIR/database/palpation_${TIMESTAMP}.db.gz" ] && echo "true" || echo "false"),
        "configuration": $([ -d "$CURRENT_BACKUP_DIR/config" ] && echo "true" || echo "false"),
        "models": $([ -f "$CURRENT_BACKUP_DIR/models/model_list.txt" ] && echo "true" || echo "false"),
        "logs": $([ -f "$CURRENT_BACKUP_DIR/logs_${TIMESTAMP}.tar.gz" ] && echo "true" || echo "false"),
        "reports": $([ -f "$CURRENT_BACKUP_DIR/reports_${TIMESTAMP}.tar.gz" ] && echo "true" || echo "false")
    },
    "backup_size": "$(du -sh $CURRENT_BACKUP_DIR | cut -f1)"
}
EOF
    
    log_success "备份元数据创建完成"
}

# 压缩整个备份
compress_backup() {
    log_info "压缩整个备份..."
    
    cd "$BACKUP_DIR"
    tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME/"
    
    if [ -f "${BACKUP_NAME}.tar.gz" ]; then
        # 删除未压缩的目录
        rm -rf "$BACKUP_NAME"
        
        COMPRESSED_SIZE=$(du -sh "${BACKUP_NAME}.tar.gz" | cut -f1)
        log_success "备份压缩完成，大小: $COMPRESSED_SIZE"
    else
        log_error "备份压缩失败"
        return 1
    fi
}

# 清理旧备份
cleanup_old_backups() {
    log_info "清理旧备份文件..."
    
    # 保留最近30天的备份
    find "$BACKUP_DIR" -name "palpation_backup_*.tar.gz" -mtime +30 -delete
    
    # 保留最多50个备份文件
    BACKUP_COUNT=$(find "$BACKUP_DIR" -name "palpation_backup_*.tar.gz" | wc -l)
    if [ "$BACKUP_COUNT" -gt 50 ]; then
        find "$BACKUP_DIR" -name "palpation_backup_*.tar.gz" -type f -printf '%T@ %p\n' | \
        sort -n | head -n $((BACKUP_COUNT - 50)) | cut -d' ' -f2- | xargs rm -f
        log_info "删除了 $((BACKUP_COUNT - 50)) 个旧备份文件"
    fi
    
    log_success "旧备份清理完成"
}

# 验证备份完整性
verify_backup() {
    log_info "验证备份完整性..."
    
    BACKUP_FILE="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    
    if [ -f "$BACKUP_FILE" ]; then
        # 测试压缩文件完整性
        if tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
            log_success "备份文件完整性验证通过"
            
            # 计算校验和
            if command -v sha256sum &> /dev/null; then
                CHECKSUM=$(sha256sum "$BACKUP_FILE" | cut -d' ' -f1)
            elif command -v shasum &> /dev/null; then
                CHECKSUM=$(shasum -a 256 "$BACKUP_FILE" | cut -d' ' -f1)
            else
                CHECKSUM="N/A"
            fi
            
            echo "$CHECKSUM  ${BACKUP_NAME}.tar.gz" > "$BACKUP_DIR/${BACKUP_NAME}.sha256"
            log_info "备份校验和: $CHECKSUM"
            
            return 0
        else
            log_error "备份文件完整性验证失败"
            return 1
        fi
    else
        log_error "备份文件不存在: $BACKUP_FILE"
        return 1
    fi
}

# 发送备份通知（可选）
send_notification() {
    local status=$1
    local message=$2
    
    # 这里可以添加邮件、Slack、微信等通知方式
    # 示例：发送到系统日志
    logger -t "palpation-backup" "$status: $message"
    
    # 示例：写入通知文件
    echo "$(date -Iseconds) - $status: $message" >> "$BACKUP_DIR/backup_notifications.log"
}

# 主备份函数
main() {
    log_info "开始执行触诊服务数据备份..."
    
    # 检查磁盘空间
    AVAILABLE_SPACE=$(df "$BACKUP_DIR" | awk 'NR==2 {print $4}')
    if [ "$AVAILABLE_SPACE" -lt 1048576 ]; then  # 小于1GB
        log_warning "可用磁盘空间不足1GB，备份可能失败"
    fi
    
    # 执行备份步骤
    if create_backup_directory && \
       backup_database && \
       backup_configuration && \
       backup_models && \
       backup_logs && \
       backup_reports && \
       create_backup_metadata && \
       compress_backup && \
       verify_backup; then
        
        cleanup_old_backups
        
        FINAL_SIZE=$(du -sh "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" | cut -f1)
        log_success "备份完成！文件: ${BACKUP_NAME}.tar.gz (大小: $FINAL_SIZE)"
        
        send_notification "SUCCESS" "备份成功完成，文件大小: $FINAL_SIZE"
        
        exit 0
    else
        log_error "备份过程中发生错误"
        send_notification "ERROR" "备份过程中发生错误"
        exit 1
    fi
}

# 运行主函数
main "$@" 