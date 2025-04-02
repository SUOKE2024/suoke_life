#!/bin/bash
# 索克生活Docker镜像优化分析工具
# 此脚本分析Dockerfile并提供精简优化建议

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 检查参数
if [ "$#" -lt 1 ]; then
  echo "用法: $0 <Dockerfile路径> [输出报告路径]"
  exit 1
fi

DOCKERFILE_PATH="$1"
REPORT_PATH="${2:-./dockerfile-optimization-report.md}"

# 检查Dockerfile是否存在
if [ ! -f "$DOCKERFILE_PATH" ]; then
  echo -e "${RED}错误: Dockerfile不存在: $DOCKERFILE_PATH${NC}"
  exit 1
fi

echo -e "${BLUE}分析Dockerfile: $DOCKERFILE_PATH${NC}"

# 初始化报告
echo "# Dockerfile优化分析报告" > "$REPORT_PATH"
echo "" >> "$REPORT_PATH"
echo "分析时间: $(date)" >> "$REPORT_PATH"
echo "分析文件: \`$DOCKERFILE_PATH\`" >> "$REPORT_PATH"
echo "" >> "$REPORT_PATH"

# 分析基础镜像
BASE_IMAGE=$(grep -E "^FROM" "$DOCKERFILE_PATH" | head -1 | awk '{print $2}')
echo -e "${BLUE}检查基础镜像: $BASE_IMAGE${NC}"

echo "## 基础镜像分析" >> "$REPORT_PATH"
echo "" >> "$REPORT_PATH"
echo "当前基础镜像: \`$BASE_IMAGE\`" >> "$REPORT_PATH"
echo "" >> "$REPORT_PATH"

# 判断基础镜像类型并提供建议
if [[ "$BASE_IMAGE" == *"node"* ]]; then
  echo "### Node.js基础镜像建议" >> "$REPORT_PATH"
  
  if [[ "$BASE_IMAGE" == *"alpine"* ]]; then
    echo -e "${GREEN}✓ 使用了Alpine版本的Node.js镜像，这是一个好的实践${NC}"
    echo "✅ 已使用Alpine版本的Node.js镜像，这是轻量级的选择" >> "$REPORT_PATH"
  else
    echo -e "${YELLOW}! 考虑使用Alpine版本的Node.js镜像减小体积${NC}"
    echo "⚠️ 建议替换为Alpine版本的Node.js镜像:" >> "$REPORT_PATH"
    echo "\`\`\`dockerfile" >> "$REPORT_PATH"
    echo "FROM node:18-alpine # 替代 $BASE_IMAGE" >> "$REPORT_PATH"
    echo "\`\`\`" >> "$REPORT_PATH"
  fi
  
  echo "其他建议:" >> "$REPORT_PATH"
  echo "- 考虑使用特定版本标签而非 \`latest\` 以确保一致性" >> "$REPORT_PATH"
  echo "- 对于生产环境，考虑使用 \`node:18-alpine3.16\` 这样的精确版本" >> "$REPORT_PATH"
elif [[ "$BASE_IMAGE" == *"python"* ]]; then
  echo "### Python基础镜像建议" >> "$REPORT_PATH"
  
  if [[ "$BASE_IMAGE" == *"slim"* || "$BASE_IMAGE" == *"alpine"* ]]; then
    echo -e "${GREEN}✓ 使用了轻量级Python镜像，这是一个好的实践${NC}"
    echo "✅ 已使用轻量级Python镜像" >> "$REPORT_PATH"
  else
    echo -e "${YELLOW}! 考虑使用slim或alpine版本的Python镜像减小体积${NC}"
    echo "⚠️ 建议替换为轻量级Python镜像:" >> "$REPORT_PATH"
    echo "\`\`\`dockerfile" >> "$REPORT_PATH"
    echo "FROM python:3.10-slim # 替代 $BASE_IMAGE" >> "$REPORT_PATH"
    echo "\`\`\`" >> "$REPORT_PATH"
    echo "注意: 如果使用Alpine版本，某些需要编译的包可能需要额外的构建依赖" >> "$REPORT_PATH"
  fi
