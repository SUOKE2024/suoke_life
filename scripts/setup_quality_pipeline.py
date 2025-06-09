#!/usr/bin/env python3
"""
代码质量检查流水线设置脚本
建立自动化代码质量检查和修复流程
"""

import os
import subprocess
import json
from pathlib import Path

class QualityPipelineSetup:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        
    def setup_pipeline(self):
        """设置完整的代码质量流水线"""
        print("🔧 设置代码质量检查流水线...")
        
        # 1. 创建pre-commit配置
        self.setup_precommit_hooks()
        
        # 2. 创建代码质量检查脚本
        self.create_quality_check_script()
        
        # 3. 创建自动修复脚本
        self.create_auto_fix_script()
        
        # 4. 设置GitHub Actions工作流
        self.setup_github_actions()
        
        # 5. 创建代码质量配置文件
        self.create_quality_configs()
        
        print("✅ 代码质量流水线设置完成!")
    
    def setup_precommit_hooks(self):
        """设置pre-commit钩子"""
        print("📋 设置pre-commit钩子...")
        
        precommit_config = """
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      - id: debug-statements
      
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.44.0
    hooks:
      - id: eslint
        files: \\.(js|jsx|ts|tsx)$
        types: [file]
"""
        
        with open(self.project_root / ".pre-commit-config.yaml", "w") as f:
            f.write(precommit_config)
        
        print("✅ pre-commit配置已创建")
    
    def create_quality_check_script(self):
        """创建代码质量检查脚本"""
        print("🔍 创建代码质量检查脚本...")
        
        quality_script = '''#!/bin/bash
# 代码质量检查脚本

echo "🔍 开始代码质量检查..."

# Python代码检查
echo "🐍 检查Python代码..."
find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" | head -10 | xargs python3 -m py_compile

# TypeScript代码检查
echo "📝 检查TypeScript代码..."
if command -v npx &> /dev/null; then
    npx tsc --noEmit --skipLibCheck
fi

# ESLint检查
echo "🔧 运行ESLint..."
if command -v npx &> /dev/null; then
    npx eslint src/ --ext .ts,.tsx,.js,.jsx --max-warnings 0 || echo "⚠️ ESLint发现问题"
fi

# 检查包依赖
echo "📦 检查包依赖..."
npm audit --audit-level moderate || echo "⚠️ 发现安全漏洞"

echo "✅ 代码质量检查完成"
'''
        
        script_path = self.project_root / "scripts" / "check_quality.sh"
        with open(script_path, "w") as f:
            f.write(quality_script)
        
        # 设置执行权限
        os.chmod(script_path, 0o755)
        
        print("✅ 代码质量检查脚本已创建")
    
    def create_auto_fix_script(self):
        """创建自动修复脚本"""
        print("🔧 创建自动修复脚本...")
        
        auto_fix_script = '''#!/bin/bash
# 自动修复脚本

echo "🔧 开始自动修复..."

# 修复Python代码格式
echo "🐍 修复Python代码格式..."
if command -v black &> /dev/null; then
    find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" | head -20 | xargs black
fi

if command -v isort &> /dev/null; then
    find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" | head -20 | xargs isort
fi

# 修复TypeScript/JavaScript代码格式
echo "📝 修复TypeScript代码格式..."
if command -v npx &> /dev/null; then
    npx prettier --write "src/**/*.{ts,tsx,js,jsx}" || echo "⚠️ Prettier修复失败"
fi

# 修复ESLint问题
echo "🔧 修复ESLint问题..."
if command -v npx &> /dev/null; then
    npx eslint src/ --ext .ts,.tsx,.js,.jsx --fix || echo "⚠️ ESLint自动修复失败"
fi

echo "✅ 自动修复完成"
'''
        
        script_path = self.project_root / "scripts" / "auto_fix.sh"
        with open(script_path, "w") as f:
            f.write(auto_fix_script)
        
        # 设置执行权限
        os.chmod(script_path, 0o755)
        
        print("✅ 自动修复脚本已创建")
    
    def setup_github_actions(self):
        """设置GitHub Actions工作流"""
        print("🚀 设置GitHub Actions工作流...")
        
        # 创建.github/workflows目录
        workflows_dir = self.project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # 代码质量检查工作流
        quality_workflow = """
name: Code Quality Check

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install black isort flake8 mypy
        
    - name: Install Node dependencies
      run: npm ci
      
    - name: Run Python quality checks
      run: |
        black --check --diff .
        isort --check-only --diff .
        flake8 .
        
    - name: Run TypeScript quality checks
      run: |
        npm run lint
        npm run type-check
        
    - name: Run tests
      run: |
        npm test
"""
        
        with open(workflows_dir / "quality-check.yml", "w") as f:
            f.write(quality_workflow)
        
        print("✅ GitHub Actions工作流已创建")
    
    def create_quality_configs(self):
        """创建代码质量配置文件"""
        print("⚙️ 创建代码质量配置文件...")
        
        # flake8配置
        flake8_config = """
[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
exclude = 
    .git,
    __pycache__,
    venv,
    .venv,
    migrations,
    node_modules
"""
        
        with open(self.project_root / ".flake8", "w") as f:
            f.write(flake8_config)
        
        # mypy配置
        mypy_config = """
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
ignore_missing_imports = True

[mypy-tests.*]
disallow_untyped_defs = False
"""
        
        with open(self.project_root / "mypy.ini", "w") as f:
            f.write(mypy_config)
        
        # prettier配置
        prettier_config = {
            "semi": True,
            "trailingComma": "es5",
            "singleQuote": True,
            "printWidth": 80,
            "tabWidth": 2,
            "useTabs": False
        }
        
        with open(self.project_root / ".prettierrc", "w") as f:
            json.dump(prettier_config, f, indent=2)
        
        # ESLint配置更新
        eslint_config = {
            "extends": [
                "@react-native-community",
                "prettier"
            ],
            "rules": {
                "prettier/prettier": "error",
                "@typescript-eslint/no-unused-vars": "error",
                "react-hooks/exhaustive-deps": "warn"
            },
            "plugins": ["prettier"]
        }
        
        with open(self.project_root / ".eslintrc.js", "w") as f:
            f.write(f"module.exports = {json.dumps(eslint_config, indent=2)};")
        
        print("✅ 代码质量配置文件已创建")

def main():
    """主函数"""
    project_root = os.getcwd()
    
    print("🚀 开始设置代码质量检查流水线...")
    
    setup = QualityPipelineSetup(project_root)
    setup.setup_pipeline()
    
    print("\n📋 下一步操作:")
    print("1. 运行: chmod +x scripts/*.sh")
    print("2. 运行: ./scripts/check_quality.sh")
    print("3. 运行: ./scripts/auto_fix.sh")
    print("4. 提交代码时会自动运行质量检查")

if __name__ == "__main__":
    main() 