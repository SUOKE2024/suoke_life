#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安全检查脚本

自动检测依赖库漏洞、代码安全问题和配置安全问题
可集成到CI/CD流程中作为安全门控
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# 颜色常量
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

# 安全工具配置
TOOLS = {
    "safety": {
        "cmd": ["safety", "check", "--json", "-r"],
        "install": "pip install safety",
        "description": "检查Python依赖中的已知安全漏洞",
    },
    "bandit": {
        "cmd": ["bandit", "-r", "-f", "json"],
        "install": "pip install bandit",
        "description": "Python代码静态安全分析",
    },
    "semgrep": {
        "cmd": ["semgrep", "--config=p/python", "--json", "--metrics", "off"],
        "install": "pip install semgrep",
        "description": "语义模式匹配的代码分析",
    },
    "trufflehog": {
        "cmd": ["trufflehog", "filesystem", "--json"],
        "install": "pip install trufflehog",
        "description": "检测代码中的密钥和凭证",
    },
}

# 设置最大允许的漏洞数量（CI门控）
MAX_VULNERABILITIES = {
    "safety": {"high": 0, "medium": 5, "low": 10},
    "bandit": {"high": 0, "medium": 3, "low": 10},
    "semgrep": {"high": 0, "medium": 5, "low": 10},
    "trufflehog": {"high": 0, "medium": 0, "low": 0},
}


def print_colored(text: str, color: str, bold: bool = False) -> None:
    """
    打印彩色文本
    
    Args:
        text: 要打印的文本
        color: 颜色代码
        bold: 是否加粗
    """
    if bold:
        print(f"{BOLD}{color}{text}{RESET}")
    else:
        print(f"{color}{text}{RESET}")


