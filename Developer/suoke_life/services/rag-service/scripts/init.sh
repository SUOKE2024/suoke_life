#!/bin/bash
#
# 索克生活APP RAG服务初始化脚本
# 负责创建必要的目录、设置权限和准备配置文件

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# 应用路径
APP_DIR="/app"
LOG_DIR="${APP_DIR}/logs"
DATA_DIR="${APP_DIR}/data"
CONFIG_DIR="${APP_DIR}/config"
MODEL_DIR="${APP_DIR}/models"
SCRIPT_DIR="${APP_DIR}/scripts"

# 检查是否以root权限运行
check_permissions() {
    if [[ $EUID -ne 0 && "$1" != "skip-root-check" ]]; then
        log_warn "此脚本需要root权限来设置适当的目录权限"
        log_info "尝试使用sudo运行: sudo $0"
        exit 1
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    # 创建主要目录
    mkdir -p ${LOG_DIR}
    mkdir -p ${DATA_DIR}/vector_store
    mkdir -p ${CONFIG_DIR}
    mkdir -p ${MODEL_DIR}/{embedding,reranker,text-generation}
    
    log_info "目录创建完成"
}

# 设置目录所有权
set_ownership() {
    # 检查appuser是否存在
    if id -u appuser >/dev/null 2>&1; then
        log_info "设置目录所有权为appuser..."
        chown -R appuser:appuser ${APP_DIR}
    else
        log_warn "appuser不存在，跳过所有权设置"
    fi
}

# 检查配置文件
check_config() {
    CONFIG_FILE="${CONFIG_DIR}/rag-config.json"
    
    if [[ ! -f ${CONFIG_FILE} ]]; then
        log_info "配置文件不存在，创建默认配置..."
        
        # 创建默认配置
        cat > ${CONFIG_FILE} << EOL
{
    "service": {
        "name": "rag-service",
        "version": "1.2.0",
        "description": "索克生活APP RAG检索增强生成服务"
    },
    "models": {
        "embedding": {
            "model_name": "BAAI/bge-small-zh-v1.5",
            "max_seq_length": 512
        },
        "reranker": {
            "model_name": "BAAI/bge-reranker-base",
            "max_length": 512
        },
        "llm": {
            "model_name": "Qwen/Qwen1.5-7B-Chat",
            "max_length": 4096,
            "temperature": 0.7,
            "top_p": 0.95
        }
    },
    "vectorDb": {
        "path": "/app/data/vector_store",
        "dimensions": 384,
        "metric": "cosine"
    },
    "generation": {
        "maxOutputLength": 2048,
        "llmConfig": {
            "promptTemplates": {
                "standard": "你是索克生活平台的AI助手，专注于中医健康领域。请基于以下信息回答用户问题：\\n\\n上下文信息：\\n{context}\\n\\n用户问题：{query}\\n\\n请给出专业、准确且易于理解的回答，引用相关的中医理论和健康建议。"
            }
        }
    },
    "retrieval": {
        "topK": 5,
        "minScore": 0.65,
        "reranking": {
            "enabled": true,
            "topK": 3,
            "minScore": 0.75
        }
    },
    "flare": {
        "enabled": true,
        "maxRetrievalRounds": 3,
        "confidenceThreshold": 0.85
    },
    "security": {
        "maxRequestSizeMb": 5
    }
}
EOL
        
        log_info "默认配置文件已创建: ${CONFIG_FILE}"
    else
        log_info "配置文件已存在: ${CONFIG_FILE}"
    fi
    
    # 设置配置文件权限
    chmod 644 ${CONFIG_FILE}
    
    # 检查appuser是否存在
    if id -u appuser >/dev/null 2>&1; then
        chown appuser:appuser ${CONFIG_FILE}
    fi
}

# 检查Python环境
check_python() {
    log_info "检查Python环境..."
    
    # 检查Python版本
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_VERSION_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_VERSION_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [[ "$PYTHON_VERSION_MAJOR" -lt 3 || ("$PYTHON_VERSION_MAJOR" -eq 3 && "$PYTHON_VERSION_MINOR" -lt 9) ]]; then
        log_error "Python版本必须为3.9或更高版本，当前版本为${PYTHON_VERSION}"
        log_info "请安装Python 3.9+并重新运行此脚本"
        exit 1
    fi
    
    log_info "Python版本检查通过: ${PYTHON_VERSION}"
}

# 检查模型文件
check_models() {
    log_info "检查模型目录..."
    
    # 创建模型缓存目录
    mkdir -p ${MODEL_DIR}/{embedding,reranker,text-generation}
    
    # 设置模型目录权限
    chmod -R 755 ${MODEL_DIR}
    
    # 检查appuser是否存在
    if id -u appuser >/dev/null 2>&1; then
        chown -R appuser:appuser ${MODEL_DIR}
    fi
    
    log_info "模型目录已准备好"
}

# 清理临时文件
cleanup() {
    log_info "清理临时文件..."
    
    # 删除临时文件
    find /tmp -name "rag_temp_*" -type f -mtime +1 -delete 2>/dev/null || true
    
    log_info "清理完成"
}

# 主函数
main() {
    log_info "开始初始化索克生活APP RAG服务..."
    
    check_permissions "$1"
    create_directories
    set_ownership
    check_config
    check_python
    check_models
    cleanup
    
    log_info "索克生活APP RAG服务初始化完成"
    log_info "应用目录: ${APP_DIR}"
    log_info "配置文件: ${CONFIG_DIR}/rag-config.json"
    log_info "数据目录: ${DATA_DIR}"
    log_info "模型目录: ${MODEL_DIR}"
    log_info "日志目录: ${LOG_DIR}"
}

# 执行主函数
main "$1" 