else
  echo -e "${YELLOW}! 基础镜像分析: 未识别的基础镜像类型${NC}"
  echo "⚠️ 未识别的基础镜像类型。通用建议:" >> "$REPORT_PATH"
  echo "- 考虑使用官方轻量级镜像版本（如Alpine或slim变体）" >> "$REPORT_PATH"
  echo "- 使用特定版本标签而非 \`latest\`" >> "$REPORT_PATH"
  echo "- 评估使用distroless镜像的可能性" >> "$REPORT_PATH"
fi

echo "" >> "$REPORT_PATH"

# 检查多阶段构建
if grep -q "FROM.*AS" "$DOCKERFILE_PATH"; then
  echo -e "${GREEN}✓ 使用了多阶段构建，这是一个好的实践${NC}"
  echo "## 多阶段构建" >> "$REPORT_PATH"
  echo "✅ 已使用多阶段构建，这有助于减小最终镜像大小" >> "$REPORT_PATH"
else
  echo -e "${YELLOW}! 未检测到多阶段构建${NC}"
  echo "## 多阶段构建" >> "$REPORT_PATH"
  echo "⚠️ 未检测到多阶段构建。建议实施多阶段构建以减小镜像大小:" >> "$REPORT_PATH"
  
  if [[ "$BASE_IMAGE" == *"node"* ]]; then
    echo "\`\`\`dockerfile" >> "$REPORT_PATH"
    echo "# 构建阶段" >> "$REPORT_PATH"
    echo "FROM node:18-alpine AS builder" >> "$REPORT_PATH"
    echo "WORKDIR /app" >> "$REPORT_PATH"
    echo "COPY package*.json ./" >> "$REPORT_PATH"
    echo "RUN npm ci" >> "$REPORT_PATH"
    echo "COPY . ." >> "$REPORT_PATH"
    echo "RUN npm run build" >> "$REPORT_PATH"
    echo "" >> "$REPORT_PATH"
    echo "# 生产阶段" >> "$REPORT_PATH"
    echo "FROM node:18-alpine" >> "$REPORT_PATH"
    echo "WORKDIR /app" >> "$REPORT_PATH"
    echo "COPY --from=builder /app/dist /app/dist" >> "$REPORT_PATH"
    echo "COPY --from=builder /app/package*.json ./" >> "$REPORT_PATH"
    echo "RUN npm ci --only=production" >> "$REPORT_PATH"
    echo "# 其余步骤..." >> "$REPORT_PATH"
    echo "\`\`\`" >> "$REPORT_PATH"
  elif [[ "$BASE_IMAGE" == *"python"* ]]; then
    echo "\`\`\`dockerfile" >> "$REPORT_PATH"
    echo "# 构建阶段" >> "$REPORT_PATH"
    echo "FROM python:3.10-slim AS builder" >> "$REPORT_PATH"
    echo "WORKDIR /app" >> "$REPORT_PATH"
    echo "COPY requirements.txt ." >> "$REPORT_PATH"
    echo "RUN pip install --user -r requirements.txt" >> "$REPORT_PATH"
    echo "COPY . ." >> "$REPORT_PATH"
    echo "" >> "$REPORT_PATH"
    echo "# 生产阶段" >> "$REPORT_PATH"
    echo "FROM python:3.10-slim" >> "$REPORT_PATH"
    echo "WORKDIR /app" >> "$REPORT_PATH"
    echo "COPY --from=builder /root/.local /root/.local" >> "$REPORT_PATH"
    echo "COPY --from=builder /app ." >> "$REPORT_PATH"
    echo "ENV PATH=/root/.local/bin:$PATH" >> "$REPORT_PATH"
    echo "# 其余步骤..." >> "$REPORT_PATH"
    echo "\`\`\`" >> "$REPORT_PATH"
  else
    echo "为您的具体语言和框架实施多阶段构建，将构建工具和依赖与运行时环境分离。" >> "$REPORT_PATH"
  fi
