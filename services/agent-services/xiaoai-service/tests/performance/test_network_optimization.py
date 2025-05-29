#!/usr/bin/env python3
"""
小艾智能体网络优化测试脚本
验证WebSocket、HTTP/2、数据压缩等双向网络优化功能
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

import aiohttp
import websockets

# 添加项目路径
sys.path.insert(0, Path().resolve())

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# 使用loguru logger

class NetworkOptimizationTest:
    """网络优化测试类"""

    def __init__(self, base_url: str= "http://localhost:8000", ws_url: str= "ws://localhost:8001"):
        self.base_url = base_url
        self.ws_url = ws_url
        self.session = None
        self.results = []

    async def setup(self):
        """设置测试环境"""
        self.session = aiohttp.ClientSession()

        # 等待服务启动
        for _ in range(30):
            try:
                async with self.session.get(f"{self.base_url}/api/v1/health/") as resp:
                    if resp.status == 200:
                        logger.info("HTTP服务已启动")
                        break
            except Exception:
                pass
            await asyncio.sleep(1)
        else:
            raise Exception("HTTP服务启动超时")

    async def cleanup(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()

    async def measure_request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        """测量单个请求的性能"""
        start_time = time.time()

        try:
            async with self.session.request(method, url, **kwargs) as resp:
                response_data = await resp.json()
                end_time = time.time()

                return {
                    "success": True,
                    "status_code": resp.status,
                    "response_time": end_time - start_time,
                    "response_data": response_data,
                    "headers": dict(resp.headers)
                }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "response_time": end_time - start_time
            }

    async def test_network_status(self) -> dict[str, Any]:
        """测试网络状态获取"""
        logger.info("测试网络状态获取")

        url = f"{self.base_url}/api/v1/network/status"
        result = await self.measure_request("GET", url)

        return {
            "test_name": "network_status",
            "success": result["success"],
            "response_time": result["response_time"],
            "has_network_stats": "connections" in result.get("response_data", {}).get("data", {}),
            "network_config": result.get("response_data", {}).get("data", {}).get("config", {})
        }

    async def test_compression_optimization(self) -> dict[str, Any]:
        """测试数据压缩优化"""
        logger.info("测试数据压缩优化")

        # 启用压缩
        url = f"{self.base_url}/api/v1/network/optimize"
        payload = {
            "user_id": "test_user",
            "optimization_type": "compression",
            "settings": {
                "level": 6,
                "threshold": 512
            }
        }

        result = await self.measure_request("POST", url, json=payload)

        # 获取压缩统计
        stats_url = f"{self.base_url}/api/v1/network/compression/stats"
        stats_result = await self.measure_request("GET", stats_url)

        return {
            "test_name": "compression_optimization",
            "optimization_success": result["success"],
            "optimization_response_time": result["response_time"],
            "stats_success": stats_result["success"],
            "compression_enabled": result.get("response_data", {}).get("data", {}).get("enabled", False),
            "compression_level": result.get("response_data", {}).get("data", {}).get("level", 0),
            "compression_stats": stats_result.get("response_data", {}).get("data", {})
        }

    async def test_http2_optimization(self) -> dict[str, Any]:
        """测试HTTP/2优化"""
        logger.info("测试HTTP/2优化")

        # 启用HTTP/2
        url = f"{self.base_url}/api/v1/network/optimize"
        payload = {
            "user_id": "test_user",
            "optimization_type": "http2",
            "settings": {
                "max_connections": 50
            }
        }

        result = await self.measure_request("POST", url, json=payload)

        # 测试HTTP/2请求
        http2_url = f"{self.base_url}/api/v1/network/http2/request"
        http2_payload = {
            "url": f"{self.base_url}/api/v1/health/",
            "method": "GET"
        }

        http2_result = await self.measure_request("POST", http2_url, json=http2_payload)

        return {
            "test_name": "http2_optimization",
            "optimization_success": result["success"],
            "optimization_response_time": result["response_time"],
            "http2_request_success": http2_result["success"],
            "http2_request_time": http2_result["response_time"],
            "http2_enabled": result.get("response_data", {}).get("data", {}).get("enabled", False),
            "max_connections": result.get("response_data", {}).get("data", {}).get("max_connections", 0),
            "http_version": http2_result.get("response_data", {}).get("data", {}).get("http_version", "unknown")
        }

    async def test_websocket_communication(self) -> dict[str, Any]:
        """测试WebSocket双向通信"""
        logger.info("测试WebSocket双向通信")

        user_id = "test_user_ws"
        messages_sent = 0
        messages_received = 0
        connection_time = 0
        communication_success = False

        try:
            # 连接WebSocket
            start_time = time.time()
            uri = f"{self.ws_url}/api/v1/network/ws/{user_id}"

            async with websockets.connect(uri) as websocket:
                connection_time = time.time() - start_time

                # 接收连接确认
                connection_msg = await websocket.recv()
                connection_data = json.loads(connection_msg)
                messages_received += 1

                if connection_data.get("type") == "connection_established":
                    connection_data.get("connection_id")

                    # 测试ping-pong
                    ping_msg = {
                        "type": "ping",
                        "timestamp": time.time()
                    }
                    await websocket.send(json.dumps(ping_msg))
                    messages_sent += 1

                    pong_response = await websocket.recv()
                    pong_data = json.loads(pong_response)
                    messages_received += 1

                    if pong_data.get("type") == "pong":
                        # 测试设备请求
                        device_msg = {
                            "type": "device_request",
                            "request_id": "test_req_001",
                            "action": "status"
                        }
                        await websocket.send(json.dumps(device_msg))
                        messages_sent += 1

                        device_response = await websocket.recv()
                        device_data = json.loads(device_response)
                        messages_received += 1

                        if device_data.get("type") == "device_response":
                            # 测试聊天消息
                            chat_msg = {
                                "type": "chat_message",
                                "message_id": "test_msg_001",
                                "message": "你好,小艾",
                                "session_id": "test_session"
                            }
                            await websocket.send(json.dumps(chat_msg))
                            messages_sent += 1

                            chat_response = await websocket.recv()
                            chat_data = json.loads(chat_response)
                            messages_received += 1

                            if chat_data.get("type") in ["chat_response", "error"]:
                                communication_success = True

        except Exception as e:
            logger.error(f"WebSocket测试失败: {e}")

        return {
            "test_name": "websocket_communication",
            "connection_success": connection_time > 0,
            "connection_time": connection_time,
            "messages_sent": messages_sent,
            "messages_received": messages_received,
            "communication_success": communication_success,
            "bidirectional_working": messages_sent > 0 and messages_received > 0
        }

    async def test_connection_management(self) -> dict[str, Any]:
        """测试连接管理"""
        logger.info("测试连接管理")

        # 获取连接信息
        url = f"{self.base_url}/api/v1/network/connections"
        result = await self.measure_request("GET", url)

        # 获取特定用户连接
        user_url = f"{self.base_url}/api/v1/network/connections?user_id=test_user"
        user_result = await self.measure_request("GET", user_url)

        return {
            "test_name": "connection_management",
            "get_all_connections_success": result["success"],
            "get_user_connections_success": user_result["success"],
            "response_time": result["response_time"],
            "has_connection_stats": "total_connections" in result.get("response_data", {}).get("data", {}),
            "user_connections_count": len(user_result.get("response_data", {}).get("data", []))
        }

    async def test_message_sending(self) -> dict[str, Any]:
        """测试消息发送优化"""
        logger.info("测试消息发送优化")

        # 发送压缩消息
        url = f"{self.base_url}/api/v1/network/message/send"
        payload = {
            "user_id": "test_user",
            "message": {
                "type": "notification",
                "content": "这是一条测试消息" * 50,  # 创建较大消息以测试压缩
                "timestamp": time.time()
            },
            "compress": True,
            "priority": "high"
        }

        compressed_result = await self.measure_request("POST", url, json=payload)

        # 发送未压缩消息
        payload["compress"] = False
        uncompressed_result = await self.measure_request("POST", url, json=payload)

        return {
            "test_name": "message_sending",
            "compressed_success": compressed_result["success"],
            "uncompressed_success": uncompressed_result["success"],
            "compressed_time": compressed_result["response_time"],
            "uncompressed_time": uncompressed_result["response_time"],
            "compression_benefit": (
                uncompressed_result["response_time"] - compressed_result["response_time"]
                if both_success(compressed_result, uncompressed_result) else 0
            )
        }

    async def test_network_latency(self) -> dict[str, Any]:
        """测试网络延迟"""
        logger.info("测试网络延迟")

        url = f"{self.base_url}/api/v1/network/test/latency"
        payload = {
            "target_url": self.base_url
        }

        result = await self.measure_request("POST", url, json=payload)

        return {
            "test_name": "network_latency",
            "test_success": result["success"],
            "test_response_time": result["response_time"],
            "latency_data": result.get("response_data", {}).get("data", {}),
            "avg_latency": result.get("response_data", {}).get("data", {}).get("avg_latency_ms", 0),
            "success_rate": result.get("response_data", {}).get("data", {}).get("success_rate", 0)
        }

    async def test_performance_report(self) -> dict[str, Any]:
        """测试性能报告"""
        logger.info("测试性能报告")

        url = f"{self.base_url}/api/v1/network/performance/report"
        result = await self.measure_request("GET", url)

        return {
            "test_name": "performance_report",
            "report_success": result["success"],
            "response_time": result["response_time"],
            "performance_data": result.get("response_data", {}).get("data", {}),
            "overall_score": result.get("response_data", {}).get("data", {}).get("overall_score", 0),
            "has_recommendations": len(result.get("response_data", {}).get("data", {}).get("recommendations", [])) > 0
        }

    async def test_concurrent_websocket_connections(self, num_connections: int = 5) -> dict[str, Any]:
        """测试并发WebSocket连接"""
        logger.info(f"测试并发WebSocket连接 ({num_connections}个连接)")

        async def create_websocket_connection(user_id: str):
            """创建单个WebSocket连接"""
            try:
                uri = f"{self.ws_url}/api/v1/network/ws/{user_id}"

                async with websockets.connect(uri) as websocket:
                    # 接收连接确认
                    connection_msg = await websocket.recv()
                    connection_data = json.loads(connection_msg)

                    if connection_data.get("type") == "connection_established":
                        # 发送测试消息
                        test_msg = {
                            "type": "ping",
                            "user_id": user_id,
                            "timestamp": time.time()
                        }
                        await websocket.send(json.dumps(test_msg))

                        # 接收响应
                        response = await websocket.recv()
                        response_data = json.loads(response)

                        return {
                            "user_id": user_id,
                            "success": True,
                            "connection_id": connection_data.get("connection_id"),
                            "response_type": response_data.get("type")
                        }

                return {"user_id": user_id, "success": False, "error": "连接失败"}

            except Exception as e:
                return {"user_id": user_id, "success": False, "error": str(e)}

        start_time = time.time()
        tasks = [
            create_websocket_connection(f"concurrent_user_{i}")
            for _ in range(num_connections)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # 分析结果
        successful_connections = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_connections = [r for r in results if isinstance(r, dict) and not r.get("success")]
        exceptions = [r for r in results if isinstance(r, Exception)]

        return {
            "test_name": "concurrent_websocket_connections",
            "total_connections": num_connections,
            "successful_connections": len(successful_connections),
            "failed_connections": len(failed_connections),
            "exceptions": len(exceptions),
            "success_rate": len(successful_connections) / num_connections * 100,
            "total_time": end_time - start_time,
            "avg_connection_time": (end_time - start_time) / num_connections
        }

    async def run_all_tests(self) -> dict[str, Any]:
        """运行所有网络优化测试"""
        logger.info("开始网络优化测试")

        await self.setup()

        try:
            # 运行各项测试
            tests = [
                self.test_network_status(),
                self.test_compression_optimization(),
                self.test_http2_optimization(),
                self.test_websocket_communication(),
                self.test_connection_management(),
                self.test_message_sending(),
                self.test_network_latency(),
                self.test_performance_report(),
                self.test_concurrent_websocket_connections()
            ]

            results = await asyncio.gather(*tests, return_exceptions=True)

            processed_results = []
            for i, _ in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "test_name": f"test_{i}",
                        "success": False,
                        "error": str(result)
                    })
                else:
                    processed_results.append(result)

            # 汇总结果
            summary = {
                "test_timestamp": time.time(),
                "test_results": processed_results,
                "overall_performance": self._calculate_overall_performance(processed_results)
            }

            return summary

        finally:
            await self.cleanup()

    def _calculate_overall_performance(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """计算整体性能指标"""
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get("success", True))

        # WebSocket性能
        ws_test = next((r for r in results if r.get("test_name") == "websocket_communication"), {})
        websocket_working = ws_test.get("bidirectional_working", False)

        # 压缩性能
        compression_test = next((r for r in results if r.get("test_name") == "compression_optimization"), {})
        compression_enabled = compression_test.get("compression_enabled", False)

        # HTTP/2性能
        http2_test = next((r for r in results if r.get("test_name") == "http2_optimization"), {})
        http2_enabled = http2_test.get("http2_enabled", False)

        # 延迟性能
        latency_test = next((r for r in results if r.get("test_name") == "network_latency"), {})
        avg_latency = latency_test.get("avg_latency", 0)

        # 并发性能
        concurrent_test = next((r for r in results if r.get("test_name") == "concurrent_websocket_connections"), {})
        concurrent_success_rate = concurrent_test.get("success_rate", 0)

        return {
            "test_success_rate": successful_tests / total_tests * 100,
            "websocket_working": websocket_working,
            "compression_enabled": compression_enabled,
            "http2_enabled": http2_enabled,
            "avg_latency_ms": avg_latency,
            "concurrent_success_rate": concurrent_success_rate,
            "network_optimization_score": self._calculate_optimization_score(
                websocket_working, compression_enabled, http2_enabled,
                avg_latency, concurrent_success_rate
            )
        }

    def _calculate_optimization_score(self, websocket_working: bool, compression_enabled: bool,
                                    http2_enabled: bool, avg_latency: float,
                                    concurrent_success_rate: float) -> float:
        """计算网络优化评分"""
        score = 0

        # WebSocket双向通信 (25分)
        if websocket_working:
            score += 25

        # 数据压缩 (20分)
        if compression_enabled:
            score += 20

        # HTTP/2支持 (20分)
        if http2_enabled:
            score += 20

        # 延迟性能 (20分)
        if avg_latency > 0:
            if avg_latency < 50:
                score += 20
            elif avg_latency < 100:
                score += 15
            elif avg_latency < 200:
                score += 10
            else:
                score += 5

        # 并发性能 (15分)
        if concurrent_success_rate >= 90:
            score += 15
        elif concurrent_success_rate >= 70:
            score += 10
        elif concurrent_success_rate >= 50:
            score += 5

        return min(100, score)

def both_success(result1: dict[str, Any], result2: dict[str, Any]) -> bool:
    """检查两个结果是否都成功"""
    return result1.get("success", False) and result2.get("success", False)

async def main():
    """主函数"""
    print("=" * 60)
    print("小艾智能体网络优化测试")
    print("=" * 60)

    # 检查服务是否运行
    test = NetworkOptimizationTest()

    try:
        results = await test.run_all_tests()

        # 输出结果
        print("\n测试结果:")
        print("-" * 40)

        for test_result in results["test_results"]:
            print(f"\n{test_result.get('test_name', 'unknown')}:")
            for key, value in test_result.items():
                if key != "test_name":
                    if isinstance(value, float):
                        print(f"  {key}: {value:.4f}")
                    elif isinstance(value, dict) and len(str(value)) > 100:
                        print(f"  {key}: <详细数据>")
                    else:
                        print(f"  {key}: {value}")

        print("\n整体网络优化指标:")
        print("-" * 40)
        overall = results["overall_performance"]
        print(f"测试成功率: {overall['test_success_rate']:.2f}%")
        print(f"WebSocket双向通信: {'✓' if overall['websocket_working'] else '✗'}")
        print(f"数据压缩启用: {'✓' if overall['compression_enabled'] else '✗'}")
        print(f"HTTP/2支持: {'✓' if overall['http2_enabled'] else '✗'}")
        print(f"平均延迟: {overall['avg_latency_ms']:.2f}ms")
        print(f"并发成功率: {overall['concurrent_success_rate']:.2f}%")

        # 网络优化评级
        score = overall['network_optimization_score']
        print(f"\n网络优化评分: {score:.0f}/100")

        if score >= 90:
            print("网络优化等级: 优秀 🚀🚀🚀🚀🚀")
        elif score >= 75:
            print("网络优化等级: 良好 🚀🚀🚀🚀")
        elif score >= 60:
            print("网络优化等级: 一般 🚀🚀🚀")
        elif score >= 40:
            print("网络优化等级: 需要改进 🚀🚀")
        else:
            print("网络优化等级: 较差 🚀")

        # 保存详细结果
        with Path("network_optimization_test_results.json").open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\n详细结果已保存到: network_optimization_test_results.json")

    except Exception as e:
        logger.error(f"测试失败: {e}")
        print(f"\n❌ 测试失败: {e}")
        print("\n请确保:")
        print("1. HTTP服务器正在运行 (python cmd/server/http_server.py)")
        print("2. WebSocket服务器正在运行")
        print("3. 所有依赖已安装 (websockets, httpx, brotli等)")
        print("4. 网络端口未被占用")
        return 1

    print("\n✅ 网络优化测试完成!")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
