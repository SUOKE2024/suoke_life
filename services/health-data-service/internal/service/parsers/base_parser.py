#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设备数据解析器基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Union


class BaseParser(ABC):
    """设备数据解析器基类"""
    
    @abstractmethod
    async def parse(self, data: Union[str, Dict, bytes], config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        解析设备数据
        
        Args:
            data: 设备数据
            config: 解析配置
            
        Returns:
            解析后的健康数据列表
        """
        pass 