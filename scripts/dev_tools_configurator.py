#!/usr/bin/env python3
"""
索克生活项目开发工具配置器
配置ESLint、Prettier、pre-commit hooks等开发工具
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List

class DevToolsConfigurator:
    def __init__(self):
        self.project_root = Path.cwd()
        self.configs_created = []
        
    def execute_dev_tools_setup(self):
        """执行开发工具配置"""
        print('🚀 启动开发工具配置器...')
        print('=' * 80)
        
        # 1. 配置ESLint
        self._configure_eslint()
        
        # 2. 配置Prettier
        self._configure_prettier()
        
        # 3. 配置pre-commit hooks
        self._configure_precommit_hooks()
        
        # 4. 配置VS Code设置
        self._configure_vscode()
        
        # 5. 生成报告
        self._generate_report()
        
        print('\n🎉 开发工具配置完成！')
        
    def _configure_eslint(self):
        """配置ESLint"""
        print('\n📋 配置ESLint...')
        print('-' * 50)
        
        # ESLint配置
        eslint_config = {
            "env": {
                "browser": True,
                "es2021": True,
                "react-native/react-native": True
            },
            "extends": [
                "eslint:recommended",
                "@typescript-eslint/recommended",
                "@react-native-community",
                "prettier"
            ],
            "parser": "@typescript-eslint/parser",
            "parserOptions": {
                "ecmaFeatures": {
                    "jsx": True
                },
                "ecmaVersion": 12,
                "sourceType": "module"
            },
            "plugins": [
                "react",
                "react-native",
                "@typescript-eslint",
                "prettier"
            ],
            "rules": {
                "prettier/prettier": "error",
                "@typescript-eslint/no-unused-vars": "warn",
                "@typescript-eslint/no-explicit-any": "warn",
                "react-native/no-unused-styles": "warn",
                "react-native/split-platform-components": "warn",
                "react-native/no-inline-styles": "warn",
                "react-native/no-color-literals": "warn",
                "react/jsx-uses-react": "off",
                "react/react-in-jsx-scope": "off",
                "no-console": "warn",
                "no-debugger": "error",
                "prefer-const": "error",
                "no-var": "error"
            },
            "settings": {
                "react": {
                    "version": "detect"
                }
            },
            "ignorePatterns": [
                "node_modules/",
                "android/",
                "ios/",
                "coverage/",
                "dist/",
                "build/"
            ]
        }
        
        # 保存ESLint配置
        with open(self.project_root / '.eslintrc.json', 'w', encoding='utf-8') as f:
            json.dump(eslint_config, f, indent=2)
            
        self.configs_created.append('.eslintrc.json')
        print('  ✅ ESLint配置已创建')
        
        # ESLint忽略文件
        eslint_ignore = """
# Dependencies
node_modules/

# Build outputs
android/
ios/
dist/
build/
coverage/

# Environment files
.env
.env.local
.env.production

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# nyc test coverage
.nyc_output

# Dependency directories
node_modules/
jspm_packages/

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env

# Metro bundler cache
.metro-cache/

# React Native packager cache
.react-native-packager-cache/

# Temporary folders
tmp/
temp/

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
"""
        
        with open(self.project_root / '.eslintignore', 'w', encoding='utf-8') as f:
            f.write(eslint_ignore.strip())
            
        self.configs_created.append('.eslintignore')
        print('  ✅ ESLint忽略文件已创建')
        
    def _configure_prettier(self):
        """配置Prettier"""
        print('\n📋 配置Prettier...')
        print('-' * 50)
        
        # Prettier配置
        prettier_config = {
            "semi": True,
            "trailingComma": "es5",
            "singleQuote": True,
            "printWidth": 80,
            "tabWidth": 2,
            "useTabs": False,
            "bracketSpacing": True,
            "bracketSameLine": False,
            "arrowParens": "avoid",
            "endOfLine": "lf",
            "quoteProps": "as-needed",
            "jsxSingleQuote": True,
            "proseWrap": "preserve"
        }
        
        # 保存Prettier配置
        with open(self.project_root / '.prettierrc.json', 'w', encoding='utf-8') as f:
            json.dump(prettier_config, f, indent=2)
            
        self.configs_created.append('.prettierrc.json')
        print('  ✅ Prettier配置已创建')
        
        # Prettier忽略文件
        prettier_ignore = """
