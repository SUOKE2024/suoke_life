"""
realtime_benchmark - 索克生活项目模块
"""

from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional, AsyncGenerator, Callable
import asyncio
import json
import logging
import time
import uuid
import websockets

"""实时流式评测模块

支持实时数据流处理和流式基准测试
"""


logger = logging.getLogger(__name__)


class StreamEventType(str, Enum):
    """流事件类型"""
    BENCHMARK_START = "benchmark_start"
    BENCHMARK_PROGRESS = "benchmark_progress"
    BENCHMARK_RESULT = "benchmark_result"
    BENCHMARK_ERROR = "benchmark_error"
    BENCHMARK_COMPLETE = "benchmark_complete"
    MODEL_PREDICTION = "model_prediction"
    METRIC_UPDATE = "metric_update"
    SYSTEM_STATUS = "system_status"


@dataclass
class StreamEvent:
    """流事件"""
    event_type: StreamEventType
    timestamp: datetime
    data: Dict[str, Any]
    event_id: str = None
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class StreamingBenchmarkSession:
    """流式基准测试会话"""
    
    def __init__(self, session_id: str, websocket: WebSocket):
        self.session_id = session_id
        self.websocket = websocket
        self.is_active = True
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.subscriptions: set[StreamEventType] = set()
        self.benchmark_tasks: Dict[str, Any] = {}
        
    async def send_event(self, event: StreamEvent):
        """发送事件"""
        if not self.is_active:
            return
        
        try:
            await self.websocket.send_text(event.to_json())
            self.last_activity = datetime.now()
        except Exception as e:
            logger.error(f"Failed to send event to session {self.session_id}: {e}")
            self.is_active = False
    
    async def close(self):
        """关闭会话"""
        self.is_active = False
        try:
            await self.websocket.close()
        except Exception:
            pass
    
    def subscribe(self, event_types: List[StreamEventType]):
        """订阅事件类型"""
        self.subscriptions.update(event_types)
    
    def unsubscribe(self, event_types: List[StreamEventType]):
        """取消订阅事件类型"""
        self.subscriptions.difference_update(event_types)
    
    def is_subscribed(self, event_type: StreamEventType) -> bool:
        """检查是否订阅了事件类型"""
        return event_type in self.subscriptions