fi

echo "" >> "$REPORT_PATH"

# 检查层优化
echo -e "${BLUE}分析层优化...${NC}"
echo "## 层优化分析" >> "$REPORT_PATH"

# 检查RUN指令合并
RUN_COUNT=$(grep -c "^RUN" "$DOCKERFILE_PATH" || echo "0")
if [ "$RUN_COUNT" -gt 3 ]; then
  echo -e "${YELLOW}! 发现多个RUN指令 ($RUN_COUNT)，考虑合并以减少层数${NC}"
  echo "⚠️ 检测到 $RUN_COUNT 个RUN指令。考虑合并RUN命令以减少层数:" >> "$REPORT_PATH"
  echo "\`\`\`dockerfile" >> "$REPORT_PATH"
  echo "# 替代多个RUN指令" >> "$REPORT_PATH"
  echo "RUN command1 \\" >> "$REPORT_PATH"
  echo "    && command2 \\" >> "$REPORT_PATH"
  echo "    && command3" >> "$REPORT_PATH"
  echo "\`\`\`" >> "$REPORT_PATH"
else
  echo -e "${GREEN}✓ RUN指令数量合理 ($RUN_COUNT)${NC}"
  echo "✅ RUN指令数量合理 ($RUN_COUNT)" >> "$REPORT_PATH"
fi

# 检查COPY指令
COPY_COUNT=$(grep -c "^COPY" "$DOCKERFILE_PATH" || echo "0")
echo -e "${BLUE}检查COPY指令 ($COPY_COUNT)${NC}"

if [ "$COPY_COUNT" -gt 0 ]; then
  # 检查.dockerignore文件
  DOCKERFILE_DIR=$(dirname "$DOCKERFILE_PATH")
  DOCKERIGNORE_PATH="$DOCKERFILE_DIR/.dockerignore"
  
  if [ -f "$DOCKERIGNORE_PATH" ]; then
    echo -e "${GREEN}✓ 使用了.dockerignore文件${NC}"
    echo "✅ 已使用.dockerignore文件控制构建上下文" >> "$REPORT_PATH"
  else
    echo -e "${YELLOW}! 未发现.dockerignore文件${NC}"
    echo "⚠️ 未发现.dockerignore文件。建议创建以排除不必要文件:" >> "$REPORT_PATH"
    echo "\`\`\`" >> "$REPORT_PATH"
    if [[ "$BASE_IMAGE" == *"node"* ]]; then
      echo "node_modules" >> "$REPORT_PATH"
      echo "npm-debug.log" >> "$REPORT_PATH"
      echo ".git" >> "$REPORT_PATH"
      echo ".github" >> "$REPORT_PATH"
      echo ".vscode" >> "$REPORT_PATH"
      echo "*.md" >> "$REPORT_PATH"
      echo "tests" >> "$REPORT_PATH"
      echo "docs" >> "$REPORT_PATH"
    elif [[ "$BASE_IMAGE" == *"python"* ]]; then
      echo "__pycache__" >> "$REPORT_PATH"
      echo "*.pyc" >> "$REPORT_PATH"
      echo "*.pyo" >> "$REPORT_PATH"
      echo "*.pyd" >> "$REPORT_PATH"
      echo ".Python" >> "$REPORT_PATH"
      echo "env/" >> "$REPORT_PATH"
      echo "venv/" >> "$REPORT_PATH"
      echo ".git" >> "$REPORT_PATH"
      echo ".github" >> "$REPORT_PATH"
      echo "tests/" >> "$REPORT_PATH"
      echo "docs/" >> "$REPORT_PATH"
    else
      echo ".git" >> "$REPORT_PATH"
      echo ".github" >> "$REPORT_PATH"
      echo ".vscode" >> "$REPORT_PATH"
      echo "*.md" >> "$REPORT_PATH"
      echo "tests/" >> "$REPORT_PATH"
      echo "docs/" >> "$REPORT_PATH"
    fi
    echo "\`\`\`" >> "$REPORT_PATH"
  fi
