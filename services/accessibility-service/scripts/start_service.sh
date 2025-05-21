#!/bin/bash
# 索克生活无障碍服务启动脚本

# 设置环境变量
export PYTHONPATH=$PYTHONPATH:$(pwd)
export ACCESSIBILITY_CONFIG_PATH=${ACCESSIBILITY_CONFIG_PATH:-"$(pwd)/config/config.yaml"}

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 找不到python3，请确保已安装Python 3.10或更高版本"
    exit 1
fi

# 检查配置文件
if [ ! -f "$ACCESSIBILITY_CONFIG_PATH" ]; then
    echo "错误: 找不到配置文件 $ACCESSIBILITY_CONFIG_PATH"
    echo "请创建配置文件或指定正确的路径: ACCESSIBILITY_CONFIG_PATH=<path> $0"
    exit 1
fi

echo "=============================================="
echo "  启动索克生活无障碍服务"
echo "  配置文件: $ACCESSIBILITY_CONFIG_PATH"
echo "=============================================="

# 创建日志目录
LOG_DIR=${LOG_DIR:-"./logs"}
mkdir -p "$LOG_DIR" || {
    echo "无法创建日志目录: $LOG_DIR"
    echo "使用当前目录作为日志目录"
    LOG_DIR="."
}

echo "日志目录: $LOG_DIR"

# 检查依赖
echo "检查依赖..."
if ! python3 -c "import grpc, yaml, numpy" 2>/dev/null; then
    echo "缺少必要的依赖，正在安装..."
    pip3 install -r requirements.txt || {
        echo "安装依赖失败，请手动安装依赖: pip install -r requirements.txt"
        exit 1
    }
fi

# 启动服务
echo "正在启动无障碍服务..."
python3 cmd/server/main.py "$@" 2>&1 | tee -a "$LOG_DIR/service.log"

# 检查是否成功启动
if [ $? -ne 0 ]; then
    echo "服务启动失败，请检查错误信息"
    exit 1
fi

echo "服务已成功启动" 