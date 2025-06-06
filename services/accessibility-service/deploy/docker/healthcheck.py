"""
healthcheck - 索克生活项目模块
"""

            import psutil
import asyncio
import logging
import socket
import sys

#!/usr/bin/env python

"""
Docker健康检查脚本
检查服务的健康状态，包括gRPC服务、数据库连接等
"""


# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self.checks = [
            self.check_grpc_service,
            self.check_memory_usage,
            self.check_disk_space,
        ]

    async def run_all_checks(self) -> bool:
        """运行所有健康检查"""
        try:
            results = []
            for check in self.checks:
                try:
                    result = await check()
                    results.append(result)
                    if not result:
                        logger.warning(f"健康检查失败: {check.__name__}")
                except Exception as e:
                    logger.error(f"健康检查异常: {check.__name__}, 错误: {str(e)}")
                    results.append(False)

            # 所有检查都必须通过
            return all(results)

        except Exception as e:
            logger.error(f"健康检查运行异常: {str(e)}")
            return False

    async def check_grpc_service(self) -> bool:
        """检查gRPC服务是否可用"""
        try:
            # 检查端口是否开放
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 50051))
            sock.close()

            if result == 0:
                logger.debug("gRPC服务端口检查通过")
                return True
            else:
                logger.warning("gRPC服务端口不可用")
                return False

        except Exception as e:
            logger.error(f"gRPC服务检查失败: {str(e)}")
            return False

    async def check_memory_usage(self) -> bool:
        """检查内存使用情况"""
        try:

            memory = psutil.virtual_memory()
            usage_percent = memory.percent

            # 内存使用超过95%认为不健康
            if usage_percent > 95:
                logger.warning(f"内存使用过高: {usage_percent:.1f}%")
                return False

            logger.debug(f"内存使用正常: {usage_percent:.1f}%")
            return True

        except ImportError:
            # 如果psutil不可用，跳过此检查
            logger.debug("psutil不可用，跳过内存检查")
            return True
        except Exception as e:
            logger.error(f"内存检查失败: {str(e)}")
            return False

    async def check_disk_space(self) -> bool:
        """检查磁盘空间"""
        try:

            disk = psutil.disk_usage('/')
            usage_percent = disk.percent

            # 磁盘使用超过98%认为不健康
            if usage_percent > 98:
                logger.warning(f"磁盘空间不足: {usage_percent:.1f}%")
                return False

            logger.debug(f"磁盘空间正常: {usage_percent:.1f}%")
            return True

        except ImportError:
            # 如果psutil不可用，跳过此检查
            logger.debug("psutil不可用，跳过磁盘检查")
            return True
        except Exception as e:
            logger.error(f"磁盘检查失败: {str(e)}")
            return False


async def main():
    """主函数"""
    checker = HealthChecker()

    try:
        # 运行健康检查
        is_healthy = await checker.run_all_checks()

        if is_healthy:
            print("健康检查通过")
            sys.exit(0)
        else:
            print("健康检查失败")
            sys.exit(1)

    except Exception as e:
        print(f"健康检查异常: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
