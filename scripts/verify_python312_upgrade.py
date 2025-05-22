#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 3.12 升级验证脚本

此脚本用于验证Python 3.12升级是否成功，检查Dockerfile和工作流文件的更新情况
"""

import os
import sys
import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("python312_verify.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("verify")

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
# 服务目录
SERVICES_DIR = PROJECT_ROOT / "services"

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
    "diagnostic-services": ["inquiry-service", "listen-service", "look-service", "palpation-service"]
}

# 验证结果结构
class VerificationResult:
    def __init__(self):
        self.services_checked = 0
        self.services_upgraded = 0
        self.dockerfiles_checked = 0
        self.dockerfiles_upgraded = 0
        self.workflows_checked = 0
        self.workflows_upgraded = 0
        self.service_details = {}
        
    def add_service(self, service_name: str):
        """添加服务检查结果"""
        if service_name not in self.service_details:
            self.service_details[service_name] = {
                "dockerfiles": [],
                "workflows": [],
                "docker_upgraded": False,
                "workflow_upgraded": False
            }
            self.services_checked += 1
    
    def add_dockerfile(self, service_name: str, dockerfile_path: str, upgraded: bool):
        """添加Dockerfile检查结果"""
        if service_name not in self.service_details:
            self.add_service(service_name)
        
        self.service_details[service_name]["dockerfiles"].append({
            "path": dockerfile_path,
            "upgraded": upgraded
        })
        
        self.dockerfiles_checked += 1
        if upgraded:
            self.dockerfiles_upgraded += 1
            self.service_details[service_name]["docker_upgraded"] = True
    
    def add_workflow(self, service_name: str, workflow_path: str, upgraded: bool):
        """添加GitHub工作流检查结果"""
        if service_name not in self.service_details:
            self.add_service(service_name)
        
        self.service_details[service_name]["workflows"].append({
            "path": workflow_path,
            "upgraded": upgraded
        })
        
        self.workflows_checked += 1
        if upgraded:
            self.workflows_upgraded += 1
            self.service_details[service_name]["workflow_upgraded"] = True
    
    def update_service_status(self):
        """更新服务升级状态"""
        for service_name, details in self.service_details.items():
            if details.get("docker_upgraded") or details.get("workflow_upgraded"):
                self.services_upgraded += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        self.update_service_status()
        
        return {
            "summary": {
                "services_checked": self.services_checked,
                "services_upgraded": self.services_upgraded,
                "dockerfiles_checked": self.dockerfiles_checked,
                "dockerfiles_upgraded": self.dockerfiles_upgraded,
                "workflows_checked": self.workflows_checked,
                "workflows_upgraded": self.workflows_upgraded,
                "upgrade_percentage": round((self.services_upgraded / self.services_checked * 100) if self.services_checked > 0 else 0, 2)
            },
            "services": self.service_details
        }

def check_dockerfile(dockerfile_path: str) -> bool:
    """检查Dockerfile是否已升级到Python 3.12"""
    with open(dockerfile_path, 'r') as f:
        content = f.read()
    
    # 检查基础镜像是否为Python 3.12
    if re.search(r'FROM\s+python:3\.12', content):
        return True
    
    if re.search(r'FROM\s+.*python-3\.12', content):
        return True
    
    return False

def check_github_workflow(workflow_path: str) -> bool:
    """检查GitHub工作流文件是否已升级到Python 3.12"""
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    # 检查Python版本是否为3.12
    if re.search(r'python-version:\s*[\'"]?3\.12[\'"]?', content):
        return True
    
    if re.search(r'python-version:\s*\[\s*[\'"]?3\.12[\'"]?', content):
        return True
    
    return False

def verify_service(service_path: Path, service_name: str, result: VerificationResult) -> None:
    """验证单个服务的Python 3.12升级情况"""
    logger.info(f"检查服务: {service_name}")
    result.add_service(service_name)
    
    # 检查Dockerfile
    dockerfile_paths = []
    
    # 直接在服务目录下查找
    dockerfile = service_path / "Dockerfile"
    if dockerfile.exists():
        dockerfile_paths.append(dockerfile)
    
    # 在deploy/docker子目录查找
    docker_dir = service_path / "deploy" / "docker"
    if docker_dir.exists():
        for docker_file in docker_dir.glob("Dockerfile*"):
            dockerfile_paths.append(docker_file)
    
    # 检查所有找到的Dockerfile
    for dockerfile_path in dockerfile_paths:
        upgraded = check_dockerfile(str(dockerfile_path))
        result.add_dockerfile(service_name, str(dockerfile_path), upgraded)
        
        if upgraded:
            logger.info(f"  Dockerfile已升级: {dockerfile_path}")
        else:
            logger.warning(f"  Dockerfile未升级: {dockerfile_path}")
    
    # 检查GitHub工作流文件
    github_dir = service_path / ".github" / "workflows"
    if github_dir.exists():
        for workflow_file in github_dir.glob("*.yml"):
            upgraded = check_github_workflow(str(workflow_file))
            result.add_workflow(service_name, str(workflow_file), upgraded)
            
            if upgraded:
                logger.info(f"  GitHub工作流已升级: {workflow_file}")
            else:
                logger.warning(f"  GitHub工作流未升级: {workflow_file}")

def get_service_paths() -> Dict[str, Path]:
    """获取所有服务的路径"""
    service_paths = {}
    
    for service_type in SERVICE_TYPES:
        service_type_path = SERVICES_DIR / service_type
        
        if not service_type_path.exists():
            continue
        
        # 检查是否有子服务
        if service_type in SUB_SERVICES:
            for sub_service in SUB_SERVICES[service_type]:
                sub_service_path = service_type_path / sub_service
                if sub_service_path.exists():
                    service_name = f"{service_type}/{sub_service}"
                    service_paths[service_name] = sub_service_path
        else:
            # 主服务目录
            service_paths[service_type] = service_type_path
    
    return service_paths

def main():
    result = VerificationResult()
    service_paths = get_service_paths()
    
    logger.info(f"开始验证Python 3.12升级情况...")
    logger.info(f"找到 {len(service_paths)} 个服务")
    
    for service_name, service_path in service_paths.items():
        verify_service(service_path, service_name, result)
    
    # 汇总结果
    verification_dict = result.to_dict()
    summary = verification_dict["summary"]
    
    # 保存结果到JSON文件
    output_file = PROJECT_ROOT / "python312_upgrade_verification.json"
    with open(output_file, 'w') as f:
        json.dump(verification_dict, f, indent=2)
    
    # 打印摘要
    logger.info("\n升级验证结果摘要:")
    logger.info(f"服务总数: {summary['services_checked']}")
    logger.info(f"已升级服务: {summary['services_upgraded']} ({summary['upgrade_percentage']}%)")
    logger.info(f"检查的Dockerfile: {summary['dockerfiles_checked']}")
    logger.info(f"已升级Dockerfile: {summary['dockerfiles_upgraded']}")
    logger.info(f"检查的工作流: {summary['workflows_checked']}")
    logger.info(f"已升级工作流: {summary['workflows_upgraded']}")
    logger.info(f"详细结果已保存到: {output_file}")
    
    # 判断整体升级成功与否
    if summary["upgrade_percentage"] >= 90:
        logger.info("Python 3.12升级基本完成 ✅")
        return 0
    elif summary["upgrade_percentage"] >= 50:
        logger.info("Python 3.12升级进行中 ⏳")
        return 0
    else:
        logger.warning("Python 3.12升级进度较低 ⚠️")
        return 1

if __name__ == "__main__":
    exit(main()) 