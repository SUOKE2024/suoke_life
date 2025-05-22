#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 3.12 依赖兼容性手动修复工具

此脚本用于手动修复自动脚本无法处理的Python 3.12依赖兼容性问题
"""

import os
import re
import argparse
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
# 服务目录
SERVICES_DIR = PROJECT_ROOT / "services"

# 需要手动修复的服务及其问题依赖
MANUAL_FIXES = {
    "blockchain-service": {
        "requirements.txt": {
            "sqlalchemy==2.0.23": "sqlalchemy>=2.0.25",
            "alembic==1.12.1": "alembic>=1.13.1"
        }
    },
    "health-data-service": {
        "requirements.txt": {
            "sqlalchemy>=2.0.17": "sqlalchemy>=2.0.25",
            "alembic>=1.11.1": "alembic>=1.13.1",
            "asyncpg>=0.28.0": "asyncpg>=0.29.0"
        }
    },
    "suoke-bench-service": {
        "requirements.txt": {
            "alembic==1.13.1": "alembic>=1.13.1"
        }
    },
    "auth-service": {
        "requirements.txt": {
            "sqlalchemy==2.0.20": "sqlalchemy>=2.0.25",
            "asyncpg==0.28.0": "asyncpg>=0.29.0",
            "alembic==1.12.0": "alembic>=1.13.1"
        }
    },
    "corn-maze-service": {
        "requirements.txt": {
            "sqlalchemy==2.0.23": "sqlalchemy>=2.0.25"
        }
    },
    "agent-services/laoke-service": {
        "requirements.txt": {
            "sqlalchemy>=2.0.25": "sqlalchemy>=2.0.25",
            "asyncpg>=0.29.0": "asyncpg>=0.29.0",
            "sqlalchemy==2.0.25": "sqlalchemy>=2.0.25",
            "asyncpg==0.29.0": "asyncpg>=0.29.0"
        }
    },
    "agent-services/xiaoai-service": {
        "requirements.txt": {
            "asyncpg>=0.27.0,<1.0.0": "asyncpg>=0.29.0,<1.0.0",
            "alembic>=1.11.1,<2.0.0": "alembic>=1.13.1,<2.0.0"
        }
    },
    "agent-services/xiaoke-service": {
        "requirements.txt": {
            "sqlalchemy==2.0.25": "sqlalchemy>=2.0.25",
            "asyncpg==0.29.0": "asyncpg>=0.29.0"
        }
    },
    "agent-services/soer-service": {
        "requirements.txt": {
            "sqlalchemy==2.0.25": "sqlalchemy>=2.0.25",
            "asyncpg==0.29.0": "asyncpg>=0.29.0"
        }
    }
}

# 替换策略：0=精确替换，1=前缀替换，2=包名替换
REPLACEMENT_STRATEGY = {
    "sqlalchemy==": 1,
    "sqlalchemy>=": 1,
    "asyncpg==": 1,
    "asyncpg>=": 1,
    "alembic==": 1,
    "alembic>=": 1,
}

def get_requirements_path(service_name: str, requirements_file: str) -> Path:
    """获取服务要求文件的完整路径"""
    if "/" in service_name:
        # 这是一个子服务
        service_parts = service_name.split("/")
        return SERVICES_DIR / service_parts[0] / service_parts[1] / requirements_file
    else:
        # 这是一个主服务
        return SERVICES_DIR / service_name / requirements_file

def backup_file(file_path: Path) -> Optional[Path]:
    """创建文件备份"""
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return None
    
    backup_path = file_path.with_suffix(file_path.suffix + ".bak")
    shutil.copy2(file_path, backup_path)
    return backup_path

def restore_file(backup_path: Path) -> bool:
    """从备份恢复文件"""
    if not backup_path.exists():
        print(f"备份文件不存在: {backup_path}")
        return False
    
    original_path = backup_path.with_suffix("")
    shutil.copy2(backup_path, original_path)
    return True

def apply_manual_fixes(service_name: str, dry_run: bool = False) -> Tuple[int, int]:
    """
    应用手动修复
    
    参数:
        service_name: 要修复的服务名称
        dry_run: 若为True，只显示将要进行的更改，不实际修改文件
    
    返回:
        (文件修改计数, 替换计数)
    """
    if service_name not in MANUAL_FIXES:
        print(f"无需手动修复的服务: {service_name}")
        return 0, 0
    
    files_changed = 0
    total_replacements = 0
    
    for req_file, replacements in MANUAL_FIXES[service_name].items():
        req_path = get_requirements_path(service_name, req_file)
        
        if not req_path.exists():
            print(f"找不到文件: {req_path}")
            continue
        
        # 创建备份
        if not dry_run:
            backup_path = backup_file(req_path)
            if not backup_path:
                continue
        
        # 读取文件内容
        with open(req_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 应用替换
        original_content = content
        replacements_made = 0
        
        for old, new in replacements.items():
            # 获取替换策略
            strategy = 0  # 默认为精确替换
            for prefix, strat in REPLACEMENT_STRATEGY.items():
                if old.startswith(prefix):
                    strategy = strat
                    break
            
            if strategy == 0:  # 精确替换
                pattern = re.escape(old)
                if re.search(f"^{pattern}$", old, re.MULTILINE):
                    content = re.sub(f"^{pattern}$", new, content, flags=re.MULTILINE)
                    replacements_made += 1
            elif strategy == 1:  # 前缀替换
                pkg_name = old.split('==')[0].split('>=')[0].split('<')[0].strip()
                content = re.sub(f"^{re.escape(pkg_name)}(==|>=|<=|<|>).*$", new, content, flags=re.MULTILINE)
                replacements_made += 1
            elif strategy == 2:  # 包名替换
                pkg_name = old.split()[0]
                content = re.sub(f"^{re.escape(pkg_name)}\\s.*$", new, content, flags=re.MULTILINE)
                replacements_made += 1
        
        # 写入修改后的内容
        if original_content != content:
            if dry_run:
                print(f"[DRY RUN] 将修改文件: {req_path}")
                print(f"[DRY RUN] 将进行 {replacements_made} 处替换")
            else:
                with open(req_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"已修改文件: {req_path}")
                print(f"已进行 {replacements_made} 处替换")
            
            files_changed += 1
            total_replacements += replacements_made
        else:
            print(f"文件无需修改: {req_path}")
    
    return files_changed, total_replacements

def list_services_to_fix() -> None:
    """列出需要手动修复的服务"""
    print("需要手动修复的服务:")
    for i, service_name in enumerate(MANUAL_FIXES.keys(), 1):
        print(f"{i}. {service_name}")
        for req_file, replacements in MANUAL_FIXES[service_name].items():
            print(f"   文件: {req_file}")
            for old, new in replacements.items():
                print(f"     {old} -> {new}")

def main():
    parser = argparse.ArgumentParser(description='Python 3.12依赖兼容性手动修复工具')
    parser.add_argument('--service', help='指定要修复的服务名称')
    parser.add_argument('--all', action='store_true', help='修复所有需要手动修复的服务')
    parser.add_argument('--list', action='store_true', help='列出需要手动修复的服务')
    parser.add_argument('--dry-run', action='store_true', help='只显示将要进行的更改，不实际修改文件')
    args = parser.parse_args()
    
    if args.list:
        list_services_to_fix()
        return 0
    
    if not args.service and not args.all:
        print("错误: 必须指定 --service 或 --all")
        return 1
    
    total_files_changed = 0
    total_replacements = 0
    
    if args.all:
        print("开始修复所有需要手动修复的服务...")
        for service_name in MANUAL_FIXES.keys():
            print(f"\n修复服务: {service_name}")
            files_changed, replacements = apply_manual_fixes(service_name, args.dry_run)
            total_files_changed += files_changed
            total_replacements += replacements
    else:
        print(f"修复服务: {args.service}")
        files_changed, replacements = apply_manual_fixes(args.service, args.dry_run)
        total_files_changed += files_changed
        total_replacements += replacements
    
    if args.dry_run:
        print(f"\n[DRY RUN] 总结: 将修改 {total_files_changed} 个文件，进行 {total_replacements} 处替换")
    else:
        print(f"\n总结: 已修改 {total_files_changed} 个文件，进行了 {total_replacements} 处替换")
    
    return 0

if __name__ == "__main__":
    exit(main()) 