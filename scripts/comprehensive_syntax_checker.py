#!/usr/bin/env python3
"""
索克生活微服务综合语法检查和修复工具
基于项目现有代码结构及具体实现，洞察微服务语法错误并修复
"""

import os
import re
import ast
import json
import logging
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SyntaxIssue:
    """语法问题数据类"""
    file: str
    line: int
    column: int
    message: str
    text: str
    error_type: str = "SyntaxError"
    severity: str = "error"

class ComprehensiveSyntaxChecker:
    """综合语法检查器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues_found = []
        self.issues_fixed = 0
        self.files_processed = 0
        
        # 微服务路径
        self.microservices = [
            "services/agent-services/xiaoai-service",
            "services/agent-services/xiaoke-service", 
            "services/agent-services/laoke-service",
            "services/agent-services/soer-service",
            "services/ai-model-service",
            "services/api-gateway",
            "services/blockchain-service",
            "services/communication-service",
            "services/diagnostic-services",
            "services/unified-health-data-service",
            "services/unified-knowledge-service",
            "services/unified-support-service",
            "services/user-management-service",
            "services/utility-services"
        ]
        
    def find_python_files(self, service_path: Path) -> List[Path]:
        """查找服务中的Python文件"""
        python_files = []
        
        if not service_path.exists():
            logger.warning(f"服务路径不存在: {service_path}")
            return python_files
            
        # 排除虚拟环境和缓存目录
        exclude_patterns = [
            "*/.venv/*", "*/__pycache__/*", "*/.pytest_cache/*",
            "*/.ruff_cache/*", "*/venv/*", "*/env/*", "*/.benchmarks/*"
        ]
        
        for py_file in service_path.rglob("*.py"):
            # 检查是否在排除列表中
            should_exclude = False
            for pattern in exclude_patterns:
                if py_file.match(pattern):
                    should_exclude = True
                    break
                    
            if not should_exclude:
                python_files.append(py_file)
                
        return python_files
        
    def check_file_syntax(self, file_path: Path) -> List[SyntaxIssue]:
        """检查单个文件的语法"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 使用AST检查语法
            try:
                ast.parse(content)
            except SyntaxError as e:
                relative_path = file_path.relative_to(self.project_root)
                issue = SyntaxIssue(
                    file=str(relative_path),
                    line=e.lineno or 0,
                    column=e.offset or 0,
                    message=str(e.msg),
                    text=e.text or "",
                    error_type="SyntaxError",
                    severity="error"
                )
                issues.append(issue)
                
            # 检查常见的代码质量问题
            issues.extend(self._check_code_quality(file_path, content))
                
        except Exception as e:
            logger.error(f"检查文件失败 {file_path}: {e}")
            
        return issues
        
    def _check_code_quality(self, file_path: Path, content: str) -> List[SyntaxIssue]:
        """检查代码质量问题"""
        issues = []
        lines = content.split('\n')
        relative_path = file_path.relative_to(self.project_root)
        
        for i, line in enumerate(lines, 1):
            # 检查混合缩进
            if '\t' in line and '    ' in line:
                issues.append(SyntaxIssue(
                    file=str(relative_path),
                    line=i,
                    column=0,
                    message="混合使用制表符和空格进行缩进",
                    text=line,
                    error_type="IndentationWarning",
                    severity="warning"
                ))
                
            # 检查行尾空白
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(SyntaxIssue(
                    file=str(relative_path),
                    line=i,
                    column=len(line.rstrip()),
                    message="行尾有多余的空白字符",
                    text=line,
                    error_type="WhitespaceWarning",
                    severity="warning"
                ))
                
            # 检查过长的行
            if len(line) > 120:
                issues.append(SyntaxIssue(
                    file=str(relative_path),
                    line=i,
                    column=120,
                    message=f"行长度超过120字符 ({len(line)})",
                    text=line,
                    error_type="LineLengthWarning",
                    severity="warning"
                ))
                
        return issues
        
    def fix_syntax_issues(self, file_path: Path, issues: List[SyntaxIssue]) -> bool:
        """修复文件中的语法问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # 修复缩进问题
            content = self._fix_indentation_issues(content)
            
            # 修复空白字符问题
            content = self._fix_whitespace_issues(content)
            
            # 修复import问题
            content = self._fix_import_issues(content)
            
            # 验证修复后的语法
            try:
                ast.parse(content)
                
                # 只有在内容发生变化时才写入
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"成功修复文件: {file_path}")
                    self.issues_fixed += len([i for i in issues if i.severity == "error"])
                    return True
                    
            except SyntaxError as e:
                logger.error(f"文件修复后仍有语法错误 {file_path}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"修复文件失败 {file_path}: {e}")
            return False
            
        return False
        
    def _fix_indentation_issues(self, content: str) -> str:
        """修复缩进问题"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # 将制表符转换为4个空格
            if '\t' in line:
                line = line.expandtabs(4)
                
            # 修复明显的缩进错误
            if line.strip():
                # 检查是否需要缩进
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if (prev_line.endswith(':') and 
                        not line.startswith(' ') and 
                        not line.startswith('#') and
                        line.strip() != ''):
                        # 添加基本缩进
                        line = '    ' + line
                        
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def _fix_whitespace_issues(self, content: str) -> str:
        """修复空白字符问题"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 移除行尾空白
            line = line.rstrip()
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def _fix_import_issues(self, content: str) -> str:
        """修复import问题"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 修复多个import在同一行的问题
            if ' import ' in line and line.count(' import ') > 1:
                # 分割多个import
                parts = line.split(' import ')
                if len(parts) > 2:
                    # 重构为多行import
                    base = parts[0] + ' import ' + parts[1]
                    fixed_lines.append(base)
                    for part in parts[2:]:
                        fixed_lines.append(f"from {parts[0].replace('from ', '')} import {part}")
                    continue
                    
            # 修复缩进的import语句
            if line.strip().startswith(('from ', 'import ')):
                if line.startswith(('    ', '\t')):
                    # 移除import语句前的缩进（除非在函数内部）
                    line = line.strip()
                    
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def scan_all_microservices(self) -> Dict[str, List[SyntaxIssue]]:
        """扫描所有微服务的语法问题"""
        all_issues = {}
        
        for service_name in self.microservices:
            service_path = self.project_root / service_name
            logger.info(f"扫描微服务: {service_name}")
            
            python_files = self.find_python_files(service_path)
            service_issues = []
            
            for py_file in python_files:
                issues = self.check_file_syntax(py_file)
                service_issues.extend(issues)
                self.files_processed += 1
                
            if service_issues:
                all_issues[service_name] = service_issues
                logger.info(f"  发现 {len(service_issues)} 个问题")
            else:
                logger.info(f"  未发现问题")
                
        return all_issues
        
    def fix_all_issues(self, all_issues: Dict[str, List[SyntaxIssue]]):
        """修复所有发现的问题"""
        files_to_fix = {}
        
        # 按文件分组问题
        for service_name, issues in all_issues.items():
            for issue in issues:
                file_path = self.project_root / issue.file
                if file_path not in files_to_fix:
                    files_to_fix[file_path] = []
                files_to_fix[file_path].append(issue)
                
        logger.info(f"需要修复 {len(files_to_fix)} 个文件")
        
        for file_path, issues in files_to_fix.items():
            if file_path.exists():
                # 只修复严重错误
                error_issues = [i for i in issues if i.severity == "error"]
                if error_issues:
                    self.fix_syntax_issues(file_path, error_issues)
                    
    def generate_report(self, all_issues: Dict[str, List[SyntaxIssue]], output_file: str = "syntax_check_report.json"):
        """生成检查报告"""
        total_issues = sum(len(issues) for issues in all_issues.values())
        error_count = sum(1 for issues in all_issues.values() 
                         for issue in issues if issue.severity == "error")
        warning_count = total_issues - error_count
        
        report = {
            "timestamp": str(Path().cwd()),
            "summary": {
                "files_processed": self.files_processed,
                "total_issues": total_issues,
                "errors": error_count,
                "warnings": warning_count,
                "issues_fixed": self.issues_fixed
            },
            "services": {}
        }
        
        for service_name, issues in all_issues.items():
            report["services"][service_name] = {
                "total_issues": len(issues),
                "errors": len([i for i in issues if i.severity == "error"]),
                "warnings": len([i for i in issues if i.severity == "warning"]),
                "issues": [
                    {
                        "file": issue.file,
                        "line": issue.line,
                        "column": issue.column,
                        "message": issue.message,
                        "type": issue.error_type,
                        "severity": issue.severity
                    }
                    for issue in issues[:10]  # 只显示前10个问题
                ]
            }
            
        output_path = self.project_root / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        logger.info(f"检查报告已生成: {output_path}")
        return report
        
    def run_comprehensive_check(self, fix_issues: bool = True):
        """运行综合检查"""
        logger.info("开始微服务综合语法检查...")
        
        # 1. 扫描所有微服务
        all_issues = self.scan_all_microservices()
        
        total_issues = sum(len(issues) for issues in all_issues.values())
        logger.info(f"扫描完成，发现 {total_issues} 个问题")
        
        # 2. 修复问题（如果启用）
        if fix_issues and all_issues:
            logger.info("开始修复语法错误...")
            self.fix_all_issues(all_issues)
            
        # 3. 生成报告
        report = self.generate_report(all_issues)
        
        # 4. 显示摘要
        print(f"\n检查摘要:")
        print(f"  处理文件数: {report['summary']['files_processed']}")
        print(f"  发现问题数: {report['summary']['total_issues']}")
        print(f"  错误数: {report['summary']['errors']}")
        print(f"  警告数: {report['summary']['warnings']}")
        print(f"  修复问题数: {report['summary']['issues_fixed']}")
        
        return report

def main():
    parser = argparse.ArgumentParser(description="索克生活微服务综合语法检查工具")
    parser.add_argument(
        "--project-root", 
        default=".", 
        help="项目根目录路径"
    )
    parser.add_argument(
        "--no-fix", 
        action="store_true", 
        help="仅检查，不修复问题"
    )
    parser.add_argument(
        "--service", 
        help="指定要检查的微服务名称"
    )
    
    args = parser.parse_args()
    
    checker = ComprehensiveSyntaxChecker(args.project_root)
    
    if args.service:
        # 只检查指定的微服务
        checker.microservices = [f"services/{args.service}"]
        
    checker.run_comprehensive_check(fix_issues=not args.no_fix)

if __name__ == "__main__":
    main() 