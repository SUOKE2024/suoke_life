"""
AI模型管理器

负责管理和优化AI模型的调用、缓存和性能监控
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor

# AI依赖的可选导入
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

try:
    from transformers import (
        AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
        pipeline
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    AutoTokenizer = AutoModel = AutoModelForSequenceClassification = pipeline = None
    TRANSFORMERS_AVAILABLE = False

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ort = None
    ONNX_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from ..config.settings import get_settings
from ..utils.exceptions import ModelError, ModelNotFoundError
from ..utils.cache import CacheManager


logger = logging.getLogger(__name__)


class ModelType(Enum):
    """模型类型枚举"""
    TRANSFORMER = "transformer"
    ONNX = "onnx"
    SENTENCE_TRANSFORMER = "sentence_transformer"
    PIPELINE = "pipeline"
    CUSTOM = "custom"


class ModelStatus(Enum):
    """模型状态枚举"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    WARMING_UP = "warming_up"


@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    model_type: ModelType
    model_path: str
    task: str
    device: str = "cpu"
    max_length: int = 512
    batch_size: int = 1
    cache_size: int = 1000
    warmup_samples: int = 5
    timeout_seconds: int = 30
    memory_limit_mb: int = 1024
    auto_unload_minutes: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelMetrics:
    """模型性能指标"""
    model_name: str
    total_calls: int = 0
    total_time_ms: int = 0
    avg_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    memory_usage_mb: float = 0.0
    last_used: Optional[datetime] = None
    error_count: int = 0


