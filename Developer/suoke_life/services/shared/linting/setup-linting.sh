#!/bin/bash
# 索克生活代码风格检查与格式化工具安装脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 目标服务
SERVICE_DIR=${1:-"."}
SERVICE_TYPE=${2:-"auto"}  # auto, node, python

echo -e "${BLUE}开始安装代码风格检查与格式化工具到: $SERVICE_DIR${NC}"

# 检测服务类型
if [ "$SERVICE_TYPE" == "auto" ]; then
  if [ -f "$SERVICE_DIR/package.json" ]; then
    SERVICE_TYPE="node"
    echo -e "${BLUE}检测到Node.js项目${NC}"
  elif [ -f "$SERVICE_DIR/requirements.txt" ]; then
    SERVICE_TYPE="python"
    echo -e "${BLUE}检测到Python项目${NC}"
  else
    echo -e "${RED}无法自动检测项目类型，请手动指定 node 或 python${NC}"
    exit 1
  fi
fi

# 设置源文件目录
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

# 安装TypeScript项目的代码检查工具
install_node_linting() {
  echo -e "${BLUE}安装TypeScript代码风格检查与格式化工具...${NC}"
  
  cd "$SERVICE_DIR"
  
  # 复制配置文件
  echo -e "${BLUE}复制ESLint和Prettier配置文件...${NC}"
  cp "$SCRIPT_DIR/.eslintrc.js" .eslintrc.js
  cp "$SCRIPT_DIR/.prettierrc" .prettierrc
  cp "$SCRIPT_DIR/.editorconfig" .editorconfig
  
  # 安装依赖
  echo -e "${BLUE}安装依赖包...${NC}"
  npm install --save-dev eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint-config-prettier eslint-plugin-import eslint-plugin-prettier prettier
  
  # 添加脚本到package.json
  if [ -f "package.json" ]; then
    if command -v jq >/dev/null 2>&1; then
      # 使用jq添加脚本
      echo -e "${BLUE}添加lint脚本到package.json...${NC}"
      TMP_FILE=$(mktemp)
      jq '.scripts.lint = "eslint \"{src,apps,libs,test}/**/*.ts\" --fix"' package.json > "$TMP_FILE"
      jq '.scripts.format = "prettier --write \"{src,apps,libs,test}/**/*.ts\""' "$TMP_FILE" > package.json
      rm "$TMP_FILE"
    else
      echo -e "${YELLOW}未安装jq工具，无法自动更新package.json，请手动添加以下脚本:${NC}"
      echo -e '"lint": "eslint \\"{src,apps,libs,test}/**/*.ts\\" --fix",'
      echo -e '"format": "prettier --write \\"{src,apps,libs,test}/**/*.ts\\""'
    fi
  else
    echo -e "${RED}未找到package.json文件${NC}"
  fi
  
  # 创建Git钩子目录
  echo -e "${BLUE}设置Git钩子...${NC}"
  mkdir -p .husky
  
  # 添加Git钩子
  cat > .husky/pre-commit << 'EOF'
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

npm run lint
npm run format
EOF
  
  chmod +x .husky/pre-commit
  
  echo -e "${GREEN}✅ TypeScript代码检查工具安装完成${NC}"
}

# 安装Python项目的代码检查工具
install_python_linting() {
  echo -e "${BLUE}安装Python代码风格检查与格式化工具...${NC}"
  
  cd "$SERVICE_DIR"
  
  # 复制配置文件
  echo -e "${BLUE}复制Pylint和EditorConfig配置文件...${NC}"
  cp "$SCRIPT_DIR/.pylintrc" .pylintrc
  cp "$SCRIPT_DIR/.editorconfig" .editorconfig
  
  # 添加black配置
  cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 100
target-version = ['py38']
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
  | venv
)/
'''

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
EOF
  
  # 添加到requirements-dev.txt
  if [ -f "requirements-dev.txt" ]; then
    echo -e "${BLUE}添加代码检查工具到requirements-dev.txt...${NC}"
    cat >> requirements-dev.txt << 'EOF'

# 代码质量工具
pylint==2.15.5
black==22.10.0
isort==5.10.1
mypy==0.991
pre-commit==2.20.0
EOF
  else
    echo -e "${BLUE}创建requirements-dev.txt...${NC}"
    cat > requirements-dev.txt << 'EOF'
# 开发依赖

# 代码质量工具
pylint==2.15.5
black==22.10.0
isort==5.10.1
mypy==0.991
pre-commit==2.20.0
EOF
  fi
  
  # 创建pre-commit配置
  echo -e "${BLUE}创建pre-commit配置...${NC}"
  cat > .pre-commit-config.yaml << 'EOF'
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.3.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
    -   id: isort

-   repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
    -   id: black

-   repo: https://github.com/pycqa/flake8
    rev: 5.0.4
    hooks:
    -   id: flake8
        additional_dependencies: [
            'flake8-docstrings==1.6.0',
            'flake8-quotes==3.3.1',
        ]
EOF
  
  echo -e "${GREEN}✅ Python代码检查工具安装完成${NC}"
  echo -e "${YELLOW}请运行以下命令安装开发依赖:${NC}"
  echo -e "pip install -r requirements-dev.txt"
  echo -e "pre-commit install"
}

# 根据服务类型安装相应工具
if [ "$SERVICE_TYPE" == "node" ]; then
  install_node_linting
elif [ "$SERVICE_TYPE" == "python" ]; then
  install_python_linting
else
  echo -e "${RED}不支持的项目类型: $SERVICE_TYPE${NC}"
  exit 1
fi

echo -e "${GREEN}✅ 代码风格检查与格式化工具安装完成！${NC}"