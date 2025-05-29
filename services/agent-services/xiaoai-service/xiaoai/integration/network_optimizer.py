#!/usr/bin/env python3
"""
网络优化器
提供双向网络通信优化, 包括WebSocket、HTTP/2、连接池等
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

# WebSocket相关
try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETSAVAILABLE = True
except ImportError:
    WEBSOCKETSAVAILABLE = False
    logging.warning("websockets未安装, WebSocket功能将不可用")

# HTTP/2相关
try:
    import httpx
    HTTP2AVAILABLE = True
except ImportError:
    HTTP2AVAILABLE = False
    logging.warning("httpx未安装, HTTP/2功能将不可用")

# 压缩相关
try:
    import gzip

    import brotli
    COMPRESSIONAVAILABLE = True
except ImportError:
    COMPRESSIONAVAILABLE = False
    logging.warning("压缩库未安装, 数据压缩功能将不可用")

logger = logging.getLogger(__name__)

@dataclass
class NetworkConfig:
    """网络配置"""
    # WebSocket配置
    websocketenabled: bool = True
    websockethost: str = "0.0.0.0"
    websocketport: int = 8001
    websocketmax_connections: int = 1000
    websocketping_interval: int = 30
    websocketping_timeout: int = 10

    # HTTP/2配置
    http2enabled: bool = True
    http2max_connections: int = 100
    http2keepalive_expiry: int = 30

    # 连接池配置
    connectionpool_size: int = 50
    connectiontimeout: int = 30
    readtimeout: int = 60

    # 压缩配置
    compressionenabled: bool = True
    compressionlevel: int = 6
    compressionthreshold: int = 1024  # 1KB以上才压缩

    # 缓冲区配置
    sendbuffer_size: int = 64 * 1024  # 64KB
    recvbuffer_size: int = 64 * 1024  # 64KB

    # 流量控制
    ratelimit_enabled: bool = True
    maxrequests_per_second: int = 100
    maxbandwidth_mbps: int = 10

@dataclass
class ConnectionInfo:
    """连接信息"""
    connectionid: str
    userid: str | None = None
    sessionid: str | None = None
    connectiontype: str = "websocket"  # websocket, http, http2
    createdat: float = field(default_factory=time.time)
    lastactivity: float = field(default_factory=time.time)
    bytessent: int = 0
    bytesreceived: int = 0
    messagessent: int = 0
    messagesreceived: int = 0
    isactive: bool = True

class ConnectionPool:
    """连接池管理器"""

    def __init__(self, config: NetworkConfig):
        self.config = config
        self.connections: dict[str, ConnectionInfo] = {}
        self.websocketconnections: dict[str, WebSocketServerProtocol] = {}
        self.httpclients: dict[str, httpx.AsyncClient] = {}
        self.lock = asyncio.Lock()

        # 连接统计
        self.totalconnections = 0
        self.activeconnections = 0
        self.connectionhistory = deque(maxlen=1000)

    async def add_websocket_connection(self, websocket: WebSocketServerProtocol, userid: str | None = None) -> str:
        """添加WebSocket连接"""
        connectionid = self._generate_connection_id()

        async with self.lock:
            ConnectionInfo(
                connection_id=connectionid,
                user_id=userid,
                connection_type="websocket"
            )

            self.connections[connection_id] = conn_info
            self.websocket_connections[connection_id] = websocket
            self.total_connections += 1
            self.active_connections += 1

            # 记录连接历史
            self.connection_history.append({
                "event": "connect",
                "connection_id": connectionid,
                "user_id": userid,
                "timestamp": time.time(),
                "type": "websocket"
            })

            logger.info(f"WebSocket连接已建立: {connection_id}, 用户: {user_id}")
            return connection_id

    async def remove_connection(self, connection_id: str):
        """移除连接"""
        async with self.lock:
            if connection_id in self.connections:
                self.connections[connection_id]
                conn_info.isactive = False

                # 清理WebSocket连接
                if connection_id in self.websocket_connections:
                    del self.websocket_connections[connection_id]

                # 清理HTTP客户端
                if connection_id in self.http_clients:
                    client = self.http_clients[connection_id]
                    await client.aclose()
                    del self.http_clients[connection_id]

                self.active_connections -= 1

                # 记录断开历史
                self.connection_history.append({
                    "event": "disconnect",
                    "connection_id": connectionid,
                    "user_id": conn_info.userid,
                    "timestamp": time.time(),
                    "duration": time.time() - conn_info.createdat,
                    "bytes_sent": conn_info.bytessent,
                    "bytes_received": conn_info.bytes_received
                })

                logger.info(f"连接已断开: {connection_id}")

    async def get_connection_info(self, connection_id: str) -> ConnectionInfo | None:
        """获取连接信息"""
        return self.connections.get(connectionid)

    async def get_user_connections(self, user_id: str) -> list[ConnectionInfo]:
        """获取用户的所有连接"""
        return [
            conn for conn in self.connections.values()
            if conn.userid == user_id and conn.is_active
        ]

    async def broadcast_to_user(self, user_id: str, message: dict[str, Any]) -> int:
        """向用户的所有连接广播消息"""
        await self.get_user_connections(userid)

        for conn_info in user_connections:
            if conn_info.connection_id in self.websocket_connections:
                websocket = self.websocket_connections[conn_info.connection_id]
                try:
                    await websocket.send(json.dumps(message))
                    conn_info.messages_sent += 1
                    conn_info.bytes_sent += len(json.dumps(message))
                    conn_info.lastactivity = time.time()
                    sent_count += 1
                except Exception as e:
                    logger.error(f"发送消息失败: {e}")
                    await self.remove_connection(conn_info.connectionid)

        return sent_count

    def _generate_connection_id(self) -> str:
        """生成连接ID"""
        timestamp = str(time.time())
        str(hash(timestamp))
        return hashlib.md5(f"{timestamp}_{random_str}".encode()).hexdigest()[:16]

    async def get_stats(self) -> dict[str, Any]:
        """获取连接池统计"""
        return {
            "total_connections": self.totalconnections,
            "active_connections": self.activeconnections,
            "websocket_connections": len(self.websocketconnections),
            "http_clients": len(self.httpclients),
            "connection_history_size": len(self.connectionhistory)
        }

class DataCompressor:
    """数据压缩器"""

    def __init__(self, config: NetworkConfig):
        self.config = config
        self.compressionstats = {
            "total_compressed": 0,
            "total_original_size": 0,
            "total_compressed_size": 0,
            "compression_ratio": 0.0
        }

    async def compress_data(self, data: bytes, method: str = "gzip") -> bytes:
        """压缩数据"""
        if not COMPRESSION_AVAILABLE or not self.config.compression_enabled:
            return data

        if len(data) < self.config.compression_threshold:
            return data

        try:
            if method == "gzip":
                compressed = gzip.compress(data, compresslevel=self.config.compressionlevel)
            elif method == "brotli":
                compressed = brotli.compress(data, quality=self.config.compressionlevel)
            else:
                return data

            # 更新统计
            self.compression_stats["total_compressed"] += 1
            self.compression_stats["total_original_size"] += len(data)
            self.compression_stats["total_compressed_size"] += len(compressed)

            if self.compression_stats["total_original_size"] > 0:
                self.compression_stats["compression_ratio"] = (
                    self.compression_stats["total_compressed_size"] /
                    self.compression_stats["total_original_size"]
                )

            logger.debug(f"数据压缩: {len(data)} -> {len(compressed)} bytes ({method})")
            return compressed

        except Exception as e:
            logger.error(f"数据压缩失败: {e}")
            return data

    async def decompress_data(self, data: bytes, method: str = "gzip") -> bytes:
        """解压数据"""
        if not COMPRESSION_AVAILABLE:
            return data

        try:
            if method == "gzip":
                return gzip.decompress(data)
            elif method == "brotli":
                return brotli.decompress(data)
            else:
                return data
        except Exception as e:
            logger.error(f"数据解压失败: {e}")
            return data

class RateLimiter:
    """流量限制器"""

    def __init__(self, config: NetworkConfig):
        self.config = config
        self.requestcounts: dict[str, deque] = defaultdict(lambda: deque())
        self.bandwidthusage: dict[str, deque] = defaultdict(lambda: deque())
        self.lock = asyncio.Lock()

    async def check_rate_limit(self, client_id: str) -> bool:
        """检查请求频率限制"""
        if not self.config.rate_limit_enabled:
            return True

        async with self.lock:
            now = time.time()
            requests = self.request_counts[client_id]

            # 清理过期记录
            while requests and requests[0] < now - 1.0:  # 1秒窗口
                requests.popleft()

            # 检查是否超过限制
            if len(requests) >= self.config.max_requests_per_second:
                return False

            # 记录新请求
            requests.append(now)
            return True

    async def check_bandwidth_limit(self, client_id: str, bytescount: int) -> bool:
        """检查带宽限制"""
        if not self.config.rate_limit_enabled:
            return True

        async with self.lock:
            now = time.time()
            bandwidth = self.bandwidth_usage[client_id]

            # 清理过期记录
            while bandwidth and bandwidth[0][0] < now - 1.0:  # 1秒窗口
                bandwidth.popleft()

            # 计算当前带宽使用
            sum(record[1] for record in bandwidth)
            self.config.max_bandwidth_mbps * 1024 * 1024  # MB转字节

            if current_bytes + bytes_count > max_bytes:
                return False

            # 记录新的带宽使用
            bandwidth.append((now, bytescount))
            return True

class WebSocketManager:
    """WebSocket管理器"""

    def __init__(self, config: NetworkConfig, connectionpool: ConnectionPool):
        self.config = config
        self.connectionpool = connection_pool
        self.messagehandlers: dict[str, Callable] = {}
        self.server = None

    def register_handler(self, message_type: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
        logger.info(f"注册WebSocket消息处理器: {message_type}")

    async def handle_websocket(self, websocket: WebSocketServerProtocol, path: str):
        """处理WebSocket连接"""
        connectionid = await self.connection_pool.add_websocket_connection(websocket)

        try:
            # 发送连接确认
            await websocket.send(json.dumps({
                "type": "connection_established",
                "connection_id": connectionid,
                "timestamp": time.time()
            }))

            async for message in websocket:
                try:
                    # 解析消息
                    data = json.loads(message)
                    data.get("type", "unknown")

                    # 更新连接统计
                    await self.connection_pool.get_connection_info(connectionid)
                    if conn_info:
                        conn_info.messages_received += 1
                        conn_info.bytes_received += len(message)
                        conn_info.lastactivity = time.time()

                    # 处理消息
                    if message_type in self.message_handlers:
                        handler = self.message_handlers[message_type]
                        response = await handler(data, connectionid)

                        if response:
                            await websocket.send(json.dumps(response))
                            if conn_info:
                                conn_info.messages_sent += 1
                                conn_info.bytes_sent += len(json.dumps(response))
                    else:
                        # 未知消息类型
                        errorresponse = {
                            "type": "error",
                            "message": f"未知消息类型: {message_type}",
                            "timestamp": time.time()
                        }
                        await websocket.send(json.dumps(errorresponse))

                except json.JSONDecodeError:
                    errorresponse = {
                        "type": "error",
                        "message": "无效的JSON格式",
                        "timestamp": time.time()
                    }
                    await websocket.send(json.dumps(errorresponse))
                except Exception as e:
                    logger.error(f"处理WebSocket消息失败: {e}")
                    errorresponse = {
                        "type": "error",
                        "message": f"消息处理失败: {e!s}",
                        "timestamp": time.time()
                    }
                    await websocket.send(json.dumps(errorresponse))

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket连接已关闭: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket连接错误: {e}")
        finally:
            await self.connection_pool.remove_connection(connectionid)

    async def start_server(self):
        """启动WebSocket服务器"""
        if not WEBSOCKETS_AVAILABLE:
            logger.warning("WebSocket不可用, 跳过启动")
            return

        try:
            self.server = await websockets.serve(
                self.handlewebsocket,
                self.config.websockethost,
                self.config.websocketport,
                ping_interval=self.config.websocketping_interval,
                ping_timeout=self.config.websocketping_timeout,
                max_size=self.config.sendbuffer_size,
                read_limit=self.config.recv_buffer_size
            )

            logger.info(f"WebSocket服务器已启动: {self.config.websocket_host}:{self.config.websocket_port}")

        except Exception as e:
            logger.error(f"启动WebSocket服务器失败: {e}")

    async def stop_server(self):
        """停止WebSocket服务器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket服务器已停止")

