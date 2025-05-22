#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 3.12 升级监控脚本

此脚本用于监控Python 3.12升级过程中的服务健康状况,
包括服务可用性、响应时间、错误率等指标
"""

import argparse
import time
import json
import datetime
import subprocess
import requests
import os
import sys
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import concurrent.futures

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("python312_upgrade_monitor.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("monitor")

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
# 监控报告目录
REPORT_DIR = PROJECT_ROOT / "monitoring_reports"
# 创建报告目录(如果不存在)
REPORT_DIR.mkdir(exist_ok=True)

# 服务配置
SERVICES_CONFIG = {
    "api-gateway": {
        "healthcheck_url": "http://localhost:8000/health",
        "metrics_url": "http://localhost:8000/metrics",
        "k8s_deployment": "api-gateway",
        "k8s_namespace": "default",
        "log_files": ["api-gateway.log"],
        "threshold_response_time": 500,  # 毫秒
        "threshold_error_rate": 0.01,    # 1% 错误率
        "threshold_cpu": 80,             # CPU使用率 80%
        "threshold_memory": 85           # 内存使用率 85%
    },
    "auth-service": {
        "healthcheck_url": "http://localhost:8001/health",
        "metrics_url": "http://localhost:8001/metrics",
        "k8s_deployment": "auth-service",
        "k8s_namespace": "default",
        "log_files": ["auth-service.log"],
        "threshold_response_time": 300,
        "threshold_error_rate": 0.01,
        "threshold_cpu": 70,
        "threshold_memory": 75
    },
    "message-bus": {
        "healthcheck_url": "http://localhost:8002/health",
        "metrics_url": "http://localhost:8002/metrics",
        "k8s_deployment": "message-bus",
        "k8s_namespace": "default",
        "log_files": ["message-bus.log"],
        "threshold_response_time": 200,
        "threshold_error_rate": 0.01,
        "threshold_cpu": 60,
        "threshold_memory": 70
    },
    "user-service": {
        "healthcheck_url": "http://localhost:8003/health",
        "metrics_url": "http://localhost:8003/metrics",
        "k8s_deployment": "user-service",
        "k8s_namespace": "default", 
        "log_files": ["user-service.log"],
        "threshold_response_time": 400,
        "threshold_error_rate": 0.01,
        "threshold_cpu": 75,
        "threshold_memory": 80
    },
    "rag-service": {
        "healthcheck_url": "http://localhost:8004/health",
        "metrics_url": "http://localhost:8004/metrics",
        "k8s_deployment": "rag-service",
        "k8s_namespace": "default",
        "log_files": ["rag-service.log"],
        "threshold_response_time": 1000,
        "threshold_error_rate": 0.02,
        "threshold_cpu": 85,
        "threshold_memory": 90
    }
    # 可以继续添加更多服务...
}

# 监控阶段
STAGES = {
    1: ["api-gateway", "auth-service", "message-bus"],
    2: ["user-service", "health-data-service", "med-knowledge", "medical-service"],
    3: ["rag-service", "agent-services/laoke-service", "agent-services/soer-service", "agent-services/xiaoai-service", "agent-services/xiaoke-service"],
    4: ["accessibility-service", "blockchain-service", "corn-maze-service", "suoke-bench-service"]
}

def get_timestamp() -> str:
    """获取当前时间戳"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def check_service_health(service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """检查服务健康状况"""
    result = {
        "service": service_name,
        "timestamp": get_timestamp(),
        "status": "unknown",
        "response_time": None,
        "error_rate": None,
        "cpu_usage": None,
        "memory_usage": None,
        "errors": [],
        "warnings": []
    }
    
    # 检查健康检查端点
    try:
        start_time = time.time()
        response = requests.get(config["healthcheck_url"], timeout=5)
        response_time = (time.time() - start_time) * 1000  # 毫秒
        
        result["response_time"] = response_time
        
        if response.status_code == 200:
            result["status"] = "healthy"
        else:
            result["status"] = "unhealthy"
            result["errors"].append(f"Health check failed with status code {response.status_code}")
    except Exception as e:
        result["status"] = "unreachable"
        result["errors"].append(f"Health check error: {str(e)}")
    
    # 获取指标数据
    try:
        metrics_response = requests.get(config["metrics_url"], timeout=5)
        if metrics_response.status_code == 200:
            # 这里假设指标是Prometheus格式，实际应根据服务的指标格式进行解析
            metrics_text = metrics_response.text
            
            # 解析错误率（示例）
            error_rate_match = None
            for line in metrics_text.split('\n'):
                if "error_rate" in line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            result["error_rate"] = float(parts[-1])
                            break
                        except ValueError:
                            pass
            
            # 解析CPU和内存使用率（示例）
            for line in metrics_text.split('\n'):
                if "cpu_usage_percent" in line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            result["cpu_usage"] = float(parts[-1])
                        except ValueError:
                            pass
                
                elif "memory_usage_percent" in line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            result["memory_usage"] = float(parts[-1])
                        except ValueError:
                            pass
    except Exception as e:
        result["warnings"].append(f"Failed to fetch metrics: {str(e)}")
    
    # 检查Kubernetes中的服务状态
    try:
        cmd = f"kubectl get deployment {config['k8s_deployment']} -n {config['k8s_namespace']} -o json"
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if proc.returncode == 0:
            deployment_info = json.loads(proc.stdout)
            status = deployment_info.get("status", {})
            
            available_replicas = status.get("availableReplicas", 0)
            desired_replicas = status.get("replicas", 0)
            
            if desired_replicas > 0 and available_replicas == desired_replicas:
                result["k8s_status"] = "healthy"
            else:
                result["k8s_status"] = "degraded"
                result["warnings"].append(f"Kubernetes deployment is degraded: {available_replicas}/{desired_replicas} replicas available")
        else:
            result["warnings"].append(f"Failed to get Kubernetes deployment status: {proc.stderr}")
    except Exception as e:
        result["warnings"].append(f"Error checking Kubernetes status: {str(e)}")
    
    # 应用阈值检查
    if result["response_time"] is not None and result["response_time"] > config["threshold_response_time"]:
        result["warnings"].append(f"Response time ({result['response_time']:.2f}ms) exceeds threshold ({config['threshold_response_time']}ms)")
    
    if result["error_rate"] is not None and result["error_rate"] > config["threshold_error_rate"]:
        result["warnings"].append(f"Error rate ({result['error_rate']:.2%}) exceeds threshold ({config['threshold_error_rate']:.2%})")
    
    if result["cpu_usage"] is not None and result["cpu_usage"] > config["threshold_cpu"]:
        result["warnings"].append(f"CPU usage ({result['cpu_usage']:.2f}%) exceeds threshold ({config['threshold_cpu']}%)")
    
    if result["memory_usage"] is not None and result["memory_usage"] > config["threshold_memory"]:
        result["warnings"].append(f"Memory usage ({result['memory_usage']:.2f}%) exceeds threshold ({config['threshold_memory']}%)")
    
    return result

def monitor_services(services: List[str], interval: int = 60, duration: int = 3600) -> List[Dict[str, Any]]:
    """监控多个服务一段时间"""
    results = []
    start_time = time.time()
    end_time = start_time + duration
    
    logger.info(f"开始监控服务: {', '.join(services)}")
    logger.info(f"监控间隔: {interval}秒, 总持续时间: {duration}秒")
    
    while time.time() < end_time:
        current_time = time.time()
        logger.info(f"执行监控检查 - 剩余时间: {int(end_time - current_time)}秒")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(services), 10)) as executor:
            future_to_service = {
                executor.submit(check_service_health, service, SERVICES_CONFIG.get(service, {})): service
                for service in services if service in SERVICES_CONFIG
            }
            
            for future in concurrent.futures.as_completed(future_to_service):
                service = future_to_service[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # 记录检查结果
                    if result["status"] == "healthy":
                        logger.info(f"服务 {service} 健康")
                    elif result["status"] == "unhealthy":
                        logger.warning(f"服务 {service} 不健康: {result['errors']}")
                    else:
                        logger.error(f"服务 {service} 无法访问: {result['errors']}")
                    
                    # 记录警告
                    for warning in result["warnings"]:
                        logger.warning(f"服务 {service} 警告: {warning}")
                    
                except Exception as e:
                    logger.error(f"监控服务 {service} 时出错: {str(e)}")
        
        # 保存中间结果
        save_results(results, f"monitoring_intermediate_{int(time.time())}.json")
        
        # 等待下一个检查间隔
        if time.time() < end_time:
            wait_time = max(1, interval - (time.time() - current_time))
            logger.info(f"等待 {int(wait_time)} 秒进行下一次检查...")
            time.sleep(wait_time)
    
    logger.info(f"监控完成, 共收集 {len(results)} 条记录")
    return results

def save_results(results: List[Dict[str, Any]], filename: str) -> None:
    """保存监控结果"""
    report_path = REPORT_DIR / filename
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    logger.info(f"监控结果已保存到 {report_path}")

def generate_report(results: List[Dict[str, Any]], stage: int) -> Dict[str, Any]:
    """生成监控报告"""
    report = {
        "stage": stage,
        "start_time": results[0]["timestamp"] if results else get_timestamp(),
        "end_time": results[-1]["timestamp"] if results else get_timestamp(),
        "services": {},
        "summary": {
            "total_services": 0,
            "healthy_services": 0,
            "unhealthy_services": 0,
            "unreachable_services": 0,
            "warnings_count": 0,
            "errors_count": 0
        }
    }
    
    # 按服务分组
    services_data = {}
    for result in results:
        service_name = result["service"]
        if service_name not in services_data:
            services_data[service_name] = []
        services_data[service_name].append(result)
    
    # 分析每个服务的数据
    for service_name, service_results in services_data.items():
        healthy_count = sum(1 for r in service_results if r["status"] == "healthy")
        unhealthy_count = sum(1 for r in service_results if r["status"] == "unhealthy")
        unreachable_count = sum(1 for r in service_results if r["status"] == "unreachable")
        total_count = len(service_results)
        
        warnings_count = sum(len(r.get("warnings", [])) for r in service_results)
        errors_count = sum(len(r.get("errors", [])) for r in service_results)
        
        avg_response_time = None
        response_times = [r["response_time"] for r in service_results if r["response_time"] is not None]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
        
        avg_error_rate = None
        error_rates = [r["error_rate"] for r in service_results if r["error_rate"] is not None]
        if error_rates:
            avg_error_rate = sum(error_rates) / len(error_rates)
        
        avg_cpu_usage = None
        cpu_usages = [r["cpu_usage"] for r in service_results if r["cpu_usage"] is not None]
        if cpu_usages:
            avg_cpu_usage = sum(cpu_usages) / len(cpu_usages)
        
        avg_memory_usage = None
        memory_usages = [r["memory_usage"] for r in service_results if r["memory_usage"] is not None]
        if memory_usages:
            avg_memory_usage = sum(memory_usages) / len(memory_usages)
        
        health_percentage = (healthy_count / total_count) * 100 if total_count > 0 else 0
        
        report["services"][service_name] = {
            "health_percentage": health_percentage,
            "healthy_count": healthy_count,
            "unhealthy_count": unhealthy_count,
            "unreachable_count": unreachable_count,
            "total_checks": total_count,
            "warnings_count": warnings_count,
            "errors_count": errors_count,
            "avg_response_time": avg_response_time,
            "avg_error_rate": avg_error_rate,
            "avg_cpu_usage": avg_cpu_usage,
            "avg_memory_usage": avg_memory_usage,
            "status": "healthy" if health_percentage >= 95 else "degraded" if health_percentage >= 80 else "unhealthy"
        }
        
        # 更新摘要
        report["summary"]["total_services"] += 1
        if report["services"][service_name]["status"] == "healthy":
            report["summary"]["healthy_services"] += 1
        elif report["services"][service_name]["status"] == "degraded":
            report["summary"]["unhealthy_services"] += 1
        else:
            report["summary"]["unreachable_services"] += 1
        
        report["summary"]["warnings_count"] += warnings_count
        report["summary"]["errors_count"] += errors_count
    
    return report

def main():
    parser = argparse.ArgumentParser(description='Python 3.12升级监控工具')
    parser.add_argument('--stage', type=int, choices=[1, 2, 3, 4], help='指定要监控的升级阶段')
    parser.add_argument('--services', nargs='+', help='指定要监控的服务列表')
    parser.add_argument('--interval', type=int, default=60, help='监控间隔（秒）')
    parser.add_argument('--duration', type=int, default=3600, help='监控持续时间（秒）')
    parser.add_argument('--output', help='监控报告输出文件名')
    args = parser.parse_args()
    
    if args.stage and args.services:
        logger.error("不能同时指定 --stage 和 --services")
        return 1
    
    if not args.stage and not args.services:
        logger.error("必须指定 --stage 或 --services")
        return 1
    
    services_to_monitor = []
    
    if args.stage:
        stage = args.stage
        services_to_monitor = STAGES.get(stage, [])
        logger.info(f"监控阶段 {stage} 的服务: {', '.join(services_to_monitor)}")
    else:
        services_to_monitor = args.services
        logger.info(f"监控指定的服务: {', '.join(services_to_monitor)}")
    
    # 执行监控
    results = monitor_services(services_to_monitor, args.interval, args.duration)
    
    # 生成和保存报告
    timestamp = int(time.time())
    results_filename = args.output or f"monitoring_results_{timestamp}.json"
    save_results(results, results_filename)
    
    # 生成分析报告
    stage = args.stage or 0
    report = generate_report(results, stage)
    report_filename = f"monitoring_report_{timestamp}.json"
    report_path = REPORT_DIR / report_filename
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"监控报告已保存到 {report_path}")
    
    # 输出报告摘要
    logger.info("监控报告摘要:")
    logger.info(f"阶段: {report['stage']}")
    logger.info(f"开始时间: {report['start_time']}")
    logger.info(f"结束时间: {report['end_time']}")
    logger.info(f"总服务数: {report['summary']['total_services']}")
    logger.info(f"健康服务数: {report['summary']['healthy_services']}")
    logger.info(f"不健康服务数: {report['summary']['unhealthy_services']}")
    logger.info(f"无法访问服务数: {report['summary']['unreachable_services']}")
    logger.info(f"警告总数: {report['summary']['warnings_count']}")
    logger.info(f"错误总数: {report['summary']['errors_count']}")
    
    return 0

if __name__ == "__main__":
    exit(main()) 