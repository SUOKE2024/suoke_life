"""
main - 索克生活项目模块
"""

            from http.server import HTTPServer, BaseHTTPRequestHandler
            from prometheus_client import start_http_server
            import json
            import threading
from api.grpc import palpation_service_pb2_grpc
from concurrent import futures
from internal.delivery.batch_analyzer import BatchAnalysisHandler
from internal.delivery.comprehensive_analysis import ComprehensiveAnalysisHandler
from internal.delivery.palpation_service_impl import PalpationServiceImpl
from internal.repository.session_repository import SessionRepository
from internal.repository.user_repository import UserRepository
from pathlib import Path
import grpc
import logging
import os
import signal
import sys
import time
import yaml

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
切诊服务主程序
启动gRPC服务器
"""



# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# 导入服务实现

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PalpationServer:
    """切诊服务器"""
    
    def __init__(self, config_path: str):
        """
        初始化服务器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.server = None
        self.is_running = False
        
        # 初始化存储库
        db_config = self.config.get('database', {})
        self.session_repository = SessionRepository(db_config)
        self.user_repository = UserRepository(db_config)
        
        # 初始化服务实现
        self.service_impl = PalpationServiceImpl(
            self.config,
            self.session_repository,
            self.user_repository
        )
        
        # 初始化综合分析处理器
        self.comprehensive_handler = ComprehensiveAnalysisHandler(
            self.session_repository,
            self.user_repository,
            self.service_impl.pulse_processor,
            self.service_impl.abdominal_analyzer,
            self.service_impl.skin_analyzer,
            self.service_impl.metrics
        )
        
        # 初始化批量分析处理器
        self.batch_handler = BatchAnalysisHandler(
            self.session_repository,
            self.user_repository,
            self.service_impl.pulse_processor,
            self.service_impl.metrics
        )
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("切诊服务器初始化完成")
    
    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 处理环境变量覆盖
            self._process_env_overrides(config)
            
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def _process_env_overrides(self, config: dict):
        """处理环境变量覆盖"""
        # 数据库配置
        if 'MONGO_HOST' in os.environ:
            config.setdefault('database', {})['host'] = os.environ['MONGO_HOST']
        if 'MONGO_PORT' in os.environ:
            config.setdefault('database', {})['port'] = int(os.environ['MONGO_PORT'])
        if 'MONGO_USERNAME' in os.environ:
            config.setdefault('database', {})['username'] = os.environ['MONGO_USERNAME']
        if 'MONGO_PASSWORD' in os.environ:
            config.setdefault('database', {})['password'] = os.environ['MONGO_PASSWORD']
        if 'MONGO_DATABASE' in os.environ:
            config.setdefault('database', {})['name'] = os.environ['MONGO_DATABASE']
        
        # Redis配置
        if 'REDIS_HOST' in os.environ:
            config.setdefault('redis', {})['host'] = os.environ['REDIS_HOST']
        if 'REDIS_PORT' in os.environ:
            config.setdefault('redis', {})['port'] = int(os.environ['REDIS_PORT'])
        if 'REDIS_PASSWORD' in os.environ:
            config.setdefault('redis', {})['password'] = os.environ['REDIS_PASSWORD']
        
        # 服务器配置
        if 'GRPC_PORT' in os.environ:
            config.setdefault('server', {})['port'] = int(os.environ['GRPC_PORT'])
        if 'MAX_WORKERS' in os.environ:
            config.setdefault('server', {})['max_workers'] = int(os.environ['MAX_WORKERS'])
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"收到信号 {signum}，准备关闭服务器...")
        self.stop()
    
    def start(self):
        """启动服务器"""
        try:
            # 创建gRPC服务器
            server_config = self.config.get('server', {})
            max_workers = server_config.get('max_workers', 10)
            
            self.server = grpc.server(
                futures.ThreadPoolExecutor(max_workers=max_workers),
                options=[
                    ('grpc.max_send_message_length', server_config.get('max_send_message_length', 50 * 1024 * 1024)),
                    ('grpc.max_receive_message_length', server_config.get('max_receive_message_length', 50 * 1024 * 1024)),
                    ('grpc.keepalive_time_ms', server_config.get('keepalive_time_ms', 10000)),
                    ('grpc.keepalive_timeout_ms', server_config.get('keepalive_timeout_ms', 5000)),
                    ('grpc.keepalive_permit_without_calls', 1),
                    ('grpc.http2.max_pings_without_data', 0),
                ]
            )
            
            # 创建包装服务实现
            wrapped_service = WrappedPalpationService(
                self.service_impl,
                self.comprehensive_handler,
                self.batch_handler
            )
            
            # 注册服务
            palpation_service_pb2_grpc.add_PalpationServiceServicer_to_server(
                wrapped_service, self.server
            )
            
            # 绑定端口
            port = server_config.get('port', 50051)
            bind_address = server_config.get('bind_address', '[::]')
            self.server.add_insecure_port(f'{bind_address}:{port}')
            
            # 启动服务器
            self.server.start()
            self.is_running = True
            
            logger.info(f"切诊服务器已启动，监听端口 {port}")
            
            # 启动健康检查端点（如果配置）
            if server_config.get('health_check_enabled', True):
                self._start_health_check_server()
            
            # 启动指标导出端点（如果配置）
            if self.config.get('monitoring', {}).get('prometheus', {}).get('enabled', False):
                self._start_metrics_server()
            
            # 等待服务器终止
            while self.is_running:
                time.sleep(1)
            
        except Exception as e:
            logger.error(f"启动服务器失败: {e}")
            raise
    
    def stop(self):
        """停止服务器"""
        if self.server and self.is_running:
            logger.info("正在停止服务器...")
            
            # 设置停止标志
            self.is_running = False
            
            # 优雅关闭，等待最多30秒
            self.server.stop(grace=30)
            
            logger.info("服务器已停止")
    
    def _start_health_check_server(self):
        """启动健康检查HTTP服务器"""
        try:
            
            class HealthCheckHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/health':
                        # 执行健康检查
                        try:
                            # 检查数据库连接
                            self.server.session_repository.ping()
                            self.server.user_repository.ping()
                            
                            health_status = {
                                'status': 'healthy',
                                'timestamp': int(time.time()),
                                'service': 'palpation-service',
                                'version': self.server.service_impl.version
                            }
                            
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps(health_status).encode())
                        except Exception as e:
                            health_status = {
                                'status': 'unhealthy',
                                'timestamp': int(time.time()),
                                'service': 'palpation-service',
                                'error': str(e)
                            }
                            
                            self.send_response(503)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps(health_status).encode())
                    else:
                        self.send_response(404)
                        self.end_headers()
                
                def log_message(self, format, *args):
                    # 禁用默认日志
                    pass
            
            # 创建HTTP服务器
            health_port = self.config.get('server', {}).get('health_check_port', 8080)
            httpd = HTTPServer(('', health_port), HealthCheckHandler)
            httpd.session_repository = self.session_repository
            httpd.user_repository = self.user_repository
            httpd.service_impl = self.service_impl
            
            # 在后台线程中运行
            health_thread = threading.Thread(target=httpd.serve_forever)
            health_thread.daemon = True
            health_thread.start()
            
            logger.info(f"健康检查服务器已启动，端口 {health_port}")
            
        except Exception as e:
            logger.warning(f"启动健康检查服务器失败: {e}")
    
    def _start_metrics_server(self):
        """启动Prometheus指标导出服务器"""
        try:
            
            metrics_port = self.config.get('monitoring', {}).get('prometheus', {}).get('port', 9090)
            start_http_server(metrics_port)
            
            logger.info(f"Prometheus指标服务器已启动，端口 {metrics_port}")
            
        except Exception as e:
            logger.warning(f"启动指标服务器失败: {e}")

