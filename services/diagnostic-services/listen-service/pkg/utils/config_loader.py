"""
配置加载器 - 负责加载和处理配置文件
"""
import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigLoader:
    """配置加载器类，用于加载和访问配置信息"""
    
    def __init__(self, config_path: str = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.config: Dict[str, Any] = {}
        
        # 默认配置路径
        if config_path is None:
            config_path = os.environ.get(
                "CONFIG_PATH", 
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "config.yaml")
            )
        
        self.config_path = config_path
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        try:
            logger.info(f"加载配置文件: {self.config_path}")
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
            
            # 处理环境变量
            self._process_env_vars(self.config)
            
            logger.info(f"配置文件加载成功")
            return self.config
        
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            # 返回空配置
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键，支持点分隔的嵌套访问
            default: 默认值，如果键不存在则返回此值
            
        Returns:
            Any: 配置值或默认值
        """
        # 处理嵌套键
        if '.' in key:
            parts = key.split('.')
            temp_config = self.config
            
            for part in parts[:-1]:
                temp_config = temp_config.get(part, {})
                if not isinstance(temp_config, dict):
                    return default
            
            return temp_config.get(parts[-1], default)
        
        return self.config.get(key, default)
    
    def _process_env_vars(self, config_dict: Dict[str, Any]) -> None:
        """
        递归处理配置字典中的环境变量引用
        
        Args:
            config_dict: 配置字典
        """
        for key, value in config_dict.items():
            if isinstance(value, dict):
                self._process_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # 提取环境变量名
                env_var = value[2:-1]
                # 获取环境变量值，如果不存在则保留原值
                config_dict[key] = os.environ.get(env_var, value)
                
                # 记录替换情况
                if env_var in os.environ:
                    logger.debug(f"环境变量替换: {key}=${{{env_var}}}")
                else:
                    logger.warning(f"环境变量不存在: {env_var}，保留原值")


# 全局配置实例
global_config = None

def get_config(config_path: str = None) -> ConfigLoader:
    """
    获取全局配置实例
    
    Args:
        config_path: 配置文件路径，仅在首次调用时有效
        
    Returns:
        ConfigLoader: 配置加载器实例
    """
    global global_config
    
    if global_config is None:
        global_config = ConfigLoader(config_path)
    
    return global_config 