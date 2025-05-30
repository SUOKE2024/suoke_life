"""
单例模式实用工具，提供Singleton元类
"""
from typing import Dict, Any, Type


class Singleton(type):
    """
    单例模式元类，确保类只有一个实例。
    
    使用方法:
    ```python
    class MyClass(metaclass=Singleton):
        pass
    ```
    
    这样MyClass的所有实例化都将返回同一个对象。
    """
    
    _instances: Dict[Type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
    @classmethod
    def clear_instance(mcs, cls):
        """
        清除指定类的单例实例
        
        Args:
            cls: 要清除实例的类
        """
        if cls in mcs._instances:
            del mcs._instances[cls]
    
    @classmethod
    def clear_all(mcs):
        """清除所有单例实例"""
        mcs._instances.clear() 