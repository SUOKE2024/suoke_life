#!/bin/bash

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 检查脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(cd "$SCRIPT_DIR/../../" && pwd)"
echo -e "${YELLOW}正在验证 auth-service GitOps 配置...${NC}"
echo "服务目录: $SERVICE_DIR"

# 检查K8S配置
echo -e "\n${YELLOW}检查 Kubernetes 配置文件...${NC}"
if [ -f "$SERVICE_DIR/k8s/argocd-app.yaml" ]; then
  echo -e "${GREEN}✓ ArgoCD 应用配置文件存在${NC}"
  
  # 检查 ArgoCD 配置指向 GitHub
  REPO_URL=$(grep "repoURL" "$SERVICE_DIR/k8s/argocd-app.yaml" | grep -o "'.*'" | tr -d "'")
  if [[ $REPO_URL == *"github.com"* ]]; then
    echo -e "${GREEN}✓ ArgoCD 配置指向 GitHub 仓库: $REPO_URL${NC}"
  else
    echo -e "${RED}✗ ArgoCD 配置未指向 GitHub 仓库: $REPO_URL${NC}"
  fi
else
  echo -e "${RED}✗ ArgoCD 应用配置文件不存在${NC}"
fi

# 检查镜像标签配置
echo -e "\n${YELLOW}检查镜像标签配置...${NC}"
if [ -f "$SERVICE_DIR/k8s/overlays/prod/kustomization.yaml" ]; then
  echo -e "${GREEN}✓ 生产环境 kustomization 配置存在${NC}"
  
  IMAGE_TAG=$(grep "newTag" "$SERVICE_DIR/k8s/overlays/prod/kustomization.yaml" | awk '{print $2}')
  echo -e "当前生产环境镜像标签: ${GREEN}$IMAGE_TAG${NC}"
else
  echo -e "${RED}✗ 生产环境 kustomization 配置不存在${NC}"
fi

# 检查CI/CD工作流配置
echo -e "\n${YELLOW}检查 CI/CD 工作流配置...${NC}"
if [ -f "$SERVICE_DIR/.github/workflows/ci-cd.yml" ]; then
  echo -e "${GREEN}✓ GitHub Actions工作流配置存在${NC}"
  
  # 检查是否配置了latest标签设置
  if grep -q "latest标签" "$SERVICE_DIR/.github/workflows/ci-cd.yml"; then
    echo -e "${GREEN}✓ CI/CD 工作流已配置镜像latest标签管理${NC}"
  else
    echo -e "${YELLOW}! CI/CD 工作流未配置镜像latest标签管理${NC}"
  fi
  
  # 检查是否配置了ArgoCD同步
  if grep -q "ArgoCD" "$SERVICE_DIR/.github/workflows/ci-cd.yml"; then
    echo -e "${GREEN}✓ CI/CD 工作流已配置 ArgoCD 同步${NC}"
  else
    echo -e "${YELLOW}! CI/CD 工作流未配置 ArgoCD 同步${NC}"
  fi
else
  echo -e "${RED}✗ GitHub Actions工作流配置不存在${NC}"
fi

# 检查脚本支持情况
echo -e "\n${YELLOW}检查镜像管理脚本...${NC}"
if [ -f "$SERVICE_DIR/scripts/aliyun-cr.sh" ]; then
  echo -e "${GREEN}✓ 阿里云容器镜像仓库管理脚本存在${NC}"
  
  # 检查脚本是否可执行
  if [ -x "$SERVICE_DIR/scripts/aliyun-cr.sh" ]; then
    echo -e "${GREEN}✓ 脚本具有执行权限${NC}"
  else
    echo -e "${RED}✗ 脚本缺少执行权限${NC}"
    echo "建议执行: chmod +x $SERVICE_DIR/scripts/aliyun-cr.sh"
  fi
  
  # 检查脚本是否支持标签管理功能
  if grep -q "copy-tag" "$SERVICE_DIR/scripts/aliyun-cr.sh"; then
    echo -e "${GREEN}✓ 脚本支持标签复制功能${NC}"
  else
    echo -e "${RED}✗ 脚本不支持标签复制功能${NC}"
  fi
else
  echo -e "${RED}✗ 阿里云容器镜像仓库管理脚本不存在${NC}"
fi

# 检查package.json配置
echo -e "\n${YELLOW}检查 package.json 配置...${NC}"
if [ -f "$SERVICE_DIR/package.json" ]; then
  echo -e "${GREEN}✓ package.json 文件存在${NC}"
  
  # 检查是否包含镜像管理命令
  if grep -q "image:copy-tag" "$SERVICE_DIR/package.json"; then
    echo -e "${GREEN}✓ package.json 包含镜像标签管理命令${NC}"
  else
    echo -e "${RED}✗ package.json 缺少镜像标签管理命令${NC}"
  fi
else
  echo -e "${RED}✗ package.json 文件不存在${NC}"
fi

echo -e "\n${YELLOW}验证结束${NC}"