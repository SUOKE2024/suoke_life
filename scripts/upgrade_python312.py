#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 3.12升级协调脚本

此脚本用于协调索克生活项目中所有Python服务从旧版本升级到Python 3.12的过程
"""

import os
import sys
import subprocess
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# 设置脚本路径
SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent

# 定义升级步骤
STEPS = [
    "check_compatibility",
    "update_dockerfiles",
    "update_workflows",
    "test_compatibility",
    "update_requirements",
]

# 颜色代码，用于终端输出
COLORS = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "ENDC": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
}

def print_colored(text: str, color: str) -> None:
    """打印彩色文本"""
    print(f"{COLORS.get(color, '')}{text}{COLORS['ENDC']}")

def run_script(script_name: str, args: Optional[List[str]] = None) -> int:
    """运行指定的Python脚本"""
    script_path = SCRIPTS_DIR / script_name
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    print_colored(f"运行脚本: {' '.join(cmd)}", "BLUE")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        print_colored(f"运行脚本 {script_name} 时出错: {str(e)}", "RED")
        return 1

def check_compatibility() -> bool:
    """检查依赖与Python 3.12的兼容性"""
    print_colored("\n=== 步骤1: 检查依赖与Python 3.12的兼容性 ===", "HEADER")
    
    # 运行兼容性检查脚本
    return run_script("check_python312_compatibility.py") == 0

def update_dockerfiles() -> bool:
    """更新Dockerfile中的Python版本"""
    print_colored("\n=== 步骤2: 更新Dockerfile中的Python版本 ===", "HEADER")
    
    # 运行Dockerfile更新脚本
    return run_script("update_dockerfiles.py") == 0

def update_workflows() -> bool:
    """更新GitHub Actions工作流中的Python版本"""
    print_colored("\n=== 步骤3: 更新GitHub Actions工作流中的Python版本 ===", "HEADER")
    
    # 运行工作流更新脚本
    return run_script("update_github_workflows.py") == 0

def test_compatibility() -> bool:
    """测试代码与Python 3.12的兼容性"""
    print_colored("\n=== 步骤4: 测试代码与Python 3.12的兼容性 ===", "HEADER")
    
    print_colored("注意: 测试代码兼容性需要Python 3.12环境", "YELLOW")
    
    # 检查当前Python版本
    if sys.version_info.major != 3 or sys.version_info.minor != 12:
        print_colored(f"警告: 当前Python版本为 {sys.version_info.major}.{sys.version_info.minor}, 但此步骤需要Python 3.12", "YELLOW")
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            return False
    
    print_colored("此步骤将运行单元测试以验证兼容性", "BLUE")
    print_colored("由于测试可能需要特殊环境，此步骤将在后续手动完成", "YELLOW")
    return True

def update_requirements() -> bool:
    """更新requirements.txt文件，如果需要"""
    print_colored("\n=== 步骤5: 更新requirements.txt文件 ===", "HEADER")
    
    print_colored("此步骤将检查并更新不兼容的依赖版本", "BLUE")
    print_colored("需要基于兼容性检查结果手动更新", "YELLOW")
    
    # 检查兼容性结果文件是否存在
    compatibility_results = SCRIPTS_DIR / "python312_compatibility_results.json"
    if not compatibility_results.exists():
        print_colored(f"找不到兼容性检查结果文件: {compatibility_results}", "RED")
        print_colored("请先运行兼容性检查步骤", "RED")
        return False
    
    # 读取兼容性结果
    try:
        with open(compatibility_results, "r") as f:
            results = json.load(f)
        
        # 显示不兼容的包
        incompatible_found = False
        for service, service_results in results.items():
            if service_results.get("incompatible"):
                incompatible_found = True
                print_colored(f"\n服务: {service}", "BOLD")
                print_colored("不兼容的包:", "YELLOW")
                for pkg in service_results["incompatible"]:
                    print(f"  - {pkg}")
        
        if not incompatible_found:
            print_colored("所有依赖都兼容Python 3.12，无需更新requirements.txt", "GREEN")
        else:
            print_colored("\n请手动更新requirements.txt文件中的不兼容包", "YELLOW")
            print_colored("完成后，重新运行兼容性检查以验证", "YELLOW")
    
    except Exception as e:
        print_colored(f"读取兼容性结果时出错: {str(e)}", "RED")
        return False
    
    return True

def generate_summary(results: Dict[str, bool]) -> None:
    """生成升级过程摘要"""
    print_colored("\n=== Python 3.12升级摘要 ===", "HEADER")
    
    all_success = all(results.values())
    
    # 显示每个步骤的结果
    for step, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        color = "GREEN" if success else "RED"
        print_colored(f"{step}: {status}", color)
    
    # 显示总结
    if all_success:
        print_colored("\n所有步骤都已成功完成!", "GREEN")
        print_colored("Python 3.12升级过程已完成", "GREEN")
    else:
        print_colored("\n部分步骤失败，请解决问题后重试", "RED")
        failed_steps = [step for step, success in results.items() if not success]
        print_colored(f"失败的步骤: {', '.join(failed_steps)}", "RED")
    
    # 下一步建议
    print_colored("\n接下来的步骤:", "BOLD")
    if all_success:
        print("1. 在Docker容器中测试各个服务")
        print("2. 更新CI/CD管道配置")
        print("3. 在测试环境中部署并验证")
        print("4. 完成生产环境迁移计划")
    else:
        print("1. 解决失败步骤中的问题")
        print("2. 重新运行升级脚本")
        print(f"   - 指定特定步骤: python {__file__} --step <step_name>")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Python 3.12升级协调脚本')
    parser.add_argument('--step', type=str, choices=STEPS, help='只运行指定的步骤')
    parser.add_argument('--skip', type=str, choices=STEPS, nargs='+', help='跳过指定的步骤')
    
    return parser.parse_args()

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    print_colored("=== 索克生活Python 3.12升级 ===", "HEADER")
    print_colored(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}", "BLUE")
    print("")
    
    # 记录步骤结果
    results = {}
    
    # 确定要运行的步骤
    steps_to_run = []
    if args.step:
        steps_to_run = [args.step]
    else:
        steps_to_run = STEPS
        if args.skip:
            steps_to_run = [s for s in steps_to_run if s not in args.skip]
    
    # 运行每个步骤
    if "check_compatibility" in steps_to_run:
        results["检查兼容性"] = check_compatibility()
    
    if "update_dockerfiles" in steps_to_run:
        results["更新Dockerfile"] = update_dockerfiles()
    
    if "update_workflows" in steps_to_run:
        results["更新工作流"] = update_workflows()
    
    if "test_compatibility" in steps_to_run:
        results["测试兼容性"] = test_compatibility()
    
    if "update_requirements" in steps_to_run:
        results["更新依赖"] = update_requirements()
    
    # 生成摘要
    generate_summary(results)
    
    print_colored(f"\n完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}", "BLUE")

if __name__ == "__main__":
    main()