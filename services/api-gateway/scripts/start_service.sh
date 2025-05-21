#!/bin/bash

# 索克生活API网关服务启动脚本

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 切换到项目根目录
cd "$PROJECT_ROOT" || { echo "无法切换到项目根目录: $PROJECT_ROOT"; exit 1; }

# 设置默认配置文件路径
CONFIG_PATH=${CONFIG_PATH:-"$PROJECT_ROOT/config/config.yaml"}

# 如果配置文件不存在，给出警告
if [ ! -f "$CONFIG_PATH" ]; then
    echo "警告: 配置文件不存在: $CONFIG_PATH"
    echo "将使用默认配置"
fi

# 设置默认日志目录
LOGGING_DIR=${LOGGING_DIR:-"$PROJECT_ROOT/logs"}
mkdir -p "$LOGGING_DIR"

# 设置默认日志文件
LOGGING_FILE=${LOGGING_FILE:-"$LOGGING_DIR/api_gateway.log"}

# 设置日志级别
LOG_LEVEL=${LOG_LEVEL:-"INFO"}

# 检查是否在虚拟环境中运行
if [ -z "$VIRTUAL_ENV" ]; then
    echo "警告: 未检测到激活的Python虚拟环境"
    
    # 如果存在venv目录，尝试激活它
    if [ -d "$PROJECT_ROOT/venv" ]; then
        echo "检测到本地venv目录，尝试激活..."
        source "$PROJECT_ROOT/venv/bin/activate" || {
            echo "无法激活虚拟环境，但仍将继续..."
        }
    else
        echo "推荐在Python虚拟环境中运行服务"
        echo "可以使用以下命令创建和激活虚拟环境:"
        echo "  python -m venv venv"
        echo "  source venv/bin/activate  # Linux/Mac"
        echo "  venv\\Scripts\\activate     # Windows"
    fi
fi

# 输出启动信息
echo "启动索克生活API网关服务..."
echo "配置文件: $CONFIG_PATH"
echo "日志文件: $LOGGING_FILE"
echo "日志级别: $LOG_LEVEL"

# 设置环境变量
export CONFIG_PATH
export LOGGING_FILE
export LOG_LEVEL

# 启动服务
python -m cmd.server.main

# 捕获退出状态
EXIT_STATUS=$?

# 输出停止信息
if [ $EXIT_STATUS -eq 0 ]; then
    echo "API网关服务已正常停止"
else
    echo "API网关服务异常退出，退出码: $EXIT_STATUS"
fi

exit $EXIT_STATUS 