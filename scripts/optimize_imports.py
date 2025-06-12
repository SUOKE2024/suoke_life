#!/usr/bin/env python3
"""
索克生活项目 - 导入语句优化工具
自动检测和修复Python代码中的导入问题
"""

import ast
import json
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ImportIssue:
    """导入问题"""

    file_path: str
    line_number: int
    issue_type: str
    original_import: str
    suggested_fix: str
    severity: str


class ImportOptimizer:
    """导入语句优化器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues_found = []
        self.backup_dir = self.project_root / "backups" / "import_optimization"

        # 排除的文件和目录
        self.exclude_patterns = {
            "venv",
            "env",
            ".env",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            "dist",
            "build",
            ".idea",
            ".vscode",
            "*.pyc",
            "*.pyo",
            "*.egg-info",
        }

    def scan_import_issues(self) -> List[ImportIssue]:
        """扫描导入问题"""
        logger.info("🔍 扫描导入语句问题...")

        python_files = self._get_python_files()

        for file_path in python_files:
            try:
                self._analyze_file_imports(file_path)
            except Exception as e:
                logger.warning(f"无法分析文件 {file_path}: {e}")

        logger.info(f"发现 {len(self.issues_found)} 个导入问题")
        return self.issues_found

    def _get_python_files(self) -> List[Path]:
        """获取所有Python文件"""
        python_files = []

        for root, dirs, files in os.walk(self.project_root):
            # 排除特定目录
            dirs[:] = [
                d
                for d in dirs
                if not any(pattern in d for pattern in self.exclude_patterns)
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    # 排除备份文件
                    if "backup" not in str(file_path).lower():
                        python_files.append(file_path)

        return python_files

    def _analyze_file_imports(self, file_path: Path):
        """分析单个文件的导入语句"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # 使用AST分析
            try:
                tree = ast.parse(content)
                self._analyze_ast_imports(file_path, tree, lines)
            except SyntaxError:
                # 如果AST解析失败，使用正则表达式
                self._analyze_regex_imports(file_path, lines)

        except Exception as e:
            logger.warning(f"无法读取文件 {file_path}: {e}")

    def _analyze_ast_imports(self, file_path: Path, tree: ast.AST, lines: List[str]):
        """使用AST分析导入语句"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                self._check_import_from(file_path, node, lines)
            elif isinstance(node, ast.Import):
                self._check_import(file_path, node, lines)

    def _check_import_from(
        self, file_path: Path, node: ast.ImportFrom, lines: List[str]
    ):
        """检查 from ... import ... 语句"""
        line_num = node.lineno
        line_content = lines[line_num - 1] if line_num <= len(lines) else ""

        # 检查通配符导入
        for alias in node.names:
            if alias.name == "*":
                issue = ImportIssue(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=line_num,
                    issue_type="wildcard_import",
                    original_import=line_content.strip(),
                    suggested_fix=self._suggest_wildcard_fix(node),
                    severity="HIGH",
                )
                self.issues_found.append(issue)

        # 检查过长的导入行
        if len(line_content) > 100:
            issue = ImportIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_num,
                issue_type="long_import_line",
                original_import=line_content.strip(),
                suggested_fix=self._suggest_multiline_import(node),
                severity="MEDIUM",
            )
            self.issues_found.append(issue)

    def _check_import(self, file_path: Path, node: ast.Import, lines: List[str]):
        """检查 import ... 语句"""
        line_num = node.lineno
        line_content = lines[line_num - 1] if line_num <= len(lines) else ""

        # 检查多个模块在一行导入
        if len(node.names) > 1:
            issue = ImportIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_num,
                issue_type="multiple_imports",
                original_import=line_content.strip(),
                suggested_fix=self._suggest_separate_imports(node),
                severity="MEDIUM",
            )
            self.issues_found.append(issue)

    def _analyze_regex_imports(self, file_path: Path, lines: List[str]):
        """使用正则表达式分析导入语句（备用方法）"""
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # 检查通配符导入
            if re.match(r"from\s+\w+.*\s+import\s+\*", line_stripped):
                issue = ImportIssue(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=line_num,
                    issue_type="wildcard_import",
                    original_import=line_stripped,
                    suggested_fix="使用具体的导入名称替换 *",
                    severity="HIGH",
                )
                self.issues_found.append(issue)

            # 检查多个导入在一行
            if re.match(r"import\s+\w+,", line_stripped):
                issue = ImportIssue(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=line_num,
                    issue_type="multiple_imports",
                    original_import=line_stripped,
                    suggested_fix="将多个导入分别写在不同行",
                    severity="MEDIUM",
                )
                self.issues_found.append(issue)

    def _suggest_wildcard_fix(self, node: ast.ImportFrom) -> str:
        """建议通配符导入的修复方案"""
        module_name = node.module or ""
        return f"""
建议修复方案：
1. 分析代码中实际使用的函数/类
2. 替换为具体导入：
   from {module_name} import specific_function, SpecificClass
