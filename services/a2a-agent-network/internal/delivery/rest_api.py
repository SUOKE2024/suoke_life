#!/usr/bin/env python3
"""
REST API 接口层
REST API Delivery Layer
"""

import asyncio
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from flask import Flask, Response, jsonify, request
from flask_cors import cross_origin

from ..model.agent import AgentRequest
from ..service.agent_manager import AgentManager

logger = logging.getLogger(__name__)


def create_rest_api(app: Flask, agent_manager: AgentManager) -> None:
    """
    创建 REST API 路由

    Args:
        app: Flask 应用实例
        agent_manager: 智能体管理器
    """

    @app.route("/health", methods=["GET"])
    @cross_origin()
    def health_check() -> Response:
        """健康检查接口"""
        return jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now(UTC).isoformat(),
                "service": "a2a-agent-network",
            }
        )

    @app.route("/api/v1/agents", methods=["GET"])
    @cross_origin()
    def get_agents() -> Response | tuple[Response, int]:
        """获取所有智能体信息"""
        try:
            agents = agent_manager.get_all_agents()
            return jsonify(
                {
                    "success": True,
                    "data": [agent.model_dump() for agent in agents],
                    "total": len(agents),
                }
            )
        except Exception as e:
            logger.error(f"获取智能体信息失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/agents/register", methods=["POST"])
    @cross_origin()
    def register_agent() -> Response | tuple[Response, int]:
        """注册智能体"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "请求数据不能为空"}), 400

            # 验证必需字段
            required_fields = ["id", "name", "url"]
            for field in required_fields:
                if field not in data:
                    return (
                        jsonify({"success": False, "error": f"缺少必需字段: {field}"}),
                        400,
                    )

            # 创建智能体对象
            from ..model.agent import AgentInfo, AgentCapability, AgentStatus
            
            capabilities = []
            for cap_data in data.get("capabilities", []):
                capability = AgentCapability(
                    name=cap_data.get("name", ""),
                    description=cap_data.get("description", ""),
                    enabled=cap_data.get("enabled", True),
                    parameters=cap_data.get("parameters", {}),
                )
                capabilities.append(capability)

            agent = AgentInfo(
                id=data["id"],
                name=data["name"],
                description=data.get("description", ""),
                version=data.get("version", "1.0.0"),
                url=data["url"],
                capabilities=capabilities,
                status=AgentStatus.OFFLINE,
                last_heartbeat=None,
                metadata=data.get("metadata", {}),
            )

            # 注册智能体
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(agent_manager.register_agent(agent))
            finally:
                loop.close()

            if success:
                return jsonify({
                    "success": True,
                    "message": "智能体注册成功",
                    "agent_id": data["id"],
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "智能体注册失败",
                }), 400

        except Exception as e:
            logger.error(f"智能体注册异常: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/agents/<agent_id>/deregister", methods=["DELETE"])
    @cross_origin()
    def deregister_agent(agent_id: str) -> Response | tuple[Response, int]:
        """注销智能体"""
        try:
            # 注销智能体
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(agent_manager.deregister_agent(agent_id))
            finally:
                loop.close()

            if success:
                return jsonify({
                    "success": True,
                    "message": "智能体注销成功",
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "智能体注销失败或不存在",
                }), 404

        except Exception as e:
            logger.error(f"智能体注销异常: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/agents/<agent_id>", methods=["GET"])
    @cross_origin()
    def get_agent(agent_id: str) -> Response | tuple[Response, int]:
        """获取指定智能体信息"""
        try:
            agent = agent_manager.get_agent_info(agent_id)
            if not agent:
                return (
                    jsonify({"success": False, "error": f"智能体 {agent_id} 不存在"}),
                    404,
                )

            return jsonify({"success": True, "data": agent.model_dump()})
        except Exception as e:
            logger.error(f"获取智能体 {agent_id} 信息失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/agents/<agent_id>/metrics", methods=["GET"])
    @cross_origin()
    def get_agent_metrics(agent_id: str) -> Response | tuple[Response, int]:
        """获取智能体指标"""
        try:
            metrics = agent_manager.get_agent_metrics(agent_id)
            if not metrics:
                return (
                    jsonify({"success": False, "error": f"智能体 {agent_id} 不存在"}),
                    404,
                )

            return jsonify({"success": True, "data": metrics.model_dump()})
        except Exception as e:
            logger.error(f"获取智能体 {agent_id} 指标失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/agents/<agent_id>/execute", methods=["POST"])
    @cross_origin()
    def execute_agent_action(agent_id: str) -> Response | tuple[Response, int]:
        """执行智能体动作"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "请求数据不能为空"}), 400

            # 验证必需字段
            required_fields = ["action", "user_id"]
            for field in required_fields:
                if field not in data:
                    return (
                        jsonify({"success": False, "error": f"缺少必需字段: {field}"}),
                        400,
                    )

            # 创建请求
            agent_request = AgentRequest(
                agent_id=agent_id,
                action=data["action"],
                parameters=data.get("parameters", {}),
                user_id=data["user_id"],
                request_id=data.get("request_id", str(uuid.uuid4())),
                timeout=data.get("timeout"),
            )

            # 执行请求
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    agent_manager.send_request(agent_request)
                )
            finally:
                loop.close()

            return jsonify(
                {
                    "success": response.success,
                    "data": response.data if response.success else None,
                    "error": response.error if not response.success else None,
                    "execution_time": response.execution_time,
                    "timestamp": response.timestamp,
                }
            )

        except Exception as e:
            logger.error(f"执行智能体 {agent_id} 动作失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/network/status", methods=["GET"])
    @cross_origin()
    def get_network_status() -> Response | tuple[Response, int]:
        """获取网络状态"""
        try:
            status = agent_manager.get_network_status()
            return jsonify({"success": True, "data": status})
        except Exception as e:
            logger.error(f"获取网络状态失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/metrics", methods=["GET"])
    @cross_origin()
    def get_all_metrics() -> Response | tuple[Response, int]:
        """获取所有智能体指标"""
        try:
            metrics = agent_manager.get_all_metrics()
            return jsonify(
                {
                    "success": True,
                    "data": [metric.model_dump() for metric in metrics],
                    "total": len(metrics),
                }
            )
        except Exception as e:
            logger.error(f"获取所有指标失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/workflows", methods=["GET"])
    @cross_origin()
    def get_workflows() -> Response | tuple[Response, int]:
        """获取可用工作流列表"""
        try:
            # 这里返回预定义的工作流信息
            workflows = [
                {
                    "id": "health_consultation",
                    "name": "健康咨询工作流",
                    "description": "用户健康咨询的完整处理流程",
                    "steps": [
                        {
                            "id": "reception",
                            "agent": "xiaoai",
                            "action": "接收用户咨询",
                        },
                        {
                            "id": "diagnosis_assessment",
                            "agent": "xiaoai",
                            "action": "诊断体质评估",
                        },
                        {
                            "id": "knowledge_support",
                            "agent": "laoke",
                            "action": "提供知识支持",
                        },
                        {
                            "id": "personalized_advice",
                            "agent": "xiaoke",
                            "action": "个性化建议",
                        },
                        {
                            "id": "lifestyle_guidance",
                            "agent": "soer",
                            "action": "生活方式指导",
                        },
                    ],
                },
                {
                    "id": "health_monitoring",
                    "name": "健康监测工作流",
                    "description": "持续健康监测和预警流程",
                    "steps": [
                        {
                            "id": "data_collection",
                            "agent": "xiaoai",
                            "action": "收集健康数据",
                        },
                        {
                            "id": "analysis",
                            "agent": "laoke",
                            "action": "数据分析",
                        },
                        {
                            "id": "alert_generation",
                            "agent": "xiaoke",
                            "action": "生成预警",
                        },
                        {
                            "id": "intervention_recommendation",
                            "agent": "soer",
                            "action": "干预建议",
                        },
                    ],
                },
            ]

            return jsonify(
                {
                    "success": True,
                    "data": workflows,
                    "total": len(workflows),
                }
            )
        except Exception as e:
            logger.error(f"获取工作流列表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/workflows/execute", methods=["POST"])
    @cross_origin()
    def execute_workflow() -> Response | tuple[Response, int]:
        """执行工作流"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "请求数据不能为空"}), 400

            # 验证必需字段
            required_fields = ["workflow_id", "user_id"]
            for field in required_fields:
                if field not in data:
                    return (
                        jsonify({"success": False, "error": f"缺少必需字段: {field}"}),
                        400,
                    )

            # 这里应该调用工作流引擎执行工作流
            # 目前返回模拟响应
            execution_id = str(uuid.uuid4())

            return jsonify(
                {
                    "success": True,
                    "data": {
                        "execution_id": execution_id,
                        "workflow_id": data["workflow_id"],
                        "status": "running",
                        "message": "工作流已开始执行",
                    },
                }
            )

        except Exception as e:
            logger.error(f"执行工作流失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.errorhandler(404)
    def not_found(error: Any) -> tuple[Response, int]:
        """404 错误处理"""
        return jsonify({"success": False, "error": "接口不存在"}), 404

    @app.errorhandler(500)
    def internal_error(error: Any) -> tuple[Response, int]:
        """500 错误处理"""
        logger.error(f"内部服务器错误: {error}")
        return jsonify({"success": False, "error": "内部服务器错误"}), 500

    logger.info("REST API 路由已注册")