class StreamingBenchmarkManager:
    """流式基准测试管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, StreamingBenchmarkSession] = {}
        self.event_queue = asyncio.Queue()
        self.is_running = False
        self.metrics_buffer = deque(maxlen=1000)
        self.prediction_buffer = deque(maxlen=1000)
        
    async def start(self):
        """启动管理器"""
        if self.is_running:
            return
        
        self.is_running = True
        asyncio.create_task(self._event_dispatcher())
        asyncio.create_task(self._session_cleanup())
        logger.info("Streaming benchmark manager started")
    
    async def stop(self):
        """停止管理器"""
        self.is_running = False
        
        # 关闭所有会话
        for session in list(self.sessions.values()):
            await session.close()
        
        self.sessions.clear()
        logger.info("Streaming benchmark manager stopped")
    
    async def add_session(self, websocket: WebSocket) -> str:
        """添加新会话"""
        session_id = str(uuid.uuid4())
        session = StreamingBenchmarkSession(session_id, websocket)
        self.sessions[session_id] = session
        
        # 发送欢迎消息
        welcome_event = StreamEvent(
            event_type=StreamEventType.SYSTEM_STATUS,
            timestamp=datetime.now(),
            data={
                "message": "Connected to streaming benchmark service",
                "session_id": session_id,
                "available_events": [e.value for e in StreamEventType]
            }
        )
        await session.send_event(welcome_event)
        
        logger.info(f"New streaming session created: {session_id}")
        return session_id
    
    async def remove_session(self, session_id: str):
        """移除会话"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            await session.close()
            del self.sessions[session_id]
            logger.info(f"Streaming session removed: {session_id}")
    
    async def broadcast_event(self, event: StreamEvent, session_filter: Callable[[StreamingBenchmarkSession], bool] = None):
        """广播事件"""
        await self.event_queue.put((event, session_filter))
    
    async def send_to_session(self, session_id: str, event: StreamEvent):
        """发送事件到特定会话"""
        if session_id in self.sessions:
            await self.sessions[session_id].send_event(event)
    
    async def start_streaming_benchmark(
        self,
        session_id: str,
        benchmark_config: Dict[str, Any]
    ) -> str:
        """启动流式基准测试"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        task_id = str(uuid.uuid4())
        session = self.sessions[session_id]
        session.benchmark_tasks[task_id] = {
            "config": benchmark_config,
            "start_time": datetime.now(),
            "status": "running"
        }
        
        # 发送开始事件
        start_event = StreamEvent(
            event_type=StreamEventType.BENCHMARK_START,
            timestamp=datetime.now(),
            data={
                "task_id": task_id,
                "benchmark_id": benchmark_config.get("benchmark_id"),
                "model_id": benchmark_config.get("model_id"),
                "config": benchmark_config
            }
        )
        await session.send_event(start_event)
        
        # 启动异步基准测试
        asyncio.create_task(self._run_streaming_benchmark(session_id, task_id, benchmark_config))
        
        return task_id
    
    async def _run_streaming_benchmark(
        self,
        session_id: str,
        task_id: str,
        config: Dict[str, Any]
    ):
        """运行流式基准测试"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return
            
            # 模拟流式处理
            total_samples = config.get("total_samples", 100)
            batch_size = config.get("batch_size", 10)
            
            processed_samples = 0
            metrics = {"accuracy": 0.0, "latency": 0.0}
            
            for batch_start in range(0, total_samples, batch_size):
                if not session.is_active:
                    break
                
                batch_end = min(batch_start + batch_size, total_samples)
                batch_samples = batch_end - batch_start
                
                # 模拟处理延迟
                await asyncio.sleep(0.1)
                
                # 模拟预测结果
                predictions = []
                for i in range(batch_samples):
                    prediction = {
                        "sample_id": batch_start + i,
                        "prediction": f"result_{batch_start + i}",
                        "confidence": 0.8 + (i % 3) * 0.1,
                        "latency_ms": 50 + (i % 5) * 10
                    }
                    predictions.append(prediction)
                
                processed_samples += batch_samples
                progress = processed_samples / total_samples
                
                # 更新指标
                metrics["accuracy"] = 0.85 + progress * 0.1
                metrics["latency"] = 60 - progress * 10
                
                # 发送进度事件
                progress_event = StreamEvent(
                    event_type=StreamEventType.BENCHMARK_PROGRESS,
                    timestamp=datetime.now(),
                    data={
                        "task_id": task_id,
                        "progress": progress,
                        "processed_samples": processed_samples,
                        "total_samples": total_samples,
                        "current_metrics": metrics,
                        "batch_predictions": predictions
                    }
                )
                await session.send_event(progress_event)
                
                # 发送预测事件
                for prediction in predictions:
                    pred_event = StreamEvent(
                        event_type=StreamEventType.MODEL_PREDICTION,
                        timestamp=datetime.now(),
                        data={
                            "task_id": task_id,
                            "prediction": prediction
                        }
                    )
                    await session.send_event(pred_event)
            
            # 发送完成事件
            complete_event = StreamEvent(
                event_type=StreamEventType.BENCHMARK_COMPLETE,
                timestamp=datetime.now(),
                data={
                    "task_id": task_id,
                    "final_metrics": metrics,
                    "total_samples": processed_samples,
                    "duration_seconds": (datetime.now() - session.benchmark_tasks[task_id]["start_time"]).total_seconds()
                }
            )
            await session.send_event(complete_event)
            
            # 更新任务状态
            session.benchmark_tasks[task_id]["status"] = "completed"
            
        except Exception as e:
            logger.error(f"Streaming benchmark failed: {e}")
            
            # 发送错误事件
            error_event = StreamEvent(
                event_type=StreamEventType.BENCHMARK_ERROR,
                timestamp=datetime.now(),
                data={
                    "task_id": task_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            
            session = self.sessions.get(session_id)
            if session:
                await session.send_event(error_event)
                session.benchmark_tasks[task_id]["status"] = "failed"
    
    async def _event_dispatcher(self):
        """事件分发器"""
        while self.is_running:
            try:
                event, session_filter = await asyncio.wait_for(
                    self.event_queue.get(), timeout=1.0
                )
                
                # 分发事件到订阅的会话
                for session in list(self.sessions.values()):
                    if not session.is_active:
                        continue
                    
                    if not session.is_subscribed(event.event_type):
                        continue
                    
                    if session_filter and not session_filter(session):
                        continue
                    
                    await session.send_event(event)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Event dispatcher error: {e}")
    
    async def _session_cleanup(self):
        """会话清理"""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # 每30秒清理一次
                
                current_time = datetime.now()
                inactive_sessions = []
                
                for session_id, session in self.sessions.items():
                    # 检查会话是否超时（5分钟无活动）
                    if (current_time - session.last_activity).total_seconds() > 300:
                        inactive_sessions.append(session_id)
                    elif not session.is_active:
                        inactive_sessions.append(session_id)
                
                # 移除非活跃会话
                for session_id in inactive_sessions:
                    await self.remove_session(session_id)
                
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """获取会话统计"""
        active_sessions = sum(1 for s in self.sessions.values() if s.is_active)
        total_tasks = sum(len(s.benchmark_tasks) for s in self.sessions.values())
        
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_sessions,
            "total_benchmark_tasks": total_tasks,
            "event_queue_size": self.event_queue.qsize()
        }


# 全局流式基准测试管理器
_streaming_manager: Optional[StreamingBenchmarkManager] = None


async def get_streaming_manager() -> StreamingBenchmarkManager:
    """获取流式基准测试管理器"""
    global _streaming_manager
    if _streaming_manager is None:
        _streaming_manager = StreamingBenchmarkManager()
        await _streaming_manager.start()
    return _streaming_manager


async def handle_websocket_connection(websocket: WebSocket):
    """处理WebSocket连接"""
    manager = await get_streaming_manager()
    session_id = None
    
    try:
        await websocket.accept()
        session_id = await manager.add_session(websocket)
        
        while True:
            # 接收客户端消息
            message = await websocket.receive_text()
            data = json.loads(message)
            
            command = data.get("command")
            
            if command == "subscribe":
                event_types = [StreamEventType(t) for t in data.get("event_types", [])]
                manager.sessions[session_id].subscribe(event_types)
                
            elif command == "unsubscribe":
                event_types = [StreamEventType(t) for t in data.get("event_types", [])]
                manager.sessions[session_id].unsubscribe(event_types)
                
            elif command == "start_benchmark":
                benchmark_config = data.get("config", {})
                task_id = await manager.start_streaming_benchmark(session_id, benchmark_config)
                
                response = {
                    "command": "benchmark_started",
                    "task_id": task_id
                }
                await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if session_id:
            await manager.remove_session(session_id) 