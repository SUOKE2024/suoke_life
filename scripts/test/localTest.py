#!/usr/bin/env python3
"""
索克生活本地集成测试脚本
模拟后端微服务，验证前后端集成功能
"""

import json
import logging
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from threading import Thread
from urllib.parse import urlparse, parse_qs
import uuid

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockService:
    """模拟服务基类"""

    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.data = {}
        self.start_time = datetime.now()

    def get_health(self):
        """健康检查"""
        return {
            "status": "healthy",
            "service": self.name,
            "port": self.port,
            "uptime": str(datetime.now() - self.start_time),
            "timestamp": datetime.now().isoformat()
        }

class AuthService(MockService):
    """认证服务模拟"""

    def __init__(self):
        super().__init__("auth-service", 50052)
        self.users = {
            "test@suoke.life": {
                "id": "user_001",
                "email": "test@suoke.life",
                "password": "hashed_password",
                "name": "测试用户",
                "role": "user"
            }
        }
        self.tokens = {}

    def login(self, email, password):
        """用户登录"""
        user = self.users.get(email)
        if user and password == "test123":  # 简化密码验证
            token = str(uuid.uuid4())
            self.tokens[token] = {
                "user_id": user["id"],
                "email": email,
                "expires_at": time.time() + 3600  # 1小时过期
            }
            return {
                "success": True,
                "token": token,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"]
                }
            }
        return {"success": False, "message": "Invalid credentials"}

    def verify_token(self, token):
        """验证令牌"""
        token_data = self.tokens.get(token)
        if token_data and token_data["expires_at"] > time.time():
            return {"valid": True, "user_id": token_data["user_id"]}
        return {"valid": False}