3. 或使用模块导入：
   import {module_name}
   # 然后使用 {module_name}.function_name
"""

    def _suggest_multiline_import(self, node: ast.ImportFrom) -> str:
        """建议多行导入的修复方案"""
        module_name = node.module or ""
        imports = [alias.name for alias in node.names]

        if len(imports) > 3:
            multiline_import = f"from {module_name} import (\n"
            for imp in imports:
                multiline_import += f"    {imp},\n"
            multiline_import += ")"

            return f"""
建议修复方案：
{multiline_import}
"""
        return "将导入语句分行以提高可读性"

    def _suggest_separate_imports(self, node: ast.Import) -> str:
        """建议分离导入的修复方案"""
        separate_imports = []
        for alias in node.names:
            separate_imports.append(f"import {alias.name}")

        return f"""
建议修复方案：
{chr(10).join(separate_imports)}
"""

    def optimize_imports_with_isort(self) -> bool:
        """使用isort优化导入语句"""
        logger.info("🔧 使用isort优化导入语句...")

        try:
            # 检查isort是否安装
            result = subprocess.run(
                ["isort", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.warning("isort未安装，跳过自动优化")
                return False

            # 创建isort配置
            self._create_isort_config()

            # 运行isort
            python_files = self._get_python_files()
            for file_path in python_files:
                try:
                    subprocess.run(
                        ["isort", str(file_path)],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    logger.warning(f"isort处理文件失败 {file_path}: {e}")

            logger.info("✅ isort优化完成")
            return True

        except Exception as e:
            logger.error(f"isort优化失败: {e}")
            return False

    def _create_isort_config(self):
        """创建isort配置文件"""
        config_content = """[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

# 导入分组
known_first_party = ["src", "services", "agents"]
known_third_party = ["fastapi", "pydantic", "sqlalchemy", "redis", "celery"]

# 导入顺序
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]

# 跳过的文件
skip = ["venv", "env", ".env", "__pycache__", ".git", "node_modules"]
"""

        config_file = self.project_root / "pyproject.toml"

        # 如果文件存在，追加配置；否则创建新文件
        if config_file.exists():
            with open(config_file, "a", encoding="utf-8") as f:
                f.write("\n" + config_content)
        else:
            with open(config_file, "w", encoding="utf-8") as f:
                f.write(config_content)

    def remove_unused_imports(self) -> bool:
        """移除未使用的导入"""
        logger.info("🧹 移除未使用的导入...")

        try:
            # 检查autoflake是否安装
            result = subprocess.run(
                ["autoflake", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.warning("autoflake未安装，跳过未使用导入移除")
                return False

            # 运行autoflake
            python_files = self._get_python_files()
            for file_path in python_files:
                try:
                    subprocess.run(
                        [
                            "autoflake",
                            "--in-place",
                            "--remove-all-unused-imports",
                            "--remove-unused-variables",
                            str(file_path),
                        ],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    logger.warning(f"autoflake处理文件失败 {file_path}: {e}")

            logger.info("✅ 未使用导入移除完成")
            return True

        except Exception as e:
            logger.error(f"移除未使用导入失败: {e}")
            return False

    def create_import_guidelines(self) -> str:
        """创建导入规范指南"""
        guidelines_path = (
            self.project_root / "docs" / "development" / "import_guidelines.md"
        )
        guidelines_path.parent.mkdir(parents=True, exist_ok=True)

        guidelines_content = """# Python导入语句规范指南

## 📋 导入顺序

按照以下顺序组织导入语句：

1. **标准库导入**
2. **第三方库导入**
3. **本地应用导入**

每组之间用空行分隔。

## ✅ 推荐做法

### 1. 使用具体导入
```python
# ✅ 推荐
from typing import List, Dict, Optional
from pathlib import Path

# ❌ 避免
from typing import *
```

### 2. 导入语句分行
```python
# ✅ 推荐 - 多个导入时使用括号分行
from some_module import (
    function_one,
    function_two,
    ClassOne,
    ClassTwo
)

# ❌ 避免 - 过长的单行导入
from some_module import function_one, function_two, ClassOne, ClassTwo, function_three
```

### 3. 模块导入 vs 具体导入
```python
# ✅ 推荐 - 对于常用的大型模块
import os
import sys
import json

# ✅ 推荐 - 对于特定功能
from datetime import datetime, timedelta
from pathlib import Path

# ❌ 避免 - 通配符导入
from os import *
```

### 4. 相对导入
```python
# ✅ 推荐 - 明确的相对导入
from .models import User
from ..utils import helper_function

# ✅ 推荐 - 绝对导入
from src.models import User
from src.utils import helper_function
```

## 🛠️ 工具配置

