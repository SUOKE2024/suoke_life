#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新所有服务的Dockerfile中的Python版本至3.12
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

# Python基础镜像正则表达式
PYTHON_BASE_IMAGE_PATTERN = re.compile(r"FROM python:(\d+\.\d+)(-\w+)?")
PYTHON_MULTILINE_BASE_IMAGE_PATTERN = re.compile(r"FROM python:(\d+\.\d+)(-\w+)?\s+(?:AS|as)")

# 记录日志
def log(message: str) -> None:
    print(f"[更新Dockerfile] {message}")

# 查找所有Dockerfile
def find_dockerfiles() -> List[Path]:
    dockerfiles = []
    
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
                if not sub_service_dir.exists():
                    continue
                
                # 查找Dockerfile
                # 直接在服务目录中查找
                dockerfile = sub_service_dir / "Dockerfile"
                if dockerfile.exists():
                    dockerfiles.append(dockerfile)
                
                # 在deploy/docker目录查找
                docker_dir = sub_service_dir / "deploy" / "docker"
                if docker_dir.exists():
                    for file in docker_dir.glob("Dockerfile*"):
                        dockerfiles.append(file)
        else:
            # 直接在服务目录中查找
            dockerfile = service_dir / "Dockerfile"
            if dockerfile.exists():
                dockerfiles.append(dockerfile)
            
            # 在deploy/docker目录查找
            docker_dir = service_dir / "deploy" / "docker"
            if docker_dir.exists():
                for file in docker_dir.glob("Dockerfile*"):
                    dockerfiles.append(file)
    
    return dockerfiles

# 更新Dockerfile中的Python版本
def update_dockerfile(dockerfile: Path) -> Tuple[bool, Dict]:
    log(f"处理文件: {dockerfile}")
    
    # 备份文件
    backup_file = dockerfile.with_suffix(".bak")
    shutil.copy2(dockerfile, backup_file)
    
    result = {
        "file": str(dockerfile),
        "updated": False,
        "old_version": None,
        "changes": [],
    }
    
    try:
        with open(dockerfile, "r") as f:
            content = f.read()
        
        # 查找并更新Python基础镜像版本
        updated_content = content
        matches = list(PYTHON_BASE_IMAGE_PATTERN.finditer(content))
        
        for match in matches:
            old_version = match.group(1)
            suffix = match.group(2) or ""
            
            if old_version != "3.12":
                old_text = f"FROM python:{old_version}{suffix}"
                new_text = f"FROM python:3.12{suffix}"
                updated_content = updated_content.replace(old_text, new_text)
                
                result["old_version"] = old_version
                result["changes"].append({
                    "line": content[:match.start()].count("\n") + 1,
                    "old": old_text,
                    "new": new_text,
                })
        
        # 处理多行形式的FROM语句 (AS builder等)
        multiline_matches = list(PYTHON_MULTILINE_BASE_IMAGE_PATTERN.finditer(content))
        
        for match in multiline_matches:
            old_version = match.group(1)
            suffix = match.group(2) or ""
            
            if old_version != "3.12":
                full_match_text = content[match.start():match.end()]
                as_part = full_match_text.split("FROM python:")[1].split(" AS")[1]
                
                old_text = f"FROM python:{old_version}{suffix} AS{as_part}"
                new_text = f"FROM python:3.12{suffix} AS{as_part}"
                updated_content = updated_content.replace(old_text, new_text)
                
                if result["old_version"] is None:
                    result["old_version"] = old_version
                
                result["changes"].append({
                    "line": content[:match.start()].count("\n") + 1,
                    "old": old_text,
                    "new": new_text,
                })
        
        # 如果有变更，写回文件
        if updated_content != content:
            with open(dockerfile, "w") as f:
                f.write(updated_content)
            
            result["updated"] = True
            log(f"已更新: {dockerfile}")
        else:
            log(f"无需更新: {dockerfile}")
            # 删除备份文件
            backup_file.unlink()
    
    except Exception as e:
        log(f"处理文件时出错: {dockerfile}, 错误: {str(e)}")
        # 恢复备份
        if backup_file.exists():
            shutil.copy2(backup_file, dockerfile)
        
        result["error"] = str(e)
    
    return result

# 主函数
def main() -> None:
    log("开始更新Dockerfile中的Python版本...")
    
    # 查找所有Dockerfile
    dockerfiles = find_dockerfiles()
    log(f"找到 {len(dockerfiles)} 个Dockerfile")
    
    # 更新结果
    results = []
    updated_count = 0
    
    # 更新每个Dockerfile
    for dockerfile in dockerfiles:
        result = update_dockerfile(dockerfile)
        results.append(result)
        
        if result.get("updated", False):
            updated_count += 1
    
    # 输出结果
    log(f"更新完成: 共 {len(dockerfiles)} 个文件, 更新了 {updated_count} 个文件")
    
    # 显示更新详情
    log("更新详情:")
    for result in results:
        if result.get("updated", False):
            log(f"  - {result['file']}: {result.get('old_version', '未知')} -> 3.12")
    
    # 显示未更新的文件
    not_updated = [r["file"] for r in results if not r.get("updated", False) and not r.get("error")]
    if not_updated:
        log("以下文件无需更新:")
        for file in not_updated:
            log(f"  - {file}")
    
    # 显示错误
    errors = [r for r in results if r.get("error")]
    if errors:
        log("更新过程中遇到错误:")
        for error in errors:
            log(f"  - {error['file']}: {error['error']}")

if __name__ == "__main__":
    main() 