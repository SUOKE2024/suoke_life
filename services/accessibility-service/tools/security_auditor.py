#!/usr/bin/env python

"""
安全审计工具
提供代码安全性检查、漏洞扫描和合规性审计

功能特性：
- 代码安全扫描
- 依赖漏洞检查
- 配置安全审计
- 权限检查
- 数据保护审计
- 合规性检查
- 安全报告生成
"""

import ast
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
import yaml

logger = logging.getLogger(__name__)


@dataclass
class SecurityIssue:
    """安全问题数据类"""

    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str  # VULNERABILITY, MISCONFIGURATION, COMPLIANCE, etc.
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    recommendation: str
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None


@dataclass
class SecurityReport:
    """安全报告数据类"""

    scan_timestamp: str
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    info_issues: int
    issues: List[SecurityIssue]
    summary: Dict[str, Any]
    recommendations: List[str]


class SecurityAuditor:
    """安全审计器"""

    def __init__(self, project_path: str):
        """
        初始化安全审计器

        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)
        self.issues: List[SecurityIssue] = []

        # 安全规则配置
        self.security_patterns = {
            "hardcoded_secrets": [
                (r'password\s*=\s*["\'][^"\']{3,}["\']', "Hardcoded password detected"),
                (r'api_key\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded API key detected"),
                (r'secret\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded secret detected"),
                (r'token\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded token detected"),
            ],
            "sql_injection": [
                (
                    r'execute\s*\(\s*["\'].*%.*["\']',
                    "Potential SQL injection vulnerability",
                ),
                (
                    r'query\s*\(\s*["\'].*\+.*["\']',
                    "Potential SQL injection vulnerability",
                ),
                (
                    r"cursor\.execute\s*\([^)]*%[^)]*\)",
                    "Potential SQL injection vulnerability",
                ),
            ],
            "command_injection": [
                (r"os\.system\s*\([^)]*\+[^)]*\)", "Potential command injection"),
                (
                    r"subprocess\.(call|run|Popen)\s*\([^)]*\+[^)]*\)",
                    "Potential command injection",
                ),
                (
                    r"eval\s*\([^)]*input[^)]*\)",
                    "Dangerous use of eval with user input",
                ),
            ],
            "path_traversal": [
                (r"open\s*\([^)]*\+[^)]*\)", "Potential path traversal vulnerability"),
                (r"file\s*\([^)]*\+[^)]*\)", "Potential path traversal vulnerability"),
            ],
            "weak_crypto": [
                (r"hashlib\.md5\s*\(", "Weak cryptographic hash MD5"),
                (r"hashlib\.sha1\s*\(", "Weak cryptographic hash SHA1"),
                (r"random\.random\s*\(", "Weak random number generator"),
            ],
            "insecure_deserialization": [
                (r"pickle\.loads?\s*\(", "Insecure deserialization with pickle"),
                (r"yaml\.load\s*\([^)]*Loader[^)]*\)", "Insecure YAML deserialization"),
            ],
            "debug_code": [
                (
                    r"print\s*\([^)]*password[^)]*\)",
                    "Debug code exposing sensitive data",
                ),
                (r"print\s*\([^)]*secret[^)]*\)", "Debug code exposing sensitive data"),
                (
                    r"console\.log\s*\([^)]*password[^)]*\)",
                    "Debug code exposing sensitive data",
                ),
            ],
        }

        # 危险函数列表
        self.dangerous_functions = {
            "eval": "CRITICAL",
            "exec": "CRITICAL",
            "compile": "HIGH",
            "__import__": "HIGH",
            "getattr": "MEDIUM",
            "setattr": "MEDIUM",
        }

        # 安全配置检查
        self.security_configs = {
            "debug_mode": ["DEBUG", "debug"],
            "secret_keys": ["SECRET_KEY", "JWT_SECRET"],
            "database_passwords": ["DB_PASSWORD", "DATABASE_PASSWORD"],
            "ssl_settings": ["SSL_VERIFY", "HTTPS_ONLY"],
        }

    def scan_project(self) -> SecurityReport:
        """扫描整个项目"""
        logger.info(f"开始安全扫描: {self.project_path}")

        # 清空之前的问题
        self.issues.clear()

        # 扫描Python文件
        self._scan_python_files()

        # 扫描配置文件
        self._scan_config_files()

        # 扫描依赖
        self._scan_dependencies()

        # 检查文件权限
        self._check_file_permissions()

        # 生成报告
        report = self._generate_report()

        logger.info(f"安全扫描完成，发现 {len(self.issues)} 个问题")
        return report

    def _scan_python_files(self) -> None:
        """扫描Python文件"""
        python_files = list(self.project_path.rglob("*.py"))

        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 静态代码分析
                self._analyze_python_code(file_path, content)

                # 模式匹配检查
                self._check_security_patterns(file_path, content)

                # AST分析
                self._analyze_ast(file_path, content)

            except Exception as e:
                logger.warning(f"无法扫描文件 {file_path}: {e}")

    def _analyze_python_code(self, file_path: Path, content: str) -> None:
        """分析Python代码"""
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # 检查危险函数
            for func_name, severity in self.dangerous_functions.items():
                if re.search(rf"\b{func_name}\s*\(", line):
                    self.issues.append(
                        SecurityIssue(
                            severity=severity,
                            category="VULNERABILITY",
                            title=f"Dangerous function: {func_name}",
                            description=f"Use of potentially dangerous function {func_name}",
                            file_path=str(file_path.relative_to(self.project_path)),
                            line_number=line_num,
                            code_snippet=line,
                            recommendation=f"Avoid using {func_name} or ensure proper input validation",
                            cwe_id="CWE-94" if func_name in ["eval", "exec"] else None,
                        )
                    )

            # 检查TODO/FIXME中的安全相关内容
            if re.search(
                r"#\s*(TODO|FIXME|XXX).*(?:security|password|auth|token)",
                line,
                re.IGNORECASE,
            ):
                self.issues.append(
                    SecurityIssue(
                        severity="MEDIUM",
                        category="COMPLIANCE",
                        title="Security-related TODO/FIXME",
                        description="Security-related TODO or FIXME comment found",
                        file_path=str(file_path.relative_to(self.project_path)),
                        line_number=line_num,
                        code_snippet=line,
                        recommendation="Address security-related TODOs promptly",
                    )
                )

    def _check_security_patterns(self, file_path: Path, content: str) -> None:
        """检查安全模式"""
        lines = content.split("\n")

        for category, patterns in self.security_patterns.items():
            for pattern, description in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        severity = self._get_severity_for_category(category)

                        self.issues.append(
                            SecurityIssue(
                                severity=severity,
                                category="VULNERABILITY",
                                title=f'{category.replace("_", " ").title()} detected',
                                description=description,
                                file_path=str(file_path.relative_to(self.project_path)),
                                line_number=line_num,
                                code_snippet=line.strip(),
                                recommendation=self._get_recommendation_for_category(
                                    category
                                ),
                                cwe_id=self._get_cwe_for_category(category),
                            )
                        )

    def _analyze_ast(self, file_path: Path, content: str) -> None:
        """AST分析"""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # 检查导入
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ["pickle", "cPickle"]:
                            self.issues.append(
                                SecurityIssue(
                                    severity="HIGH",
                                    category="VULNERABILITY",
                                    title="Insecure import: pickle",
                                    description="Pickle module can execute arbitrary code during deserialization",
                                    file_path=str(
                                        file_path.relative_to(self.project_path)
                                    ),
                                    line_number=node.lineno,
                                    code_snippet=f"import {alias.name}",
                                    recommendation="Use json or other safe serialization formats",
                                    cwe_id="CWE-502",
                                )
                            )

                # 检查函数调用
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        if func_name in self.dangerous_functions:
                            self.issues.append(
                                SecurityIssue(
                                    severity=self.dangerous_functions[func_name],
                                    category="VULNERABILITY",
                                    title=f"Dangerous function call: {func_name}",
                                    description=f"Call to potentially dangerous function {func_name}",
                                    file_path=str(
                                        file_path.relative_to(self.project_path)
                                    ),
                                    line_number=node.lineno,
                                    code_snippet=(
                                        ast.unparse(node)
                                        if hasattr(ast, "unparse")
                                        else str(node)
                                    ),
                                    recommendation=f"Avoid using {func_name} or ensure proper input validation",
                                )
                            )

                # 检查字符串常量中的敏感信息
                elif isinstance(node, ast.Str):
                    if self._contains_sensitive_data(node.s):
                        self.issues.append(
                            SecurityIssue(
                                severity="HIGH",
                                category="VULNERABILITY",
                                title="Potential sensitive data in string",
                                description="String constant may contain sensitive information",
                                file_path=str(file_path.relative_to(self.project_path)),
                                line_number=node.lineno,
                                code_snippet=(
                                    f'"{node.s[:50]}..."'
                                    if len(node.s) > 50
                                    else f'"{node.s}"'
                                ),
                                recommendation="Use environment variables or secure configuration",
                            )
                        )

        except SyntaxError as e:
            logger.warning(f"语法错误，无法解析 {file_path}: {e}")

    def _scan_config_files(self) -> None:
        """扫描配置文件"""
        config_patterns = ["*.yaml", "*.yml", "*.json", "*.ini", "*.conf", "*.cfg"]

        for pattern in config_patterns:
            for config_file in self.project_path.rglob(pattern):
                if self._should_skip_file(config_file):
                    continue

                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    self._check_config_security(config_file, content)

                except Exception as e:
                    logger.warning(f"无法扫描配置文件 {config_file}: {e}")

    def _check_config_security(self, file_path: Path, content: str) -> None:
        """检查配置文件安全性"""
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # 检查调试模式
            if re.search(r"debug\s*[:=]\s*true", line, re.IGNORECASE):
                self.issues.append(
                    SecurityIssue(
                        severity="MEDIUM",
                        category="MISCONFIGURATION",
                        title="Debug mode enabled",
                        description="Debug mode is enabled in configuration",
                        file_path=str(file_path.relative_to(self.project_path)),
                        line_number=line_num,
                        code_snippet=line,
                        recommendation="Disable debug mode in production",
                    )
                )

            # 检查硬编码密码
            if re.search(
                r'password\s*[:=]\s*["\'][^"\']{3,}["\']', line, re.IGNORECASE
            ):
                self.issues.append(
                    SecurityIssue(
                        severity="CRITICAL",
                        category="VULNERABILITY",
                        title="Hardcoded password in config",
                        description="Password is hardcoded in configuration file",
                        file_path=str(file_path.relative_to(self.project_path)),
                        line_number=line_num,
                        code_snippet=line,
                        recommendation="Use environment variables for passwords",
                    )
                )

            # 检查弱密钥
            if re.search(
                r'secret\s*[:=]\s*["\'](?:secret|password|123|test)["\']',
                line,
                re.IGNORECASE,
            ):
                self.issues.append(
                    SecurityIssue(
                        severity="HIGH",
                        category="VULNERABILITY",
                        title="Weak secret key",
                        description="Weak or default secret key detected",
                        file_path=str(file_path.relative_to(self.project_path)),
                        line_number=line_num,
                        code_snippet=line,
                        recommendation="Use strong, randomly generated secret keys",
                    )
                )

    def _scan_dependencies(self) -> None:
        """扫描依赖漏洞"""
        # 检查requirements.txt
        req_files = ["requirements.txt", "pyproject.toml", "Pipfile"]

        for req_file in req_files:
            req_path = self.project_path / req_file
            if req_path.exists():
                self._check_dependency_vulnerabilities(req_path)

    def _check_dependency_vulnerabilities(self, req_path: Path) -> None:
        """检查依赖漏洞"""
        try:
            # 使用safety检查已知漏洞
            result = subprocess.run(
                ["python", "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                cwd=self.project_path,
            )

            if result.returncode == 0:
                packages = json.loads(result.stdout)
                self._check_known_vulnerabilities(packages, req_path)

        except Exception as e:
            logger.warning(f"无法检查依赖漏洞: {e}")

    def _check_known_vulnerabilities(
        self, packages: List[Dict], req_path: Path
    ) -> None:
        """检查已知漏洞"""
        # 已知有漏洞的包版本（示例）
        vulnerable_packages = {
            "django": ["<3.2.13", "<4.0.4"],
            "flask": ["<2.0.3"],
            "requests": ["<2.20.0"],
            "pyyaml": ["<5.4"],
            "pillow": ["<8.3.2"],
        }

        for package in packages:
            name = package["name"].lower()
            version = package["version"]

            if name in vulnerable_packages:
                self.issues.append(
                    SecurityIssue(
                        severity="HIGH",
                        category="VULNERABILITY",
                        title=f"Vulnerable dependency: {name}",
                        description=f"Package {name} version {version} has known vulnerabilities",
                        file_path=str(req_path.relative_to(self.project_path)),
                        line_number=1,
                        code_snippet=f"{name}=={version}",
                        recommendation=f"Update {name} to the latest secure version",
                    )
                )

    def _check_file_permissions(self) -> None:
        """检查文件权限"""
        sensitive_files = [
            "*.key",
            "*.pem",
            "*.p12",
            "*.pfx",
            "id_rsa",
            "id_dsa",
            "id_ecdsa",
            ".env",
            ".env.*",
            "config.py",
        ]

        for pattern in sensitive_files:
            for file_path in self.project_path.rglob(pattern):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        mode = oct(stat.st_mode)[-3:]

                        # 检查是否对其他用户可读
                        if int(mode[2]) & 4:  # 其他用户可读
                            self.issues.append(
                                SecurityIssue(
                                    severity="MEDIUM",
                                    category="MISCONFIGURATION",
                                    title="Sensitive file readable by others",
                                    description=f"Sensitive file has permissive permissions: {mode}",
                                    file_path=str(
                                        file_path.relative_to(self.project_path)
                                    ),
                                    line_number=0,
                                    code_snippet=f"File permissions: {mode}",
                                    recommendation="Restrict file permissions (e.g., chmod 600)",
                                )
                            )

                    except Exception as e:
                        logger.warning(f"无法检查文件权限 {file_path}: {e}")

    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".pytest_cache",
            ".coverage",
            "*.pyc",
            "*.pyo",
        ]

        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)

    def _contains_sensitive_data(self, text: str) -> bool:
        """检查字符串是否包含敏感数据"""
        sensitive_patterns = [
            r"[A-Za-z0-9]{32,}",  # 长字符串可能是密钥
            r"sk_[a-zA-Z0-9]{24,}",  # Stripe密钥
            r"pk_[a-zA-Z0-9]{24,}",  # Stripe公钥
            r"AKIA[0-9A-Z]{16}",  # AWS访问密钥
            r"ghp_[a-zA-Z0-9]{36}",  # GitHub个人访问令牌
        ]

        return any(re.search(pattern, text) for pattern in sensitive_patterns)

    def _get_severity_for_category(self, category: str) -> str:
        """获取类别对应的严重程度"""
        severity_map = {
            "hardcoded_secrets": "CRITICAL",
            "sql_injection": "CRITICAL",
            "command_injection": "CRITICAL",
            "path_traversal": "HIGH",
            "weak_crypto": "MEDIUM",
            "insecure_deserialization": "HIGH",
            "debug_code": "LOW",
        }
        return severity_map.get(category, "MEDIUM")

    def _get_recommendation_for_category(self, category: str) -> str:
        """获取类别对应的建议"""
        recommendations = {
            "hardcoded_secrets": "Use environment variables or secure configuration management",
            "sql_injection": "Use parameterized queries or ORM",
            "command_injection": "Validate and sanitize all user inputs",
            "path_traversal": "Validate file paths and use safe file operations",
            "weak_crypto": "Use strong cryptographic algorithms (SHA-256 or better)",
            "insecure_deserialization": "Use safe serialization formats like JSON",
            "debug_code": "Remove debug code before production deployment",
        }
        return recommendations.get(category, "Review and fix the security issue")

    def _get_cwe_for_category(self, category: str) -> Optional[str]:
        """获取类别对应的CWE ID"""
        cwe_map = {
            "hardcoded_secrets": "CWE-798",
            "sql_injection": "CWE-89",
            "command_injection": "CWE-78",
            "path_traversal": "CWE-22",
            "weak_crypto": "CWE-327",
            "insecure_deserialization": "CWE-502",
        }
        return cwe_map.get(category)

    def _generate_report(self) -> SecurityReport:
        """生成安全报告"""
        # 统计问题数量
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)

        for issue in self.issues:
            severity_counts[issue.severity] += 1
            category_counts[issue.category] += 1

        # 生成建议
        recommendations = self._generate_recommendations()

        # 创建报告
        report = SecurityReport(
            scan_timestamp=datetime.now().isoformat(),
            total_issues=len(self.issues),
            critical_issues=severity_counts["CRITICAL"],
            high_issues=severity_counts["HIGH"],
            medium_issues=severity_counts["MEDIUM"],
            low_issues=severity_counts["LOW"],
            info_issues=severity_counts["INFO"],
            issues=self.issues,
            summary={
                "severity_distribution": dict(severity_counts),
                "category_distribution": dict(category_counts),
                "files_scanned": len(list(self.project_path.rglob("*.py"))),
                "scan_duration": "完成",
            },
            recommendations=recommendations,
        )

        return report

    def _generate_recommendations(self) -> List[str]:
        """生成安全建议"""
        recommendations = []

        # 基于发现的问题生成建议
        severity_counts = defaultdict(int)
        for issue in self.issues:
            severity_counts[issue.severity] += 1

        if severity_counts["CRITICAL"] > 0:
            recommendations.append(
                "立即修复所有严重安全问题，这些问题可能导致系统被完全攻破"
            )

        if severity_counts["HIGH"] > 0:
            recommendations.append(
                "优先修复高危安全问题，这些问题可能导致数据泄露或系统损害"
            )

        if severity_counts["MEDIUM"] > 0:
            recommendations.append("及时修复中等安全问题，提高系统整体安全性")

        # 通用安全建议
        recommendations.extend(
            [
                "定期更新依赖包到最新安全版本",
                "实施代码审查流程，确保安全最佳实践",
                "使用静态代码分析工具进行持续安全检查",
                "建立安全开发生命周期(SDLC)流程",
                "定期进行安全培训，提高开发团队安全意识",
            ]
        )

        return recommendations

    def export_report(self, output_path: str, format: str = "json") -> None:
        """导出安全报告"""
        report = self._generate_report()

        if format.lower() == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(asdict(report), f, indent=2, ensure_ascii=False, default=str)

        elif format.lower() == "html":
            self._export_html_report(report, output_path)

        elif format.lower() == "csv":
            self._export_csv_report(report, output_path)

        else:
            raise ValueError(f"不支持的格式: {format}")

        logger.info(f"安全报告已导出到: {output_path}")

    def _export_html_report(self, report: SecurityReport, output_path: str) -> None:
        """导出HTML格式报告"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>安全审计报告</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #f5f5f5; padding: 20px; border-radius: 5px; }
                .summary { display: flex; gap: 20px; margin: 20px 0; }
                .metric { background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }
                .critical { background: #dc3545; color: white; }
                .high { background: #fd7e14; color: white; }
                .medium { background: #ffc107; }
                .low { background: #28a745; color: white; }
                .issue { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
                .issue-title { font-weight: bold; margin-bottom: 10px; }
                .code { background: #f8f9fa; padding: 10px; border-radius: 3px; font-family: monospace; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔒 索克生活无障碍服务 - 安全审计报告</h1>
                <p>扫描时间: {scan_timestamp}</p>
                <p>总问题数: {total_issues}</p>
            </div>
            
            <div class="summary">
                <div class="metric critical">
                    <h3>严重</h3>
                    <p>{critical_issues}</p>
                </div>
                <div class="metric high">
                    <h3>高危</h3>
                    <p>{high_issues}</p>
                </div>
                <div class="metric medium">
                    <h3>中等</h3>
                    <p>{medium_issues}</p>
                </div>
                <div class="metric low">
                    <h3>低危</h3>
                    <p>{low_issues}</p>
                </div>
            </div>
            
            <h2>安全问题详情</h2>
            {issues_html}
            
            <h2>安全建议</h2>
            <ul>
                {recommendations_html}
            </ul>
        </body>
        </html>
        """

        # 生成问题HTML
        issues_html = ""
        for issue in report.issues:
            severity_class = issue.severity.lower()
            # 转义HTML特殊字符
            title = issue.title.replace("<", "&lt;").replace(">", "&gt;")
            description = issue.description.replace("<", "&lt;").replace(">", "&gt;")
            code_snippet = issue.code_snippet.replace("<", "&lt;").replace(">", "&gt;")
            recommendation = issue.recommendation.replace("<", "&lt;").replace(
                ">", "&gt;"
            )

            issues_html += f"""
            <div class="issue {severity_class}">
                <div class="issue-title">[{issue.severity}] {title}</div>
                <p><strong>文件:</strong> {issue.file_path}:{issue.line_number}</p>
                <p><strong>描述:</strong> {description}</p>
                <div class="code">{code_snippet}</div>
                <p><strong>建议:</strong> {recommendation}</p>
            </div>
            """

        # 生成建议HTML
        recommendations_html = ""
        for rec in report.recommendations:
            recommendations_html += f"<li>{rec}</li>"

        # 填充模板
        html_content = html_template.format(
            scan_timestamp=report.scan_timestamp,
            total_issues=report.total_issues,
            critical_issues=report.critical_issues,
            high_issues=report.high_issues,
            medium_issues=report.medium_issues,
            low_issues=report.low_issues,
            issues_html=issues_html,
            recommendations_html=recommendations_html,
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _export_csv_report(self, report: SecurityReport, output_path: str) -> None:
        """导出CSV格式报告"""
        import csv

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Severity",
                    "Category",
                    "Title",
                    "Description",
                    "File",
                    "Line",
                    "Code",
                    "Recommendation",
                    "CWE",
                ]
            )

            for issue in report.issues:
                writer.writerow(
                    [
                        issue.severity,
                        issue.category,
                        issue.title,
                        issue.description,
                        issue.file_path,
                        issue.line_number,
                        issue.code_snippet,
                        issue.recommendation,
                        issue.cwe_id or "",
                    ]
                )


def main():
    """主函数"""
    print("🔒 索克生活无障碍服务 - 安全审计工具")
    print("=" * 50)

    # 获取项目路径
    project_path = input("请输入项目路径 (默认: 当前目录): ").strip() or "."

    # 创建安全审计器
    auditor = SecurityAuditor(project_path)

    try:
        # 执行安全扫描
        print("🔍 开始安全扫描...")
        report = auditor.scan_project()

        # 显示摘要
        print(f"\n📊 扫描结果摘要:")
        print(f"总问题数: {report.total_issues}")
        print(f"严重问题: {report.critical_issues}")
        print(f"高危问题: {report.high_issues}")
        print(f"中等问题: {report.medium_issues}")
        print(f"低危问题: {report.low_issues}")

        # 导出报告
        print("\n💾 导出安全报告...")
        auditor.export_report("security_report.json", "json")
        # auditor.export_report("security_report.html", "html")
        # auditor.export_report("security_report.csv", "csv")

        print("✅ 安全审计完成！")

        if report.critical_issues > 0:
            print("⚠️  发现严重安全问题，请立即修复！")

    except Exception as e:
        print(f"❌ 安全审计失败: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
