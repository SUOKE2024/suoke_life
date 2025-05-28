#!/usr/bin/env python3
"""
A2A 智能体网络微服务主入口
A2A Agent Network Microservice Main Entry
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

import yaml
from flask import Flask
from flask_cors import CORS

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from internal.delivery.rest_api import create_rest_api
from internal.service.agent_manager import AgentManager
from pkg.logging.logger import setup_logging

logger = logging.getLogger(__name__)


class A2ANetworkService:
    """A2A 智能体网络服务"""

    def __init__(self, config_path: str = None):
        """
        初始化服务

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or "config/config.yaml"
        self.config = self._load_config()
        self.agent_manager: AgentManager | None = None
        self.app: Flask | None = None
        self._shutdown_event = asyncio.Event()

        # 设置日志
        setup_logging(self.config.get("logging", {}))

        logger.info("A2A 智能体网络服务初始化完成")

    def _load_config(self) -> dict:
        """加载配置文件"""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                # 尝试相对于项目根目录的路径
                config_file = project_root / self.config_path

            if not config_file.exists():
                logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
                return self._get_default_config()

            with open(config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                logger.info(f"已加载配置文件: {config_file}")
                return config

        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            "server": {"host": "0.0.0.0", "port": 5000, "debug": False},
            "agents": {
                "xiaoai": {
                    "name": "小艾智能体",
                    "url": "http://localhost:5001",
                    "timeout": 30,
                },
                "xiaoke": {
                    "name": "小克智能体",
                    "url": "http://localhost:5002",
                    "timeout": 30,
                },
                "laoke": {
                    "name": "老克智能体",
                    "url": "http://localhost:5003",
                    "timeout": 30,
                },
                "soer": {
                    "name": "索儿智能体",
                    "url": "http://localhost:5004",
                    "timeout": 30,
                },
            },
            "logging": {"level": "INFO"},
        }

    async def start(self):
        """启动服务"""
        try:
            # 初始化智能体管理器
            self.agent_manager = AgentManager(self.config)
            await self.agent_manager.start()

            # 创建 Flask 应用
            self.app = Flask(__name__)
            CORS(self.app)

            # 注册 REST API
            create_rest_api(self.app, self.agent_manager)

            # 设置信号处理
            self._setup_signal_handlers()

            # 启动 Flask 服务器
            server_config = self.config.get("server", {})
            host = server_config.get("host", "0.0.0.0")
            port = server_config.get("port", 5000)
            debug = server_config.get("debug", False)

            logger.info(f"A2A 智能体网络服务启动在 {host}:{port}")

            # 在单独的线程中运行 Flask
            import threading

            flask_thread = threading.Thread(
                target=lambda: self.app.run(
                    host=host, port=port, debug=debug, use_reloader=False
                ),
                daemon=True,
            )
            flask_thread.start()

            # 等待关闭信号
            await self._shutdown_event.wait()

        except Exception as e:
            logger.error(f"服务启动失败: {e}")
            raise

    async def stop(self):
        """停止服务"""
        logger.info("正在停止 A2A 智能体网络服务...")

        if self.agent_manager:
            await self.agent_manager.stop()

        self._shutdown_event.set()
        logger.info("A2A 智能体网络服务已停止")

    def _setup_signal_handlers(self):
        """设置信号处理器"""

        def signal_handler(signum, frame):
            logger.info(f"收到信号 {signum}，准备关闭服务...")
            asyncio.create_task(self.stop())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="A2A 智能体网络微服务")
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--host", default=None, help="服务器主机地址")
    parser.add_argument("--port", type=int, default=None, help="服务器端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")

    args = parser.parse_args()

    # 创建服务实例
    service = A2ANetworkService(args.config)

    # 覆盖命令行参数
    if args.host:
        service.config.setdefault("server", {})["host"] = args.host
    if args.port:
        service.config.setdefault("server", {})["port"] = args.port
    if args.debug:
        service.config.setdefault("server", {})["debug"] = True

    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    except Exception as e:
        logger.error(f"服务运行异常: {e}")
        sys.exit(1)
    finally:
        await service.stop()


if __name__ == "__main__":
    # 设置事件循环策略（Windows 兼容性）
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())