class ModelInstance:
    """模型实例"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        self.status = ModelStatus.UNLOADED
        self.metrics = ModelMetrics(model_name=config.name)
        self.last_used: Optional[datetime] = None
        self.load_time: Optional[float] = None
        self.lock = threading.RLock()
        
    async def load(self) -> None:
        """加载模型"""
        with self.lock:
            if self.status==ModelStatus.LOADED:
                return
                
            if self.status==ModelStatus.LOADING:
                # 等待加载完成
                while self.status==ModelStatus.LOADING:
                    await asyncio.sleep(0.1)
                return
                
            self.status = ModelStatus.LOADING
            
        try:
            start_time = time.time()
            
            if self.config.model_type==ModelType.TRANSFORMER:
                await self._load_transformer()
            elif self.config.model_type==ModelType.ONNX:
                await self._load_onnx()
            elif self.config.model_type==ModelType.SENTENCE_TRANSFORMER:
                await self._load_sentence_transformer()
            elif self.config.model_type==ModelType.PIPELINE:
                await self._load_pipeline()
            else:
                raise ModelError(f"不支持的模型类型: {self.config.model_type}")
                
            self.load_time = time.time() - start_time
            self.status = ModelStatus.LOADED
            self.last_used = datetime.now(timezone.utc)
            
            # 预热模型
            await self._warmup()
            
            logger.info(f"模型加载成功: {self.config.name}, 耗时: {self.load_time:.2f}s")
            
        except Exception as e:
            self.status = ModelStatus.ERROR
            logger.error(f"模型加载失败: {self.config.name}, 错误: {e}")
            raise ModelError(f"无法加载模型 {self.config.name}: {e}")
            
    async def _load_transformer(self) -> None:
        """加载Transformer模型"""
        if not TRANSFORMERS_AVAILABLE:
            raise ModelError("transformers库未安装，无法加载Transformer模型")
        if not TORCH_AVAILABLE:
            raise ModelError("torch库未安装，无法加载Transformer模型")
            
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_path)
        
        if self.config.task=="classification":
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.config.model_path
            )
        else:
            self.model = AutoModel.from_pretrained(self.config.model_path)
            
        # 移动到指定设备
        if self.config.device!="cpu" and TORCH_AVAILABLE and torch.cuda.is_available():
            self.model = self.model.to(self.config.device)
            
    async def _load_onnx(self) -> None:
        """加载ONNX模型"""
        if not ONNX_AVAILABLE:
            raise ModelError("onnxruntime库未安装，无法加载ONNX模型")
            
        providers = ['CPUExecutionProvider']
        if self.config.device!="cpu" and ort.get_device()=='GPU':
            providers.insert(0, 'CUDAExecutionProvider')
            
        self.model = ort.InferenceSession(
            self.config.model_path,
            providers=providers
        )
        
    async def _load_sentence_transformer(self) -> None:
        """加载SentenceTransformer模型"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ModelError("sentence-transformers库未安装，无法加载SentenceTransformer模型")
            
        self.model = SentenceTransformer(
            self.config.model_path,
            device=self.config.device
        )
        
    async def _load_pipeline(self) -> None:
        """加载Pipeline模型"""
        if not TRANSFORMERS_AVAILABLE:
            raise ModelError("transformers库未安装，无法加载Pipeline模型")
        if not TORCH_AVAILABLE:
            raise ModelError("torch库未安装，无法加载Pipeline模型")
            
        device = -1  # 默认CPU
        if self.config.device!="cpu" and TORCH_AVAILABLE and torch.cuda.is_available():
            device = 0
            
        self.model = pipeline(
            self.config.task,
            model=self.config.model_path,
            device=device
        )
        
    async def _warmup(self) -> None:
        """预热模型"""
        if self.status!=ModelStatus.LOADED:
            return
            
        self.status = ModelStatus.WARMING_UP
        
        try:
            # 生成预热样本
            warmup_inputs = self._generate_warmup_inputs()
            
            for _ in range(self.config.warmup_samples):
                for warmup_input in warmup_inputs:
                    await self._predict_internal(warmup_input, warmup=True)
                    
            logger.info(f"模型预热完成: {self.config.name}")
            
        except Exception as e:
            logger.warning(f"模型预热失败: {self.config.name}, 错误: {e}")
        finally:
            self.status = ModelStatus.LOADED
            
    def _generate_warmup_inputs(self) -> List[Any]:
        """生成预热输入"""
        if self.config.model_type==ModelType.TRANSFORMER:
            return ["这是一个测试文本"] * 3
        elif self.config.model_type==ModelType.SENTENCE_TRANSFORMER:
            return ["测试句子1", "测试句子2"]
        elif self.config.model_type==ModelType.PIPELINE:
            if self.config.task=="text-classification":
                return ["测试分类文本"]
            elif self.config.task=="sentiment-analysis":
                return ["这是一个积极的评论"]
        return ["test"]
        
    async def predict(self, inputs: Any,**kwargs) -> Any:
        """预测"""
        if self.status!=ModelStatus.LOADED:
            await self.load()
            
        start_time = time.time()
        
        try:
            result = await self._predict_internal(inputs,**kwargs)
            
            # 更新指标
            processing_time = int((time.time() - start_time) * 1000)
            self._update_metrics(processing_time, success=True)
            
            return result
            
        except Exception as e:
            self._update_metrics(0, success=False)
            raise ModelError(f"模型预测失败: {e}")
            
    async def _predict_internal(self, inputs: Any, warmup: bool = False,**kwargs) -> Any:
        """内部预测方法"""
        if self.config.model_type==ModelType.TRANSFORMER:
            return await self._predict_transformer(inputs,**kwargs)
        elif self.config.model_type==ModelType.ONNX:
            return await self._predict_onnx(inputs,**kwargs)
        elif self.config.model_type==ModelType.SENTENCE_TRANSFORMER:
            return await self._predict_sentence_transformer(inputs,**kwargs)
        elif self.config.model_type==ModelType.PIPELINE:
            return await self._predict_pipeline(inputs,**kwargs)
        else:
            raise ModelError(f"不支持的模型类型: {self.config.model_type}")
            
    async def _predict_transformer(self, inputs: Union[str, List[str]],**kwargs) -> Any:
        """Transformer模型预测"""
        if isinstance(inputs, str):
            inputs = [inputs]
            
        # 分词
        encoded = self.tokenizer(
            inputs,
            padding=True,
            truncation=True,
            max_length=self.config.max_length,
            return_tensors="pt"
        )
        
        # 移动到设备
        if self.config.device!="cpu" and TORCH_AVAILABLE:
            encoded = {k: v.to(self.config.device) for k, v in encoded.items()}
            
        # 预测
        if not TORCH_AVAILABLE:
            raise ModelError("torch库未安装，无法进行Transformer预测")
            
        with torch.no_grad():
            outputs = self.model(**encoded)
            
        return outputs.last_hidden_state if hasattr(outputs, 'last_hidden_state') else outputs.logits
        
    async def _predict_onnx(self, inputs: Any,**kwargs) -> Any:
        """ONNX模型预测"""
        # 准备输入
        if isinstance(inputs, str):
            # 简单的文本编码示例
            if NUMPY_AVAILABLE:
                inputs = np.array([[ord(c) for c in inputs[:self.config.max_length]]], dtype=np.int64)
            else:
                raise ModelError("numpy库未安装，无法处理ONNX模型输入")
            
        input_name = self.model.get_inputs()[0].name
        outputs = self.model.run(None, {input_name: inputs})
        
        return outputs[0]
        
    async def _predict_sentence_transformer(self, inputs: Union[str, List[str]],**kwargs) -> Any:
        """SentenceTransformer模型预测"""
        if isinstance(inputs, str):
            inputs = [inputs]
            
        embeddings = self.model.encode(inputs,**kwargs)
        return embeddings
        
    async def _predict_pipeline(self, inputs: Any,**kwargs) -> Any:
        """Pipeline模型预测"""
        return self.model(inputs,**kwargs)
        
    def _update_metrics(self, processing_time_ms: int, success: bool) -> None:
        """更新性能指标"""
        self.metrics.total_calls+=1
        self.last_used = datetime.now(timezone.utc)
        self.metrics.last_used = self.last_used
        
        if success:
            self.metrics.total_time_ms+=processing_time_ms
            self.metrics.avg_time_ms = self.metrics.total_time_ms / self.metrics.total_calls
        else:
            self.metrics.error_count+=1
            
    def unload(self) -> None:
        """卸载模型"""
        with self.lock:
            if self.status==ModelStatus.UNLOADED:
                return
                
            try:
                # 清理模型资源
                if hasattr(self.model, 'cpu'):
                    self.model.cpu()
                    
                del self.model
                del self.tokenizer
                
                # 清理GPU缓存
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
                self.model = None
                self.tokenizer = None
                self.status = ModelStatus.UNLOADED
                
                logger.info(f"模型卸载成功: {self.config.name}")
                
            except Exception as e:
                logger.error(f"模型卸载失败: {self.config.name}, 错误: {e}")
                
    def get_memory_usage(self) -> float:
        """获取内存使用量(MB)"""
        if self.model is None:
            return 0.0
            
        try:
            if hasattr(self.model, 'get_memory_footprint'):
                return self.model.get_memory_footprint() / 1024 / 1024
            elif hasattr(self.model, 'parameters'):
                total_params = sum(p.numel() for p in self.model.parameters())
                return total_params * 4 / 1024 / 1024  # 假设float32
            else:
                return 100.0  # 默认估计值
        except Exception:
            return 0.0