fi

echo "" >> "$REPORT_PATH"

# 检查包管理器缓存清理
if [[ "$BASE_IMAGE" == *"node"* ]]; then
  if grep -q "npm cache clean" "$DOCKERFILE_PATH" || grep -q "rm -rf /root/.npm" "$DOCKERFILE_PATH"; then
    echo -e "${GREEN}✓ 清理了npm缓存${NC}"
    echo "✅ 已清理npm缓存" >> "$REPORT_PATH"
  else
    echo -e "${YELLOW}! 未检测到npm缓存清理${NC}"
    echo "⚠️ 建议清理npm缓存以减小镜像大小:" >> "$REPORT_PATH"
    echo "\`\`\`dockerfile" >> "$REPORT_PATH"
    echo "RUN npm ci \\" >> "$REPORT_PATH"
    echo "    && npm cache clean --force" >> "$REPORT_PATH"
    echo "\`\`\`" >> "$REPORT_PATH"
  fi
elif [[ "$BASE_IMAGE" == *"python"* ]]; then
  if grep -q "pip cache purge" "$DOCKERFILE_PATH" || grep -q "rm -rf /root/.cache/pip" "$DOCKERFILE_PATH"; then
    echo -e "${GREEN}✓ 清理了pip缓存${NC}"
    echo "✅ 已清理pip缓存" >> "$REPORT_PATH"
  else
    echo -e "${YELLOW}! 未检测到pip缓存清理${NC}"
    echo "⚠️ 建议清理pip缓存以减小镜像大小:" >> "$REPORT_PATH"
    echo "\`\`\`dockerfile" >> "$REPORT_PATH"
    echo "RUN pip install -r requirements.txt \\" >> "$REPORT_PATH"
    echo "    && pip cache purge" >> "$REPORT_PATH"
    echo "\`\`\`" >> "$REPORT_PATH"
  fi
fi

# 检查系统包管理器缓存清理
if grep -q "apt-get" "$DOCKERFILE_PATH" && ! grep -q "apt-get clean" "$DOCKERFILE_PATH"; then
  echo -e "${YELLOW}! 使用apt-get但未清理缓存${NC}"
  echo "⚠️ 使用apt-get但未清理缓存。建议添加清理步骤:" >> "$REPORT_PATH"
  echo "\`\`\`dockerfile" >> "$REPORT_PATH"
  echo "RUN apt-get update \\" >> "$REPORT_PATH"
  echo "    && apt-get install -y --no-install-recommends <包名> \\" >> "$REPORT_PATH"
  echo "    && apt-get clean \\" >> "$REPORT_PATH"
  echo "    && rm -rf /var/lib/apt/lists/*" >> "$REPORT_PATH"
  echo "\`\`\`" >> "$REPORT_PATH"
fi

if grep -q "apk add" "$DOCKERFILE_PATH" && ! grep -q "apk cache clean" "$DOCKERFILE_PATH" && ! grep -q "apk add --no-cache" "$DOCKERFILE_PATH"; then
  echo -e "${YELLOW}! 使用apk但未使用--no-cache选项${NC}"
  echo "⚠️ 使用apk但未使用--no-cache选项。建议修改:" >> "$REPORT_PATH"
  echo "\`\`\`dockerfile" >> "$REPORT_PATH"
  echo "RUN apk add --no-cache <包名>" >> "$REPORT_PATH"
  echo "\`\`\`" >> "$REPORT_PATH"
fi

echo "" >> "$REPORT_PATH"

