"""
plugin_system - 索克生活项目模块
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Type, Callable
import importlib
import inspect
import json
import logging
import os
import sys

"""插件系统

支持自定义评测模板和扩展功能
"""


logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """插件元数据"""
    name: str
    version: str
    description: str
    author: str
    category: str
    dependencies: List[str] = None
    config_schema: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.config_schema is None:
            self.config_schema = {}


class PluginInterface(ABC):
    """插件接口基类"""
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """插件元数据"""
        pass
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """清理插件资源"""
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        return True


class BenchmarkPlugin(PluginInterface):
    """基准测试插件基类"""
    
    @abstractmethod
    async def run_benchmark(
        self,
        model_id: str,
        test_data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """运行基准测试"""
        pass
    
    @abstractmethod
    def get_metrics_definition(self) -> Dict[str, Any]:
        """获取指标定义"""
        pass


class ModelPlugin(PluginInterface):
    """模型插件基类"""
    
    @abstractmethod
    async def load_model(self, model_config: Dict[str, Any]) -> Any:
        """加载模型"""
        pass
    
    @abstractmethod
    async def predict(self, model: Any, inputs: List[Any]) -> List[Any]:
        """模型预测"""
        pass
    
    @abstractmethod
    async def unload_model(self, model: Any) -> None:
        """卸载模型"""
        pass


class DataProcessorPlugin(PluginInterface):
    """数据处理插件基类"""
    
    @abstractmethod
    async def process_data(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """处理数据"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """获取支持的数据格式"""
        pass


class MetricsPlugin(PluginInterface):
    """指标计算插件基类"""
    
    @abstractmethod
    async def calculate_metrics(
        self,
        predictions: List[Any],
        ground_truth: List[Any],
        config: Dict[str, Any]
    ) -> Dict[str, float]:
        """计算指标"""
        pass
    
    @abstractmethod
    def get_metric_names(self) -> List[str]:
        """获取指标名称"""
        pass


class PluginRegistry:
    """插件注册表"""
    
    def __init__(self):
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_types: Dict[str, List[str]] = {
            "benchmark": [],
            "model": [],
            "data_processor": [],
            "metrics": []
        }
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        self.plugin_states: Dict[str, str] = {}  # loaded, initialized, error
    
    def register_plugin(self, plugin: PluginInterface) -> bool:
        """注册插件"""
        try:
            metadata = plugin.metadata
            plugin_name = metadata.name
            
            if plugin_name in self.plugins:
                logger.warning(f"Plugin {plugin_name} already registered")
                return False
            
            # 确定插件类型
            plugin_type = self._determine_plugin_type(plugin)
            if not plugin_type:
                logger.error(f"Unknown plugin type for {plugin_name}")
                return False
            
            self.plugins[plugin_name] = plugin
            self.plugin_types[plugin_type].append(plugin_name)
            self.plugin_states[plugin_name] = "loaded"
            
            logger.info(f"Plugin {plugin_name} registered as {plugin_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register plugin: {e}")
            return False
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """注销插件"""
        try:
            if plugin_name not in self.plugins:
                return False
            
            plugin = self.plugins[plugin_name]
            
            # 清理插件
            if self.plugin_states.get(plugin_name) == "initialized":
                asyncio.create_task(plugin.cleanup())
            
            # 从注册表中移除
            del self.plugins[plugin_name]
            
            # 从类型列表中移除
            for plugin_type, plugin_list in self.plugin_types.items():
                if plugin_name in plugin_list:
                    plugin_list.remove(plugin_name)
                    break
            
            # 清理状态和配置
            self.plugin_states.pop(plugin_name, None)
            self.plugin_configs.pop(plugin_name, None)
            
            logger.info(f"Plugin {plugin_name} unregistered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister plugin {plugin_name}: {e}")
            return False
    
    async def initialize_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> bool:
        """初始化插件"""
        try:
            if plugin_name not in self.plugins:
                logger.error(f"Plugin {plugin_name} not found")
                return False
            
            plugin = self.plugins[plugin_name]
            config = config or {}
            
            # 验证配置
            if not plugin.validate_config(config):
                logger.error(f"Invalid config for plugin {plugin_name}")
                return False
            
            # 初始化插件
            success = await plugin.initialize(config)
            if success:
                self.plugin_configs[plugin_name] = config
                self.plugin_states[plugin_name] = "initialized"
                logger.info(f"Plugin {plugin_name} initialized")
            else:
                self.plugin_states[plugin_name] = "error"
                logger.error(f"Failed to initialize plugin {plugin_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error initializing plugin {plugin_name}: {e}")
            self.plugin_states[plugin_name] = "error"
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """获取插件实例"""
        return self.plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: str) -> List[PluginInterface]:
        """根据类型获取插件"""
        plugin_names = self.plugin_types.get(plugin_type, [])
        return [self.plugins[name] for name in plugin_names if name in self.plugins]
    
    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """列出所有插件"""
        result = {}
        for name, plugin in self.plugins.items():
            result[name] = {
                "metadata": plugin.metadata.__dict__,
                "state": self.plugin_states.get(name, "unknown"),
                "type": self._determine_plugin_type(plugin)
            }
        return result
    
    def _determine_plugin_type(self, plugin: PluginInterface) -> Optional[str]:
        """确定插件类型"""
        if isinstance(plugin, BenchmarkPlugin):
            return "benchmark"
        elif isinstance(plugin, ModelPlugin):
            return "model"
        elif isinstance(plugin, DataProcessorPlugin):
            return "data_processor"
        elif isinstance(plugin, MetricsPlugin):
            return "metrics"
        return None


class PluginLoader:
    """插件加载器"""
    
    def __init__(self, plugin_dirs: List[str] = None):
        self.plugin_dirs = plugin_dirs or ["plugins"]
        self.registry = PluginRegistry()
    
    def load_plugins_from_directory(self, directory: str) -> int:
        """从目录加载插件"""
        loaded_count = 0
        plugin_path = Path(directory)
        
        if not plugin_path.exists():
            logger.warning(f"Plugin directory {directory} does not exist")
            return 0
        
        # 添加插件目录到Python路径
        if str(plugin_path) not in sys.path:
            sys.path.insert(0, str(plugin_path))
        
        try:
            for plugin_file in plugin_path.glob("*.py"):
                if plugin_file.name.startswith("__"):
                    continue
                
                try:
                    module_name = plugin_file.stem
                    spec = importlib.util.spec_from_file_location(module_name, plugin_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 查找插件类
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, PluginInterface) and 
                            obj != PluginInterface and
                            not inspect.isabstract(obj)):
                            
                            try:
                                plugin_instance = obj()
                                if self.registry.register_plugin(plugin_instance):
                                    loaded_count += 1
                                    logger.info(f"Loaded plugin {name} from {plugin_file}")
                            except Exception as e:
                                logger.error(f"Failed to instantiate plugin {name}: {e}")
                
                except Exception as e:
                    logger.error(f"Failed to load plugin from {plugin_file}: {e}")
        
        finally:
            # 移除插件目录从Python路径
            if str(plugin_path) in sys.path:
                sys.path.remove(str(plugin_path))
        
        return loaded_count
    
    def load_all_plugins(self) -> int:
        """加载所有插件目录中的插件"""
        total_loaded = 0
        for directory in self.plugin_dirs:
            total_loaded += self.load_plugins_from_directory(directory)
        return total_loaded
    
    def get_registry(self) -> PluginRegistry:
        """获取插件注册表"""
        return self.registry


class PluginManager:
    """插件管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.loader = PluginLoader(self.config.get("plugin_dirs", ["plugins"]))
        self.registry = self.loader.get_registry()
        self.auto_load = self.config.get("auto_load", True)
        
    async def initialize(self) -> None:
        """初始化插件管理器"""
        if self.auto_load:
            loaded_count = self.loader.load_all_plugins()
            logger.info(f"Auto-loaded {loaded_count} plugins")
            
            # 自动初始化插件
            plugin_configs = self.config.get("plugin_configs", {})
            for plugin_name, plugin_config in plugin_configs.items():
                await self.registry.initialize_plugin(plugin_name, plugin_config)
    
    async def run_benchmark_with_plugin(
        self,
        plugin_name: str,
        model_id: str,
        test_data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用插件运行基准测试"""
        plugin = self.registry.get_plugin(plugin_name)
        if not plugin or not isinstance(plugin, BenchmarkPlugin):
            raise ValueError(f"Benchmark plugin {plugin_name} not found")
        
        if self.registry.plugin_states.get(plugin_name) != "initialized":
            raise ValueError(f"Plugin {plugin_name} not initialized")
        
        return await plugin.run_benchmark(model_id, test_data, config)
    
    def get_available_benchmarks(self) -> List[Dict[str, Any]]:
        """获取可用的基准测试插件"""
        benchmarks = []
        for plugin in self.registry.get_plugins_by_type("benchmark"):
            if self.registry.plugin_states.get(plugin.metadata.name) == "initialized":
                benchmarks.append({
                    "name": plugin.metadata.name,
                    "description": plugin.metadata.description,
                    "version": plugin.metadata.version,
                    "metrics": plugin.get_metrics_definition()
                })
        return benchmarks
    
    def create_custom_benchmark_template(
        self,
        name: str,
        description: str,
        metrics_config: Dict[str, Any],
        data_processing_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """创建自定义基准测试模板"""
        template = {
            "name": name,
            "description": description,
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "metrics_config": metrics_config,
            "data_processing_steps": data_processing_steps,
            "plugin_dependencies": []
        }
        
        # 保存模板
        template_dir = Path("templates")
        template_dir.mkdir(exist_ok=True)
        
        template_file = template_dir / f"{name}.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Created benchmark template: {name}")
        return template
    
    def list_benchmark_templates(self) -> List[Dict[str, Any]]:
        """列出基准测试模板"""
        templates = []
        template_dir = Path("templates")
        
        if template_dir.exists():
            for template_file in template_dir.glob("*.json"):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template = json.load(f)
                        templates.append(template)
                except Exception as e:
                    logger.error(f"Failed to load template {template_file}: {e}")
        
        return templates


# 全局插件管理器
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """获取插件管理器"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


async def init_plugin_manager(config: Dict[str, Any] = None) -> PluginManager:
    """初始化插件管理器"""
    global _plugin_manager
    _plugin_manager = PluginManager(config)
    await _plugin_manager.initialize()
    return _plugin_manager


# 示例插件实现
class TCMDiagnosisPlugin(BenchmarkPlugin):
    """中医诊断基准测试插件示例"""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="tcm_diagnosis",
            version="1.0.0",
            description="中医诊断基准测试",
            author="Suoke Life Team",
            category="medical",
            dependencies=["numpy", "pandas"],
            config_schema={
                "diagnosis_types": {"type": "array", "items": {"type": "string"}},
                "evaluation_metrics": {"type": "array", "items": {"type": "string"}}
            }
        )
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        self.config = config
        self.diagnosis_types = config.get("diagnosis_types", ["望", "闻", "问", "切"])
        return True
    
    async def cleanup(self) -> None:
        """清理插件资源"""
        pass
    
    async def run_benchmark(
        self,
        model_id: str,
        test_data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """运行中医诊断基准测试"""
        # 模拟中医诊断评测
        results = {
            "model_id": model_id,
            "total_samples": len(test_data),
            "metrics": {
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.88,
                "f1_score": 0.85,
                "diagnosis_accuracy": {
                    "望诊": 0.87,
                    "闻诊": 0.83,
                    "问诊": 0.89,
                    "切诊": 0.81
                }
            },
            "execution_time": 120.5
        }
        return results
    
    def get_metrics_definition(self) -> Dict[str, Any]:
        """获取指标定义"""
        return {
            "accuracy": {"description": "整体准确率", "unit": "%", "range": [0, 1]},
            "precision": {"description": "精确率", "unit": "%", "range": [0, 1]},
            "recall": {"description": "召回率", "unit": "%", "range": [0, 1]},
            "f1_score": {"description": "F1分数", "unit": "%", "range": [0, 1]},
            "diagnosis_accuracy": {"description": "各诊断方法准确率", "unit": "%", "type": "dict"}
        } 