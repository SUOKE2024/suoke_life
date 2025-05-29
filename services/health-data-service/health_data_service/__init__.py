"""
索克生活健康数据服务

基于AI的健康数据管理和分析服务，提供：
- 健康数据收集和存储
- 数据分析和处理
- AI模型推理
- 数据可视化
- API接口服务
"""

__version__ = "0.1.0"
__author__ = "Song Xu"
__email__ = "song.xu@icloud.com"

# 导出主要组件
from health_data_service.core.config import settings

__all__ = [
    "settings",
    "__version__",
    "__author__",
    "__email__",
]
