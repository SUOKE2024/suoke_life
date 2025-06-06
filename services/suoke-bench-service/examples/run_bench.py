"""
run_bench - 索克生活项目模块
"""

from internal.suokebench.runner import SuokeBenchRunner
from pathlib import Path
import logging
import sys

"""
SuokeBench评测示例
"""


# 添加项目根目录到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent))



def main():
    """运行SuokeBench评测"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    # 加载配置
    # 如果config.yaml不存在，将使用默认配置
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"

    # 创建并运行评测
    runner = SuokeBenchRunner(str(config_path) if config_path.exists() else None)
    runner.run()


if __name__ == "__main__":
    main()
