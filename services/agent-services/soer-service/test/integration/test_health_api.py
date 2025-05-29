#!/usr/bin/env python3
"""
健康检查API集成测试
"""
import os
import sys
import unittest

from fastapi.testclient import TestClient

# 确保能够导入应用代码
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from internal.delivery.rest import init_rest_app


class TestHealthAPI(unittest.TestCase):
    """健康检查API集成测试"""

    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 启动REST应用(不启动实际服务器)
        cls.rest_client = TestClient(init_rest_app())

    def test_health_check(self):
        """测试健康检查接口"""
        response = self.rest_client.get("/health")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("version", data)
        self.assertIn("uptime", data)
        self.assertIn("services", data)

    def test_readiness_check(self):
        """测试就绪检查接口"""
        response = self.rest_client.get("/health/readiness")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["status"], "ready")

    def test_liveness_check(self):
        """测试存活检查接口"""
        response = self.rest_client.get("/health/liveness")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["status"], "alive")

    def test_root_endpoint(self):
        """测试根路径接口"""
        response = self.rest_client.get("/")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["service"], "soer-service")
        self.assertIn("version", data)
        self.assertEqual(data["status"], "running")


# 如果使用真实服务进行测试，可以使用以下代码
# 需要先将下面代码移出TestHealthAPI类，放到单独的模块中运行
"""
async def start_server():
    '''启动测试服务器'''
    # 设置环境变量为测试模式
    os.environ['SOER_ENV'] = 'test'
    os.environ['MOCK_LLM'] = 'true'

    # 启动服务器进程
    server_process = subprocess.Popen(
        ["python", "cmd/server.py", "--config", "config/test_config.yaml", "--mock"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # 等待服务器启动
    time.sleep(5)

    return server_process

def stop_server(server_process):
    '''停止测试服务器'''
    if server_process:
        os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
        server_process.wait()

# 启动服务器
server_process = asyncio.run(start_server())

try:
    # 进行HTTP请求测试
    response = requests.get("http://localhost:8054/health")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")

    # 进行gRPC请求测试
    with grpc.insecure_channel('localhost:50054') as channel:
        stub = soer_service_pb2_grpc.SoerServiceStub(channel)
        # 调用具体的gRPC方法
        # response = stub.SomeMethod(soer_service_pb2.SomeRequest())
finally:
    # 测试完成后停止服务器
    stop_server(server_process)
"""


if __name__ == "__main__":
    unittest.main()
