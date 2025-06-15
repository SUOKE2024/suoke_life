#!/usr/bin/env python3
"""
代码质量检查脚本 - 全面分析代码质量并生成报告
"""

import ast
import logging
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """代码质量指标"""

    total_files: int = 0
    total_lines: int = 0
    functions_with_types: int = 0
    functions_without_types: int = 0
    complex_functions: int = 0
    security_issues: int = 0
    code_smells: int = 0
    test_coverage: float = 0.0
    maintainability_index: float = 0.0


@dataclass
class SecurityIssue:
    """安全问题"""

    file_path: str
    line_number: int
    issue_type: str
    description: str
    severity: str


@dataclass
class CodeSmell:
    """代码异味"""

    file_path: str
    line_number: int
    smell_type: str
    description: str


class CodeQualityChecker:
    """代码质量检查器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.metrics = QualityMetrics()
        self.security_issues: List[SecurityIssue] = []
        self.code_smells: List[CodeSmell] = []
        self.type_annotation_issues: List[Dict[str, Any]] = []

        # 安全模式检查
        self.security_patterns = {
            "hardcoded_password": [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'pwd\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
            ],
            "sql_injection": [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']',
            ],
            "command_injection": [
                r"os\.system\s*\(",
                r"subprocess\.call\s*\(",
                r"eval\s*\(",
            ],
            "weak_crypto": [r"md5\s*\(", r"sha1\s*\(", r"DES\s*\("],
        }

        # 代码异味模式
        self.code_smell_patterns = {
            "long_parameter_list": r"def\s+\w+\s*\([^)]{100,}\)",
            "magic_numbers": r"\b(?<![\w.])\d{2,}\b(?![\w.])",
            "duplicate_code": r"(.{50,})\n.*\1",
            "large_class": r"class\s+\w+.*?(?=class|\Z)",
            "god_method": r"def\s+\w+.*?(?=def|\Z)",
        }

    def analyze_project(self) -> Dict[str, Any]:
        """分析整个项目"""
        logger.info("开始代码质量分析...")
        start_time = time.time()

        # 获取所有Python文件
        python_files = list(self.project_root.rglob("*.py"))
        self.metrics.total_files = len(python_files)

        logger.info(f"找到 {len(python_files)} 个Python文件")

        # 分析每个文件
        for file_path in python_files:
            try:
                self._analyze_file(file_path)
            except Exception as e:
                logger.error(f"分析文件 {file_path} 时出错: {e}")

        # 计算综合指标
        self._calculate_metrics()

        analysis_time = time.time() - start_time
        logger.info(f"代码质量分析完成，耗时 {analysis_time:.2f} 秒")

        return self._generate_report()

    def _analyze_file(self, file_path: Path) -> None:
        """分析单个文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 统计行数
            lines = content.split("\n")
            self.metrics.total_lines += len(lines)

            # 解析AST
            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, file_path)
            except SyntaxError as e:
                logger.warning(f"语法错误在文件 {file_path}: {e}")

            # 安全检查
            self._check_security_issues(content, file_path)

            # 代码异味检查
            self._check_code_smells(content, file_path)

        except Exception as e:
            logger.error(f"读取文件 {file_path} 时出错: {e}")

    def _analyze_ast(self, tree: ast.AST, file_path: Path) -> None:
        """分析AST树"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._analyze_function(node, file_path)
            elif isinstance(node, ast.ClassDef):
                self._analyze_class(node, file_path)

    def _analyze_function(self, node: ast.FunctionDef, file_path: Path) -> None:
        """分析函数"""
        # 检查类型注解
        has_return_annotation = node.returns is not None
        has_param_annotations = any(
            arg.annotation is not None for arg in node.args.args
        )

        if has_return_annotation and has_param_annotations:
            self.metrics.functions_with_types += 1
        else:
            self.metrics.functions_without_types += 1
            self.type_annotation_issues.append(
                {
                    "file": str(file_path),
                    "function": node.name,
                    "line": node.lineno,
                    "missing_return_type": not has_return_annotation,
                    "missing_param_types": not has_param_annotations,
                }
            )

        # 检查复杂度
        complexity = self._calculate_complexity(node)
        if complexity > 10:  # McCabe复杂度阈值
            self.metrics.complex_functions += 1
            self.code_smells.append(
                CodeSmell(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    smell_type="high_complexity",
                    description=f"函数 {node.name} 复杂度过高: {complexity}",
                )
            )

    def _analyze_class(self, node: ast.ClassDef, file_path: Path) -> None:
        """分析类"""
        # 检查类的大小
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) > 20:  # 方法数量阈值
            self.code_smells.append(
                CodeSmell(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    smell_type="large_class",
                    description=f"类 {node.name} 方法过多: {len(methods)}",
                )
            )

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数的McCabe复杂度"""
        complexity = 1  # 基础复杂度

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _check_security_issues(self, content: str, file_path: Path) -> None:
        """检查安全问题"""
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for issue_type, patterns in self.security_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        severity = (
                            "HIGH"
                            if issue_type in ["hardcoded_password", "sql_injection"]
                            else "MEDIUM"
                        )
                        self.security_issues.append(
                            SecurityIssue(
                                file_path=str(file_path),
                                line_number=line_num,
                                issue_type=issue_type,
                                description=f"检测到 {issue_type}: {line.strip()}",
                                severity=severity,
                            )
                        )
                        self.metrics.security_issues += 1

    def _check_code_smells(self, content: str, file_path: Path) -> None:
        """检查代码异味"""
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            # 检查魔法数字
            if re.search(self.code_smell_patterns["magic_numbers"], line):
                # 排除常见的非魔法数字
                if not re.search(r"\b(0|1|2|10|100|1000)\b", line):
                    self.code_smells.append(
                        CodeSmell(
                            file_path=str(file_path),
                            line_number=line_num,
                            smell_type="magic_numbers",
                            description=f"发现魔法数字: {line.strip()}",
                        )
                    )
                    self.metrics.code_smells += 1

    def _calculate_metrics(self) -> None:
        """计算综合指标"""
        total_functions = (
            self.metrics.functions_with_types + self.metrics.functions_without_types
        )

        if total_functions > 0:
            type_coverage = (self.metrics.functions_with_types / total_functions) * 100
        else:
            type_coverage = 0

        # 计算可维护性指数 (简化版)
        security_penalty = min(self.metrics.security_issues * 10, 50)
        complexity_penalty = min(self.metrics.complex_functions * 5, 30)
        smell_penalty = min(self.metrics.code_smells * 2, 20)

        self.metrics.maintainability_index = max(
            0, 100 - security_penalty - complexity_penalty - smell_penalty
        )

    def _generate_report(self) -> Dict[str, Any]:
        """生成分析报告"""
        total_functions = (
            self.metrics.functions_with_types + self.metrics.functions_without_types
        )
        type_coverage = (
            (self.metrics.functions_with_types / total_functions * 100)
            if total_functions > 0
            else 0
        )

        report = {
            "summary": {
                "total_files": self.metrics.total_files,
                "total_lines": self.metrics.total_lines,
                "type_annotation_coverage": f"{type_coverage:.1f}%",
                "security_issues": self.metrics.security_issues,
                "code_smells": self.metrics.code_smells,
                "complex_functions": self.metrics.complex_functions,
                "maintainability_index": f"{self.metrics.maintainability_index:.1f}/100",
            },
            "type_annotations": {
                "functions_with_types": self.metrics.functions_with_types,
                "functions_without_types": self.metrics.functions_without_types,
                "missing_annotations": self.type_annotation_issues[:10],  # 显示前10个
            },
            "security_issues": {
                "total": len(self.security_issues),
                "high_severity": len(
                    [i for i in self.security_issues if i.severity == "HIGH"]
                ),
                "medium_severity": len(
                    [i for i in self.security_issues if i.severity == "MEDIUM"]
                ),
                "issues": self.security_issues[:10],  # 显示前10个
            },
            "code_smells": {
                "total": len(self.code_smells),
                "by_type": self._group_smells_by_type(),
                "issues": self.code_smells[:10],  # 显示前10个
            },
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _group_smells_by_type(self) -> Dict[str, int]:
        """按类型分组代码异味"""
        groups = defaultdict(int)
        for smell in self.code_smells:
            groups[smell.smell_type] += 1
        return dict(groups)

    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if self.metrics.functions_without_types > 0:
            recommendations.append(
                f"添加类型注解到 {self.metrics.functions_without_types} 个函数"
            )

        if self.metrics.security_issues > 0:
            recommendations.append(f"修复 {self.metrics.security_issues} 个安全问题")

        if self.metrics.complex_functions > 0:
            recommendations.append(f"重构 {self.metrics.complex_functions} 个复杂函数")

        if self.metrics.code_smells > 0:
            recommendations.append(f"清理 {self.metrics.code_smells} 个代码异味")

        if self.metrics.maintainability_index < 70:
            recommendations.append("提高代码可维护性指数")

        return recommendations

    def save_report(self, output_file: str = "code_quality_report.json") -> None:
        """保存报告到文件"""
        import json

        report = self._generate_report()

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"代码质量报告已保存到: {output_file}")

    def print_summary(self) -> None:
        """打印摘要报告"""
        report = self._generate_report()

        print("\n" + "=" * 60)
        print("📊 代码质量分析报告")
        print("=" * 60)

        print(f"📁 总文件数: {report['summary']['total_files']}")
        print(f"📄 总行数: {report['summary']['total_lines']}")
        print(f"🏷️  类型注解覆盖率: {report['summary']['type_annotation_coverage']}")
        print(f"🔒 安全问题: {report['summary']['security_issues']}")
        print(f"👃 代码异味: {report['summary']['code_smells']}")
        print(f"🔄 复杂函数: {report['summary']['complex_functions']}")
        print(f"📈 可维护性指数: {report['summary']['maintainability_index']}")

        if report["recommendations"]:
            print("\n🎯 改进建议:")
            for i, rec in enumerate(report["recommendations"], 1):
                print(f"  {i}. {rec}")

        print("\n" + "=" * 60)


def main() -> None:
    """主函数"""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."

    checker = CodeQualityChecker(project_root)

    try:
        # 执行分析
        report = checker.analyze_project()

        # 打印摘要
        checker.print_summary()

        # 保存详细报告
        checker.save_report("code_quality_report.json")

        # 根据质量指标设置退出码
        if checker.metrics.security_issues > 0:
            sys.exit(1)  # 有安全问题时失败
        elif checker.metrics.maintainability_index < 50:
            sys.exit(1)  # 可维护性太低时失败
        else:
            sys.exit(0)  # 成功

    except Exception as e:
        logger.error(f"代码质量检查失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
