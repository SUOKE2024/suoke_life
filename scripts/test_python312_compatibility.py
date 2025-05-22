#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试服务在Python 3.12环境下的兼容性

此脚本运行各服务的单元测试和集成测试，验证它们在Python 3.12环境下是否正常工作
"""

import os
import sys
import subprocess
import json
import argparse
import shutil
import tempfile
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# 服务目录
SERVICES_DIR = Path(__file__).parent.parent / "services"

# 需要测试的服务类型目录
SERVICE_TYPES = [
    "accessibility-service",
    "agent-services",
    "api-gateway",
    "auth-service",
    "blockchain-service",
    "corn-maze-service",
    "diagnostic-services",
    "health-data-service",
    "med-knowledge",
    "medical-service",
    "message-bus",
    "rag-service",
    "suoke-bench-service",
    "user-service",
]

# 子服务目录 (在一些服务类型下有多个子服务)
SUB_SERVICES = {
    "agent-services": ["laoke-service", "soer-service", "xiaoai-service", "xiaoke-service"],
    "diagnostic-services": ["inquiry-service", "listen-service", "look-service", "palpation-service"],
}

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

def log(message: str, level: str = "INFO") -> None:
    """记录日志"""
    color_map = {
        "INFO": "BLUE",
        "WARNING": "YELLOW",
        "ERROR": "RED",
        "SUCCESS": "GREEN",
    }
    print_colored(f"[{level}] {message}", color_map.get(level, "BLUE"))

def find_services() -> List[Dict]:
    """查找所有需要测试的服务"""
    services = []
    
    # 检查每个服务目录
    for service_type in SERVICE_TYPES:
        service_dir = SERVICES_DIR / service_type
        
        if not service_dir.exists():
            log(f"服务目录不存在: {service_dir}", "WARNING")
            continue
        
        # 检查是否有子服务
        if service_type in SUB_SERVICES:
            for sub_service in SUB_SERVICES[service_type]:
                sub_service_dir = service_dir / sub_service
                if sub_service_dir.exists():
                    service_name = f"{service_type}/{sub_service}"
                    test_dir = sub_service_dir / "test"
                    
                    if test_dir.exists():
                        services.append({
                            "service_name": service_name,
                            "service_dir": sub_service_dir,
                            "test_dir": test_dir,
                        })
                    else:
                        log(f"服务 {service_name} 没有test目录", "WARNING")
        else:
            # 检查主服务
            test_dir = service_dir / "test"
            if test_dir.exists():
                services.append({
                    "service_name": service_type,
                    "service_dir": service_dir,
                    "test_dir": test_dir,
                })
            else:
                log(f"服务 {service_type} 没有test目录", "WARNING")
    
    return services

def find_test_types(test_dir: Path) -> Dict[str, Path]:
    """查找服务的测试类型目录"""
    test_types = {}
    
    # 常见的测试类型
    test_type_dirs = ["unit", "integration", "functional", "performance", "e2e", "end_to_end", "system"]
    
    # 查找测试类型目录
    for test_type in test_type_dirs:
        test_type_dir = test_dir / test_type
        if test_type_dir.exists():
            test_types[test_type] = test_type_dir
    
    # 如果没有子目录，使用测试目录本身
    if not test_types and any(test_dir.glob("test_*.py")):
        test_types["all"] = test_dir
    
    return test_types

def run_tests(service_info: Dict, test_types: Optional[List[str]] = None) -> Dict:
    """运行服务的测试"""
    service_name = service_info["service_name"]
    service_dir = service_info["service_dir"]
    test_dir = service_info["test_dir"]
    
    log(f"测试服务: {service_name}")
    
    result = {
        "service_name": service_name,
        "service_dir": str(service_dir),
        "test_dir": str(test_dir),
        "test_results": {},
        "success": True,
        "error": None,
    }
    
    try:
        # 查找可用的测试类型
        available_test_types = find_test_types(test_dir)
        
        if not available_test_types:
            log(f"服务 {service_name} 没有找到可用的测试", "WARNING")
            result["error"] = "没有找到可用的测试"
            result["success"] = False
            return result
        
        # 确定要运行的测试类型
        if test_types:
            test_types_to_run = {k: v for k, v in available_test_types.items() if k in test_types}
            if not test_types_to_run:
                log(f"服务 {service_name} 没有指定类型的测试: {test_types}", "WARNING")
                result["error"] = f"没有指定类型的测试: {test_types}"
                result["success"] = False
                return result
        else:
            test_types_to_run = available_test_types
        
        # 运行每种类型的测试
        for test_type, test_type_dir in test_types_to_run.items():
            log(f"运行 {test_type} 测试")
            
            # 使用pytest运行测试
            cmd = [
                sys.executable, "-m", "pytest", str(test_type_dir), 
                "-v", "--no-header", "--no-summary"
            ]
            
            # 设置环境变量
            env = os.environ.copy()
            env["PYTHONPATH"] = str(service_dir)
            
            # 运行测试
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=service_dir,
                env=env,
            )
            
            # 解析测试结果
            test_result = {
                "returncode": process.returncode,
                "passed": process.returncode == 0,
                "output": process.stdout,
                "error": process.stderr,
            }
            
            # 保存结果
            result["test_results"][test_type] = test_result
            
            # 更新总体成功状态
            if not test_result["passed"]:
                result["success"] = False
                
                # 输出测试错误
                if test_result["error"]:
                    log(f"{test_type} 测试失败: {test_result['error']}", "ERROR")
                elif test_result["output"]:
                    # 提取失败的测试用例
                    log(f"{test_type} 测试失败", "ERROR")
                    for line in test_result["output"].splitlines():
                        if "FAILED" in line:
                            log(f"  {line}", "ERROR")
            else:
                log(f"{test_type} 测试通过", "SUCCESS")
    
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        log(f"测试 {service_name} 时出错: {str(e)}", "ERROR")
    
    return result

def generate_report(results: List[Dict]) -> None:
    """生成测试报告"""
    success_services = [r for r in results if r.get("success", False)]
    failed_services = [r for r in results if not r.get("success", False) and not r.get("error")]
    error_services = [r for r in results if r.get("error")]
    
    print("\n" + "="*80)
    print_colored("Python 3.12兼容性测试报告", "HEADER")
    print("="*80)
    
    # 打印总结
    print_colored(f"\n总结: ", "BOLD")
    print_colored(f"✅ 通过: {len(success_services)} 个服务", "GREEN")
    print_colored(f"❌ 失败: {len(failed_services)} 个服务", "RED")
    print_colored(f"⚠️ 错误: {len(error_services)} 个服务", "YELLOW")
    
    # 显示失败的服务
    if failed_services:
        print_colored("\n测试失败的服务:", "RED")
        for r in failed_services:
            print(f" - {r['service_name']}")
            for test_type, test_result in r.get("test_results", {}).items():
                if not test_result.get("passed", False):
                    print(f"   * {test_type} 测试失败")
    
    # 显示错误的服务
    if error_services:
        print_colored("\n测试出错的服务:", "YELLOW")
        for r in error_services:
            print(f" - {r['service_name']}: {r['error']}")
    
    # 保存详细报告到JSON文件
    report_file = Path(__file__).parent / "python312_test_report.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n详细报告已保存到: {report_file}")
    
    # 提供修复建议
    if failed_services or error_services:
        print_colored("\n修复建议:", "BOLD")
        print("1. 查看详细的测试输出，了解具体的失败原因")
        print("2. 关注与Python 3.12相关的兼容性问题")
        print("3. 修复测试环境问题（如缺少依赖、环境变量等）")
        print("4. 针对特定服务单独运行测试，使用 --service 参数")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='测试服务在Python 3.12环境下的兼容性')
    parser.add_argument('--service', type=str, help='只测试指定的服务')
    parser.add_argument('--test-type', type=str, choices=['unit', 'integration', 'functional', 'all'], 
                        help='只运行指定类型的测试')
    parser.add_argument('--list', action='store_true', help='列出可用的服务和测试类型')
    parser.add_argument('--parallel', action='store_true', help='并行运行测试')
    
    return parser.parse_args()

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 检查Python版本
    if sys.version_info.major != 3 or sys.version_info.minor != 12:
        log(f"警告: 当前Python版本为 {sys.version_info.major}.{sys.version_info.minor}, 但此脚本需要在Python 3.12环境中运行", "WARNING")
        response = input("是否继续? (y/n): ")
        if response.lower() != "y":
            log("已取消操作", "INFO")
            return
    
    # 查找所有服务
    all_services = find_services()
    log(f"找到 {len(all_services)} 个可测试的服务")
    
    # 如果只是列出服务
    if args.list:
        print_colored("\n可用的服务:", "BOLD")
        for service in sorted(all_services, key=lambda s: s["service_name"]):
            print(f" - {service['service_name']}")
            test_types = find_test_types(service["test_dir"])
            if test_types:
                print(f"   可用的测试类型: {', '.join(test_types.keys())}")
            else:
                print("   没有找到可用的测试")
        return
    
    # 过滤服务
    if args.service:
        filtered_services = [s for s in all_services if args.service.lower() in s["service_name"].lower()]
        if not filtered_services:
            log(f"未找到名称包含 '{args.service}' 的服务", "ERROR")
            return
        services = filtered_services
    else:
        services = all_services
    
    # 确定要运行的测试类型
    test_types = None
    if args.test_type:
        if args.test_type == "all":
            test_types = None  # 运行所有测试
        else:
            test_types = [args.test_type]
    
    # 并行或顺序运行测试
    results = []
    
    if args.parallel and len(services) > 1:
        log(f"并行测试 {len(services)} 个服务")
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(os.cpu_count() or 4, len(services))) as executor:
            futures = {executor.submit(run_tests, service, test_types): service for service in services}
            for future in concurrent.futures.as_completed(futures):
                service = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    status = "✅ 通过" if result["success"] else "❌ 失败"
                    if result["error"]:
                        status = "⚠️ 错误"
                    
                    color = "GREEN" if result["success"] else "RED"
                    if result["error"]:
                        color = "YELLOW"
                    
                    print_colored(f"{service['service_name']}: {status}", color)
                except Exception as exc:
                    log(f"测试 {service['service_name']} 时发生异常: {exc}", "ERROR")
                    results.append({
                        "service_name": service["service_name"],
                        "service_dir": str(service["service_dir"]),
                        "test_dir": str(service["test_dir"]),
                        "success": False,
                        "error": str(exc),
                    })
    else:
        log(f"顺序测试 {len(services)} 个服务")
        for service in services:
            result = run_tests(service, test_types)
            results.append(result)
            
            # 显示测试结果
            status = "✅ 通过" if result["success"] else "❌ 失败"
            if result["error"]:
                status = "⚠️ 错误"
            
            color = "GREEN" if result["success"] else "RED"
            if result["error"]:
                color = "YELLOW"
            
            print_colored(f"{service['service_name']}: {status}", color)
    
    # 生成报告
    generate_report(results)

if __name__ == "__main__":
    main() 