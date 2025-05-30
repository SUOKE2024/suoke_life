import argparse
import asyncio
import logging
import os
import signal
import sys
from concurrent import futures

import grpc
import uvicorn
from dotenv import load_dotenv

# 确保Python能够找到模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入gRPC服务定义
from api.grpc import soer_service_pb2_grpc
from internal.delivery.grpc.soer_service_impl import SoerServiceImpl
from internal.delivery.rest import init_rest_app
from pkg.utils.config_loader import load_config
from pkg.utils.metrics import initialize_metrics

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'soer-service.log'))
    ]
)
logger = logging.getLogger(__name__)

# 全局服务器实例，便于优雅关闭
grpc_server = None
rest_server = None

def handle_exit_signal():
    """处理退出信号"""
    def _handle_signal(sig, frame):
        logger.info(f"收到退出信号: {sig}")
        asyncio.create_task(shutdown())

    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, _handle_signal)

async def shutdown():
    """优雅关闭服务"""
    logger.info("开始优雅关闭服务...")

    if grpc_server:
        logger.info("关闭gRPC服务器...")
        await grpc_server.stop(grace=5.0)

    if rest_server:
        logger.info("关闭REST API服务器...")
        # 通常REST服务器会在主循环结束时自动关闭

    logger.info("服务已关闭")

async def serve(config):
    """启动服务"""
    global grpc_server, rest_server

    # 初始化指标收集器
    initialize_metrics(config.get('metrics', {}))

    # 创建gRPC服务器
    grpc_server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=config.get('grpc', {}).get('max_workers', 10))
    )

    # 注册服务实现
    service_impl = SoerServiceImpl()
    soer_service_pb2_grpc.add_SoerServiceServicer_to_server(service_impl, grpc_server)

    # 启动gRPC服务器
    grpc_port = config.get('grpc', {}).get('port', 50054)
    grpc_server.add_insecure_port(f'[::]:{grpc_port}')
    await grpc_server.start()
    logger.info(f"gRPC服务器启动于端口 {grpc_port}")

    # 启动REST API
    rest_app = init_rest_app()
    rest_port = config.get('rest', {}).get('port', 8054)

    # 配置uvicorn
    config = uvicorn.Config(
        rest_app,
        host="0.0.0.0",
        port=rest_port,
        log_level="info"
    )
    rest_server = uvicorn.Server(config)

    # 注册信号处理
    handle_exit_signal()

    # 启动REST服务器
    logger.info(f"REST API服务器启动于端口 {rest_port}")
    await rest_server.serve()

    # 等待gRPC服务器被终止
    await grpc_server.wait_for_termination()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="索儿智能体服务")
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    parser.add_argument('--dev', action='store_true', help='启用开发模式')
    parser.add_argument('--mock', action='store_true', help='启用模拟模式，不会实际调用LLM API')
    args = parser.parse_args()

    # 设置环境变量
    if args.dev:
        os.environ['SOER_ENV'] = 'development'

    if args.mock:
        os.environ['MOCK_LLM'] = 'true'

    # 加载配置
    config = load_config(args.config)

    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)

    # 启动服务
    asyncio.run(serve(config))