class UserService(MockService):
    """用户服务模拟"""

    def __init__(self):
        super().__init__("user-service", 50051)
        self.users = {
            "user_001": {
                "id": "user_001",
                "email": "test@suoke.life",
                "name": "测试用户",
                "age": 30,
                "gender": "male",
                "health_profile": {
                    "height": 175,
                    "weight": 70,
                    "blood_type": "A",
                    "allergies": []
                },
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

    def get_user(self, user_id):
        """获取用户信息"""
        user = self.users.get(user_id)
        if user:
            return {"success": True, "data": user}
        return {"success": False, "message": "User not found"}

    def update_user(self, user_id, data):
        """更新用户信息"""
        if user_id in self.users:
            self.users[user_id].update(data)
            return {"success": True, "data": self.users[user_id]}
        return {"success": False, "message": "User not found"}

class AgentService(MockService):
    """智能体服务模拟"""

    def __init__(self, agent_name, port):
        super().__init__(f"{agent_name}-service", port)
        self.agent_name = agent_name
        self.capabilities = self._get_capabilities()

    def _get_capabilities(self):
        """获取智能体能力"""
        capabilities_map = {
            "xiaoai": ["health_monitoring", "data_analysis", "recommendation"],
            "xiaoke": ["diagnosis_support", "symptom_analysis", "treatment_plan"],
            "laoke": ["traditional_medicine", "herbal_prescription", "acupuncture"],
            "soer": ["lifestyle_guidance", "nutrition_advice", "exercise_plan"]
        }
        return capabilities_map.get(self.agent_name, [])

    def process_request(self, request_type, data):
        """处理智能体请求"""
        return {
            "success": True,
            "agent": self.agent_name,
            "request_type": request_type,
            "result": f"{self.agent_name} processed {request_type}",
            "capabilities": self.capabilities,
            "timestamp": datetime.now().isoformat()
        }

class DiagnosisService(MockService):
    """诊断服务模拟"""

    def __init__(self, diagnosis_type, port):
        super().__init__(f"{diagnosis_type}-service", port)
        self.diagnosis_type = diagnosis_type

    def analyze(self, data):
        """分析诊断数据"""
        return {
            "success": True,
            "diagnosis_type": self.diagnosis_type,
            "analysis": f"{self.diagnosis_type} analysis completed",
            "confidence": 0.85,
            "recommendations": [
                f"Based on {self.diagnosis_type}, recommend action 1",
                f"Based on {self.diagnosis_type}, recommend action 2"
            ],
            "timestamp": datetime.now().isoformat()
        }

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """多线程HTTP服务器"""
    allow_reuse_address = True

class MockServiceHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""

    def __init__(self, services, *args, **kwargs):
        self.services = services
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """处理GET请求"""
        self._handle_request('GET')

    def do_POST(self):
        """处理POST请求"""
        self._handle_request('POST')

    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self._send_cors_headers()
        self.end_headers()

    def _handle_request(self, method):
        """处理HTTP请求"""
        try:
            # 解析URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)

            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'

            try:
                request_data = json.loads(request_body) if request_body else {}
            except json.JSONDecodeError:
                request_data = {}

            # 路由请求
            response = self._route_request(method, path, request_data, query_params)

            # 发送响应
            self._send_response(200, response)

        except Exception as e:
            logger.error(f"Request handling error: {e}")
            self._send_response(500, {"error": str(e)})

    def _route_request(self, method, path, data, params):
        """路由请求到相应的服务"""

        # 健康检查
        if path == '/health':
            return {
                "status": "ok",
                "services": [service.get_health() for service in self.services.values()],
                "timestamp": datetime.now().isoformat()
            }

        # 认证服务
        if path.startswith('/api/auth'):
            auth_service = self.services.get('auth')
            if path == '/api/auth/login' and method == 'POST':
                return auth_service.login(data.get('email'), data.get('password'))
            elif path == '/api/auth/verify' and method == 'POST':
                return auth_service.verify_token(data.get('token'))

        # 用户服务
        elif path.startswith('/api/user'):
            user_service = self.services.get('user')
            if path.startswith('/api/user/') and method == 'GET':
                user_id = path.split('/')[-1]
                return user_service.get_user(user_id)
            elif path.startswith('/api/user/') and method == 'PUT':
                user_id = path.split('/')[-1]
                return user_service.update_user(user_id, data)

        # 智能体服务
        elif path.startswith('/api/agent'):
            parts = path.split('/')
            if len(parts) >= 4:
                agent_name = parts[3]
                agent_service = self.services.get(agent_name)
                if agent_service:
                    return agent_service.process_request(data.get('type', 'general'), data)

        # 诊断服务
        elif path.startswith('/api/diagnosis'):
            parts = path.split('/')
            if len(parts) >= 4:
                diagnosis_type = parts[3]
                diagnosis_service = self.services.get(f"{diagnosis_type}_diagnosis")
                if diagnosis_service:
                    return diagnosis_service.analyze(data)

        # 默认响应
        return {
            "message": "Suoke Life Mock API",
            "version": "1.0.0",
            "path": path,
            "method": method,
            "timestamp": datetime.now().isoformat()
        }

    def _send_response(self, status_code, data):
        """发送HTTP响应"""
        self.send_response(status_code)
        self._send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode('utf-8'))

    def _send_cors_headers(self):
        """发送CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def log_message(self, format, *args):
        """自定义日志格式"""
        logger.info(f"{self.address_string()} - {format % args}")

def create_handler(services):
    """创建请求处理器"""
    def handler(*args, **kwargs):
        MockServiceHandler(services, *args, **kwargs)
    return handler

def start_mock_services():
    """启动模拟服务"""
    logger.info("Starting Suoke Life Mock Services...")

    # 创建服务实例
    services = {
        'auth': AuthService(),
        'user': UserService(),
        'xiaoai': AgentService('xiaoai', 50053),
        'xiaoke': AgentService('xiaoke', 50054),
        'laoke': AgentService('laoke', 50055),
        'soer': AgentService('soer', 50056),
        'look_diagnosis': DiagnosisService('look', 50057),
        'listen_diagnosis': DiagnosisService('listen', 50058),
        'inquiry_diagnosis': DiagnosisService('inquiry', 50059),
        'palpation_diagnosis': DiagnosisService('palpation', 50060)
    }

    # 启动HTTP服务器
    port = 8080
    handler = create_handler(services)
    server = ThreadedHTTPServer(('localhost', port), handler)

    logger.info(f"Mock API Gateway started on http://localhost:{port}")
    logger.info("Available endpoints:")
    logger.info("  - GET  /health - Health check")
    logger.info("  - POST /api/auth/login - User login")
    logger.info("  - POST /api/auth/verify - Token verification")
    logger.info("  - GET  /api/user/{id} - Get user info")
    logger.info("  - PUT  /api/user/{id} - Update user info")
    logger.info("  - POST /api/agent/{name} - Agent processing")
    logger.info("  - POST /api/diagnosis/{type} - Diagnosis analysis")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down mock services...")
        server.shutdown()

def run_integration_tests():
    """运行集成测试"""
    import requests
    import time

    base_url = "http://localhost:8080"

    logger.info("Running integration tests...")

    # 等待服务启动
    time.sleep(2)

    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "url": f"{base_url}/health",
            "expected_status": 200
        },
        {
            "name": "User Login",
            "method": "POST",
            "url": f"{base_url}/api/auth/login",
            "data": {"email": "test@suoke.life", "password": "test123"},
            "expected_status": 200
        },
        {
            "name": "Get User Info",
            "method": "GET",
            "url": f"{base_url}/api/user/user_001",
            "expected_status": 200
        },
        {
            "name": "Agent Processing",
            "method": "POST",
            "url": f"{base_url}/api/agent/xiaoai",
            "data": {"type": "health_analysis", "data": {"symptoms": ["fatigue", "headache"]}},
            "expected_status": 200
        },
        {
            "name": "Diagnosis Analysis",
            "method": "POST",
            "url": f"{base_url}/api/diagnosis/look",
            "data": {"image_data": "base64_encoded_image", "patient_id": "user_001"},
            "expected_status": 200
        }
    ]

    results = []

    for test in tests:
        try:
            if test["method"] == "GET":
                response = requests.get(test["url"], timeout=5)
            elif test["method"] == "POST":
                response = requests.post(test["url"], json=test.get("data", {}), timeout=5)

            success = response.status_code == test["expected_status"]
            results.append({
                "test": test["name"],
                "status": "PASS" if success else "FAIL",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            })

            if success:
                logger.info(f"✓ {test['name']} - PASS")
            else:
                logger.error(f"✗ {test['name']} - FAIL (Status: {response.status_code})")

        except Exception as e:
            results.append({
                "test": test["name"],
                "status": "ERROR",
                "error": str(e)
            })
            logger.error(f"✗ {test['name']} - ERROR: {e}")

    # 输出测试结果
    logger.info("\n" + "="*50)
    logger.info("INTEGRATION TEST RESULTS")
    logger.info("="*50)

    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)

    for result in results:
        status_icon = "✓" if result["status"] == "PASS" else "✗"
        logger.info(f"{status_icon} {result['test']}: {result['status']}")

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    return results

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 启动服务器并运行测试
        server_thread = Thread(target=start_mock_services, daemon=True)
        server_thread.start()

        # 等待服务器启动
        time.sleep(3)

        # 运行测试
        run_integration_tests()
    else:
        # 只启动服务器
        start_mock_services()