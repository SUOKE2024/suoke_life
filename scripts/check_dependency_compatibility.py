#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进版的Python 3.12依赖兼容性检查脚本

此脚本使用虚拟环境来检查项目中所有服务的依赖是否与Python 3.12兼容
"""

import os
import sys
import subprocess
import json
import tempfile
import shutil
import venv
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor

# 服务目录
SERVICES_DIR = Path(__file__).parent.parent / "services"

# 需要检查的服务类型目录
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

# 查找requirements.txt文件
def find_requirements_files() -> List[Dict]:
    requirements_files = []
    
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
                    req_file = sub_service_dir / "requirements.txt"
                    if req_file.exists():
                        service_name = f"{service_type}/{sub_service}"
                        requirements_files.append({
                            "service_name": service_name,
                            "requirements_file": req_file,
                            "service_dir": sub_service_dir,
                        })
        else:
            # 直接查找requirements.txt
            req_file = service_dir / "requirements.txt"
            if req_file.exists():
                requirements_files.append({
                    "service_name": service_type,
                    "requirements_file": req_file,
                    "service_dir": service_dir,
                })
    
    return requirements_files

# 创建虚拟环境
def create_virtual_env(venv_path: Path) -> bool:
    try:
        log(f"创建虚拟环境: {venv_path}")
        venv.create(venv_path, with_pip=True)
        return True
    except Exception as e:
        log(f"创建虚拟环境失败: {str(e)}", "ERROR")
        return False

# 获取虚拟环境中的Python解释器路径
def get_venv_python(venv_path: Path) -> Path:
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"

# 升级pip
def upgrade_pip(venv_python: Path) -> bool:
    try:
        log(f"升级pip")
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except Exception as e:
        log(f"升级pip失败: {str(e)}", "ERROR")
        return False

# 检查依赖兼容性
def check_compatibility(service_info: Dict) -> Dict:
    service_name = service_info["service_name"]
    requirements_file = service_info["requirements_file"]
    
    log(f"检查服务 {service_name} 的依赖兼容性")
    
    # 创建临时目录用于虚拟环境
    temp_dir = tempfile.mkdtemp(prefix="py312_compat_")
    venv_path = Path(temp_dir) / "venv"
    
    result = {
        "service_name": service_name,
        "requirements_file": str(requirements_file),
        "compatible": False,
        "compatible_packages": [],
        "incompatible_packages": [],
        "error": None,
    }
    
    try:
        # 创建虚拟环境
        if not create_virtual_env(venv_path):
            result["error"] = "创建虚拟环境失败"
            return result
        
        venv_python = get_venv_python(venv_path)
        
        # 升级pip
        if not upgrade_pip(venv_python):
            result["error"] = "升级pip失败"
            return result
        
        # 读取requirements.txt
        with open(requirements_file, "r") as f:
            requirements = f.read().splitlines()
        
        # 过滤掉注释和空行
        requirements = [r.strip() for r in requirements if r.strip() and not r.strip().startswith("#")]
        
        # 逐个测试安装依赖
        for req in requirements:
            try:
                # 使用--dry-run选项测试安装
                log(f"测试安装: {req}")
                result_install = subprocess.run(
                    [str(venv_python), "-m", "pip", "install", "--dry-run", req],
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                
                if result_install.returncode == 0:
                    result["compatible_packages"].append(req)
                else:
                    result["incompatible_packages"].append({
                        "package": req,
                        "error": result_install.stderr.strip(),
                    })
                    log(f"不兼容: {req}", "WARNING")
                    log(f"错误: {result_install.stderr.strip()}", "WARNING")
            except Exception as e:
                result["incompatible_packages"].append({
                    "package": req,
                    "error": str(e),
                })
                log(f"检查出错: {req}, 错误: {str(e)}", "ERROR")
        
        # 设置兼容性结果
        result["compatible"] = len(result["incompatible_packages"]) == 0
        
    except Exception as e:
        result["error"] = str(e)
        log(f"检查服务 {service_name} 时出错: {str(e)}", "ERROR")
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass
    
    return result

# 生成报告
def generate_report(results: List[Dict]) -> None:
    compatible_services = [r for r in results if r["compatible"]]
    incompatible_services = [r for r in results if not r["compatible"] and not r["error"]]
    error_services = [r for r in results if r["error"]]
    
    print("\n" + "="*80)
    print_colored("Python 3.12兼容性检查报告", "HEADER")
    print("="*80)
    
    # 打印总结
    print_colored(f"\n总结: ", "BOLD")
    print_colored(f"✅ 兼容: {len(compatible_services)} 个服务", "GREEN")
    print_colored(f"⚠️ 不兼容: {len(incompatible_services)} 个服务", "YELLOW")
    print_colored(f"❌ 错误: {len(error_services)} 个服务", "RED")
    
    # 显示不兼容的服务
    if incompatible_services:
        print_colored("\n不兼容的服务:", "YELLOW")
        for r in incompatible_services:
            print(f" - {r['service_name']} ({len(r['incompatible_packages'])}个包有问题)")
    
    # 显示错误的服务
    if error_services:
        print_colored("\n出错的服务:", "RED")
        for r in error_services:
            print(f" - {r['service_name']}: {r['error']}")
    
    # 保存详细报告到JSON文件
    report_file = Path(__file__).parent / "python312_compatibility_report.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n详细报告已保存到: {report_file}")
    
    # 提供修复建议
    if incompatible_services:
        print_colored("\n修复建议:", "BOLD")
        print("1. 更新不兼容的包到最新版本")
        print("2. 寻找Python 3.12兼容的替代包")
        print("3. 检查不兼容包的GitHub Issues或文档，了解Python 3.12兼容性计划")
        print("4. 对于关键依赖，考虑维护一个分支，直到上游支持Python 3.12")

# 主函数
def main() -> None:
    log("开始检查Python 3.12兼容性...")
    
    # 检查Python版本
    if sys.version_info.major != 3 or sys.version_info.minor != 12:
        log(f"警告: 当前Python版本为 {sys.version_info.major}.{sys.version_info.minor}, 但此脚本应在Python 3.12环境中运行", "WARNING")
        response = input("是否继续? (y/n): ")
        if response.lower() != "y":
            log("已取消操作", "INFO")
            return
    
    # 查找所有requirements.txt文件
    services_info = find_requirements_files()
    log(f"找到 {len(services_info)} 个服务")
    
    if not services_info:
        log("未找到任何服务", "ERROR")
        return
    
    # 并行检查兼容性
    results = []
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
        for result in executor.map(check_compatibility, services_info):
            results.append(result)
            # 实时显示进度
            status = "✅ 兼容" if result["compatible"] else "❌ 不兼容"
            if result["error"]:
                status = "⚠️ 错误"
            
            color = "GREEN" if result["compatible"] else "RED"
            if result["error"]:
                color = "YELLOW"
            
            print_colored(f"{result['service_name']}: {status}", color)
    
    # 生成报告
    generate_report(results)

if __name__ == "__main__":
    main() 