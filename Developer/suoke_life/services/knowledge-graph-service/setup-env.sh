#!/bin/bash
set -e

# 配置文件路径
ENV_EXAMPLE=".env.example"
ENV_FILE=".env"
CONFIG_DIR="config"
CONFIG_FILE="${CONFIG_DIR}/default.yaml"

echo "===== 开始自动配置环境 ====="

# 检查.env.example文件是否存在
if [ ! -f "$ENV_EXAMPLE" ]; then
  echo "错误：$ENV_EXAMPLE 文件不存在"
  exit 1
fi

# 创建配置目录
mkdir -p $CONFIG_DIR

# 复制.env.example到.env（如果不存在）
if [ ! -f "$ENV_FILE" ]; then
  echo "创建 $ENV_FILE 文件..."
  cp $ENV_EXAMPLE $ENV_FILE
  echo "$ENV_FILE 文件创建成功"
else
  echo "$ENV_FILE 文件已存在，跳过创建"
fi

# 读取.env.example内容，创建配置文件
echo "生成 $CONFIG_FILE 配置文件..."

# 确保配置文件目录存在
mkdir -p $(dirname $CONFIG_FILE)

# 转换.env格式为YAML格式
cat $ENV_EXAMPLE | grep -v "^#" | grep -v "^$" | sed 's/=/:/' | sed 's/^/  /' > $CONFIG_FILE.tmp

# 添加YAML头部
echo "app:" > $CONFIG_FILE
cat $CONFIG_FILE.tmp >> $CONFIG_FILE
rm $CONFIG_FILE.tmp

echo "$CONFIG_FILE 配置文件生成成功"

# 检查并替换注册表凭据
echo "检查注册表凭据..."

# 从.env.example提取注册表凭据
REGISTRY_URL=$(grep "REGISTRY_URL" $ENV_EXAMPLE | cut -d '=' -f2)
REGISTRY_USERNAME=$(grep "REGISTRY_USERNAME" $ENV_EXAMPLE | cut -d '=' -f2)
REGISTRY_PASSWORD=$(grep "REGISTRY_PASSWORD" $ENV_EXAMPLE | cut -d '=' -f2)

# 检查登录阿里云容器镜像仓库
echo "登录阿里云容器镜像仓库..."
docker login --username $REGISTRY_USERNAME --password $REGISTRY_PASSWORD $REGISTRY_URL

echo "===== 环境配置完成 ====="
echo "配置文件已生成：$CONFIG_FILE"
echo "环境变量文件已设置：$ENV_FILE"
echo "注册表已登录：$REGISTRY_URL" 