def check_tool_installed(tool_name: str) -> bool:
    """
    检查工具是否已安装
    
    Args:
        tool_name: 工具名称
        
    Returns:
        是否已安装
    """
    try:
        subprocess.run(
            ["which", tool_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError:
        return False


def install_tools() -> List[str]:
    """
    安装所有必要的安全工具
    
    Returns:
        未能安装的工具列表
    """
    failed_tools = []
    
    for tool_name, tool_info in TOOLS.items():
        if not check_tool_installed(tool_name):
            print_colored(f"安装 {tool_name}...", BLUE)
            try:
                subprocess.run(
                    tool_info["install"].split(),
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print_colored(f"{tool_name} 安装成功", GREEN)
            except subprocess.CalledProcessError as e:
                print_colored(f"{tool_name} 安装失败: {e}", RED)
                failed_tools.append(tool_name)
    
    return failed_tools


def run_safety_check(requirements_file: Path) -> Tuple[List[Dict], int, int, int]:
    """
    运行Safety检查依赖漏洞
    
    Args:
        requirements_file: requirements.txt文件路径
        
    Returns:
        (漏洞列表, 高危数量, 中危数量, 低危数量)
    """
    print_colored("运行 Safety 检查依赖库漏洞...", BLUE, bold=True)
    
    cmd = TOOLS["safety"]["cmd"] + [str(requirements_file)]
    
    try:
        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Safety返回非零状态码表示发现漏洞
        if result.returncode != 0 and result.stdout:
            vulnerabilities = json.loads(result.stdout)
            
            high = len([v for v in vulnerabilities if v.get("severity", "") == "high"])
            medium = len([v for v in vulnerabilities if v.get("severity", "") == "medium"])
            low = len([v for v in vulnerabilities if v.get("severity", "") == "low"])
            
            return vulnerabilities, high, medium, low
        
        return [], 0, 0, 0
    
    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        print_colored(f"Safety 检查失败: {e}", RED)
        return [], 0, 0, 0


def run_bandit_check(code_path: Path) -> Tuple[List[Dict], int, int, int]:
    """
    运行Bandit代码安全检查
    
    Args:
        code_path: 代码路径
        
    Returns:
        (问题列表, 高危数量, 中危数量, 低危数量)
    """
    print_colored("运行 Bandit 代码安全检查...", BLUE, bold=True)
    
    cmd = TOOLS["bandit"]["cmd"] + [str(code_path)]
    
    try:
        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Bandit返回非零状态码表示发现问题
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                issues = data.get("results", [])
                
                high = len([i for i in issues if i.get("issue_severity") == "HIGH"])
                medium = len([i for i in issues if i.get("issue_severity") == "MEDIUM"])
                low = len([i for i in issues if i.get("issue_severity") == "LOW"])
                
                return issues, high, medium, low
            except json.JSONDecodeError:
                print_colored("Bandit 输出解析失败", RED)
        
        return [], 0, 0, 0
    
    except subprocess.SubprocessError as e:
        print_colored(f"Bandit 检查失败: {e}", RED)
        return [], 0, 0, 0


def run_semgrep_check(code_path: Path) -> Tuple[List[Dict], int, int, int]:
    """
    运行Semgrep代码模式匹配检查
    
    Args:
        code_path: 代码路径
        
    Returns:
        (问题列表, 高危数量, 中危数量, 低危数量)
    """
    print_colored("运行 Semgrep 代码分析...", BLUE, bold=True)
    
    cmd = TOOLS["semgrep"]["cmd"] + [str(code_path)]
    
    try:
        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                issues = data.get("results", [])
                
                high = len([i for i in issues if i.get("extra", {}).get("severity") == "ERROR"])
                medium = len([i for i in issues if i.get("extra", {}).get("severity") == "WARNING"])
                low = len([i for i in issues if i.get("extra", {}).get("severity") == "INFO"])
                
                return issues, high, medium, low
            except json.JSONDecodeError:
                print_colored("Semgrep 输出解析失败", RED)
        
        return [], 0, 0, 0
    
    except subprocess.SubprocessError as e:
        print_colored(f"Semgrep 检查失败: {e}", RED)
        return [], 0, 0, 0


def run_trufflehog_check(code_path: Path) -> Tuple[List[Dict], int, int, int]:
    """
    运行TruffleHog检查密钥泄露
    
    Args:
        code_path: 代码路径
        
    Returns:
        (问题列表, 高危数量, 中危数量, 低危数量)
    """
    print_colored("运行 TruffleHog 密钥泄露检查...", BLUE, bold=True)
    
    cmd = TOOLS["trufflehog"]["cmd"] + [str(code_path)]
    
    try:
        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        if result.stdout:
            # TruffleHog输出每行一个JSON对象
            lines = result.stdout.strip().split("\n")
            issues = [json.loads(line) for line in lines if line.strip()]
            
            # 所有密钥泄露都认为是高危
            high = len(issues)
            medium = 0
            low = 0
            
            return issues, high, medium, low
        
        return [], 0, 0, 0
    
    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        print_colored(f"TruffleHog 检查失败: {e}", RED)
        return [], 0, 0, 0


def print_safety_vulnerabilities(vulnerabilities: List[Dict]) -> None:
    """
    打印Safety发现的依赖漏洞
    
    Args:
        vulnerabilities: 漏洞列表
    """
    if not vulnerabilities:
        print_colored("未发现依赖库漏洞", GREEN)
        return
    
    print_colored(f"发现 {len(vulnerabilities)} 个依赖库漏洞:", YELLOW, bold=True)
    
    for i, vuln in enumerate(vulnerabilities, 1):
        severity = vuln.get("severity", "unknown")
        color = RED if severity == "high" else (YELLOW if severity == "medium" else BLUE)
        
        print_colored(f"\n漏洞 #{i}:", color, bold=True)
        print(f"包名: {vuln.get('package_name', 'N/A')}")
        print(f"受影响版本: {vuln.get('vulnerable_spec', 'N/A')}")
        print(f"安装版本: {vuln.get('installed_version', 'N/A')}")
        print(f"严重级别: {severity.upper()}")
        print(f"漏洞ID: {vuln.get('vulnerability_id', 'N/A')}")
        print(f"描述: {vuln.get('advisory', 'N/A')}")
        print(f"修复建议: 升级到 {vuln.get('fix_version', '(无修复版本)')}")


def print_bandit_issues(issues: List[Dict]) -> None:
    """
    打印Bandit发现的代码安全问题
    
    Args:
        issues: 问题列表
    """
    if not issues:
        print_colored("未发现代码安全问题", GREEN)
        return
    
    print_colored(f"发现 {len(issues)} 个代码安全问题:", YELLOW, bold=True)
    
    for i, issue in enumerate(issues, 1):
        severity = issue.get("issue_severity", "UNKNOWN")
        color = RED if severity == "HIGH" else (YELLOW if severity == "MEDIUM" else BLUE)
        
        print_colored(f"\n问题 #{i}:", color, bold=True)
        print(f"文件: {issue.get('filename', 'N/A')}:{issue.get('line_number', 'N/A')}")
        print(f"严重级别: {severity}")
        print(f"置信度: {issue.get('issue_confidence', 'N/A')}")
        print(f"问题类型: {issue.get('issue_text', 'N/A')}")
        print(f"代码: {issue.get('code', 'N/A')}")
        print(f"CWE: {issue.get('cwe', {}).get('id', 'N/A')}")


def print_semgrep_issues(issues: List[Dict]) -> None:
    """
    打印Semgrep发现的代码问题
    
    Args:
        issues: 问题列表
    """
    if not issues:
        print_colored("未发现代码模式问题", GREEN)
        return
    
    print_colored(f"发现 {len(issues)} 个代码模式问题:", YELLOW, bold=True)
    
    for i, issue in enumerate(issues, 1):
        severity = issue.get("extra", {}).get("severity", "UNKNOWN")
        color = RED if severity == "ERROR" else (YELLOW if severity == "WARNING" else BLUE)
        
        print_colored(f"\n问题 #{i}:", color, bold=True)
        print(f"文件: {issue.get('path', 'N/A')}:{issue.get('start', {}).get('line', 'N/A')}")
        print(f"严重级别: {severity}")
        print(f"规则ID: {issue.get('check_id', 'N/A')}")
        print(f"问题描述: {issue.get('extra', {}).get('message', 'N/A')}")
        print(f"代码: {issue.get('extra', {}).get('lines', 'N/A')}")


def print_trufflehog_issues(issues: List[Dict]) -> None:
    """
    打印TruffleHog发现的密钥泄露
    
    Args:
        issues: 问题列表
    """
    if not issues:
        print_colored("未发现密钥泄露", GREEN)
        return
    
    print_colored(f"发现 {len(issues)} 个密钥泄露!", RED, bold=True)
    
    for i, issue in enumerate(issues, 1):
        print_colored(f"\n泄露 #{i}:", RED, bold=True)
        print(f"文件: {issue.get('SourceMetadata', {}).get('Data', {}).get('Filename', 'N/A')}")
        print(f"类型: {issue.get('DetectorType', 'N/A')}")
        print(f"描述: {issue.get('Description', 'N/A')}")
        
        # 不要直接打印实际的密钥
        print(f"行: {issue.get('SourceMetadata', {}).get('Data', {}).get('Line', 'N/A')}")
        print("警告: 发现可能的密钥泄露，请立即处理！")


def check_security(code_path: Path, requirements_file: Path, detailed: bool) -> bool:
    """
    运行所有安全检查
    
    Args:
        code_path: 代码路径
        requirements_file: requirements.txt文件路径
        detailed: 是否显示详细报告
        
    Returns:
        是否通过安全检查
    """
    print_colored("\n安全检查开始...", BLUE, bold=True)
    print(f"代码路径: {code_path}")
    print(f"依赖文件: {requirements_file}")
    print("-" * 80)
    
    # 检查Safety
    safety_vulns, safety_high, safety_medium, safety_low = run_safety_check(requirements_file)
    
    if detailed:
        print_safety_vulnerabilities(safety_vulns)
    else:
        print_colored(
            f"依赖库漏洞: 高危 {safety_high}, 中危 {safety_medium}, 低危 {safety_low}",
            RED if safety_high > 0 else (YELLOW if safety_medium > 0 else GREEN)
        )
    
    print("-" * 80)
    
    # 检查Bandit
    bandit_issues, bandit_high, bandit_medium, bandit_low = run_bandit_check(code_path)
    
    if detailed:
        print_bandit_issues(bandit_issues)
    else:
        print_colored(
            f"代码安全问题: 高危 {bandit_high}, 中危 {bandit_medium}, 低危 {bandit_low}",
            RED if bandit_high > 0 else (YELLOW if bandit_medium > 0 else GREEN)
        )
    
    print("-" * 80)
    
    # 检查Semgrep
    semgrep_issues, semgrep_high, semgrep_medium, semgrep_low = run_semgrep_check(code_path)
    
    if detailed:
        print_semgrep_issues(semgrep_issues)
    else:
        print_colored(
            f"代码模式问题: 高危 {semgrep_high}, 中危 {semgrep_medium}, 低危 {semgrep_low}",
            RED if semgrep_high > 0 else (YELLOW if semgrep_medium > 0 else GREEN)
        )
    
    print("-" * 80)
    
    # 检查TruffleHog
    trufflehog_issues, trufflehog_high, trufflehog_medium, trufflehog_low = run_trufflehog_check(code_path)
    
    if detailed:
        print_trufflehog_issues(trufflehog_issues)
    else:
        print_colored(
            f"密钥泄露: {trufflehog_high} 个",
            RED if trufflehog_high > 0 else GREEN
        )
    
    print("-" * 80)
    
    # 检查是否违反安全门控标准
    safety_fail = (
        safety_high > MAX_VULNERABILITIES["safety"]["high"] or
        safety_medium > MAX_VULNERABILITIES["safety"]["medium"] or
        safety_low > MAX_VULNERABILITIES["safety"]["low"]
    )
    
    bandit_fail = (
        bandit_high > MAX_VULNERABILITIES["bandit"]["high"] or
        bandit_medium > MAX_VULNERABILITIES["bandit"]["medium"] or
        bandit_low > MAX_VULNERABILITIES["bandit"]["low"]
    )
    
    semgrep_fail = (
        semgrep_high > MAX_VULNERABILITIES["semgrep"]["high"] or
        semgrep_medium > MAX_VULNERABILITIES["semgrep"]["medium"] or
        semgrep_low > MAX_VULNERABILITIES["semgrep"]["low"]
    )
    
    trufflehog_fail = (
        trufflehog_high > MAX_VULNERABILITIES["trufflehog"]["high"] or
        trufflehog_medium > MAX_VULNERABILITIES["trufflehog"]["medium"] or
        trufflehog_low > MAX_VULNERABILITIES["trufflehog"]["low"]
    )
    
    # 总结结果
    if safety_fail or bandit_fail or semgrep_fail or trufflehog_fail:
        print_colored("安全检查未通过!", RED, bold=True)
        
        if safety_fail:
            print_colored(f"✘ 依赖库漏洞超过允许的阈值", RED)
        
        if bandit_fail:
            print_colored(f"✘ 代码安全问题超过允许的阈值", RED)
        
        if semgrep_fail:
            print_colored(f"✘ 代码模式问题超过允许的阈值", RED)
        
        if trufflehog_fail:
            print_colored(f"✘ 发现密钥泄露，这是不允许的", RED)
        
        return False
    else:
        print_colored("✓ 安全检查通过!", GREEN, bold=True)
        return True


def main() -> int:
    """
    主函数
    
    处理命令行参数并运行安全检查
    
    Returns:
        退出码
    """
    parser = argparse.ArgumentParser(description="运行安全检查工具")
    parser.add_argument(
        "--code-path",
        "-c",
        type=str,
        default=".",
        help="要检查的代码目录路径"
    )
    parser.add_argument(
        "--requirements",
        "-r",
        type=str,
        default="requirements.txt",
        help="requirements.txt文件路径"
    )
    parser.add_argument(
        "--install-tools",
        "-i",
        action="store_true",
        help="安装所需的安全工具"
    )
    parser.add_argument(
        "--detailed",
        "-d",
        action="store_true",
        help="显示详细报告"
    )
    
    args = parser.parse_args()
    
    code_path = Path(args.code_path)
    requirements_file = Path(args.requirements)
    
    # 检查路径有效性
    if not code_path.exists():
        print_colored(f"错误: 代码路径 '{code_path}' 不存在", RED)
        return 1
    
    if not requirements_file.exists():
        print_colored(f"错误: requirements.txt 文件 '{requirements_file}' 不存在", RED)
        return 1
    
    # 安装工具(如果需要)
    if args.install_tools:
        failed_tools = install_tools()
        if failed_tools:
            print_colored(
                f"警告: 以下工具安装失败: {', '.join(failed_tools)}",
                YELLOW
            )
    
    # 运行安全检查
    success = check_security(code_path, requirements_file, args.detailed)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 