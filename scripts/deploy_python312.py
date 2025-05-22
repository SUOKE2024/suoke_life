#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 3.12 升级部署脚本

此脚本用于按照定义的阶段在不同环境中部署Python 3.12升级
"""

import os
import sys
import json
import time
import argparse
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("python312_deploy.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("deploy")

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
# 部署配置目录
DEPLOY_CONFIG_DIR = PROJECT_ROOT / "deploy_configs"
# 确保配置目录存在
DEPLOY_CONFIG_DIR.mkdir(exist_ok=True)

# 部署阶段定义
STAGES = {
    1: {  # 基础服务
        "services": ["api-gateway", "auth-service", "message-bus"],
        "description": "基础服务(第1阶段)",
        "dependencies": []
    },
    2: {  # 核心业务服务
        "services": ["user-service", "health-data-service", "med-knowledge", "medical-service"],
        "description": "核心业务服务(第2阶段)",
        "dependencies": [1]  # 依赖阶段1
    },
    3: {  # 智能体服务
        "services": ["rag-service", "agent-services/laoke-service", "agent-services/soer-service", 
                    "agent-services/xiaoai-service", "agent-services/xiaoke-service"],
        "description": "智能体服务(第3阶段)",
        "dependencies": [1, 2]  # 依赖阶段1和2
    },
    4: {  # 辅助服务
        "services": ["accessibility-service", "blockchain-service", "corn-maze-service", 
                    "suoke-bench-service", "diagnostic-services/listen-service", 
                    "diagnostic-services/inquiry-service", "diagnostic-services/palpation-service", 
                    "diagnostic-services/look-service"],
        "description": "辅助服务(第4阶段)",
        "dependencies": [1, 2, 3]  # 依赖阶段1、2和3
    }
}

# 环境定义
ENVIRONMENTS = {
    "test": {
        "description": "测试环境",
        "k8s_context": "test-cluster",
        "deploy_namespace": "suoke-test"
    },
    "staging": {
        "description": "预发布环境",
        "k8s_context": "staging-cluster",
        "deploy_namespace": "suoke-staging"
    },
    "production": {
        "description": "生产环境",
        "k8s_context": "prod-cluster",
        "deploy_namespace": "suoke-prod"
    }
}

# 获取服务的容器名
def get_service_container_name(service: str) -> str:
    """从服务名生成容器名"""
    if "/" in service:
        parts = service.split("/")
        return f"{parts[-1]}-container"
    else:
        return f"{service}-container"

# 获取服务的部署名
def get_service_deployment_name(service: str) -> str:
    """从服务名生成Kubernetes部署名"""
    if "/" in service:
        parts = service.split("/")
        return f"{parts[-1]}-deployment"
    else:
        return f"{service}-deployment"

# 检查依赖阶段是否完成
def check_stage_dependencies(stage: int, env: str) -> bool:
    """检查当前阶段的依赖阶段是否已完成"""
    if stage not in STAGES:
        logger.error(f"无效的阶段: {stage}")
        return False
    
    dependencies = STAGES[stage].get("dependencies", [])
    if not dependencies:
        return True
    
    # 检查每个依赖阶段的状态
    for dep_stage in dependencies:
        status_file = DEPLOY_CONFIG_DIR / f"stage{dep_stage}_{env}_status.json"
        if not status_file.exists():
            logger.error(f"依赖阶段 {dep_stage} 在 {env} 环境中尚未部署，无法继续")
            return False
        
        try:
            with open(status_file, 'r') as f:
                status = json.load(f)
                if status.get("status") != "completed":
                    logger.error(f"依赖阶段 {dep_stage} 在 {env} 环境中部署未完成，状态: {status.get('status')}")
                    return False
        except Exception as e:
            logger.error(f"读取依赖阶段状态失败: {str(e)}")
            return False
    
    return True

# 获取当前部署状态
def get_deployment_status(service: str, env: str) -> Dict[str, Any]:
    """获取服务在指定环境的部署状态"""
    env_config = ENVIRONMENTS.get(env)
    if not env_config:
        return {"status": "unknown", "error": f"未知环境: {env}"}
    
    deployment_name = get_service_deployment_name(service)
    namespace = env_config.get("deploy_namespace")
    k8s_context = env_config.get("k8s_context")
    
    try:
        # 切换Kubernetes上下文
        subprocess.run(
            ["kubectl", "config", "use-context", k8s_context],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        # 获取部署状态
        result = subprocess.run(
            ["kubectl", "get", "deployment", deployment_name, 
             "-n", namespace, "-o", "json"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        deployment_info = json.loads(result.stdout)
        status = deployment_info.get("status", {})
        
        desired_replicas = status.get("replicas", 0)
        available_replicas = status.get("availableReplicas", 0)
        updated_replicas = status.get("updatedReplicas", 0)
        
        # 获取容器镜像版本
        containers = deployment_info.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
        image = containers[0].get("image") if containers else "unknown"
        
        return {
            "service": service,
            "deployment": deployment_name,
            "namespace": namespace,
            "image": image,
            "desired_replicas": desired_replicas,
            "available_replicas": available_replicas,
            "updated_replicas": updated_replicas,
            "status": "healthy" if desired_replicas > 0 and available_replicas == desired_replicas else "degraded",
            "python_version": "3.12" if "python:3.12" in image or "python-3.12" in image else "unknown"
        }
    
    except subprocess.CalledProcessError as e:
        if "NotFound" in e.stderr:
            return {"status": "not_deployed", "service": service}
        else:
            return {"status": "error", "service": service, "error": e.stderr}
    
    except Exception as e:
        return {"status": "error", "service": service, "error": str(e)}

# 部署服务
def deploy_service(service: str, env: str, rollback: bool = False) -> Dict[str, Any]:
    """部署服务到指定环境，或回滚服务"""
    env_config = ENVIRONMENTS.get(env)
    if not env_config:
        return {"status": "failed", "error": f"未知环境: {env}"}
    
    deployment_name = get_service_deployment_name(service)
    namespace = env_config.get("deploy_namespace")
    k8s_context = env_config.get("k8s_context")
    
    try:
        # 检查服务目录是否存在
        service_path = get_service_path(service)
        if not service_path.exists():
            return {"status": "failed", "error": f"服务目录不存在: {service_path}"}
        
        # 获取当前状态（用于回滚）
        current_status = get_deployment_status(service, env)
        
        # 切换Kubernetes上下文
        subprocess.run(
            ["kubectl", "config", "use-context", k8s_context],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        if rollback:
            # 回滚操作
            logger.info(f"开始回滚服务 {service} 在 {env} 环境")
            
            # 如果有备份文件，从备份恢复
            backup_file = DEPLOY_CONFIG_DIR / f"{service.replace('/', '_')}_{env}_backup.json"
            if backup_file.exists():
                with open(backup_file, 'r') as f:
                    backup = json.load(f)
                    original_image = backup.get("image")
                    
                    if original_image:
                        # 设置回原镜像
                        result = subprocess.run(
                            ["kubectl", "set", "image", 
                             f"deployment/{deployment_name}", 
                             f"{get_service_container_name(service)}={original_image}",
                             "-n", namespace],
                            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                        )
                        
                        logger.info(f"服务 {service} 已回滚到镜像: {original_image}")
                        return {"status": "rollback_success", "service": service, "image": original_image}
                    else:
                        return {"status": "rollback_failed", "error": "备份中没有镜像信息"}
            else:
                return {"status": "rollback_failed", "error": "找不到备份文件"}
        
        else:
            # 部署操作
            logger.info(f"开始部署服务 {service} 到 {env} 环境")
            
            # 备份当前状态
            if current_status.get("status") not in ["not_deployed", "error"]:
                backup_file = DEPLOY_CONFIG_DIR / f"{service.replace('/', '_')}_{env}_backup.json"
                with open(backup_file, 'w') as f:
                    json.dump(current_status, f, indent=2)
            
            # 使用kubectl apply部署更新的清单
            k8s_dir = service_path / "deploy" / "kubernetes"
            if not k8s_dir.exists():
                k8s_dir = service_path / "deploy" / "k8s"
            
            if not k8s_dir.exists():
                return {"status": "failed", "error": f"找不到Kubernetes部署文件目录: {k8s_dir}"}
            
            # 应用部署文件
            deploy_files = list(k8s_dir.glob("*.yaml")) + list(k8s_dir.glob("*.yml"))
            if not deploy_files:
                return {"status": "failed", "error": f"在 {k8s_dir} 中找不到部署文件"}
            
            for deploy_file in deploy_files:
                subprocess.run(
                    ["kubectl", "apply", "-f", str(deploy_file), "-n", namespace],
                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
            
            logger.info(f"已应用部署文件: {[f.name for f in deploy_files]}")
            
            # 等待部署完成
            logger.info(f"等待服务 {service} 部署完成...")
            max_wait = 300  # 最多等待5分钟
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                status = get_deployment_status(service, env)
                
                if status.get("status") == "healthy":
                    logger.info(f"服务 {service} 部署成功: {status.get('python_version')} 版本")
                    return {"status": "success", "service": service, "deployment": status}
                
                if status.get("status") == "error":
                    logger.error(f"部署出错: {status.get('error')}")
                    return {"status": "failed", "error": status.get('error')}
                
                logger.info(f"服务 {service} 正在部署: {status.get('available_replicas')}/{status.get('desired_replicas')} 已就绪")
                time.sleep(10)
            
            # 超时
            return {"status": "timeout", "service": service, "message": "部署超时，请手动检查状态"}
    
    except subprocess.CalledProcessError as e:
        logger.error(f"部署命令失败: {e.stderr}")
        return {"status": "failed", "error": e.stderr}
    
    except Exception as e:
        logger.error(f"部署出错: {str(e)}")
        return {"status": "failed", "error": str(e)}

# 获取服务的路径
def get_service_path(service: str) -> Path:
    """获取服务的目录路径"""
    services_dir = PROJECT_ROOT / "services"
    
    if "/" in service:
        # 子服务
        parts = service.split("/")
        return services_dir / parts[0] / parts[1]
    else:
        # 主服务
        return services_dir / service

# 部署阶段
def deploy_stage(stage: int, env: str, rollback: bool = False) -> Dict[str, Any]:
    """部署或回滚指定阶段的所有服务"""
    if stage not in STAGES:
        return {"status": "failed", "error": f"无效的阶段: {stage}"}
    
    env_config = ENVIRONMENTS.get(env)
    if not env_config:
        return {"status": "failed", "error": f"未知环境: {env}"}
    
    # 非回滚模式下检查依赖阶段
    if not rollback and not check_stage_dependencies(stage, env):
        return {"status": "failed", "error": "依赖阶段尚未完成"}
    
    services = STAGES[stage].get("services", [])
    stage_description = STAGES[stage].get("description", f"阶段{stage}")
    
    logger.info(f"开始{'回滚' if rollback else '部署'} {stage_description} 到 {env_config.get('description')}")
    
    results = []
    failed_services = []
    
    for service in services:
        logger.info(f"{'回滚' if rollback else '部署'}服务: {service}")
        result = deploy_service(service, env, rollback)
        results.append(result)
        
        if result.get("status") not in ["success", "rollback_success"]:
            failed_services.append(service)
    
    # 保存阶段状态
    status_file = DEPLOY_CONFIG_DIR / f"stage{stage}_{env}_status.json"
    status = {
        "stage": stage,
        "environment": env,
        "services": services,
        "results": results,
        "failed_services": failed_services,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "failed" if failed_services else "completed",
        "action": "rollback" if rollback else "deploy"
    }
    
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    if failed_services:
        logger.error(f"{stage_description} {'回滚' if rollback else '部署'}失败：{len(failed_services)}/{len(services)} 个服务出错")
        for service in failed_services:
            result = next((r for r in results if r.get("service") == service), {})
            logger.error(f"  - {service}: {result.get('error', '未知错误')}")
        
        return {"status": "failed", "failed_services": failed_services, "results": results}
    else:
        logger.info(f"{stage_description} {'回滚' if rollback else '部署'}完成：所有 {len(services)} 个服务成功")
        return {"status": "success", "services": services, "results": results}

# 检查阶段状态
def check_stage_status(stage: int, env: str) -> Dict[str, Any]:
    """检查指定阶段的部署状态"""
    if stage not in STAGES:
        return {"status": "failed", "error": f"无效的阶段: {stage}"}
    
    env_config = ENVIRONMENTS.get(env)
    if not env_config:
        return {"status": "failed", "error": f"未知环境: {env}"}
    
    services = STAGES[stage].get("services", [])
    stage_description = STAGES[stage].get("description", f"阶段{stage}")
    
    logger.info(f"检查 {stage_description} 在 {env_config.get('description')} 的状态")
    
    results = []
    healthy_services = []
    unhealthy_services = []
    not_deployed_services = []
    
    for service in services:
        status = get_deployment_status(service, env)
        results.append(status)
        
        if status.get("status") == "healthy":
            healthy_services.append(service)
        elif status.get("status") == "not_deployed":
            not_deployed_services.append(service)
        else:
            unhealthy_services.append(service)
    
    # 分析Python版本
    python312_services = [s for s in results if s.get("python_version") == "3.12"]
    
    # 保存检查结果
    check_file = DEPLOY_CONFIG_DIR / f"stage{stage}_{env}_check.json"
    check_result = {
        "stage": stage,
        "environment": env,
        "total_services": len(services),
        "healthy_services": len(healthy_services),
        "unhealthy_services": len(unhealthy_services),
        "not_deployed_services": len(not_deployed_services),
        "python312_services": len(python312_services),
        "services_results": results,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(check_file, 'w') as f:
        json.dump(check_result, f, indent=2)
    
    logger.info(f"状态检查结果:")
    logger.info(f"  总服务数: {len(services)}")
    logger.info(f"  健康服务: {len(healthy_services)}")
    logger.info(f"  不健康服务: {len(unhealthy_services)}")
    logger.info(f"  未部署服务: {len(not_deployed_services)}")
    logger.info(f"  Python 3.12服务: {len(python312_services)}")
    
    return check_result

def main():
    parser = argparse.ArgumentParser(description='Python 3.12 升级部署工具')
    parser.add_argument('--stage', type=int, choices=[1, 2, 3, 4], help='指定要部署的阶段')
    parser.add_argument('--services', nargs='+', help='指定要部署的服务列表')
    parser.add_argument('--env', choices=['test', 'staging', 'production'], default='test', help='部署环境')
    parser.add_argument('--rollback', action='store_true', help='回滚到之前的版本')
    parser.add_argument('--check', action='store_true', help='只检查部署状态，不执行部署')
    parser.add_argument('--force', action='store_true', help='强制部署，忽略依赖检查')
    args = parser.parse_args()
    
    if args.stage is None and not args.services and not args.check:
        logger.error("必须指定 --stage 或 --services 或 --check")
        return 1
    
    # 检查模式
    if args.check:
        if args.stage:
            result = check_stage_status(args.stage, args.env)
            if result.get("error"):
                logger.error(f"检查失败: {result.get('error')}")
                return 1
        elif args.services:
            for service in args.services:
                status = get_deployment_status(service, args.env)
                logger.info(f"服务 {service} 状态: {status.get('status')}")
                
                if status.get("status") == "healthy":
                    logger.info(f"  Python版本: {status.get('python_version')}")
                    logger.info(f"  副本: {status.get('available_replicas')}/{status.get('desired_replicas')}")
                    logger.info(f"  镜像: {status.get('image')}")
        else:
            # 检查所有阶段
            for stage in STAGES.keys():
                check_stage_status(stage, args.env)
        
        return 0
    
    # 部署模式
    if args.stage:
        result = deploy_stage(args.stage, args.env, args.rollback)
        if result.get("status") != "success":
            logger.error(f"阶段{args.stage}{'回滚' if args.rollback else '部署'}失败")
            return 1
    
    elif args.services:
        failed_services = []
        
        for service in args.services:
            logger.info(f"{'回滚' if args.rollback else '部署'}服务: {service}")
            result = deploy_service(service, args.env, args.rollback)
            
            if result.get("status") not in ["success", "rollback_success"]:
                logger.error(f"服务 {service} {'回滚' if args.rollback else '部署'}失败: {result.get('error', '未知错误')}")
                failed_services.append(service)
        
        if failed_services:
            logger.error(f"以下服务{'回滚' if args.rollback else '部署'}失败: {', '.join(failed_services)}")
            return 1
    
    logger.info("操作完成")
    return 0

if __name__ == "__main__":
    exit(main()) 