### isort配置
在 `pyproject.toml` 中配置：
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
include_trailing_comma = true
```

### autoflake配置
移除未使用的导入：
```bash
autoflake --in-place --remove-all-unused-imports file.py
```

## 🚫 避免的做法

1. **通配符导入**
   ```python
   # ❌ 避免
   from module import *
   ```

2. **多个模块单行导入**
   ```python
   # ❌ 避免
   import os, sys, json
   ```

3. **未使用的导入**
   ```python
   # ❌ 避免
   import unused_module
   ```

4. **循环导入**
   ```python
   # ❌ 避免
   # file_a.py
   from file_b import something
   
   # file_b.py
   from file_a import something_else
   ```

## 🔧 自动化工具

### 1. 使用isort排序导入
```bash
isort your_file.py
```

### 2. 使用autoflake移除未使用导入
```bash
autoflake --in-place --remove-all-unused-imports your_file.py
```

### 3. 使用black格式化代码
```bash
black your_file.py
```

## 📝 检查清单

在提交代码前检查：

- [ ] 导入语句按正确顺序排列
- [ ] 没有通配符导入
- [ ] 没有未使用的导入
- [ ] 长导入语句已分行
- [ ] 没有循环导入

## 🎯 最佳实践

1. **定期运行导入优化工具**
2. **在CI/CD中集成导入检查**
3. **团队代码审查时关注导入质量**
4. **使用IDE插件自动优化导入**
"""

        with open(guidelines_path, "w", encoding="utf-8") as f:
            f.write(guidelines_content)

        return str(guidelines_path)

    def generate_report(self) -> str:
        """生成导入优化报告"""
        logger.info("📊 生成导入优化报告...")

        report = f"""# 导入语句优化报告

## 📊 扫描结果概览

- **扫描文件数量**: {len(self._get_python_files())}
- **发现导入问题**: {len(self.issues_found)}
- **问题类型分布**:
"""

        # 统计问题类型
        issue_types = {}
        severity_count = {}

        for issue in self.issues_found:
            issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
            severity_count[issue.severity] = severity_count.get(issue.severity, 0) + 1

        for issue_type, count in issue_types.items():
            report += f"  - {issue_type}: {count}\n"

        report += "\n- **严重性分布**:\n"
        for severity, count in severity_count.items():
            report += f"  - {severity}: {count}\n"

        report += "\n## 🔍 发现的导入问题详情\n\n"

        # 按严重性分组
        by_severity = {}
        for issue in self.issues_found:
            if issue.severity not in by_severity:
                by_severity[issue.severity] = []
            by_severity[issue.severity].append(issue)

        for severity in ["HIGH", "MEDIUM", "LOW"]:
            if severity in by_severity:
                report += f"### {severity} 严重性\n\n"
                for issue in by_severity[severity]:
                    report += f"**文件**: `{issue.file_path}:{issue.line_number}`\n"
                    report += f"**类型**: {issue.issue_type}\n"
                    report += f"**原始导入**: `{issue.original_import}`\n"
                    report += f"**修复建议**: {issue.suggested_fix}\n\n"

        report += """
## 🛠️ 修复步骤

### 1. 自动修复
```bash
# 安装工具
pip install isort autoflake black

# 优化导入顺序
isort .

# 移除未使用导入
autoflake --in-place --remove-all-unused-imports --recursive .

# 格式化代码
black .
```

### 2. 手动修复
1. 替换所有通配符导入为具体导入
2. 将长导入语句分行
3. 分离多个模块的导入语句

### 3. 配置工具
1. 配置isort和autoflake
2. 在IDE中启用导入优化
3. 在CI/CD中添加导入检查

## 📋 导入规范

请参考 `docs/development/import_guidelines.md` 了解详细的导入规范。

## ⚠️ 注意事项

1. **通配符导入**可能导致命名冲突和难以追踪的bug
2. **未使用的导入**会增加代码复杂度和加载时间
3. **不规范的导入顺序**会影响代码可读性
4. **循环导入**会导致运行时错误
"""

        return report


def main():
    """主函数"""
    project_root = os.getcwd()
    print("📦 索克生活项目 - 导入语句优化工具")
    print("=" * 60)

    optimizer = ImportOptimizer(project_root)

    # 1. 扫描导入问题
    issues = optimizer.scan_import_issues()

    # 2. 自动优化导入（如果工具可用）
    isort_success = optimizer.optimize_imports_with_isort()
    autoflake_success = optimizer.remove_unused_imports()

    # 3. 创建导入规范指南
    guidelines_file = optimizer.create_import_guidelines()
    print(f"✅ 已创建导入规范指南: {guidelines_file}")

    # 4. 生成报告
    report = optimizer.generate_report()

    # 保存报告
    report_file = Path(project_root) / "import_optimization_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"📊 优化报告已保存到: {report_file}")

    if issues:
        print(f"\n⚠️  发现 {len(issues)} 个导入问题，请查看报告详情")
    else:
        print("\n✅ 未发现导入问题")

    if isort_success:
        print("✅ isort导入排序完成")

    if autoflake_success:
        print("✅ 未使用导入移除完成")


if __name__ == "__main__":
    main()
