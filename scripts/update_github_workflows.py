#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新所有GitHub Actions工作流文件中的Python版本至3.12
"""

import os
import re
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

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
    print(f"[更新工作流] {message}")

# 查找所有GitHub工作流文件
def find_workflow_files() -> List[Path]:
    workflow_files = []
    
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
                
                # 查找.github/workflows目录
                workflow_dir = sub_service_dir / ".github" / "workflows"
                if workflow_dir.exists():
                    for file in workflow_dir.glob("*.y*ml"):
                        workflow_files.append(file)
        else:
            # 查找.github/workflows目录
            workflow_dir = service_dir / ".github" / "workflows"
            if workflow_dir.exists():
                for file in workflow_dir.glob("*.y*ml"):
                    workflow_files.append(file)
    
    return workflow_files

# 安全读取YAML文件
def safe_load_yaml(file_path: Path) -> Dict:
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        log(f"读取YAML文件失败: {file_path}, 错误: {str(e)}")
        return {}

# 安全写入YAML文件
def safe_dump_yaml(data: Dict, file_path: Path) -> bool:
    try:
        with open(file_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        log(f"写入YAML文件失败: {file_path}, 错误: {str(e)}")
        return False

# 更新Python版本
def update_python_version(data: Dict, target_version: str = "3.12") -> Tuple[Dict, List[Dict]]:
    changes = []
    
    def process_dict(d: Dict, path: List[str]) -> None:
        if not isinstance(d, dict):
            return
        
        for key, value in d.items():
            current_path = path + [key]
            
            if isinstance(value, dict):
                process_dict(value, current_path)
            elif isinstance(value, list):
                process_list(value, current_path)
            elif key == "python-version" and isinstance(value, str):
                # 更新Python版本
                old_version = value
                if old_version != target_version:
                    d[key] = target_version
                    changes.append({
                        "path": ".".join(current_path),
                        "old": old_version,
                        "new": target_version
                    })
    
    def process_list(lst: List, path: List[str]) -> None:
        if not isinstance(lst, list):
            return
        
        for i, item in enumerate(lst):
            current_path = path + [str(i)]
            
            if isinstance(item, dict):
                process_dict(item, current_path)
            elif isinstance(item, list):
                process_list(item, current_path)
    
    process_dict(data, [])
    return data, changes

# 使用正则表达式更新文本文件中的Python版本
def update_workflow_file_with_regex(file_path: Path) -> Tuple[bool, List[Dict]]:
    log(f"使用正则表达式处理文件: {file_path}")
    
    # 备份文件
    backup_file = file_path.with_suffix(file_path.suffix + ".bak")
    shutil.copy2(file_path, backup_file)
    
    changes = []
    updated = False
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
        
        # 使用正则表达式查找并替换Python版本
        # 匹配 python-version: '3.x'、python-version: "3.x" 和 python-version: 3.x
        pattern = r'(python-version:\s*[\'\"]?)(\d+\.\d+)([\'\"]?)'
        
        def replace_version(match):
            nonlocal updated, changes
            prefix = match.group(1)
            version = match.group(2)
            suffix = match.group(3)
            
            if version != "3.12":
                line_number = content[:match.start()].count('\n') + 1
                changes.append({
                    "line": line_number,
                    "old": f"{prefix}{version}{suffix}",
                    "new": f"{prefix}3.12{suffix}"
                })
                updated = True
                return f"{prefix}3.12{suffix}"
            return match.group(0)
        
        updated_content = re.sub(pattern, replace_version, content)
        
        # 如果有变更，写回文件
        if updated:
            with open(file_path, "w") as f:
                f.write(updated_content)
            log(f"已更新: {file_path}")
        else:
            log(f"无需更新: {file_path}")
            # 删除备份文件
            backup_file.unlink()
        
        return updated, changes
    
    except Exception as e:
        log(f"处理文件时出错: {file_path}, 错误: {str(e)}")
        # 恢复备份
        if backup_file.exists():
            shutil.copy2(backup_file, file_path)
        return False, []

# 更新工作流文件
def update_workflow_file(workflow_file: Path) -> Dict:
    log(f"处理文件: {workflow_file}")
    
    result = {
        "file": str(workflow_file),
        "updated": False,
        "changes": [],
        "error": None
    }
    
    try:
        # 尝试使用正则表达式更新
        updated, changes = update_workflow_file_with_regex(workflow_file)
        
        result["updated"] = updated
        result["changes"] = changes
    
    except Exception as e:
        result["error"] = str(e)
        log(f"处理文件时出错: {workflow_file}, 错误: {str(e)}")
    
    return result

# 主函数
def main() -> None:
    log("开始更新GitHub Actions工作流文件中的Python版本...")
    
    # 查找所有工作流文件
    workflow_files = find_workflow_files()
    log(f"找到 {len(workflow_files)} 个工作流文件")
    
    # 更新结果
    results = []
    updated_count = 0
    
    # 更新每个工作流文件
    for workflow_file in workflow_files:
        result = update_workflow_file(workflow_file)
        results.append(result)
        
        if result["updated"]:
            updated_count += 1
    
    # 输出结果
    log(f"更新完成: 共 {len(workflow_files)} 个文件, 更新了 {updated_count} 个文件")
    
    # 显示更新详情
    if updated_count > 0:
        log("更新详情:")
        for result in results:
            if result["updated"]:
                log(f"  - {result['file']}")
                for change in result["changes"]:
                    log(f"    * 第 {change['line']} 行: {change['old']} -> {change['new']}")
    
    # 显示未更新的文件
    not_updated = [r["file"] for r in results if not r["updated"] and not r["error"]]
    if not_updated:
        log("以下文件无需更新:")
        for file in not_updated:
            log(f"  - {file}")
    
    # 显示错误
    errors = [r for r in results if r["error"]]
    if errors:
        log("更新过程中遇到错误:")
        for error in errors:
            log(f"  - {error['file']}: {error['error']}")

if __name__ == "__main__":
    main() 