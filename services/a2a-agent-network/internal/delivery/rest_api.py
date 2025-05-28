#!/usr/bin/env python3
"""
REST API 接口层
REST API Delivery Layer
"""

import asyncio
import logging
import uuid
from datetime import UTC, datetime

from flask import Flask, jsonify, request
from flask_cors import cross_origin

from ..model.agent import AgentRequest
from ..service.agent_manager import AgentManager

logger = logging.getLogger(__name__)


def create_rest_api(app: Flask, agent_manager: AgentManager):
    """
    创建 REST API 路由

    Args:
        app: Flask 应用实例
        agent_manager: 智能体管理器
    """

    @app.route("/health", methods=["GET"])
    @cross_origin()
    def health_check():
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
    def get_agents():
        """获取所有智能体信息"""
        try:
            agents = agent_manager.get_all_agents()
            return jsonify(
                {
                    "success": True,
                    "data": [agent.dict() for agent in agents],
                    "total": len(agents),
                }
            )
        except Exception as e:
            logger.error(f"获取智能体信息失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/agents/<agent_id>", methods=["GET"])
    @cross_origin()
    def get_agent(agent_id: str):
        """获取指定智能体信息"""
        try:
            agent = agent_manager.get_agent_info(agent_id)
            if not agent:
                return (
                    jsonify({"success": False, "error": f"智能体 {agent_id} 不存在"}),
                    404,
                )

            return jsonify({"success": True, "data": agent.dict()})
        except Exception as e:
            logger.error(f"获取智能体 {agent_id} 信息失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/agents/<agent_id>/metrics", methods=["GET"])
    @cross_origin()
    def get_agent_metrics(agent_id: str):
        """获取智能体指标"""
        try:
            metrics = agent_manager.get_agent_metrics(agent_id)
            if not metrics:
                return (
                    jsonify({"success": False, "error": f"智能体 {agent_id} 不存在"}),
                    404,
                )

            return jsonify({"success": True, "data": metrics.dict()})
        except Exception as e:
            logger.error(f"获取智能体 {agent_id} 指标失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/agents/<agent_id>/execute", methods=["POST"])
    @cross_origin()
    def execute_agent_action(agent_id: str):
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
    def get_network_status():
        """获取网络状态"""
        try:
            status = agent_manager.get_network_status()
            return jsonify({"success": True, "data": status})
        except Exception as e:
            logger.error(f"获取网络状态失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/metrics", methods=["GET"])
    @cross_origin()
    def get_all_metrics():
        """获取所有智能体指标"""
        try:
            metrics = agent_manager.get_all_metrics()
            return jsonify(
                {
                    "success": True,
                    "data": [metric.dict() for metric in metrics],
                    "total": len(metrics),
                }
            )
        except Exception as e:
            logger.error(f"获取所有指标失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/workflows", methods=["GET"])
    @cross_origin()
    def get_workflows():
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
                            "id": "health_profile",
                            "agent": "soer",
                            "action": "生成健康画像",
                        },
                    ],
                },
                {
                    "id": "lifestyle_management",
                    "name": "生活方式工作流",
                    "description": "基于生活数据的健康管理流程",
                    "steps": [
                        {
                            "id": "data_collection",
                            "agent": "soer",
                            "action": "数据采集接收",
                        },
                        {
                            "id": "health_profile_analysis",
                            "agent": "soer",
                            "action": "健康画像分析",
                        },
                        {
                            "id": "knowledge_support",
                            "agent": "laoke",
                            "action": "提供知识支持",
                        },
                        {
                            "id": "comprehensive_response",
                            "agent": "soer",
                            "action": "综合回复",
                        },
                    ],
                },
                {
                    "id": "product_customization",
                    "name": "农产品定制工作流",
                    "description": "基于健康画像的个性化农产品定制流程",
                    "steps": [
                        {
                            "id": "health_profile_input",
                            "agent": "soer",
                            "action": "健康画像输入",
                        },
                        {
                            "id": "nutrition_analysis",
                            "agent": "xiaoke",
                            "action": "营养分析",
                        },
                        {
                            "id": "knowledge_support",
                            "agent": "laoke",
                            "action": "知识支持",
                        },
                        {
                            "id": "requirement_analysis",
                            "agent": "xiaoke",
                            "action": "需求分析",
                        },
                        {
                            "id": "product_recommendation",
                            "agent": "xiaoke",
                            "action": "产品推荐",
                        },
                    ],
                },
            ]

            return jsonify(
                {"success": True, "data": workflows, "total": len(workflows)}
            )
        except Exception as e:
            logger.error(f"获取工作流列表失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/workflows/execute", methods=["POST"])
    @cross_origin()
    def execute_workflow():
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

            workflow_id = data["workflow_id"]
            _user_id = data["user_id"]  # 暂时未使用，但保留用于未来扩展
            _parameters = data.get("parameters", {})  # 暂时未使用，但保留用于未来扩展

            # 简化的工作流执行逻辑
            # 实际实现中应该有专门的工作流引擎
            execution_id = str(uuid.uuid4())

            return jsonify(
                {
                    "success": True,
                    "data": {
                        "execution_id": execution_id,
                        "workflow_id": workflow_id,
                        "status": "started",
                        "message": f"工作流 {workflow_id} 已开始执行",
                    },
                }
            )

        except Exception as e:
            logger.error(f"执行工作流失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.errorhandler(404)
    def not_found(error):
        """404 错误处理"""
        return jsonify({"success": False, "error": "接口不存在"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """500 错误处理"""
        return jsonify({"success": False, "error": "内部服务器错误"}), 500

    logger.info("REST API 路由已注册")