# 检查安全最佳实践
echo -e "${BLUE}分析安全最佳实践...${NC}"
echo "## 安全最佳实践" >> "$REPORT_PATH"

# 检查非root用户
if grep -q "USER" "$DOCKERFILE_PATH"; then
  echo -e "${GREEN}✓ 设置了非root用户${NC}"
  echo "✅ 已设置非root用户运行容器" >> "$REPORT_PATH"
else
  echo -e "${YELLOW}! 未设置非root用户${NC}"
  echo "⚠️ 建议设置非root用户运行容器:" >> "$REPORT_PATH"
  echo "\`\`\`dockerfile" >> "$REPORT_PATH"
  echo "# 创建非root用户" >> "$REPORT_PATH"
  if [[ "$BASE_IMAGE" == *"alpine"* ]]; then
    echo "RUN addgroup -S appgroup && adduser -S appuser -G appgroup" >> "$REPORT_PATH"
  else
    echo "RUN groupadd -r appgroup && useradd -r -g appgroup appuser" >> "$REPORT_PATH"
  fi
  echo "USER appuser" >> "$REPORT_PATH"
  echo "\`\`\`" >> "$REPORT_PATH"
fi

# 检查HEALTHCHECK
if grep -q "HEALTHCHECK" "$DOCKERFILE_PATH"; then
  echo -e "${GREEN}✓ 设置了健康检查${NC}"
  echo "✅ 已设置容器健康检查" >> "$REPORT_PATH"
else
  echo -e "${YELLOW}! 未设置健康检查${NC}"
  echo "⚠️ 建议添加容器健康检查:" >> "$REPORT_PATH"
  echo "\`\`\`dockerfile" >> "$REPORT_PATH"
  if [[ "$BASE_IMAGE" == *"node"* ]]; then
    echo "HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \\" >> "$REPORT_PATH"
    echo "  CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1" >> "$REPORT_PATH"
  elif [[ "$BASE_IMAGE" == *"python"* ]]; then
    echo "HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \\" >> "$REPORT_PATH"
    echo "  CMD curl -f http://localhost:8000/health || exit 1" >> "$REPORT_PATH"
  else
    echo "HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \\" >> "$REPORT_PATH"
    echo "  CMD curl -f http://localhost:<port>/health || exit 1" >> "$REPORT_PATH"
  fi
  echo "\`\`\`" >> "$REPORT_PATH"
fi

echo "" >> "$REPORT_PATH"

# 其他优化建议
echo "## 其他优化建议" >> "$REPORT_PATH"
echo "" >> "$REPORT_PATH"

# 生成总结和优化模板
echo "## 总结和优化模板" >> "$REPORT_PATH"
echo "" >> "$REPORT_PATH"
echo "根据分析结果，以下是优化后的Dockerfile模板:" >> "$REPORT_PATH"
echo "" >> "$REPORT_PATH"

