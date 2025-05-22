#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Python 3.12不兼容的依赖项

该脚本根据兼容性检查结果，为每个服务更新不兼容的依赖项版本。
"""

import os
import json
import re
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
# 服务目录
SERVICES_DIR = PROJECT_ROOT / "services"
# 兼容性检查报告路径
COMPATIBILITY_REPORT = PROJECT_ROOT / "python312_compatibility_report.json"

# 依赖更新映射表
DEPENDENCY_FIXES = {
    # 包名: 新版本或替代包
    "numpy": "numpy>=1.26.3",
    "scipy": "scipy>=1.12.0",
    "torch": "torch>=2.6.0",
    "torchvision": "torchvision>=0.21.0",
    "torchaudio": "torchaudio>=2.6.0",
    "tensorflow-lite": None,  # 考虑替代方案
    "tflite-runtime": None,  # 考虑替代方案
    "onnxruntime": "onnxruntime>=1.20.0",
    "pysnark": None,  # 需要替代方案
    "zokrates": None,  # 需要替代方案
    "opentelemetry-exporter-prometheus": "opentelemetry-exporter-otlp>=1.21.0",  # 替代方案
    "grafana-api-client": "grafana-api-client>=0.2.0",
    # 修复格式错误的依赖项
    "asyncpg>=0.27.0,<0.28.0  # PostgreSQL async client": "asyncpg>=0.27.0,<0.28.0",
    "sqlalchemy>=2.0.0,<2.1.0  # ORM support": "sqlalchemy>=2.0.0,<2.1.0",
    "alembic>=1.11.0,<1.12.0  # Database migrations": "alembic>=1.11.0,<1.12.0",
    "</kodu_content>": None,  # 删除无效依赖
}

# 尝试修复依赖的策略
FIX_STRATEGIES = {
    "tensorflow-lite": "# tensorflow-lite==2.14.0 # Python 3.12 暂不支持，考虑使用替代方案",
    "tflite-runtime": "# tflite-runtime==2.14.0 # Python 3.12 暂不支持，考虑使用替代方案",
    "pysnark": "# pysnark==0.4.0 # Python 3.12 暂不支持，考虑使用替代方案",
    "zokrates": "# zokrates==0.7.13 # Python 3.12 暂不支持，考虑使用替代方案",
}

# 已知需要修复的依赖列表 (基于之前的兼容性检查)
KNOWN_INCOMPATIBLE_PACKAGES = [
    "numpy", "scipy", "torch", "torchvision", "torchaudio", 
    "tensorflow-lite", "tflite-runtime", "onnxruntime",
    "pysnark", "zokrates", "opentelemetry-exporter-prometheus",
    "grafana-api-client", "asyncpg", "sqlalchemy", "alembic"
]

def load_compatibility_report() -> List[Dict[str, Any]]:
    """加载兼容性检查报告"""
    if not COMPATIBILITY_REPORT.exists():
        print(f"兼容性报告文件不存在: {COMPATIBILITY_REPORT}")
        print("使用内置的已知不兼容依赖列表继续...")
        return []
    
    with open(COMPATIBILITY_REPORT, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_service_name_from_path(file_path: str) -> str:
    """从文件路径中提取服务名称"""
    path = Path(file_path)
    parts = path.parts
    
    # 查找services目录的索引
    try:
        services_idx = parts.index('services')
    except ValueError:
        return "unknown"
    
    # 提取服务名称
    if services_idx + 1 < len(parts):
        service_name = parts[services_idx + 1]
        
        # 检查是否有子服务
        if service_name == 'agent-services' and services_idx + 2 < len(parts):
            return f"{service_name}/{parts[services_idx + 2]}"
        elif service_name == 'diagnostic-services' and services_idx + 2 < len(parts):
            return f"{service_name}/{parts[services_idx + 2]}"
        else:
            return service_name
    
    return "unknown"

def find_requirements_files() -> Dict[str, Path]:
    """查找所有服务的requirements.txt文件"""
    requirements_files = {}
    
    for service_dir in SERVICES_DIR.glob("*"):
        if service_dir.is_dir():
            service_name = service_dir.name
            
            # 检查主服务目录中的requirements.txt
            req_file = service_dir / "requirements.txt"
            if req_file.exists():
                requirements_files[service_name] = req_file
            
            # 检查子服务目录中的requirements.txt
            for subservice_dir in service_dir.glob("*"):
                if subservice_dir.is_dir():
                    subservice_name = f"{service_name}/{subservice_dir.name}"
                    sub_req_file = subservice_dir / "requirements.txt"
                    if sub_req_file.exists():
                        requirements_files[subservice_name] = sub_req_file
    
    return requirements_files

def update_requirements_file(req_file: Path) -> Tuple[int, List[str]]:
    """
    更新requirements.txt文件中的不兼容依赖项
    
    返回: (更新的依赖项数量, 无法更新的依赖项列表)
    """
    if not req_file.exists():
        return 0, []
    
    with open(req_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    updated_count = 0
    unfixed_deps = []
    updated_lines = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            updated_lines.append(line)
            continue
        
        # 提取包名
        match = re.match(r'^([a-zA-Z0-9_\-]+)', line)
        if match:
            pkg_name = match.group(1)
            
            # 检查完整依赖字符串是否在更新映射表中
            if line in DEPENDENCY_FIXES:
                if DEPENDENCY_FIXES[line] is None:
                    # 删除此依赖
                    updated_count += 1
                    continue
                else:
                    # 更新为新版本
                    updated_lines.append(DEPENDENCY_FIXES[line])
                    updated_count += 1
                    continue
            
            # 检查包名是否在更新映射表中
            if pkg_name in DEPENDENCY_FIXES:
                if DEPENDENCY_FIXES[pkg_name] is None:
                    # 如果有特定的修复策略，应用它
                    if pkg_name in FIX_STRATEGIES:
                        updated_lines.append(FIX_STRATEGIES[pkg_name])
                        updated_count += 1
                    else:
                        # 如果没有特定策略但需要删除，则跳过此行
                        updated_count += 1
                    continue
                else:
                    # 更新为新版本
                    updated_lines.append(DEPENDENCY_FIXES[pkg_name])
                    updated_count += 1
                    continue
            
            # 检查此包是否在已知不兼容列表中
            if pkg_name in KNOWN_INCOMPATIBLE_PACKAGES:
                unfixed_deps.append(line)
        
        updated_lines.append(line)
    
    # 写入更新后的文件
    with open(req_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines) + '\n')
    
    return updated_count, unfixed_deps

def main():
    parser = argparse.ArgumentParser(description='修复Python 3.12不兼容的依赖项')
    parser.add_argument('--service', help='指定要修复的服务名称')
    args = parser.parse_args()
    
    try:
        # 加载兼容性报告
        report_entries = load_compatibility_report()
        
        # 从报告中提取服务信息
        services_to_fix = {}
        for entry in report_entries:
            if not entry.get("compatible", True):
                file_path = entry.get("file", "")
                service_name = get_service_name_from_path(file_path)
                incompatible_packages = entry.get("incompatible_packages", [])
                
                if service_name not in services_to_fix:
                    services_to_fix[service_name] = set()
                
                services_to_fix[service_name].update(incompatible_packages)
        
        # 如果报告为空，使用所有服务
        if not services_to_fix:
            requirements_files = find_requirements_files()
            for service_name in requirements_files.keys():
                services_to_fix[service_name] = set(KNOWN_INCOMPATIBLE_PACKAGES)
        else:
            # 查找所有requirements.txt文件
            requirements_files = find_requirements_files()
        
        total_updated = 0
        services_updated = 0
        services_with_unfixed_deps = 0
        
        print("开始修复Python 3.12不兼容的依赖项...")
        
        # 对指定服务或所有不兼容服务进行修复
        for service_name, incompatible_deps in services_to_fix.items():
            if args.service and args.service != service_name:
                continue
            
            if service_name in requirements_files:
                req_file = requirements_files[service_name]
                print(f"正在修复 {service_name} 的依赖...")
                
                updated_count, unfixed_deps = update_requirements_file(req_file)
                total_updated += updated_count
                
                if updated_count > 0:
                    services_updated += 1
                    print(f"  ✅ 已更新 {updated_count} 个依赖项")
                
                if unfixed_deps:
                    services_with_unfixed_deps += 1
                    print(f"  ⚠️ 无法自动修复的依赖项: {', '.join(unfixed_deps)}")
                else:
                    print(f"  ✅ 所有不兼容依赖已修复")
            else:
                print(f"⚠️ 找不到 {service_name} 的requirements.txt文件")
        
        print("\n修复完成!")
        print(f"共更新了 {services_updated} 个服务的 {total_updated} 个依赖项")
        if services_with_unfixed_deps > 0:
            print(f"有 {services_with_unfixed_deps} 个服务仍有无法自动修复的依赖项，需要手动处理")
    
    except Exception as e:
        print(f"错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 