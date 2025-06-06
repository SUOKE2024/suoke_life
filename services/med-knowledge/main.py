"""
main - 索克生活项目模块
"""

from app.core.config import get_settings
from app.core.logger import setup_logging
from loguru import logger
from pathlib import Path
from typing import Optional
import argparse
import asyncio
import os
import signal
import sys
import uvicorn

#!/usr/bin/env python3
"""
索克生活-医学知识服务启动脚本
支持开发、生产、测试等多种运行模式
"""



# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))



class MedKnowledgeServer:
    """医学知识服务器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.settings = None
        self.server = None
        self.shutdown_event = asyncio.Event()
    
    def setup_environment(self, env: str = "development"):
        """设置环境变量"""
        os.environ.setdefault("ENVIRONMENT", env)
        if self.config_file:
            os.environ.setdefault("CONFIG_FILE", self.config_file)
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"收到信号 {signum}，准备关闭服务...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8000, 
                          workers: int = 1, reload: bool = False):
        """启动服务器"""
        try:
            # 设置日志
            setup_logging()
            
            # 获取配置
            self.settings = get_settings()
            
            logger.info("=" * 60)
            logger.info("🏥 索克生活-医学知识服务启动中...")
            logger.info(f"📍 环境: {self.settings.environment}")
            logger.info(f"🌐 地址: http://{host}:{port}")
            logger.info(f"📚 API文档: http://{host}:{port}/api/docs")
            logger.info(f"⚡ 工作进程: {workers}")
            logger.info("=" * 60)
            
            # 配置服务器
            config = uvicorn.Config(
                "app.main:app",
                host=host,
                port=port,
                workers=workers if not reload else 1,
                reload=reload,
                reload_dirs=[str(project_root / "app")] if reload else None,
                log_config=None,  # 使用自定义日志配置
                access_log=False,  # 通过中间件处理访问日志
            )
            
            self.server = uvicorn.Server(config)
            
            # 启动服务器
            await self.server.serve()
            
        except Exception as e:
            logger.error(f"服务启动失败: {e}")
            sys.exit(1)
    
    def run_development(self, host: str = "127.0.0.1", port: int = 8000):
        """开发模式运行"""
        self.setup_environment("development")
        self.setup_signal_handlers()
        
        logger.info("🚀 开发模式启动...")
        asyncio.run(self.start_server(
            host=host, 
            port=port, 
            workers=1, 
            reload=True
        ))
    
    def run_production(self, host: str = "0.0.0.0", port: int = 8000, workers: int = 4):
        """生产模式运行"""
        self.setup_environment("production")
        self.setup_signal_handlers()
        
        logger.info("🏭 生产模式启动...")
        asyncio.run(self.start_server(
            host=host, 
            port=port, 
            workers=workers, 
            reload=False
        ))
    
    def run_testing(self, host: str = "127.0.0.1", port: int = 8001):
        """测试模式运行"""
        self.setup_environment("testing")
        
        logger.info("🧪 测试模式启动...")
        asyncio.run(self.start_server(
            host=host, 
            port=port, 
            workers=1, 
            reload=False
        ))


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="索克生活-医学知识服务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py dev                    # 开发模式
  python main.py prod --workers 4      # 生产模式，4个工作进程
  python main.py test                   # 测试模式
  python main.py --host 0.0.0.0 --port 8080  # 自定义地址和端口
        """
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest="mode", help="运行模式")
    
    # 开发模式
    dev_parser = subparsers.add_parser("dev", help="开发模式")
    dev_parser.add_argument("--host", default="127.0.0.1", help="绑定地址")
    dev_parser.add_argument("--port", type=int, default=8000, help="端口号")
    
    # 生产模式
    prod_parser = subparsers.add_parser("prod", help="生产模式")
    prod_parser.add_argument("--host", default="0.0.0.0", help="绑定地址")
    prod_parser.add_argument("--port", type=int, default=8000, help="端口号")
    prod_parser.add_argument("--workers", type=int, default=4, help="工作进程数")
    
    # 测试模式
    test_parser = subparsers.add_parser("test", help="测试模式")
    test_parser.add_argument("--host", default="127.0.0.1", help="绑定地址")
    test_parser.add_argument("--port", type=int, default=8001, help="端口号")
    
    # 通用参数
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--host", default="127.0.0.1", help="绑定地址")
    parser.add_argument("--port", type=int, default=8000, help="端口号")
    parser.add_argument("--workers", type=int, default=1, help="工作进程数")
    parser.add_argument("--reload", action="store_true", help="启用热重载")
    
    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 创建服务器实例
    server = MedKnowledgeServer(config_file=args.config)
    
    try:
        if args.mode == "dev":
            server.run_development(host=args.host, port=args.port)
        elif args.mode == "prod":
            server.run_production(
                host=args.host, 
                port=args.port, 
                workers=args.workers
            )
        elif args.mode == "test":
            server.run_testing(host=args.host, port=args.port)
        else:
            # 默认模式
            server.setup_environment("development" if args.reload else "production")
            server.setup_signal_handlers()
            
            asyncio.run(server.start_server(
                host=args.host,
                port=args.port,
                workers=args.workers,
                reload=args.reload
            ))
    
    except KeyboardInterrupt:
        logger.info("👋 服务已停止")
    except Exception as e:
        logger.error(f"服务运行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