if [[ "$BASE_IMAGE" == *"node"* ]]; then
  echo "\`\`\`dockerfile" >> "$REPORT_PATH"
  echo "# 构建阶段" >> "$REPORT_PATH"
  echo "FROM node:18-alpine AS builder" >> "$REPORT_PATH"
  echo "WORKDIR /app" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 首先复制依赖文件以利用缓存" >> "$REPORT_PATH"
  echo "COPY package*.json ./" >> "$REPORT_PATH"
  echo "RUN npm ci" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 复制源代码并构建" >> "$REPORT_PATH"
  echo "COPY . ." >> "$REPORT_PATH"
  echo "RUN npm run build \\" >> "$REPORT_PATH"
  echo "    && npm prune --production \\" >> "$REPORT_PATH"
  echo "    && npm cache clean --force" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 生产阶段" >> "$REPORT_PATH"
  echo "FROM node:18-alpine" >> "$REPORT_PATH"
  echo "WORKDIR /app" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 创建非root用户" >> "$REPORT_PATH"
  echo "RUN addgroup -S appgroup && adduser -S appuser -G appgroup" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 从构建阶段复制构建产物和依赖" >> "$REPORT_PATH"
  echo "COPY --from=builder /app/dist /app/dist" >> "$REPORT_PATH"
  echo "COPY --from=builder /app/node_modules /app/node_modules" >> "$REPORT_PATH"
  echo "COPY --from=builder /app/package*.json ./" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 设置环境变量" >> "$REPORT_PATH"
  echo "ENV NODE_ENV=production" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 切换到非root用户" >> "$REPORT_PATH"
  echo "USER appuser" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 健康检查" >> "$REPORT_PATH"
  echo "HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \\" >> "$REPORT_PATH"
  echo "  CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 暴露端口" >> "$REPORT_PATH"
  echo "EXPOSE 3000" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 启动命令" >> "$REPORT_PATH"
  echo "CMD [\"node\", \"dist/main.js\"]" >> "$REPORT_PATH"
  echo "\`\`\`" >> "$REPORT_PATH"
elif [[ "$BASE_IMAGE" == *"python"* ]]; then
  echo "\`\`\`dockerfile" >> "$REPORT_PATH"
  echo "# 构建阶段" >> "$REPORT_PATH"
  echo "FROM python:3.10-slim AS builder" >> "$REPORT_PATH"
  echo "WORKDIR /app" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 安装构建依赖" >> "$REPORT_PATH"
  echo "COPY requirements.txt ." >> "$REPORT_PATH"
  echo "RUN pip install --user --no-warn-script-location -r requirements.txt \\" >> "$REPORT_PATH"
  echo "    && pip cache purge" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 复制源代码" >> "$REPORT_PATH"
  echo "COPY . ." >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 生产阶段" >> "$REPORT_PATH"
  echo "FROM python:3.10-slim" >> "$REPORT_PATH"
  echo "WORKDIR /app" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 安装运行时依赖" >> "$REPORT_PATH"
  echo "RUN apt-get update \\" >> "$REPORT_PATH"
  echo "    && apt-get install -y --no-install-recommends curl \\" >> "$REPORT_PATH"
  echo "    && apt-get clean \\" >> "$REPORT_PATH"
  echo "    && rm -rf /var/lib/apt/lists/*" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 创建非root用户" >> "$REPORT_PATH"
  echo "RUN groupadd -r appgroup && useradd -r -g appgroup appuser" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 从构建阶段复制依赖和代码" >> "$REPORT_PATH"
  echo "COPY --from=builder /root/.local /home/appuser/.local" >> "$REPORT_PATH"
  echo "COPY --from=builder /app ." >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 设置路径和权限" >> "$REPORT_PATH"
  echo "ENV PATH=/home/appuser/.local/bin:$PATH" >> "$REPORT_PATH"
  echo "RUN chown -R appuser:appgroup /app" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 切换到非root用户" >> "$REPORT_PATH"
  echo "USER appuser" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 健康检查" >> "$REPORT_PATH"
  echo "HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \\" >> "$REPORT_PATH"
  echo "  CMD curl -f http://localhost:8000/health || exit 1" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 暴露端口" >> "$REPORT_PATH"
  echo "EXPOSE 8000" >> "$REPORT_PATH"
  echo "" >> "$REPORT_PATH"
  echo "# 启动命令" >> "$REPORT_PATH"
  echo "CMD [\"python\", \"main.py\"]" >> "$REPORT_PATH"
  echo "\`\`\`" >> "$REPORT_PATH"
else
  echo "请根据您的具体技术栈参考上述优化建议，创建符合最佳实践的Dockerfile。" >> "$REPORT_PATH"
fi

echo -e "${GREEN}✅ 分析完成！优化报告已保存至: $REPORT_PATH${NC}"
echo "查看完整的优化建议和Dockerfile模板。"