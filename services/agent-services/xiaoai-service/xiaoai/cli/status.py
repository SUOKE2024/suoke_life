#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体状态检查模块
XiaoAI Agent Status Check Module

提供小艾智能体的状态检查和监控功能。
"""

from __future__ import annotations

import json
from typing import Any, Dict

import click
import yaml
from loguru import logger
from tabulate import tabulate


def check_status(format: str = "table") -> Dict[str, Any]:
    """
    检查小艾智能体状态
    
    Args:
        format: 输出格式 (json, yaml, table)
        
    Returns:
        状态信息字典
    """
    logger.info("开始检查小艾智能体状态...")
    
    status_data = {
        "service": "xiaoai-agent",
        "version": "1.0.0",
        "status": "unknown",
        "components": {},
        "timestamp": None,
    }
    
    try:
        # 检查各个组件状态
        status_data["components"] = {
            "database": _check_database_status(),
            "cache": _check_cache_status(),
            "message_queue": _check_message_queue_status(),
            "ai_models": _check_ai_models_status(),
            "external_services": _check_external_services_status(),
        }
        
        # 计算整体状态
        all_healthy = all(
            comp.get("status") == "healthy" 
            for comp in status_data["components"].values()
        )
        status_data["status"] = "healthy" if all_healthy else "unhealthy"
        
        # 添加时间戳
        from datetime import datetime
        status_data["timestamp"] = datetime.now().isoformat()
        
    except Exception as e:
        logger.error(f"状态检查失败: {e}")
        status_data["status"] = "error"
        status_data["error"] = str(e)
    
    # 输出结果
    _output_status(status_data, format)
    
    return status_data


def _check_database_status() -> Dict[str, Any]:
    """检查数据库状态"""
    try:
        # 这里应该实际连接数据库进行检查
        # 暂时返回模拟状态
        return {
            "status": "healthy",
            "type": "postgresql",
            "connection": "active",
            "response_time_ms": 15,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


def _check_cache_status() -> Dict[str, Any]:
    """检查缓存状态"""
    try:
        # 这里应该实际连接 Redis 进行检查
        # 暂时返回模拟状态
        return {
            "status": "healthy",
            "type": "redis",
            "connection": "active",
            "memory_usage": "45%",
            "response_time_ms": 2,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


def _check_message_queue_status() -> Dict[str, Any]:
    """检查消息队列状态"""
    try:
        # 这里应该实际连接消息队列进行检查
        # 暂时返回模拟状态
        return {
            "status": "healthy",
            "type": "celery",
            "broker": "redis",
            "active_workers": 4,
            "pending_tasks": 12,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


def _check_ai_models_status() -> Dict[str, Any]:
    """检查AI模型状态"""
    try:
        # 这里应该实际检查AI模型加载状态
        # 暂时返回模拟状态
        return {
            "status": "healthy",
            "loaded_models": [
                "syndrome_analyzer",
                "feature_extractor",
                "health_advisor"
            ],
            "model_memory_usage": "2.1GB",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


def _check_external_services_status() -> Dict[str, Any]:
    """检查外部服务状态"""
    try:
        # 这里应该实际检查外部服务连接状态
        # 暂时返回模拟状态
        services = {
            "look_service": "healthy",
            "listen_service": "healthy", 
            "inquiry_service": "healthy",
            "palpation_service": "healthy",
        }
        
        all_healthy = all(status == "healthy" for status in services.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "services": services,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


def _output_status(status_data: Dict[str, Any], format: str) -> None:
    """
    输出状态信息
    
    Args:
        status_data: 状态数据
        format: 输出格式
    """
    if format == "json":
        click.echo(json.dumps(status_data, indent=2, ensure_ascii=False))
    elif format == "yaml":
        click.echo(yaml.dump(status_data, default_flow_style=False, allow_unicode=True))
    elif format == "table":
        _output_table_format(status_data)
    else:
        click.echo(f"不支持的输出格式: {format}")


def _output_table_format(status_data: Dict[str, Any]) -> None:
    """
    以表格格式输出状态信息
    
    Args:
        status_data: 状态数据
    """
    # 整体状态
    overall_color = "green" if status_data["status"] == "healthy" else "red"
    click.echo(click.style(f"\n小艾智能体状态: {status_data['status'].upper()}", fg=overall_color, bold=True))
    click.echo(f"版本: {status_data['version']}")
    click.echo(f"检查时间: {status_data.get('timestamp', 'N/A')}")
    
    # 组件状态表格
    if "components" in status_data:
        click.echo("\n组件状态:")
        
        table_data = []
        for component, details in status_data["components"].items():
            status = details.get("status", "unknown")
            status_color = "green" if status == "healthy" else "red"
            
            # 构建详细信息
            info_parts = []
            for key, value in details.items():
                if key != "status":
                    info_parts.append(f"{key}: {value}")
            info = ", ".join(info_parts) if info_parts else "-"
            
            table_data.append([
                component.replace("_", " ").title(),
                click.style(status.upper(), fg=status_color),
                info
            ])
        
        click.echo(tabulate(
            table_data,
            headers=["组件", "状态", "详细信息"],
            tablefmt="grid"
        ))
    
    # 错误信息
    if "error" in status_data:
        click.echo(click.style(f"\n错误: {status_data['error']}", fg="red"))


if __name__ == "__main__":
    check_status() 