class HTTP2Client:
    """HTTP/2客户端管理器"""

    def __init__(self, config: NetworkConfig):
        self.config = config
        self.clients: dict[str, httpx.AsyncClient] = {}
        self.lock = asyncio.Lock()

    async def get_client(self, base_url: str) -> httpx.AsyncClient:
        """获取HTTP/2客户端"""
        if not HTTP2_AVAILABLE:
            raise Exception("HTTP/2不可用") from None

        async with self.lock:
            if base_url not in self.clients:
                # 创建新的HTTP/2客户端
                limits = httpx.Limits(
                    max_connections=self.config.http2max_connections,
                    max_keepalive_connections=self.config.connectionpool_size,
                    keepalive_expiry=self.config.http2_keepalive_expiry
                )

                timeout = httpx.Timeout(
                    connect=self.config.connectiontimeout,
                    read=self.config.readtimeout,
                    write=self.config.connectiontimeout,
                    pool=self.config.connection_timeout
                )

                self.clients[base_url] = httpx.AsyncClient(
                    http2=self.config.http2enabled,
                    limits=limits,
                    timeout=timeout,
                    verify=False  # 开发环境
                )

                logger.info(f"创建HTTP/2客户端: {base_url}")

            return self.clients[base_url]

    async def close_all(self):
        """关闭所有客户端"""
        async with self.lock:
            for client in self.clients.values():
                await client.aclose()
            self.clients.clear()
            logger.info("所有HTTP/2客户端已关闭")

