#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索克生活认证服务 - 代码质量分析器

分析代码质量、识别问题并提供修复建议。
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import logging
from dataclasses import dataclass
from collections import defaultdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CodeIssue:
    """代码问题数据类"""
    file_path: str
    line_number: int
    column: int
    issue_type: str
    severity: str
    message: str
    rule_code: str


class CodeQualityAnalyzer:
    """代码质量分析器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues: List[CodeIssue] = []
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'issues_by_type': defaultdict(int),
            'issues_by_severity': defaultdict(int),
            'files_with_issues': set()
        }
    
    def run_flake8_analysis(self) -> List[CodeIssue]:
        """运行flake8分析"""
        logger.info("🔍 运行 Flake8 代码风格检查...")
        
        cmd = [
            "flake8",
            "--max-line-length=120",
            "--ignore=E501,W503,E203",
            "--format=json",
            "internal/", "app/", "api/"
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            
            issues = []
            if result.stdout:
                # flake8 doesn't output JSON by default, parse text output
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        parts = line.split(':', 4)
                        if len(parts) >= 4:
                            file_path = parts[0]
                            line_num = int(parts[1]) if parts[1].isdigit() else 0
                            col = int(parts[2]) if parts[2].isdigit() else 0
                            code_msg = parts[3].strip()
                            
                            # 解析错误代码和消息
                            if ' ' in code_msg:
                                code, message = code_msg.split(' ', 1)
                            else:
                                code, message = code_msg, ""
                            
                            severity = self._get_severity_from_code(code)
                            
                            issues.append(CodeIssue(
                                file_path=file_path,
                                line_number=line_num,
                                column=col,
                                issue_type="style",
                                severity=severity,
                                message=message,
                                rule_code=code
                            ))
            
            logger.info(f"   发现 {len(issues)} 个代码风格问题")
            return issues
            
        except Exception as e:
            logger.error(f"Flake8 分析失败: {e}")
            return []
    
    def run_mypy_analysis(self) -> List[CodeIssue]:
        """运行mypy类型检查"""
        logger.info("🔍 运行 MyPy 类型检查...")
        
        cmd = [
            "mypy",
            "--ignore-missing-imports",
            "--show-error-codes",
            "--no-error-summary",
            "internal/", "app/", "api/"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if ':' in line and 'error:' in line:
                        parts = line.split(':', 3)
                        if len(parts) >= 3:
                            file_path = parts[0]
                            line_num = int(parts[1]) if parts[1].isdigit() else 0
                            message = parts[2].replace('error:', '').strip()
                            
                            issues.append(CodeIssue(
                                file_path=file_path,
                                line_number=line_num,
                                column=0,
                                issue_type="type",
                                severity="error",
                                message=message,
                                rule_code="mypy"
                            ))
            
            logger.info(f"   发现 {len(issues)} 个类型检查问题")
            return issues
            
        except Exception as e:
            logger.error(f"MyPy 分析失败: {e}")
            return []
    
    def analyze_code_complexity(self) -> List[CodeIssue]:
        """分析代码复杂度"""
        logger.info("🔍 分析代码复杂度...")
        
        issues = []
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if "venv" in str(py_file) or "cleanup_backup" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                # 检查文件长度
                if len(lines) > 500:
                    issues.append(CodeIssue(
                        file_path=str(py_file.relative_to(self.project_root)),
                        line_number=1,
                        column=0,
                        issue_type="complexity",
                        severity="warning",
                        message=f"文件过长 ({len(lines)} 行)，建议拆分",
                        rule_code="file_length"
                    ))
                
                # 检查函数长度
                current_function = None
                function_start = 0
                indent_level = 0
                
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    
                    if stripped.startswith('def ') or stripped.startswith('async def '):
                        if current_function and i - function_start > 50:
                            issues.append(CodeIssue(
                                file_path=str(py_file.relative_to(self.project_root)),
                                line_number=function_start,
                                column=0,
                                issue_type="complexity",
                                severity="warning",
                                message=f"函数 {current_function} 过长 ({i - function_start} 行)",
                                rule_code="function_length"
                            ))
                        
                        current_function = stripped.split('(')[0].replace('def ', '').replace('async def ', '')
                        function_start = i
                        indent_level = len(line) - len(line.lstrip())
                    
                    elif current_function and line.strip() and len(line) - len(line.lstrip()) <= indent_level and not line.startswith(' ' * (indent_level + 4)):
                        if i - function_start > 50:
                            issues.append(CodeIssue(
                                file_path=str(py_file.relative_to(self.project_root)),
                                line_number=function_start,
                                column=0,
                                issue_type="complexity",
                                severity="warning",
                                message=f"函数 {current_function} 过长 ({i - function_start} 行)",
                                rule_code="function_length"
                            ))
                        current_function = None
                        
            except Exception as e:
                logger.warning(f"分析文件 {py_file} 时出错: {e}")
        
        logger.info(f"   发现 {len(issues)} 个复杂度问题")
        return issues
    
    def check_security_issues(self) -> List[CodeIssue]:
        """检查安全问题"""
        logger.info("🔍 检查安全问题...")
        
        issues = []
        security_patterns = [
            ("password", "密码相关代码需要特别注意"),
            ("secret", "密钥相关代码需要特别注意"),
            ("token", "令牌相关代码需要特别注意"),
            ("eval(", "使用eval()可能存在安全风险"),
            ("exec(", "使用exec()可能存在安全风险"),
            ("shell=True", "使用shell=True可能存在命令注入风险"),
            ("pickle.loads", "使用pickle.loads可能存在反序列化风险"),
        ]
        
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if "venv" in str(py_file) or "cleanup_backup" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines, 1):
                    line_lower = line.lower()
                    for pattern, message in security_patterns:
                        if pattern in line_lower:
                            issues.append(CodeIssue(
                                file_path=str(py_file.relative_to(self.project_root)),
                                line_number=i,
                                column=line.find(pattern),
                                issue_type="security",
                                severity="warning",
                                message=message,
                                rule_code="security_check"
                            ))
                            
            except Exception as e:
                logger.warning(f"检查文件 {py_file} 时出错: {e}")
        
        logger.info(f"   发现 {len(issues)} 个潜在安全问题")
        return issues
    
    def analyze_imports(self) -> List[CodeIssue]:
        """分析导入问题"""
        logger.info("🔍 分析导入问题...")
        
        issues = []
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if "venv" in str(py_file) or "cleanup_backup" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                # 检查通配符导入
                for i, line in enumerate(lines, 1):
                    if 'from' in line and 'import *' in line:
                        issues.append(CodeIssue(
                            file_path=str(py_file.relative_to(self.project_root)),
                            line_number=i,
                            column=0,
                            issue_type="import",
                            severity="warning",
                            message="避免使用通配符导入 (import *)",
                            rule_code="wildcard_import"
                        ))
                
                # 检查未使用的导入 (简单检查)
                import_lines = []
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_lines.append((i, line.strip()))
                
                for line_num, import_line in import_lines:
                    if 'import' in import_line:
                        # 提取导入的模块名
                        if 'from' in import_line:
                            parts = import_line.split('import')
                            if len(parts) > 1:
                                imported = parts[1].strip().split(',')
                                for imp in imported:
                                    imp_name = imp.strip().split(' as ')[0]
                                    if imp_name not in content.replace(import_line, ''):
                                        issues.append(CodeIssue(
                                            file_path=str(py_file.relative_to(self.project_root)),
                                            line_number=line_num,
                                            column=0,
                                            issue_type="import",
                                            severity="info",
                                            message=f"可能未使用的导入: {imp_name}",
                                            rule_code="unused_import"
                                        ))
                        
            except Exception as e:
                logger.warning(f"分析文件 {py_file} 时出错: {e}")
        
        logger.info(f"   发现 {len(issues)} 个导入问题")
        return issues
    
    def _get_severity_from_code(self, code: str) -> str:
        """根据错误代码确定严重程度"""
        if code.startswith('E'):
            return "error"
        elif code.startswith('W'):
            return "warning"
        elif code.startswith('F'):
            return "error"
        else:
            return "info"
    
    def run_full_analysis(self) -> None:
        """运行完整分析"""
        logger.info("🚀 开始完整代码质量分析...")
        
        # 收集所有问题
        all_issues = []
        
        # Flake8 分析
        all_issues.extend(self.run_flake8_analysis())
        
        # MyPy 分析
        all_issues.extend(self.run_mypy_analysis())
        
        # 复杂度分析
        all_issues.extend(self.analyze_code_complexity())
        
        # 安全检查
        all_issues.extend(self.check_security_issues())
        
        # 导入分析
        all_issues.extend(self.analyze_imports())
        
        self.issues = all_issues
        self._calculate_stats()
    
    def _calculate_stats(self) -> None:
        """计算统计信息"""
        python_files = list(self.project_root.rglob("*.py"))
        self.stats['total_files'] = len([f for f in python_files if "venv" not in str(f) and "cleanup_backup" not in str(f)])
        
        total_lines = 0
        for py_file in python_files:
            if "venv" not in str(py_file) and "cleanup_backup" not in str(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        total_lines += len(f.readlines())
                except:
                    pass
        
        self.stats['total_lines'] = total_lines
        
        for issue in self.issues:
            self.stats['issues_by_type'][issue.issue_type] += 1
            self.stats['issues_by_severity'][issue.severity] += 1
            self.stats['files_with_issues'].add(issue.file_path)
    
    def generate_report(self) -> str:
        """生成分析报告"""
        report = []
        report.append("# 索克生活认证服务 - 代码质量分析报告")
        report.append("=" * 60)
        report.append("")
        
        # 总体统计
        report.append("## 📊 总体统计")
        report.append(f"- 总文件数: {self.stats['total_files']}")
        report.append(f"- 总代码行数: {self.stats['total_lines']:,}")
        report.append(f"- 发现问题总数: {len(self.issues)}")
        report.append(f"- 有问题的文件数: {len(self.stats['files_with_issues'])}")
        report.append("")
        
        # 问题类型分布
        report.append("## 🔍 问题类型分布")
        for issue_type, count in self.stats['issues_by_type'].items():
            report.append(f"- {issue_type}: {count} 个问题")
        report.append("")
        
        # 严重程度分布
        report.append("## ⚠️ 严重程度分布")
        for severity, count in self.stats['issues_by_severity'].items():
            emoji = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(severity, "⚪")
            report.append(f"- {emoji} {severity}: {count} 个问题")
        report.append("")
        
        # 详细问题列表
        report.append("## 📋 详细问题列表")
        
        # 按文件分组
        issues_by_file = defaultdict(list)
        for issue in self.issues:
            issues_by_file[issue.file_path].append(issue)
        
        for file_path in sorted(issues_by_file.keys()):
            report.append(f"\n### 📄 {file_path}")
            
            for issue in sorted(issues_by_file[file_path], key=lambda x: x.line_number):
                emoji = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(issue.severity, "⚪")
                report.append(f"- {emoji} 第{issue.line_number}行: [{issue.rule_code}] {issue.message}")
        
        # 修复建议
        report.append("\n## 🛠️ 修复建议")
        report.append("\n### 高优先级修复")
        
        high_priority = [issue for issue in self.issues if issue.severity == "error"]
        if high_priority:
            for issue in high_priority[:10]:  # 显示前10个
                report.append(f"- {issue.file_path}:{issue.line_number} - {issue.message}")
        else:
            report.append("- ✅ 没有高优先级问题")
        
        report.append("\n### 代码质量改进建议")
        report.append("1. 修复所有 Flake8 代码风格问题")
        report.append("2. 添加类型注解，修复 MyPy 类型检查问题")
        report.append("3. 重构过长的函数和文件")
        report.append("4. 移除未使用的导入")
        report.append("5. 审查安全相关代码")
        
        # 质量评分
        total_issues = len(self.issues)
        total_lines = self.stats['total_lines']
        
        if total_lines > 0:
            issues_per_1000_lines = (total_issues / total_lines) * 1000
            
            if issues_per_1000_lines < 10:
                quality_score = "A (优秀)"
            elif issues_per_1000_lines < 25:
                quality_score = "B (良好)"
            elif issues_per_1000_lines < 50:
                quality_score = "C (一般)"
            else:
                quality_score = "D (需要改进)"
        else:
            quality_score = "无法评估"
        
        report.append(f"\n## 🏆 代码质量评分: {quality_score}")
        report.append(f"- 每千行代码问题数: {issues_per_1000_lines:.1f}")
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "CODE_QUALITY_REPORT.md") -> None:
        """保存报告到文件"""
        report_content = self.generate_report()
        report_path = self.project_root / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"📄 报告已保存到: {report_path}")
    
    def auto_fix_simple_issues(self) -> None:
        """自动修复简单问题"""
        logger.info("🔧 开始自动修复简单问题...")
        
        fixed_count = 0
        
        # 运行 black 格式化
        try:
            subprocess.run(
                ["black", "--line-length=120", "internal/", "app/", "api/"],
                cwd=self.project_root,
                check=True
            )
            logger.info("   ✅ Black 代码格式化完成")
            fixed_count += 1
        except Exception as e:
            logger.error(f"   ❌ Black 格式化失败: {e}")
        
        # 运行 isort 导入排序
        try:
            subprocess.run(
                ["isort", "--profile=black", "internal/", "app/", "api/"],
                cwd=self.project_root,
                check=True
            )
            logger.info("   ✅ isort 导入排序完成")
            fixed_count += 1
        except Exception as e:
            logger.error(f"   ❌ isort 排序失败: {e}")
        
        logger.info(f"🎉 自动修复完成，修复了 {fixed_count} 类问题")


def main():
    """主函数"""
    print("🔍 索克生活认证服务 - 代码质量分析器")
    print("=" * 50)
    
    analyzer = CodeQualityAnalyzer()
    
    # 运行完整分析
    analyzer.run_full_analysis()
    
    # 显示简要统计
    print(f"\n📊 分析完成:")
    print(f"   - 总文件数: {analyzer.stats['total_files']}")
    print(f"   - 总代码行数: {analyzer.stats['total_lines']:,}")
    print(f"   - 发现问题: {len(analyzer.issues)} 个")
    print(f"   - 有问题的文件: {len(analyzer.stats['files_with_issues'])} 个")
    
    # 保存详细报告
    analyzer.save_report()
    
    # 询问是否自动修复
    if analyzer.issues:
        response = input(f"\n发现 {len(analyzer.issues)} 个问题，是否自动修复简单问题? (y/N): ")
        if response.lower() in ['y', 'yes']:
            analyzer.auto_fix_simple_issues()
            print("\n建议重新运行分析以查看修复效果。")
    
    print("\n🎉 代码质量分析完成!")
    print("详细报告已保存到 CODE_QUALITY_REPORT.md")


if __name__ == "__main__":
    main() 