#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查项目中所有Python服务的依赖是否与Python 3.12兼容
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

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

# 记录日志
def log(message: str) -> None:
    print(f"[Python 3.12兼容性检查] {message}")

# 查找requirements.txt文件
def find_requirements_files() -> List[Path]:
    requirements_files = []
    
    # 检查每个服务目录
    for service_type in SERVICE_TYPES:
        service_dir = SERVICES_DIR / service_type
        
        if not service_dir.exists():
            log(f"警告: 服务目录不存在: {service_dir}")
            continue
        
        # 检查是否有子服务
        if service_type in SUB_SERVICES:
            for sub_service in SUB_SERVICES[service_type]:
                sub_service_dir = service_dir / sub_service
                if sub_service_dir.exists():
                    req_file = sub_service_dir / "requirements.txt"
                    if req_file.exists():
                        requirements_files.append(req_file)
        else:
            # 直接查找requirements.txt
            req_file = service_dir / "requirements.txt"
            if req_file.exists():
                requirements_files.append(req_file)
    
    return requirements_files

# 检查依赖兼容性
def check_compatibility(requirements_file: Path) -> Tuple[Set[str], Set[str]]:
    log(f"检查依赖: {requirements_file}")
    
    try:
        # 读取requirements.txt内容
        with open(requirements_file, "r") as f:
            requirements = f.read().splitlines()
        
        # 过滤掉注释和空行
        requirements = [r.strip() for r in requirements if r.strip() and not r.strip().startswith("#")]
        
        # 使用pip检查兼容性
        compatible_packages = set()
        incompatible_packages = set()
        
        for req in requirements:
            try:
                # 使用pip check命令检查兼容性
                result = subprocess.run(
                    ["pip", "install", "--dry-run", f"{req}"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                
                if result.returncode == 0:
                    compatible_packages.add(req)
                else:
                    incompatible_packages.add(req)
                    log(f"不兼容的包: {req}, 原因: {result.stderr}")
            except Exception as e:
                incompatible_packages.add(req)
                log(f"检查出错: {req}, 异常: {str(e)}")
        
        return compatible_packages, incompatible_packages
    
    except Exception as e:
        log(f"处理文件时出错 {requirements_file}: {str(e)}")
        return set(), set()

# 主函数
def main() -> None:
    log("开始检查Python 3.12兼容性...")
    
    # 检查Python版本
    if sys.version_info.major != 3 or sys.version_info.minor != 12:
        log(f"警告: 当前Python版本为 {sys.version_info.major}.{sys.version_info.minor}, 但此脚本应在Python 3.12环境中运行")
    
    # 查找所有requirements.txt文件
    requirements_files = find_requirements_files()
    log(f"找到 {len(requirements_files)} 个requirements.txt文件")
    
    # 检查结果
    results = {}
    all_compatible = True
    
    # 检查每个文件的兼容性
    for req_file in requirements_files:
        compatible, incompatible = check_compatibility(req_file)
        
        service_name = req_file.parent.name
        if service_name in SERVICE_TYPES:
            service_name = req_file.parent.name
        else:
            service_name = f"{req_file.parent.parent.name}/{service_name}"
        
        results[service_name] = {
            "compatible": sorted(list(compatible)),
            "incompatible": sorted(list(incompatible)),
            "requirements_file": str(req_file),
        }
        
        if incompatible:
            all_compatible = False
    
    # 保存结果
    output_file = Path(__file__).parent / "python312_compatibility_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    log(f"兼容性检查完成, 结果已保存到: {output_file}")
    
    if all_compatible:
        log("所有依赖都与Python 3.12兼容")
        sys.exit(0)
    else:
        log("有些依赖与Python 3.12不兼容, 请查看结果文件")
        sys.exit(1)

if __name__ == "__main__":
    main() 