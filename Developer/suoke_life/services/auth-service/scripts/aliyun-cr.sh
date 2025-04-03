#!/bin/bash
# 索克生活认证服务 - 阿里云容器仓库管理脚本

# 加载环境变量
if [ -f ".env" ]; then
  source .env
elif [ -f "../.env" ]; then
  source ../.env
elif [ -f "../../.env" ]; then
  source ../../.env
fi

# 阿里云容器仓库信息
REPO_NAMESPACE="suoke"
REPO_NAME="auth-service"
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"

# 列出所有镜像标签
list_tags() {
  echo "获取镜像标签列表..."
  aliyun cr GET /repos/$REPO_NAMESPACE/$REPO_NAME/tags 2>/dev/null || \
    docker images | grep "$REGISTRY/$REPO_NAMESPACE/$REPO_NAME"
}

# 删除指定标签
delete_tag() {
  if [ -z "$1" ]; then
    echo "请指定要删除的标签"
    exit 1
  fi
  
  echo "删除标签: $1"
  aliyun cr DELETE /repos/$REPO_NAMESPACE/$REPO_NAME/tags/$1 2>/dev/null || \
    echo "使用阿里云控制台删除: https://cr.console.aliyun.com/"
}

# 推送当前版本镜像
push_current() {
  GIT_SHA=$(git rev-parse --short HEAD)
  echo "正在推送镜像: sha-$GIT_SHA"
  
  # 标记镜像
  docker tag $REGISTRY/$REPO_NAMESPACE/$REPO_NAME:dev \
    $REGISTRY/$REPO_NAMESPACE/$REPO_NAME:sha-$GIT_SHA
  
  # 推送镜像
  docker push $REGISTRY/$REPO_NAMESPACE/$REPO_NAME:sha-$GIT_SHA
  
  echo "已成功推送镜像: $REGISTRY/$REPO_NAMESPACE/$REPO_NAME:sha-$GIT_SHA"
}

# 使用方法
usage() {
  echo "用法: $0 {list|delete <标签>|push}"
  echo "  list              - 列出所有标签"
  echo "  delete <标签>     - 删除指定标签"
  echo "  push              - 推送当前版本"
  exit 1
}

# 命令分发
case "$1" in
  list)
    list_tags
    ;;
  delete)
    delete_tag $2
    ;;
  push)
    push_current
    ;;
  *)
    usage
    ;;
esac 