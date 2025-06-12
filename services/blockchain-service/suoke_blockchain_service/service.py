"""
service模块
"""

import logging

logger = logging.getLogger(__name__)


def main() -> None:
    """主函数"""
    logger.info(f"service模块已加载")


if __name__ == "__main__":
    main()