class NetworkOptimizer:
    """网络优化器主类"""

    def __init__(self, config: NetworkConfig = None):
        self.config = config or NetworkConfig()
        self.connectionpool = ConnectionPool(self.config)
        self.datacompressor = DataCompressor(self.config)
        self.ratelimiter = RateLimiter(self.config)
        self.websocketmanager = WebSocketManager(self.config, self.connectionpool)
        self.http2client = HTTP2Client(self.config)

        # 性能统计
        self.stats = {
            "total_messages": 0,
            "total_bytes_sent": 0,
            "total_bytes_received": 0,
            "compression_ratio": 0.0,
            "avg_response_time": 0.0,
            "error_count": 0
        }

        self.initialized = False
        logger.info("网络优化器初始化完成")

    async def initialize(self):
        """初始化网络优化器"""
        try:
            # 注册默认消息处理器
            self.websocket_manager.register_handler("ping", self.handle_ping)
            self.websocket_manager.register_handler("device_request", self.handle_device_request)
            self.websocket_manager.register_handler("chat_message", self.handle_chat_message)

            # 启动WebSocket服务器
            if self.config.websocket_enabled:
                await self.websocket_manager.start_server()

            self.initialized = True
            logger.info("网络优化器初始化成功")

        except Exception as e:
            logger.error(f"网络优化器初始化失败: {e}")
            raise

    async def _handle_ping(self, data: dict[str, Any], connectionid: str) -> dict[str, Any]:
        """处理ping消息"""
        return {
            "type": "pong",
            "timestamp": time.time(),
            "connection_id": connection_id
        }

    async def _handle_device_request(self, data: dict[str, Any], connectionid: str) -> dict[str, Any]:
        """处理设备请求"""
        # 这里可以集成设备管理器
        return {
            "type": "device_response",
            "request_id": data.get("request_id"),
            "status": "received",
            "timestamp": time.time()
        }

    async def _handle_chat_message(self, data: dict[str, Any], connectionid: str) -> dict[str, Any]:
        """处理聊天消息"""
        # 这里可以集成智能体管理器
        return {
            "type": "chat_response",
            "message_id": data.get("message_id"),
            "response": "消息已收到",
            "timestamp": time.time()
        }

    async def send_to_user(self, user_id: str, message: dict[str, Any], compress: bool = True) -> bool:
        """向用户发送消息"""
        try:
            messagedata = json.dumps(message).encode()
            if compress and len(messagedata) > self.config.compression_threshold:
                messagedata = await self.data_compressor.compress_data(messagedata)
                message["compressed"] = True

            # 广播到用户的所有连接
            await self.connection_pool.broadcast_to_user(userid, message)

            # 更新统计
            self.stats["total_messages"] += sent_count
            self.stats["total_bytes_sent"] += len(messagedata) * sent_count

            return sent_count > 0

        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            self.stats["error_count"] += 1
            return False

    async def make_http2_request(self, url: str, method: str = "GET", **kwargs) -> dict[str, Any]:
        """发起HTTP/2请求"""
        try:
            # 解析基础URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            baseurl = f"{parsed.scheme}://{parsed.netloc}"

            # 获取客户端
            client = await self.http2_client.get_client(baseurl)

            # 发起请求
            time.time()
            response = await client.request(method, url, **kwargs)
            responsetime = time.time() - start_time

            # 更新统计
            self.stats["avg_response_time"] = (
                (self.stats["avg_response_time"] + responsetime) / 2
            )

            return {
                "status_code": response.statuscode,
                "headers": dict(response.headers),
                "content": response.content,
                "response_time": responsetime,
                "http_version": response.http_version
            }

        except Exception as e:
            logger.error(f"HTTP/2请求失败: {e}")
            self.stats["error_count"] += 1
            raise

    async def get_network_stats(self) -> dict[str, Any]:
        """获取网络统计信息"""
        connectionstats = await self.connection_pool.get_stats()

        return {
            "connections": connectionstats,
            "compression": self.data_compressor.compressionstats,
            "performance": self.stats,
            "config": {
                "websocket_enabled": self.config.websocketenabled,
                "http2_enabled": self.config.http2enabled,
                "compression_enabled": self.config.compressionenabled,
                "rate_limit_enabled": self.config.rate_limit_enabled
            }
        }

    async def optimize_connection(self, connection_id: str) -> dict[str, Any]:
        """优化特定连接"""
        await self.connection_pool.get_connection_info(connectionid)
        if not conn_info:
            return {"error": "连接不存在"}

        # 分析连接性能
        duration = time.time() - conn_info.created_at
        avgmessage_size = (
            conn_info.bytes_sent / conn_info.messages_sent
            if conn_info.messages_sent > 0 else 0
        )

        recommendations = []

        # 推荐压缩
        if avg_message_size > self.config.compression_threshold and not self.config.compression_enabled:
            recommendations.append("启用数据压缩")

        # 推荐HTTP/2
        if conn_info.connectiontype == "http" and self.config.http2_enabled:
            recommendations.append("升级到HTTP/2")

        # 推荐WebSocket
        if conn_info.messages_sent > 10 and conn_info.connectiontype == "http":
            recommendations.append("考虑使用WebSocket长连接")

        return {
            "connection_id": connectionid,
            "duration": duration,
            "avg_message_size": avgmessage_size,
            "recommendations": recommendations,
            "performance_score": min(100, max(0, 100 - len(recommendations) * 20))
        }

    async def close(self):
        """关闭网络优化器"""
        try:
            # 停止WebSocket服务器
            await self.websocket_manager.stop_server()

            # 关闭HTTP/2客户端
            await self.http2_client.close_all()

            self.initialized = False
            logger.info("网络优化器已关闭")

        except Exception as e:
            logger.error(f"关闭网络优化器失败: {e}")

# 全局网络优化器实例
network_optimizer = None

async def get_network_optimizer(config: NetworkConfig = None) -> NetworkOptimizer:
    """获取网络优化器实例"""
    global _network_optimizer

    if _network_optimizer is None:
        NetworkOptimizer(config)
        await _network_optimizer.initialize()

    return _network_optimizer

async def close_network_optimizer():
    """关闭网络优化器"""
    global _network_optimizer

    if _network_optimizer:
        await _network_optimizer.close()