# Dependencies
node_modules/

# Build outputs
android/
ios/
dist/
build/
coverage/

# Generated files
*.generated.*
*.min.js
*.min.css

# Package files
package-lock.json
yarn.lock

# Environment files
.env*

# Logs
*.log

# Metro bundler cache
.metro-cache/

# React Native packager cache
.react-native-packager-cache/

# IDE files
.vscode/
.idea/

# OS generated files
.DS_Store
Thumbs.db
"""
        
        with open(self.project_root / '.prettierignore', 'w', encoding='utf-8') as f:
            f.write(prettier_ignore.strip())
            
        self.configs_created.append('.prettierignore')
        print('  ✅ Prettier忽略文件已创建')
        
    def _configure_precommit_hooks(self):
        """配置pre-commit hooks"""
        print('\n📋 配置pre-commit hooks...')
        print('-' * 50)
        
        # Husky配置
        husky_config = {
            "hooks": {
                "pre-commit": "lint-staged",
                "commit-msg": "commitlint -E HUSKY_GIT_PARAMS"
            }
        }
        
        # lint-staged配置
        lint_staged_config = {
            "*.{ts,tsx,js,jsx}": [
                "eslint --fix",
                "prettier --write",
                "git add"
            ],
            "*.{json,md,yml,yaml}": [
                "prettier --write",
                "git add"
            ]
        }
        
        # 更新package.json
        package_json_path = self.project_root / 'package.json'
        if package_json_path.exists():
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                
            # 添加husky和lint-staged配置
            package_data['husky'] = husky_config
            package_data['lint-staged'] = lint_staged_config
            
            # 添加脚本
            if 'scripts' not in package_data:
                package_data['scripts'] = {}
                
            package_data['scripts'].update({
                "lint": "eslint src/ --ext .ts,.tsx,.js,.jsx",
                "lint:fix": "eslint src/ --ext .ts,.tsx,.js,.jsx --fix",
                "format": "prettier --write src/",
                "format:check": "prettier --check src/",
                "type-check": "tsc --noEmit",
                "pre-commit": "lint-staged"
            })
            
            with open(package_json_path, 'w', encoding='utf-8') as f:
                json.dump(package_data, f, indent=2, ensure_ascii=False)
                
            print('  ✅ package.json已更新')
            
        # commitlint配置
        commitlint_config = {
            "extends": ["@commitlint/config-conventional"],
            "rules": {
                "type-enum": [
                    2,
                    "always",
                    [
                        "feat",
                        "fix",
                        "docs",
                        "style",
                        "refactor",
                        "perf",
                        "test",
                        "chore",
                        "revert"
                    ]
                ],
                "subject-case": [2, "never", ["sentence-case", "start-case", "pascal-case", "upper-case"]],
                "subject-empty": [2, "never"],
                "subject-full-stop": [2, "never", "."],
                "header-max-length": [2, "always", 72]
            }
        }
        
        with open(self.project_root / 'commitlint.config.js', 'w', encoding='utf-8') as f:
            f.write(f'module.exports = {json.dumps(commitlint_config, indent=2)};')
            
        self.configs_created.append('commitlint.config.js')
        print('  ✅ commitlint配置已创建')
        
    def _configure_vscode(self):
        """配置VS Code设置"""
        print('\n📋 配置VS Code设置...')
        print('-' * 50)
        
        # 创建.vscode目录
        vscode_dir = self.project_root / '.vscode'
        vscode_dir.mkdir(exist_ok=True)
        
        # VS Code设置
        vscode_settings = {
            "editor.formatOnSave": True,
            "editor.defaultFormatter": "esbenp.prettier-vscode",
            "editor.codeActionsOnSave": {
                "source.fixAll.eslint": True,
                "source.organizeImports": True
            },
            "typescript.preferences.importModuleSpecifier": "relative",
            "typescript.suggest.autoImports": True,
            "emmet.includeLanguages": {
                "typescript": "typescriptreact",
                "javascript": "javascriptreact"
            },
            "files.associations": {
                "*.tsx": "typescriptreact",
                "*.ts": "typescript"
            },
            "search.exclude": {
                "**/node_modules": True,
                "**/android": True,
                "**/ios": True,
                "**/coverage": True,
                "**/dist": True,
                "**/build": True
            },
            "files.exclude": {
                "**/.git": True,
                "**/.DS_Store": True,
                "**/node_modules": True,
                "**/coverage": True
            }
        }
        
        with open(vscode_dir / 'settings.json', 'w', encoding='utf-8') as f:
            json.dump(vscode_settings, f, indent=2)
            
        # VS Code扩展推荐
        vscode_extensions = {
            "recommendations": [
                "esbenp.prettier-vscode",
                "dbaeumer.vscode-eslint",
                "ms-vscode.vscode-typescript-next",
                "bradlc.vscode-tailwindcss",
                "ms-vscode.vscode-json",
                "formulahendry.auto-rename-tag",
                "christian-kohler.path-intellisense",
                "ms-vscode.vscode-react-native"
            ]
        }
        
        with open(vscode_dir / 'extensions.json', 'w', encoding='utf-8') as f:
            json.dump(vscode_extensions, f, indent=2)
            
        self.configs_created.extend(['.vscode/settings.json', '.vscode/extensions.json'])
        print('  ✅ VS Code配置已创建')
        
    def _generate_report(self):
        """生成配置报告"""
        print('\n📊 生成开发工具配置报告...')
        
        report_content = f"""# 开发工具配置报告

