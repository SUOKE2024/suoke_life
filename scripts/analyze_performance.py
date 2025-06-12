#!/usr/bin/env python3
"""
性能分析工具
分析代码复杂度、检测性能瓶颈并提供优化建议
"""

import ast
import logging
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """性能分析器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.complexity_issues: List[Dict] = []
        self.performance_issues: List[Dict] = []
        self.optimization_suggestions: List[Dict] = []

        # 忽略的目录和文件
        self.ignore_dirs = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            "env",
            ".env",
            "build",
            "dist",
            ".idea",
            ".vscode",
            "logs",
            "temp",
            "tmp",
        }
        self.ignore_files = {"__init__.py", "conftest.py", "setup.py", "manage.py"}

        # 性能问题模式
        self.performance_patterns = {
            "nested_loops": {
                "pattern": r"for\s+\w+\s+in\s+.*:\s*\n\s*for\s+\w+\s+in\s+.*:",
                "severity": "HIGH",
                "description": "嵌套循环可能导致性能问题",
            },
            "string_concatenation": {
                "pattern": r'\w+\s*\+=\s*["\'].*["\']',
                "severity": "MEDIUM",
                "description": "字符串拼接应使用join()或f-string",
            },
            "list_comprehension_in_loop": {
                "pattern": r"for\s+\w+\s+in\s+.*:\s*\n\s*.*\[.*for.*in.*\]",
                "severity": "MEDIUM",
                "description": "循环中的列表推导式可能影响性能",
            },
            "global_variable_access": {
                "pattern": r"global\s+\w+",
                "severity": "LOW",
                "description": "全局变量访问可能影响性能",
            },
        }

    def should_ignore_path(self, path: Path) -> bool:
        """检查是否应该忽略路径"""
        # 检查目录
        for part in path.parts:
            if part in self.ignore_dirs or part.startswith("."):
                return True

        # 检查文件
        if path.name in self.ignore_files:
            return True

        # 只处理Python文件
        if path.suffix != ".py":
            return True

        return False

    def calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1

        return complexity

    def analyze_function_complexity(
        self, node: ast.FunctionDef, file_path: str
    ) -> Dict:
        """分析函数复杂度"""
        complexity = self.calculate_cyclomatic_complexity(node)
        lines_count = (node.end_lineno or node.lineno) - node.lineno + 1

        # 计算嵌套深度
        max_depth = self.calculate_nesting_depth(node)

        # 计算参数数量
        param_count = len(node.args.args)
        if node.args.vararg:
            param_count += 1
        if node.args.kwarg:
            param_count += 1

        return {
            "name": node.name,
            "file_path": file_path,
            "line_number": node.lineno,
            "cyclomatic_complexity": complexity,
            "lines_count": lines_count,
            "max_nesting_depth": max_depth,
            "parameter_count": param_count,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
        }

    def calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """计算最大嵌套深度"""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(
                child,
                (
                    ast.If,
                    ast.While,
                    ast.For,
                    ast.AsyncFor,
                    ast.With,
                    ast.AsyncWith,
                    ast.Try,
                ),
            ):
                child_depth = self.calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self.calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def detect_performance_patterns(self, file_path: Path) -> List[Dict]:
        """检测性能问题模式"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            for pattern_name, pattern_info in self.performance_patterns.items():
                matches = re.finditer(pattern_info["pattern"], content, re.MULTILINE)

                for match in matches:
                    # 计算行号
                    line_number = content[: match.start()].count("\n") + 1

                    issues.append(
                        {
                            "type": pattern_name,
                            "file_path": str(file_path),
                            "line_number": line_number,
                            "severity": pattern_info["severity"],
                            "description": pattern_info["description"],
                            "code_snippet": (
                                lines[line_number - 1].strip()
                                if line_number <= len(lines)
                                else ""
                            ),
                        }
                    )

        except Exception as e:
            logger.warning(f"无法分析文件 {file_path}: {e}")

        return issues

    def analyze_imports(self, file_path: Path) -> List[Dict]:
        """分析导入性能问题"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    # 检测通配符导入
                    for alias in node.names:
                        if alias.name == "*":
                            issues.append(
                                {
                                    "type": "wildcard_import",
                                    "file_path": str(file_path),
                                    "line_number": node.lineno,
                                    "severity": "MEDIUM",
                                    "description": f"通配符导入 from {node.module} import * 可能影响性能",
                                    "module": node.module,
                                }
                            )

                elif isinstance(node, ast.Import):
                    # 检测大型库导入
                    large_libraries = {
                        "pandas",
                        "numpy",
                        "matplotlib",
                        "tensorflow",
                        "torch",
                    }
                    for alias in node.names:
                        if alias.name in large_libraries:
                            issues.append(
                                {
                                    "type": "large_library_import",
                                    "file_path": str(file_path),
                                    "line_number": node.lineno,
                                    "severity": "LOW",
                                    "description": f"大型库 {alias.name} 导入可能影响启动性能",
                                    "library": alias.name,
                                }
                            )

        except Exception as e:
            logger.warning(f"无法分析导入 {file_path}: {e}")

        return issues

    def analyze_file(self, file_path: Path) -> Dict:
        """分析单个文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            file_analysis = {
                "path": str(file_path),
                "functions": [],
                "classes": [],
                "performance_issues": [],
                "import_issues": [],
            }

            # 分析函数复杂度
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_analysis = self.analyze_function_complexity(
                        node, str(file_path)
                    )
                    file_analysis["functions"].append(func_analysis)

                elif isinstance(node, ast.ClassDef):
                    class_analysis = {
                        "name": node.name,
                        "line_number": node.lineno,
                        "methods_count": len(
                            [
                                n
                                for n in node.body
                                if isinstance(
                                    n, (ast.FunctionDef, ast.AsyncFunctionDef)
                                )
                            ]
                        ),
                        "lines_count": (node.end_lineno or node.lineno)
                        - node.lineno
                        + 1,
                    }
                    file_analysis["classes"].append(class_analysis)

            # 检测性能问题模式
            file_analysis["performance_issues"] = self.detect_performance_patterns(
                file_path
            )

            # 分析导入问题
            file_analysis["import_issues"] = self.analyze_imports(file_path)

            return file_analysis

        except Exception as e:
            logger.warning(f"无法分析文件 {file_path}: {e}")
            return None

    def scan_project(self):
        """扫描项目中的所有Python文件"""
        logger.info("🔍 扫描项目进行性能分析...")

        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # 过滤忽略的目录
            dirs[:] = [
                d for d in dirs if d not in self.ignore_dirs and not d.startswith(".")
            ]

            for file in files:
                file_path = Path(root) / file
                if not self.should_ignore_path(file_path):
                    python_files.append(file_path)

        logger.info(f"找到 {len(python_files)} 个Python文件")

        for file_path in python_files:
            file_analysis = self.analyze_file(file_path)
            if file_analysis:
                # 收集复杂度问题
                for func in file_analysis["functions"]:
                    if func["cyclomatic_complexity"] > 10:
                        self.complexity_issues.append(
                            {
                                "type": "high_complexity",
                                "severity": (
                                    "HIGH"
                                    if func["cyclomatic_complexity"] > 15
                                    else "MEDIUM"
                                ),
                                "function_name": func["name"],
                                "file_path": func["file_path"],
                                "line_number": func["line_number"],
                                "complexity": func["cyclomatic_complexity"],
                                "description": f"函数 {func['name']} 圈复杂度过高 ({func['cyclomatic_complexity']})",
                            }
                        )

                    if func["lines_count"] > 50:
                        self.complexity_issues.append(
                            {
                                "type": "long_function",
                                "severity": "MEDIUM",
                                "function_name": func["name"],
                                "file_path": func["file_path"],
                                "line_number": func["line_number"],
                                "lines_count": func["lines_count"],
                                "description": f"函数 {func['name']} 过长 ({func['lines_count']} 行)",
                            }
                        )

                    if func["parameter_count"] > 7:
                        self.complexity_issues.append(
                            {
                                "type": "too_many_parameters",
                                "severity": "MEDIUM",
                                "function_name": func["name"],
                                "file_path": func["file_path"],
                                "line_number": func["line_number"],
                                "parameter_count": func["parameter_count"],
                                "description": f"函数 {func['name']} 参数过多 ({func['parameter_count']} 个)",
                            }
                        )

                # 收集性能问题
                self.performance_issues.extend(file_analysis["performance_issues"])
                self.performance_issues.extend(file_analysis["import_issues"])

        logger.info(f"发现 {len(self.complexity_issues)} 个复杂度问题")
        logger.info(f"发现 {len(self.performance_issues)} 个性能问题")

    def generate_optimization_suggestions(self) -> List[Dict]:
        """生成优化建议"""
        suggestions = []

        # 基于复杂度问题的建议
        high_complexity_funcs = [
            issue
            for issue in self.complexity_issues
            if issue["type"] == "high_complexity"
        ]
        if high_complexity_funcs:
            suggestions.append(
                {
                    "category": "代码复杂度优化",
                    "priority": "HIGH",
                    "title": "降低函数复杂度",
                    "description": f"发现 {len(high_complexity_funcs)} 个高复杂度函数",
                    "recommendations": [
                        "将复杂函数拆分为多个小函数",
                        "使用早期返回减少嵌套",
                        "提取条件判断到独立函数",
                        "使用策略模式替换复杂的if-else",
                    ],
                }
            )

        # 基于性能问题的建议
        nested_loops = [
            issue
            for issue in self.performance_issues
            if issue["type"] == "nested_loops"
        ]
        if nested_loops:
            suggestions.append(
                {
                    "category": "性能优化",
                    "priority": "HIGH",
                    "title": "优化嵌套循环",
                    "description": f"发现 {len(nested_loops)} 个嵌套循环",
                    "recommendations": [
                        "考虑使用字典或集合优化查找",
                        "使用生成器减少内存使用",
                        "考虑使用numpy等优化库",
                        "缓存重复计算的结果",
                    ],
                }
            )

        string_concat = [
            issue
            for issue in self.performance_issues
            if issue["type"] == "string_concatenation"
        ]
        if string_concat:
            suggestions.append(
                {
                    "category": "性能优化",
                    "priority": "MEDIUM",
                    "title": "优化字符串操作",
                    "description": f"发现 {len(string_concat)} 个字符串拼接问题",
                    "recommendations": [
                        "使用f-string替换字符串拼接",
                        "使用join()方法连接多个字符串",
                        "避免在循环中进行字符串拼接",
                        "使用StringIO处理大量字符串操作",
                    ],
                }
            )

        return suggestions

    def create_performance_guide(self) -> str:
        """创建性能优化指南"""
        guide_content = """# Python性能优化指南

## 代码复杂度优化

### 1. 降低圈复杂度
- **目标**: 保持函数圈复杂度 < 10
- **方法**: 
  - 提取子函数
  - 使用早期返回
  - 简化条件判断
  - 使用设计模式

### 2. 控制函数长度
- **目标**: 保持函数长度 < 50 行
- **方法**:
  - 单一职责原则
  - 提取重复代码
  - 分离业务逻辑

### 3. 减少参数数量
- **目标**: 函数参数 < 7 个
- **方法**:
  - 使用数据类或字典
  - 参数对象模式
  - 配置对象

## 性能优化策略

### 1. 循环优化
```python
# 避免
for i in range(len(items)):
    for j in range(len(other_items)):
        if items[i] == other_items[j]:
            # 处理

# 推荐
item_set = set(items)
for item in other_items:
    if item in item_set:
        # 处理
```

### 2. 字符串优化
```python
# 避免
result = ""
for item in items:
    result += str(item)

# 推荐
result = "".join(str(item) for item in items)
# 或
result = f"{''.join(str(item) for item in items)}"
```

### 3. 数据结构选择
- **查找操作**: 使用set或dict而不是list
- **频繁插入/删除**: 使用deque而不是list
- **大量数值计算**: 使用numpy数组

### 4. 内存优化
```python
# 使用生成器
def process_large_data():
    for item in large_dataset:
        yield process(item)

# 使用上下文管理器
with open('file.txt') as f:
    data = f.read()
```

## 导入优化

### 1. 避免通配符导入
```python
# 避免
from module import *

# 推荐
from module import specific_function
```

### 2. 延迟导入
```python
def heavy_function():
    import heavy_library  # 只在需要时导入
    return heavy_library.process()
```

## 性能测试

### 1. 使用cProfile
```python
import cProfile
cProfile.run('your_function()')
```

### 2. 使用timeit
```python
import timeit
time_taken = timeit.timeit('your_function()', number=1000)
```

### 3. 内存分析
```python
from memory_profiler import profile

@profile
def your_function():
    # 函数代码
```

## 最佳实践

1. **测量优先**: 先测量再优化
2. **关注瓶颈**: 优化最耗时的部分
3. **保持简单**: 不要过度优化
4. **定期检查**: 使用工具定期检查性能
"""
        return guide_content

    def generate_report(self) -> str:
        """生成性能分析报告"""
        logger.info("📊 生成性能分析报告...")

        suggestions = self.generate_optimization_suggestions()

        # 统计信息
        total_issues = len(self.complexity_issues) + len(self.performance_issues)
        high_priority = len(
            [
                issue
                for issue in self.complexity_issues + self.performance_issues
                if issue.get("severity") == "HIGH"
            ]
        )
        medium_priority = len(
            [
                issue
                for issue in self.complexity_issues + self.performance_issues
                if issue.get("severity") == "MEDIUM"
            ]
        )
        low_priority = len(
            [
                issue
                for issue in self.complexity_issues + self.performance_issues
                if issue.get("severity") == "LOW"
            ]
        )

        report = f"""# 性能分析报告

## 📊 分析统计

- **总问题数**: {total_issues}
- **高优先级**: {high_priority} 个
- **中优先级**: {medium_priority} 个
- **低优先级**: {low_priority} 个

## 🔍 复杂度问题

"""

        if self.complexity_issues:
            # 按严重程度分组
            severity_groups = defaultdict(list)
            for issue in self.complexity_issues:
                severity_groups[issue["severity"]].append(issue)

            for severity in ["HIGH", "MEDIUM", "LOW"]:
                if severity in severity_groups:
                    report += f"### {severity} 优先级\n\n"
                    for issue in severity_groups[severity]:
                        report += f"- **{issue['function_name']}** ({issue['file_path']}:{issue['line_number']})\n"
                        report += f"  - {issue['description']}\n\n"
        else:
            report += "✅ 未发现复杂度问题\n\n"

        report += """## ⚡ 性能问题

"""

        if self.performance_issues:
            # 按类型分组
            type_groups = defaultdict(list)
            for issue in self.performance_issues:
                type_groups[issue["type"]].append(issue)

            for issue_type, issues in type_groups.items():
                report += f"### {issue_type.replace('_', ' ').title()}\n\n"
                for issue in issues[:5]:  # 只显示前5个
                    report += f"- **{issue['file_path']}:{issue['line_number']}**\n"
                    report += f"  - {issue['description']}\n"
                    if "code_snippet" in issue and issue["code_snippet"]:
                        report += f"  - 代码: `{issue['code_snippet']}`\n"
                    report += "\n"

                if len(issues) > 5:
                    report += f"  *... 还有 {len(issues) - 5} 个类似问题*\n\n"
        else:
            report += "✅ 未发现性能问题\n\n"

        report += """## 🚀 优化建议

"""

        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                report += f"### {i}. {suggestion['title']} ({suggestion['priority']} 优先级)\n\n"
                report += f"**类别**: {suggestion['category']}\n\n"
                report += f"**问题**: {suggestion['description']}\n\n"
                report += "**建议**:\n"
                for rec in suggestion["recommendations"]:
                    report += f"- {rec}\n"
                report += "\n"
        else:
            report += "✅ 当前代码性能良好\n"

        report += f"""

## 📋 总结

本次分析发现了 {total_issues} 个性能相关问题。

### 优先级建议

1. **立即处理**: {high_priority} 个高优先级问题
2. **短期处理**: {medium_priority} 个中优先级问题  
3. **长期优化**: {low_priority} 个低优先级问题

### 下一步行动

1. 查看性能优化指南: `docs/development/performance_guide.md`
2. 按优先级修复性能问题
3. 建立性能监控机制
4. 定期运行性能分析

---
*报告生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return report


def main():
    """主函数"""
    project_root = os.getcwd()
    print("⚡ 索克生活项目 - 性能分析工具")
    print("=" * 60)

    analyzer = PerformanceAnalyzer(project_root)

    # 1. 扫描项目
    analyzer.scan_project()

    # 2. 创建性能优化指南
    print("📝 创建性能优化指南...")
    guide_content = analyzer.create_performance_guide()

    # 确保目录存在
    docs_dir = Path(project_root) / "docs" / "development"
    docs_dir.mkdir(parents=True, exist_ok=True)

    guide_file = docs_dir / "performance_guide.md"
    with open(guide_file, "w", encoding="utf-8") as f:
        f.write(guide_content)

    print(f"✅ 已创建性能优化指南: {guide_file}")

    # 3. 生成报告
    print("📊 生成报告...")
    report = analyzer.generate_report()

    # 保存报告
    report_file = Path(project_root) / "performance_analysis_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"📊 性能分析报告已保存到: {report_file}")

    total_issues = len(analyzer.complexity_issues) + len(analyzer.performance_issues)
    if total_issues > 0:
        print(f"\n⚠️  发现 {total_issues} 个性能问题，请查看报告详情")
    else:
        print("\n✅ 未发现性能问题")


if __name__ == "__main__":
    main()