class AIModelManager:
    """AI模型管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.models: Dict[str, ModelInstance] = {}
        self.cache_manager = CacheManager()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.auto_unload_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> None:
        """初始化模型管理器"""
        logger.info("初始化AI模型管理器...")
        
        try:
            # 加载模型配置
            await self._load_model_configs()
            
            # 启动自动卸载任务
            self.auto_unload_task = asyncio.create_task(self._auto_unload_loop())
            
            logger.info("AI模型管理器初始化完成")
            
        except Exception as e:
            logger.error(f"AI模型管理器初始化失败: {e}")
            raise ModelError(f"无法初始化AI模型管理器: {e}")
            
    async def _load_model_configs(self) -> None:
        """加载模型配置"""
        # 从配置文件加载模型定义
        model_configs = [
            ModelConfig(
                name="tcm_syndrome_classifier",
                model_type=ModelType.TRANSFORMER,
                model_path="bert-base-chinese",
                task="classification",
                device="cpu",
                max_length=256,
                batch_size=8
            ),
            ModelConfig(
                name="constitution_analyzer",
                model_type=ModelType.SENTENCE_TRANSFORMER,
                model_path="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                task="embedding",
                device="cpu"
            ),
            ModelConfig(
                name="symptom_extractor",
                model_type=ModelType.PIPELINE,
                model_path="bert-base-chinese",
                task="ner",
                device="cpu"
            )
        ]
        
        for config in model_configs:
            self.models[config.name] = ModelInstance(config)
            
    async def get_model(self, model_name: str) -> ModelInstance:
        """获取模型实例"""
        if model_name not in self.models:
            raise ModelNotFoundError(f"模型不存在: {model_name}")
            
        model_instance = self.models[model_name]
        
        # 确保模型已加载
        if model_instance.status!=ModelStatus.LOADED:
            await model_instance.load()
            
        return model_instance
        
    async def predict(self, model_name: str, inputs: Any, use_cache: bool = True,**kwargs) -> Any:
        """执行预测"""
        # 检查缓存
        if use_cache:
            cache_key = self._generate_cache_key(model_name, inputs, kwargs)
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
                
        # 获取模型并预测
        model_instance = await self.get_model(model_name)
        result = await model_instance.predict(inputs,**kwargs)
        
        # 缓存结果
        if use_cache:
            await self.cache_manager.set(cache_key, result, ttl=3600)
            
        return result
        
    def _generate_cache_key(self, model_name: str, inputs: Any, kwargs: Dict[str, Any]) -> str:
        """生成缓存键"""
        content = f"{model_name}:{str(inputs)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(content.encode()).hexdigest()
        
    async def batch_predict(self, model_name: str, inputs_list: List[Any],**kwargs) -> List[Any]:
        """批量预测"""
        model_instance = await self.get_model(model_name)
        
        # 分批处理
        batch_size = model_instance.config.batch_size
        results = []
        
        for i in range(0, len(inputs_list), batch_size):
            batch_inputs = inputs_list[i:i + batch_size]
            batch_results = await model_instance.predict(batch_inputs,**kwargs)
            
            if isinstance(batch_results, (list, tuple)):
                results.extend(batch_results)
            else:
                results.append(batch_results)
                
        return results
        
    async def preload_models(self, model_names: List[str]) -> None:
        """预加载模型"""
        tasks = []
        for model_name in model_names:
            if model_name in self.models:
                tasks.append(self.models[model_name].load())
                
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def unload_model(self, model_name: str) -> None:
        """卸载模型"""
        if model_name in self.models:
            self.models[model_name].unload()
            
    async def unload_all_models(self) -> None:
        """卸载所有模型"""
        for model_instance in self.models.values():
            model_instance.unload()
            
    async def _auto_unload_loop(self) -> None:
        """自动卸载循环"""
        while True:
            try:
                await asyncio.sleep(300)  # 每5分钟检查一次
                
                current_time = datetime.now(timezone.utc)
                
                for model_name, model_instance in self.models.items():
                    if (model_instance.status==ModelStatus.LOADED and 
                        model_instance.last_used and
                        (current_time - model_instance.last_used).total_seconds() > 
                        model_instance.config.auto_unload_minutes * 60):
                        
                        logger.info(f"自动卸载长时间未使用的模型: {model_name}")
                        model_instance.unload()
                        
            except Exception as e:
                logger.error(f"自动卸载任务错误: {e}")
                
    def get_model_metrics(self, model_name: str) -> Optional[ModelMetrics]:
        """获取模型性能指标"""
        if model_name in self.models:
            return self.models[model_name].metrics
        return None
        
    def get_all_metrics(self) -> Dict[str, ModelMetrics]:
        """获取所有模型的性能指标"""
        return {name: instance.metrics for name, instance in self.models.items()}
        
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            "total_models": len(self.models),
            "loaded_models": 0,
            "total_memory_mb": 0.0,
            "models": {}
        }
        
        for name, instance in self.models.items():
            model_status = {
                "status": instance.status.value,
                "memory_mb": instance.get_memory_usage(),
                "total_calls": instance.metrics.total_calls,
                "avg_time_ms": instance.metrics.avg_time_ms,
                "error_count": instance.metrics.error_count
            }
            
            if instance.status==ModelStatus.LOADED:
                status["loaded_models"]+=1
                status["total_memory_mb"]+=model_status["memory_mb"]
                
            status["models"][name] = model_status
            
        return status
        
    async def close(self) -> None:
        """关闭模型管理器"""
        if self.auto_unload_task:
            self.auto_unload_task.cancel()
            
        await self.unload_all_models()
        self.executor.shutdown(wait=True)
        
        logger.info("AI模型管理器已关闭")


# 全局模型管理器实例
_model_manager: Optional[AIModelManager] = None


async def get_model_manager() -> AIModelManager:
    """获取全局模型管理器实例"""
    global _model_manager
    if _model_manager is None:
        _model_manager = AIModelManager()
        await _model_manager.initialize()
    return _model_manager


async def predict(model_name: str, inputs: Any,**kwargs) -> Any:
    """便捷的预测函数"""
    manager = await get_model_manager()
    return await manager.predict(model_name, inputs,**kwargs)


async def batch_predict(model_name: str, inputs_list: List[Any],**kwargs) -> List[Any]:
    """便捷的批量预测函数"""
    manager = await get_model_manager()
    return await manager.batch_predict(model_name, inputs_list,**kwargs)