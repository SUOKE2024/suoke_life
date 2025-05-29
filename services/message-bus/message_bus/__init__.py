"""
索克生活消息总线服务

负责系统间事件传递和通知的分布式消息中间件，支持：
- gRPC 服务间通信
- Kafka 异步消息队列
- Redis 缓存和发布订阅
- 健康检查和监控
- 分布式追踪
"""

__version__ = "0.1.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suokelife.com"

from .main import main

__all__ = ["main"]
