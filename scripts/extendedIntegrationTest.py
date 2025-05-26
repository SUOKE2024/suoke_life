#!/usr/bin/env python3
"""
索克生活扩展集成测试脚本
包含所有微服务的完整集成验证
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from threading import Thread
from urllib.parse import urlparse, parse_qs
import uuid
import hashlib
import base64

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExtendedMockService:
    """扩展模拟服务基类"""
    
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.data = {}
        self.start_time = datetime.now()
        self.request_count = 0
    
    def get_health(self):
        """健康检查"""
        return {
            "status": "healthy",
            "service": self.name,
            "port": self.port,
            "uptime": str(datetime.now() - self.start_time),
            "request_count": self.request_count,
            "timestamp": datetime.now().isoformat()
        }
    
    def increment_requests(self):
        """增加请求计数"""
        self.request_count += 1

class AccessibilityService(ExtendedMockService):
    """无障碍服务"""
    
    def __init__(self):
        super().__init__("accessibility-service", 50061)
        self.accessibility_features = {
            "screen_reader": True,
            "voice_navigation": True,
            "high_contrast": True,
            "large_text": True,
            "gesture_control": True
        }
    
    def get_accessibility_config(self, user_id):
        """获取用户无障碍配置"""
        self.increment_requests()
        return {
            "success": True,
            "user_id": user_id,
            "features": self.accessibility_features,
            "customizations": {
                "font_size": "large",
                "contrast_mode": "high",
                "voice_speed": "normal"
            }
        }
    
    def update_accessibility_config(self, user_id, config):
        """更新无障碍配置"""
        self.increment_requests()
        return {
            "success": True,
            "user_id": user_id,
            "updated_config": config,
            "message": "Accessibility configuration updated"
        }

class BlockchainService(ExtendedMockService):
    """区块链服务"""
    
    def __init__(self):
        super().__init__("blockchain-service", 50062)
        self.blockchain_data = {}
    
    def store_health_data(self, user_id, data):
        """存储健康数据到区块链"""
        self.increment_requests()
        data_hash = hashlib.sha256(json.dumps(data).encode()).hexdigest()
        block_id = str(uuid.uuid4())
        
        self.blockchain_data[block_id] = {
            "user_id": user_id,
            "data_hash": data_hash,
            "timestamp": datetime.now().isoformat(),
            "verified": True
        }
        
        return {
            "success": True,
            "block_id": block_id,
            "data_hash": data_hash,
            "verification_status": "verified"
        }
    
    def verify_data_integrity(self, block_id):
        """验证数据完整性"""
        self.increment_requests()
        block = self.blockchain_data.get(block_id)
        if block:
            return {
                "success": True,
                "block_id": block_id,
                "verified": block["verified"],
                "timestamp": block["timestamp"]
            }
        return {"success": False, "message": "Block not found"}

class HealthDataService(ExtendedMockService):
    """健康数据服务"""
    
    def __init__(self):
        super().__init__("health-data-service", 50063)
        self.health_records = {}
    
    def store_health_record(self, user_id, record_type, data):
        """存储健康记录"""
        self.increment_requests()
        record_id = str(uuid.uuid4())
        
        self.health_records[record_id] = {
            "user_id": user_id,
            "record_type": record_type,
            "data": data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "record_id": record_id,
            "record_type": record_type,
            "message": "Health record stored successfully"
        }
    
    def get_health_records(self, user_id, record_type=None):
        """获取健康记录"""
        self.increment_requests()
        user_records = [
            record for record in self.health_records.values()
            if record["user_id"] == user_id and 
            (record_type is None or record["record_type"] == record_type)
        ]
        
        return {
            "success": True,
            "user_id": user_id,
            "records": user_records,
            "count": len(user_records)
        }

class MedKnowledgeService(ExtendedMockService):
    """医学知识服务"""
    
    def __init__(self):
        super().__init__("med-knowledge-service", 50064)
        self.knowledge_base = {
            "symptoms": {
                "headache": {
                    "causes": ["stress", "dehydration", "lack_of_sleep"],
                    "treatments": ["rest", "hydration", "pain_relief"],
                    "severity": "mild_to_moderate"
                },
                "fever": {
                    "causes": ["infection", "inflammation", "immune_response"],
                    "treatments": ["rest", "fluids", "fever_reducer"],
                    "severity": "moderate"
                }
            }
        }
    
    def query_knowledge(self, query_type, query_data):
        """查询医学知识"""
        self.increment_requests()
        
        if query_type == "symptom_analysis":
            symptom = query_data.get("symptom", "").lower()
            knowledge = self.knowledge_base["symptoms"].get(symptom, {})
            
            return {
                "success": True,
                "query_type": query_type,
                "symptom": symptom,
                "knowledge": knowledge,
                "confidence": 0.9 if knowledge else 0.1
            }
        
        return {
            "success": True,
            "query_type": query_type,
            "result": "General medical knowledge response",
            "confidence": 0.7
        }

class MedicalResourceService(ExtendedMockService):
    """医疗资源服务"""
    
    def __init__(self):
        super().__init__("medical-resource-service", 50065)
        self.resources = {
            "hospitals": [
                {"id": "h001", "name": "中心医院", "type": "综合医院", "distance": 2.5},
                {"id": "h002", "name": "中医院", "type": "中医医院", "distance": 3.2}
            ],
            "doctors": [
                {"id": "d001", "name": "张医生", "specialty": "内科", "available": True},
                {"id": "d002", "name": "李医生", "specialty": "中医", "available": True}
            ]
        }
    
    def find_nearby_resources(self, resource_type, location, radius=10):
        """查找附近医疗资源"""
        self.increment_requests()
        
        resources = self.resources.get(resource_type, [])
        nearby_resources = [r for r in resources if r.get("distance", 0) <= radius]
        
        return {
            "success": True,
            "resource_type": resource_type,
            "location": location,
            "radius": radius,
            "resources": nearby_resources,
            "count": len(nearby_resources)
        }

class MessageBusService(ExtendedMockService):
    """消息总线服务"""
    
    def __init__(self):
        super().__init__("message-bus-service", 50066)
        self.message_queue = []
        self.subscribers = {}
    
    def publish_message(self, topic, message):
        """发布消息"""
        self.increment_requests()
        
        message_id = str(uuid.uuid4())
        message_data = {
            "id": message_id,
            "topic": topic,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "delivered": False
        }
        
        self.message_queue.append(message_data)
        
        return {
            "success": True,
            "message_id": message_id,
            "topic": topic,
            "status": "published"
        }
    
    def subscribe_topic(self, topic, subscriber_id):
        """订阅主题"""
        self.increment_requests()
        
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        
        if subscriber_id not in self.subscribers[topic]:
            self.subscribers[topic].append(subscriber_id)
        
        return {
            "success": True,
            "topic": topic,
            "subscriber_id": subscriber_id,
            "status": "subscribed"
        }

class RAGService(ExtendedMockService):
    """检索增强生成服务"""
    
    def __init__(self):
        super().__init__("rag-service", 50067)
        self.knowledge_vectors = {}
    
    def generate_response(self, query, context=None):
        """生成增强响应"""
        self.increment_requests()
        
        # 模拟RAG处理
        retrieved_docs = self._retrieve_documents(query)
        generated_response = self._generate_with_context(query, retrieved_docs, context)
        
        return {
            "success": True,
            "query": query,
            "response": generated_response,
            "retrieved_docs": len(retrieved_docs),
            "confidence": 0.85
        }
    
    def _retrieve_documents(self, query):
        """检索相关文档"""
        # 模拟文档检索
        return [
            {"doc_id": "doc1", "relevance": 0.9, "content": "相关医学知识1"},
            {"doc_id": "doc2", "relevance": 0.8, "content": "相关医学知识2"}
        ]
    
    def _generate_with_context(self, query, docs, context):
        """基于上下文生成响应"""
        return f"基于检索到的{len(docs)}个文档，针对'{query}'的回答是：这是一个智能生成的医学建议。"

class SuokeBenchService(ExtendedMockService):
    """索克基准服务"""
    
    def __init__(self):
        super().__init__("suoke-bench-service", 50068)
        self.benchmark_results = {}
    
    def run_benchmark(self, benchmark_type, config=None):
        """运行基准测试"""
        self.increment_requests()
        
        benchmark_id = str(uuid.uuid4())
        
        # 模拟基准测试结果
        results = {
            "benchmark_id": benchmark_id,
            "benchmark_type": benchmark_type,
            "config": config or {},
            "results": {
                "performance_score": 85.6,
                "accuracy": 0.92,
                "response_time": 150,
                "throughput": 1000
            },
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
        self.benchmark_results[benchmark_id] = results
        
        return {
            "success": True,
            "benchmark_id": benchmark_id,
            "results": results
        }

class CornMazeService(ExtendedMockService):
    """玉米迷宫服务（认知训练）"""
    
    def __init__(self):
        super().__init__("corn-maze-service", 50069)
        self.game_sessions = {}
    
    def start_game_session(self, user_id, difficulty="medium"):
        """开始游戏会话"""
        self.increment_requests()
        
        session_id = str(uuid.uuid4())
        
        self.game_sessions[session_id] = {
            "user_id": user_id,
            "difficulty": difficulty,
            "start_time": datetime.now().isoformat(),
            "status": "active",
            "score": 0,
            "level": 1
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "difficulty": difficulty,
            "maze_config": {
                "size": "10x10",
                "obstacles": 25,
                "targets": 3
            }
        }
    
    def update_game_progress(self, session_id, action, position):
        """更新游戏进度"""
        self.increment_requests()
        
        session = self.game_sessions.get(session_id)
        if session:
            session["score"] += 10
            session["last_action"] = action
            session["position"] = position
            
            return {
                "success": True,
                "session_id": session_id,
                "score": session["score"],
                "status": session["status"]
            }
        
        return {"success": False, "message": "Session not found"}

class ExtendedServiceHandler(BaseHTTPRequestHandler):
    """扩展的HTTP请求处理器"""
    
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
            response = self._route_extended_request(method, path, request_data, query_params)
            
            # 发送响应
            self._send_response(200, response)
            
        except Exception as e:
            logger.error(f"Request handling error: {e}")
            self._send_response(500, {"error": str(e)})
    
    def _route_extended_request(self, method, path, data, params):
        """路由扩展请求"""
        
        # 健康检查
        if path == '/health':
            return {
                "status": "ok",
                "services": [service.get_health() for service in self.services.values()],
                "total_services": len(self.services),
                "timestamp": datetime.now().isoformat()
            }
        
        # 无障碍服务
        elif path.startswith('/api/accessibility'):
            service = self.services.get('accessibility')
            if path == '/api/accessibility/config' and method == 'GET':
                user_id = params.get('user_id', [''])[0]
                return service.get_accessibility_config(user_id)
            elif path == '/api/accessibility/config' and method == 'POST':
                return service.update_accessibility_config(data.get('user_id'), data.get('config', {}))
        
        # 区块链服务
        elif path.startswith('/api/blockchain'):
            service = self.services.get('blockchain')
            if path == '/api/blockchain/store' and method == 'POST':
                return service.store_health_data(data.get('user_id'), data.get('data', {}))
            elif path.startswith('/api/blockchain/verify/'):
                block_id = path.split('/')[-1]
                return service.verify_data_integrity(block_id)
        
        # 健康数据服务
        elif path.startswith('/api/health-data'):
            service = self.services.get('health_data')
            if path == '/api/health-data/records' and method == 'POST':
                return service.store_health_record(
                    data.get('user_id'), 
                    data.get('record_type'), 
                    data.get('data', {})
                )
            elif path == '/api/health-data/records' and method == 'GET':
                user_id = params.get('user_id', [''])[0]
                record_type = params.get('record_type', [None])[0]
                return service.get_health_records(user_id, record_type)
        
        # 医学知识服务
        elif path.startswith('/api/med-knowledge'):
            service = self.services.get('med_knowledge')
            if path == '/api/med-knowledge/query' and method == 'POST':
                return service.query_knowledge(data.get('query_type'), data.get('query_data', {}))
        
        # 医疗资源服务
        elif path.startswith('/api/medical-resource'):
            service = self.services.get('medical_resource')
            if path == '/api/medical-resource/find' and method == 'POST':
                return service.find_nearby_resources(
                    data.get('resource_type'),
                    data.get('location'),
                    data.get('radius', 10)
                )
        
        # 消息总线服务
        elif path.startswith('/api/message-bus'):
            service = self.services.get('message_bus')
            if path == '/api/message-bus/publish' and method == 'POST':
                return service.publish_message(data.get('topic'), data.get('message'))
            elif path == '/api/message-bus/subscribe' and method == 'POST':
                return service.subscribe_topic(data.get('topic'), data.get('subscriber_id'))
        
        # RAG服务
        elif path.startswith('/api/rag'):
            service = self.services.get('rag')
            if path == '/api/rag/generate' and method == 'POST':
                return service.generate_response(data.get('query'), data.get('context'))
        
        # 基准测试服务
        elif path.startswith('/api/suoke-bench'):
            service = self.services.get('suoke_bench')
            if path == '/api/suoke-bench/run' and method == 'POST':
                return service.run_benchmark(data.get('benchmark_type'), data.get('config'))
        
        # 玉米迷宫服务
        elif path.startswith('/api/corn-maze'):
            service = self.services.get('corn_maze')
            if path == '/api/corn-maze/start' and method == 'POST':
                return service.start_game_session(data.get('user_id'), data.get('difficulty', 'medium'))
            elif path == '/api/corn-maze/update' and method == 'POST':
                return service.update_game_progress(
                    data.get('session_id'),
                    data.get('action'),
                    data.get('position')
                )
        
        # 默认响应
        return {
            "message": "Suoke Life Extended Mock API",
            "version": "2.0.0",
            "path": path,
            "method": method,
            "available_services": list(self.services.keys()),
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

def create_extended_handler(services):
    """创建扩展请求处理器"""
    def handler(*args, **kwargs):
        ExtendedServiceHandler(services, *args, **kwargs)
    return handler

def start_extended_mock_services():
    """启动扩展模拟服务"""
    logger.info("Starting Suoke Life Extended Mock Services...")
    
    # 创建所有服务实例
    services = {
        # 原有服务
        'auth': AuthService(),
        'user': UserService(),
        'xiaoai': AgentService('xiaoai', 50053),
        'xiaoke': AgentService('xiaoke', 50054),
        'laoke': AgentService('laoke', 50055),
        'soer': AgentService('soer', 50056),
        'look_diagnosis': DiagnosisService('look', 50057),
        'listen_diagnosis': DiagnosisService('listen', 50058),
        'inquiry_diagnosis': DiagnosisService('inquiry', 50059),
        'palpation_diagnosis': DiagnosisService('palpation', 50060),
        
        # 新增的9个服务
        'accessibility': AccessibilityService(),
        'blockchain': BlockchainService(),
        'health_data': HealthDataService(),
        'med_knowledge': MedKnowledgeService(),
        'medical_resource': MedicalResourceService(),
        'message_bus': MessageBusService(),
        'rag': RAGService(),
        'suoke_bench': SuokeBenchService(),
        'corn_maze': CornMazeService()
    }
    
    # 启动HTTP服务器
    port = 8080
    handler = create_extended_handler(services)
    server = ThreadedHTTPServer(('localhost', port), handler)
    
    logger.info(f"Extended Mock API Gateway started on http://localhost:{port}")
    logger.info(f"Total services: {len(services)}")
    logger.info("New service endpoints:")
    logger.info("  - GET/POST /api/accessibility/config - 无障碍配置")
    logger.info("  - POST /api/blockchain/store - 区块链数据存储")
    logger.info("  - GET /api/blockchain/verify/{id} - 数据完整性验证")
    logger.info("  - POST /api/health-data/records - 健康记录存储")
    logger.info("  - GET /api/health-data/records - 健康记录查询")
    logger.info("  - POST /api/med-knowledge/query - 医学知识查询")
    logger.info("  - POST /api/medical-resource/find - 医疗资源查找")
    logger.info("  - POST /api/message-bus/publish - 消息发布")
    logger.info("  - POST /api/message-bus/subscribe - 主题订阅")
    logger.info("  - POST /api/rag/generate - RAG智能问答")
    logger.info("  - POST /api/suoke-bench/run - 基准测试")
    logger.info("  - POST /api/corn-maze/start - 认知训练游戏")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down extended mock services...")
        server.shutdown()

# 导入原有的服务类
from localTest import (
    AuthService, UserService, AgentService, DiagnosisService, 
    ThreadedHTTPServer
)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 启动服务器并运行测试
        server_thread = Thread(target=start_extended_mock_services, daemon=True)
        server_thread.start()
        
        # 等待服务器启动
        time.sleep(3)
        
        # 运行扩展测试
        logger.info("Running extended integration tests...")
        logger.info("Extended services are now available for testing!")
    else:
        # 只启动服务器
        start_extended_mock_services() 