from typing import Dict, List, Any, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .main import create_app

"""
索克生活第三方健康平台集成服务

提供与各种健康平台的数据集成功能，包括：
- Apple Health
- Google Fit
- Fitbit
- 小米健康
- 华为健康
- 微信运动
- 支付宝健康等
"""

__version__ = "0.1.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suokelife.com"


__all__ = ["create_app"]