class WrappedPalpationService(palpation_service_pb2_grpc.PalpationServiceServicer):
    """包装的切诊服务实现，整合多个处理器"""
    
    def __init__(self, service_impl, comprehensive_handler, batch_handler):
        self.service_impl = service_impl
        self.comprehensive_handler = comprehensive_handler
        self.batch_handler = batch_handler
    
    # 委托给主服务实现
    def StartPulseSession(self, request, context):
        return self.service_impl.StartPulseSession(request, context)
    
    def RecordPulseData(self, request_iterator, context):
        return self.service_impl.RecordPulseData(request_iterator, context)
    
    def ExtractPulseFeatures(self, request, context):
        return self.service_impl.ExtractPulseFeatures(request, context)
    
    def AnalyzePulse(self, request, context):
        return self.service_impl.AnalyzePulse(request, context)
    
    def AnalyzeAbdominalPalpation(self, request, context):
        return self.service_impl.AnalyzeAbdominalPalpation(request, context)
    
    def AnalyzeSkinPalpation(self, request, context):
        return self.service_impl.AnalyzeSkinPalpation(request, context)
    
    def HealthCheck(self, request, context):
        return self.service_impl.HealthCheck(request, context)
    
    # 委托给综合分析处理器
    def GetComprehensivePalpationAnalysis(self, request, context):
        return self.comprehensive_handler.handle_comprehensive_analysis(request, context)
    
    # 委托给批量分析处理器
    def BatchAnalyzePulseData(self, request, context):
        return self.batch_handler.handle_batch_analysis(request, context)
    
    def ComparePulseSessions(self, request, context):
        return self.batch_handler.handle_compare_pulse_sessions(request, context)
    
    def GeneratePalpationReport(self, request, context):
        return self.batch_handler.handle_generate_report(request, context)

def main():
    """主函数"""
    # 获取配置文件路径
    config_path = os.environ.get('CONFIG_PATH', 'config/config.yaml')
    if not os.path.exists(config_path):
        # 尝试使用相对于脚本的路径
        config_path = os.path.join(project_root, 'config', 'config.yaml')
    
    if not os.path.exists(config_path):
        logger.error(f"配置文件不存在: {config_path}")
        sys.exit(1)
    
    # 创建并启动服务器
    server = PalpationServer(config_path)
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("收到键盘中断，正在关闭...")
    except Exception as e:
        logger.error(f"服务器运行错误: {e}")
        sys.exit(1)
    finally:
        server.stop()

if __name__ == '__main__':
    main()