## 配置概览

**配置时间**: {self._get_current_time()}  
**配置文件数**: {len(self.configs_created)}  
**配置类型**: ESLint, Prettier, pre-commit hooks, VS Code

---

## 配置文件列表

"""

        for config_file in self.configs_created:
            report_content += f"- ✅ {config_file}\n"
            
        report_content += f"""

---

## 配置详情

### ESLint配置
- **配置文件**: `.eslintrc.json`
- **忽略文件**: `.eslintignore`
- **功能**: TypeScript、React Native代码检查
- **规则**: 推荐规则 + 自定义规则

### Prettier配置
- **配置文件**: `.prettierrc.json`
- **忽略文件**: `.prettierignore`
- **功能**: 代码格式化
- **风格**: 单引号、分号、2空格缩进

### Pre-commit Hooks
- **工具**: Husky + lint-staged
- **功能**: 提交前自动检查和格式化
- **检查**: ESLint + Prettier + TypeScript

### VS Code配置
- **设置文件**: `.vscode/settings.json`
- **扩展推荐**: `.vscode/extensions.json`
- **功能**: 保存时自动格式化和修复

---

## 使用指南

### 1. 安装依赖
```bash
npm install --save-dev eslint prettier husky lint-staged @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

### 2. 初始化Husky
```bash
npx husky install
```

### 3. 运行代码检查
```bash
npm run lint          # 检查代码
npm run lint:fix      # 修复代码
npm run format        # 格式化代码
npm run type-check    # TypeScript检查
```

### 4. VS Code设置
1. 安装推荐扩展
2. 重启VS Code
3. 保存时自动格式化

---

## 下一步建议

1. **运行初始化**:
   ```bash
   npm install
   npx husky install
   ```

2. **测试配置**:
   ```bash
   npm run lint
   npm run format:check
   ```

3. **提交测试**:
   ```bash
   git add .
   git commit -m "feat: 配置开发工具"
   ```

---

**状态**: 开发工具配置完成  
**下一步**: 验证修复效果  
"""

        # 保存报告
        with open('DEV_TOOLS_CONFIG_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        print(f'  ✅ 配置报告已生成: DEV_TOOLS_CONFIG_REPORT.md')
        print(f'  📊 总计配置: {len(self.configs_created)}个文件')
        
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def main():
    """主函数"""
    configurator = DevToolsConfigurator()
    configurator.execute_dev_tools_setup()

if __name__ == "__main__":
    main() 