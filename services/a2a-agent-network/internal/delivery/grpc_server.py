#!/usr/bin/env python3
"""
gRPC 服务器实现
gRPC Server Implementation
"""

import asyncio
import logging
from concurrent import futures
from datetime import UTC, datetime
from typing import Any, AsyncIterator

import grpc
from google.protobuf import struct_pb2, timestamp_pb2

# 导入生成的 protobuf 文件
from api.grpc.generated import agent_service_pb2, agent_service_pb2_grpc

from ..service.agent_manager import AgentManager
from ..service.workflow_engine import WorkflowEngine

logger = logging.getLogger(__name__)


class AgentNetworkServicer:
    """gRPC 服务实现"""

    def __init__(self, agent_manager: AgentManager, workflow_engine: WorkflowEngine):
        """
        初始化 gRPC 服务

        Args:
            agent_manager: 智能体管理器
            workflow_engine: 工作流引擎
        """
        self.agent_manager = agent_manager
        self.workflow_engine = workflow_engine
        self._event_subscribers: dict[str, list[Any]] = {
            "agent_events": [],
            "workflow_events": [],
        }

    async def HealthCheck(self, request, context):
        """健康检查"""
        try:
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(datetime.now(UTC))

            # 这里返回的是 protobuf 消息，需要根据生成的代码调整
            return {
                "status": "healthy",
                "timestamp": timestamp,
                "service": "a2a-agent-network",
            }
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {}

    async def ListAgents(self, request, context):
        """获取智能体列表"""
        try:
            agents = self.agent_manager.get_all_agents()
            
            # 转换为 protobuf 格式
            agent_list = []
            for agent in agents:
                agent_pb = self._convert_agent_to_pb(agent)
                agent_list.append(agent_pb)

            return {
                "agents": agent_list,
                "total": len(agent_list),
            }
        except Exception as e:
            logger.error(f"获取智能体列表失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {}

    async def GetAgent(self, request, context):
        """获取指定智能体"""
        try:
            agent = self.agent_manager.get_agent_info(request.agent_id)
            if not agent:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"智能体不存在: {request.agent_id}")
                return {}

            agent_pb = self._convert_agent_to_pb(agent)
            return {"agent": agent_pb}
        except Exception as e:
            logger.error(f"获取智能体失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {}

    async def GetAgentMetrics(self, request, context):
        """获取智能体指标"""
        try:
            metrics = self.agent_manager.get_agent_metrics(request.agent_id)
            if not metrics:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"智能体不存在: {request.agent_id}")
                return {}

            metrics_pb = self._convert_metrics_to_pb(metrics)
            return {"metrics": metrics_pb}
        except Exception as e:
            logger.error(f"获取智能体指标失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {}

    async def ExecuteAgentAction(self, request, context):
        """执行智能体动作"""
        try:
            from ..model.agent import AgentRequest

            # 转换参数
            parameters = self._convert_struct_to_dict(request.parameters)

            agent_request = AgentRequest(
                agent_id=request.agent_id,
                action=request.action,
                parameters=parameters,
                user_id=request.user_id,
                request_id=request.request_id,
                timeout=request.timeout if request.timeout > 0 else None,
            )

            response = await self.agent_manager.send_request(agent_request)

            # 转换响应
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(datetime.now(UTC))

            data_struct = struct_pb2.Struct()
            if response.data:
                data_struct.update(response.data)

            return {
                "success": response.success,
                "data": data_struct,
                "error": response.error,
                "execution_time": response.execution_time,
                "timestamp": timestamp,
            }
        except Exception as e:
            logger.error(f"执行智能体动作失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {}

    async def ListWorkflows(self, request, context):
        """获取工作流列表"""
        try:
            workflows = self.workflow_engine.list_workflows()
            
            workflow_list = []
            for workflow in workflows:
                workflow_pb = self._convert_workflow_to_pb(workflow)
                workflow_list.append(workflow_pb)

            return {
                "workflows": workflow_list,
                "total": len(workflow_list),
            }
        except Exception as e:
            logger.error(f"获取工作流列表失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {}

    async def ExecuteWorkflow(self, request, context):
        """执行工作流"""
        try:
            parameters = self._convert_struct_to_dict(request.parameters)
            workflow_context = self._convert_struct_to_dict(request.context)

            execution = await self.workflow_engine.execute_workflow(
                workflow_id=request.workflow_id,
                parameters=parameters,
                user_id=request.user_id,
                context=workflow_context,
            )

            # 发送工作流事件
            await self._emit_workflow_event(
                execution.execution_id,
                execution.workflow_id,
                "started",
                {"execution_id": execution.execution_id},
            )

            return {
                "execution_id": execution.execution_id,
                "status": self._convert_workflow_status_to_pb(execution.status),
                "result": struct_pb2.Struct(),
                "error": execution.error,
                "execution_time": execution.execution_time,
                "steps_completed": 0,
                "total_steps": len(execution.steps),
            }
        except Exception as e:
            logger.error(f"执行工作流失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {}

    async def GetWorkflowExecution(self, request, context):
        """获取工作流执行"""
        try:
            execution = self.workflow_engine.get_execution(request.execution_id)
            if not execution:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"工作流执行不存在: {request.execution_id}")
                return {}

            execution_pb = self._convert_execution_to_pb(execution)
            return {"execution": execution_pb}
        except Exception as e:
            logger.error(f"获取工作流执行失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {}

    async def CancelWorkflowExecution(self, request, context):
        """取消工作流执行"""
        try:
            success = await self.workflow_engine.cancel_execution(request.execution_id)
            
            if success:
                await self._emit_workflow_event(
                    request.execution_id,
                    "",  # workflow_id 需要从执行记录获取
                    "cancelled",
                    {"execution_id": request.execution_id},
                )

            return {
                "success": success,
                "message": "工作流执行已取消" if success else "取消失败",
            }
        except Exception as e:
            logger.error(f"取消工作流执行失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {}

    async def GetWorkflowProgress(self, request, context):
        """获取工作流进度"""
        try:
            progress = self.workflow_engine.get_execution_progress(request.execution_id)
            if not progress:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"工作流执行不存在: {request.execution_id}")
                return {}

            return self._convert_progress_to_pb(progress)
        except Exception as e:
            logger.error(f"获取工作流进度失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {}

    async def GetNetworkStatus(self, request, context):
        """获取网络状态"""
        try:
            status = self.agent_manager.get_network_status()
            
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(datetime.now(UTC))

            return {
                "status": {
                    "total_agents": status.get("total_agents", 0),
                    "online_agents": status.get("online_agents", 0),
                    "offline_agents": status.get("offline_agents", 0),
                    "network_health": status.get("network_health", 0.0),
                    "agents": status.get("agents", {}),
                    "last_updated": timestamp,
                }
            }
        except Exception as e:
            logger.error(f"获取网络状态失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return {}

    async def StreamAgentEvents(self, request, context) -> AsyncIterator[Any]:
        """智能体事件流"""
        try:
            # 创建事件队列
            event_queue = asyncio.Queue()
            self._event_subscribers["agent_events"].append(event_queue)

            try:
                while True:
                    # 等待事件
                    event = await event_queue.get()
                    
                    # 过滤事件（如果指定了智能体ID）
                    if request.agent_ids and event.get("agent_id") not in request.agent_ids:
                        continue

                    yield event
            finally:
                # 清理订阅
                if event_queue in self._event_subscribers["agent_events"]:
                    self._event_subscribers["agent_events"].remove(event_queue)

        except Exception as e:
            logger.error(f"智能体事件流失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    async def StreamWorkflowEvents(self, request, context) -> AsyncIterator[Any]:
        """工作流事件流"""
        try:
            # 创建事件队列
            event_queue = asyncio.Queue()
            self._event_subscribers["workflow_events"].append(event_queue)

            try:
                while True:
                    # 等待事件
                    event = await event_queue.get()
                    
                    # 过滤事件
                    if request.workflow_ids and event.get("workflow_id") not in request.workflow_ids:
                        continue
                    
                    if request.user_id and event.get("user_id") != request.user_id:
                        continue

                    yield event
            finally:
                # 清理订阅
                if event_queue in self._event_subscribers["workflow_events"]:
                    self._event_subscribers["workflow_events"].remove(event_queue)

        except Exception as e:
            logger.error(f"工作流事件流失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    # 辅助方法
    def _convert_agent_to_pb(self, agent) -> dict[str, Any]:
        """转换智能体为 protobuf 格式"""
        timestamp = timestamp_pb2.Timestamp()
        if agent.last_heartbeat:
            try:
                heartbeat_time = datetime.fromisoformat(agent.last_heartbeat.replace('Z', '+00:00'))
                timestamp.FromDatetime(heartbeat_time)
            except:
                pass

        return {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "version": agent.version,
            "status": self._convert_agent_status_to_pb(agent.status),
            "url": agent.url,
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "enabled": cap.enabled,
                    "parameters": struct_pb2.Struct(),
                }
                for cap in agent.capabilities
            ],
            "last_heartbeat": timestamp,
            "metadata": struct_pb2.Struct(),
        }

    def _convert_agent_status_to_pb(self, status) -> int:
        """转换智能体状态为 protobuf 枚举"""
        status_map = {
            "online": 1,  # AGENT_STATUS_ONLINE
            "offline": 2,  # AGENT_STATUS_OFFLINE
            "busy": 3,    # AGENT_STATUS_BUSY
            "error": 4,   # AGENT_STATUS_ERROR
        }
        return status_map.get(status.value if hasattr(status, 'value') else status, 0)

    def _convert_workflow_status_to_pb(self, status) -> int:
        """转换工作流状态为 protobuf 枚举"""
        status_map = {
            "pending": 1,    # WORKFLOW_STATUS_PENDING
            "running": 2,    # WORKFLOW_STATUS_RUNNING
            "completed": 3,  # WORKFLOW_STATUS_COMPLETED
            "failed": 4,     # WORKFLOW_STATUS_FAILED
            "cancelled": 5,  # WORKFLOW_STATUS_CANCELLED
            "paused": 6,     # WORKFLOW_STATUS_PAUSED
        }
        return status_map.get(status.value if hasattr(status, 'value') else status, 0)

    def _convert_struct_to_dict(self, struct_pb) -> dict[str, Any]:
        """转换 protobuf Struct 为字典"""
        if not struct_pb:
            return {}
        
        # 这里需要根据实际的 protobuf 库实现
        # 暂时返回空字典
        return {}

    def _convert_metrics_to_pb(self, metrics) -> dict[str, Any]:
        """转换指标为 protobuf 格式"""
        timestamp = timestamp_pb2.Timestamp()
        if metrics.last_request_time:
            try:
                request_time = datetime.fromisoformat(metrics.last_request_time.replace('Z', '+00:00'))
                timestamp.FromDatetime(request_time)
            except:
                pass

        return {
            "agent_id": metrics.agent_id,
            "request_count": metrics.request_count,
            "success_count": metrics.success_count,
            "error_count": metrics.error_count,
            "avg_response_time": metrics.avg_response_time,
            "last_request_time": timestamp,
            "uptime": metrics.uptime,
        }

    def _convert_workflow_to_pb(self, workflow) -> dict[str, Any]:
        """转换工作流为 protobuf 格式"""
        return {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "version": workflow.version,
            "timeout": workflow.timeout,
            "retry_count": workflow.retry_count,
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "agent": step.agent,
                    "action": step.action,
                    "description": step.description,
                    "timeout": step.timeout,
                    "retry_count": step.retry_count,
                    "condition": step.condition or "",
                    "parameters": struct_pb2.Struct(),
                    "dependencies": step.dependencies,
                }
                for step in workflow.steps
            ],
            "metadata": struct_pb2.Struct(),
            "tags": workflow.tags,
        }

    def _convert_execution_to_pb(self, execution) -> dict[str, Any]:
        """转换工作流执行为 protobuf 格式"""
        start_timestamp = timestamp_pb2.Timestamp()
        end_timestamp = timestamp_pb2.Timestamp()
        
        if execution.start_time:
            try:
                start_time = datetime.fromisoformat(execution.start_time.replace('Z', '+00:00'))
                start_timestamp.FromDatetime(start_time)
            except:
                pass
        
        if execution.end_time:
            try:
                end_time = datetime.fromisoformat(execution.end_time.replace('Z', '+00:00'))
                end_timestamp.FromDatetime(end_time)
            except:
                pass

        return {
            "execution_id": execution.execution_id,
            "workflow_id": execution.workflow_id,
            "workflow_name": execution.workflow_name,
            "status": self._convert_workflow_status_to_pb(execution.status),
            "user_id": execution.user_id,
            "start_time": start_timestamp,
            "end_time": end_timestamp,
            "execution_time": execution.execution_time,
            "steps": [
                self._convert_step_execution_to_pb(step)
                for step in execution.steps
            ],
            "context": struct_pb2.Struct(),
            "result": struct_pb2.Struct(),
            "error": execution.error or "",
            "metadata": struct_pb2.Struct(),
        }

    def _convert_step_execution_to_pb(self, step) -> dict[str, Any]:
        """转换步骤执行为 protobuf 格式"""
        start_timestamp = timestamp_pb2.Timestamp()
        end_timestamp = timestamp_pb2.Timestamp()
        
        if step.start_time:
            try:
                start_time = datetime.fromisoformat(step.start_time.replace('Z', '+00:00'))
                start_timestamp.FromDatetime(start_time)
            except:
                pass
        
        if step.end_time:
            try:
                end_time = datetime.fromisoformat(step.end_time.replace('Z', '+00:00'))
                end_timestamp.FromDatetime(end_time)
            except:
                pass

        return {
            "step_id": step.step_id,
            "status": self._convert_step_status_to_pb(step.status),
            "agent_id": step.agent_id,
            "start_time": start_timestamp,
            "end_time": end_timestamp,
            "execution_time": step.execution_time,
            "result": struct_pb2.Struct(),
            "error": step.error or "",
            "retry_count": step.retry_count,
        }

    def _convert_step_status_to_pb(self, status) -> int:
        """转换步骤状态为 protobuf 枚举"""
        status_map = {
            "pending": 1,    # STEP_STATUS_PENDING
            "running": 2,    # STEP_STATUS_RUNNING
            "completed": 3,  # STEP_STATUS_COMPLETED
            "failed": 4,     # STEP_STATUS_FAILED
            "skipped": 5,    # STEP_STATUS_SKIPPED
        }
        return status_map.get(status.value if hasattr(status, 'value') else status, 0)

    def _convert_progress_to_pb(self, progress) -> dict[str, Any]:
        """转换进度为 protobuf 格式"""
        return {
            "execution_id": progress["execution_id"],
            "status": self._convert_workflow_status_to_pb(progress["status"]),
            "progress": {
                "total_steps": progress["progress"]["total_steps"],
                "completed_steps": progress["progress"]["completed_steps"],
                "failed_steps": progress["progress"]["failed_steps"],
                "running_steps": progress["progress"]["running_steps"],
                "progress_percentage": progress["progress"]["progress_percentage"],
            },
            "current_steps": [
                self._convert_step_execution_to_pb(step)
                for step in progress["current_steps"]
            ],
        }

    async def _emit_agent_event(self, agent_id: str, event_type: str, data: dict[str, Any]) -> None:
        """发送智能体事件"""
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(datetime.now(UTC))

        event = {
            "agent_id": agent_id,
            "event_type": event_type,
            "data": struct_pb2.Struct(),
            "timestamp": timestamp,
        }

        # 发送给所有订阅者
        for queue in self._event_subscribers["agent_events"]:
            try:
                await queue.put(event)
            except Exception as e:
                logger.error(f"发送智能体事件失败: {e}")

    async def _emit_workflow_event(self, execution_id: str, workflow_id: str, event_type: str, data: dict[str, Any]) -> None:
        """发送工作流事件"""
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(datetime.now(UTC))

        event = {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "event_type": event_type,
            "data": struct_pb2.Struct(),
            "timestamp": timestamp,
        }

        # 发送给所有订阅者
        for queue in self._event_subscribers["workflow_events"]:
            try:
                await queue.put(event)
            except Exception as e:
                logger.error(f"发送工作流事件失败: {e}")


async def create_grpc_server(
    agent_manager: AgentManager,
    workflow_engine: WorkflowEngine,
    host: str = "0.0.0.0",
    port: int = 50051,
) -> grpc.aio.Server:
    """
    创建 gRPC 服务器

    Args:
        agent_manager: 智能体管理器
        workflow_engine: 工作流引擎
        host: 服务器主机
        port: 服务器端口

    Returns:
        gRPC 服务器实例
    """
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # 添加服务
    servicer = AgentNetworkServicer(agent_manager, workflow_engine)
    
    # 这里需要根据生成的 protobuf 代码添加服务
    # agent_service_pb2_grpc.add_AgentNetworkServiceServicer_to_server(servicer, server)
    
    # 添加监听地址
    listen_addr = f"{host}:{port}"
    server.add_insecure_port(listen_addr)
    
    logger.info(f"gRPC 服务器将在 {listen_addr} 启动")
    
    return server 