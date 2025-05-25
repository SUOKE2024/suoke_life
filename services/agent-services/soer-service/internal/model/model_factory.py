"""
模型工厂
负责创建和管理不同类型的AI模型实例
"""
import logging
from typing import Dict, Any, Optional, Union, List
from enum import Enum
import asyncio
from abc import ABC, abstractmethod

from pkg.utils.dependency_injection import ServiceLifecycle
from pkg.utils.enhanced_config import get_config
from pkg.utils.error_handling import ModelException, retry_async, RetryConfig
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """模型类型枚举"""
    CHAT = "chat"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    SENTIMENT = "sentiment"
    TCM_DIAGNOSIS = "tcm_diagnosis"
    HEALTH_ASSESSMENT = "health_assessment"

class ModelProvider(Enum):
    """模型提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"
    CUSTOM = "custom"

class BaseModel(ABC):
    """基础模型抽象类"""
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        self.model_name = model_name
        self.config = config
        self.metrics = get_metrics_collector()
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化模型"""
        pass
    
    @abstractmethod
    async def predict(self, input_data: Any, **kwargs) -> Any:
        """模型预测"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """清理资源"""
        pass
    
    async def health_check(self) -> bool:
        """健康检查"""
        return self._initialized

class ChatModel(BaseModel):
    """聊天模型"""
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name, config)
        self.client = None
        self.max_tokens = config.get("max_tokens", 2048)
        self.temperature = config.get("temperature", 0.7)
        self.provider = ModelProvider(config.get("provider", "openai"))
    
    async def initialize(self) -> None:
        """初始化聊天模型"""
        try:
            if self.provider == ModelProvider.OPENAI:
                import openai
                self.client = openai.AsyncOpenAI(
                    api_key=self.config.get("api_key"),
                    base_url=self.config.get("base_url")
                )
            elif self.provider == ModelProvider.ANTHROPIC:
                import anthropic
                self.client = anthropic.AsyncAnthropic(
                    api_key=self.config.get("api_key")
                )
            elif self.provider == ModelProvider.LOCAL:
                # 本地模型初始化
                await self._initialize_local_model()
            
            self._initialized = True
            logger.info(f"聊天模型 {self.model_name} 初始化成功")
            
        except Exception as e:
            logger.error(f"聊天模型 {self.model_name} 初始化失败: {e}")
            raise ModelException(f"聊天模型初始化失败: {e}")
    
    async def _initialize_local_model(self) -> None:
        """初始化本地模型"""
        # 这里可以集成本地模型，如Ollama、vLLM等
        model_path = self.config.get("model_path")
        if not model_path:
            raise ModelException("本地模型路径未配置")
        
        # 示例：使用transformers库加载本地模型
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
        except ImportError:
            logger.warning("transformers库未安装，无法加载本地模型")
            raise ModelException("transformers库未安装")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def predict(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """聊天预测"""
        if not self._initialized:
            raise ModelException("模型未初始化")
        
        try:
            self.metrics.increment_counter("soer_model_requests", {
                "model": self.model_name,
                "type": "chat"
            })
            
            with self.metrics.timer("soer_model_response_time", {
                "model": self.model_name,
                "type": "chat"
            }):
                if self.provider == ModelProvider.OPENAI:
                    response = await self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        max_tokens=kwargs.get("max_tokens", self.max_tokens),
                        temperature=kwargs.get("temperature", self.temperature)
                    )
                    return response.choices[0].message.content
                
                elif self.provider == ModelProvider.ANTHROPIC:
                    # 转换消息格式
                    system_message = ""
                    user_messages = []
                    
                    for msg in messages:
                        if msg["role"] == "system":
                            system_message = msg["content"]
                        else:
                            user_messages.append(msg)
                    
                    response = await self.client.messages.create(
                        model=self.model_name,
                        max_tokens=kwargs.get("max_tokens", self.max_tokens),
                        temperature=kwargs.get("temperature", self.temperature),
                        system=system_message,
                        messages=user_messages
                    )
                    return response.content[0].text
                
                elif self.provider == ModelProvider.LOCAL:
                    return await self._predict_local(messages, **kwargs)
                
                else:
                    raise ModelException(f"不支持的模型提供商: {self.provider}")
        
        except Exception as e:
            self.metrics.increment_counter("soer_model_errors", {
                "model": self.model_name,
                "type": "chat"
            })
            logger.error(f"聊天模型预测失败: {e}")
            raise ModelException(f"聊天模型预测失败: {e}")
    
    async def _predict_local(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """本地模型预测"""
        try:
            # 构建输入文本
            input_text = ""
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                if role == "system":
                    input_text += f"System: {content}\n"
                elif role == "user":
                    input_text += f"User: {content}\n"
                elif role == "assistant":
                    input_text += f"Assistant: {content}\n"
            
            input_text += "Assistant: "
            
            # 编码输入
            inputs = self.tokenizer.encode(input_text, return_tensors="pt")
            
            # 生成响应
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + kwargs.get("max_tokens", self.max_tokens),
                    temperature=kwargs.get("temperature", self.temperature),
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # 解码输出
            response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            return response.strip()
            
        except Exception as e:
            raise ModelException(f"本地模型预测失败: {e}")
    
    async def cleanup(self) -> None:
        """清理资源"""
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'tokenizer'):
            del self.tokenizer
        self._initialized = False

class EmbeddingModel(BaseModel):
    """嵌入模型"""
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name, config)
        self.client = None
        self.provider = ModelProvider(config.get("provider", "openai"))
        self.dimension = config.get("dimension", 1536)
    
    async def initialize(self) -> None:
        """初始化嵌入模型"""
        try:
            if self.provider == ModelProvider.OPENAI:
                import openai
                self.client = openai.AsyncOpenAI(
                    api_key=self.config.get("api_key"),
                    base_url=self.config.get("base_url")
                )
            elif self.provider == ModelProvider.HUGGINGFACE:
                await self._initialize_huggingface_model()
            elif self.provider == ModelProvider.LOCAL:
                await self._initialize_local_embedding_model()
            
            self._initialized = True
            logger.info(f"嵌入模型 {self.model_name} 初始化成功")
            
        except Exception as e:
            logger.error(f"嵌入模型 {self.model_name} 初始化失败: {e}")
            raise ModelException(f"嵌入模型初始化失败: {e}")
    
    async def _initialize_huggingface_model(self) -> None:
        """初始化HuggingFace模型"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except ImportError:
            raise ModelException("sentence-transformers库未安装")
    
    async def _initialize_local_embedding_model(self) -> None:
        """初始化本地嵌入模型"""
        model_path = self.config.get("model_path")
        if not model_path:
            raise ModelException("本地嵌入模型路径未配置")
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_path)
        except ImportError:
            raise ModelException("sentence-transformers库未安装")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def predict(self, texts: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]:
        """生成嵌入向量"""
        if not self._initialized:
            raise ModelException("模型未初始化")
        
        try:
            self.metrics.increment_counter("soer_model_requests", {
                "model": self.model_name,
                "type": "embedding"
            })
            
            with self.metrics.timer("soer_model_response_time", {
                "model": self.model_name,
                "type": "embedding"
            }):
                if self.provider == ModelProvider.OPENAI:
                    if isinstance(texts, str):
                        texts = [texts]
                    
                    response = await self.client.embeddings.create(
                        model=self.model_name,
                        input=texts
                    )
                    
                    embeddings = [data.embedding for data in response.data]
                    return embeddings[0] if len(embeddings) == 1 else embeddings
                
                elif self.provider in [ModelProvider.HUGGINGFACE, ModelProvider.LOCAL]:
                    embeddings = self.model.encode(texts)
                    return embeddings.tolist()
                
                else:
                    raise ModelException(f"不支持的嵌入模型提供商: {self.provider}")
        
        except Exception as e:
            self.metrics.increment_counter("soer_model_errors", {
                "model": self.model_name,
                "type": "embedding"
            })
            logger.error(f"嵌入模型预测失败: {e}")
            raise ModelException(f"嵌入模型预测失败: {e}")
    
    async def cleanup(self) -> None:
        """清理资源"""
        if hasattr(self, 'model'):
            del self.model
        self._initialized = False

class ClassificationModel(BaseModel):
    """分类模型"""
    
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name, config)
        self.model = None
        self.tokenizer = None
        self.labels = config.get("labels", [])
        self.provider = ModelProvider(config.get("provider", "huggingface"))
    
    async def initialize(self) -> None:
        """初始化分类模型"""
        try:
            if self.provider == ModelProvider.HUGGINGFACE:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                import torch
                
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
                
                if torch.cuda.is_available():
                    self.model = self.model.cuda()
            
            elif self.provider == ModelProvider.LOCAL:
                await self._initialize_local_classification_model()
            
            self._initialized = True
            logger.info(f"分类模型 {self.model_name} 初始化成功")
            
        except Exception as e:
            logger.error(f"分类模型 {self.model_name} 初始化失败: {e}")
            raise ModelException(f"分类模型初始化失败: {e}")
    
    async def _initialize_local_classification_model(self) -> None:
        """初始化本地分类模型"""
        model_path = self.config.get("model_path")
        if not model_path:
            raise ModelException("本地分类模型路径未配置")
        
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            
            if torch.cuda.is_available():
                self.model = self.model.cuda()
                
        except ImportError:
            raise ModelException("transformers库未安装")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def predict(self, text: str, **kwargs) -> Dict[str, Any]:
        """文本分类预测"""
        if not self._initialized:
            raise ModelException("模型未初始化")
        
        try:
            self.metrics.increment_counter("soer_model_requests", {
                "model": self.model_name,
                "type": "classification"
            })
            
            with self.metrics.timer("soer_model_response_time", {
                "model": self.model_name,
                "type": "classification"
            }):
                import torch
                
                # 编码输入
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    padding=True,
                    max_length=512
                )
                
                if torch.cuda.is_available():
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                
                # 预测
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
                # 处理结果
                predictions = predictions.cpu().numpy()[0]
                
                if self.labels:
                    results = {
                        label: float(score) 
                        for label, score in zip(self.labels, predictions)
                    }
                    predicted_label = self.labels[predictions.argmax()]
                else:
                    results = {f"label_{i}": float(score) for i, score in enumerate(predictions)}
                    predicted_label = f"label_{predictions.argmax()}"
                
                return {
                    "predicted_label": predicted_label,
                    "confidence": float(predictions.max()),
                    "all_scores": results
                }
        
        except Exception as e:
            self.metrics.increment_counter("soer_model_errors", {
                "model": self.model_name,
                "type": "classification"
            })
            logger.error(f"分类模型预测失败: {e}")
            raise ModelException(f"分类模型预测失败: {e}")
    
    async def cleanup(self) -> None:
        """清理资源"""
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'tokenizer'):
            del self.tokenizer
        self._initialized = False

class ModelFactory(ServiceLifecycle):
    """模型工厂"""
    
    def __init__(self):
        self.config = get_config()
        self.models: Dict[str, BaseModel] = {}
        self.metrics = get_metrics_collector()
        self._model_configs = {}
    
    async def start(self) -> None:
        """启动模型工厂"""
        try:
            # 加载模型配置
            self._model_configs = self.config.get_section("models", {})
            
            # 预加载配置中的模型
            for model_id, model_config in self._model_configs.items():
                if model_config.get("preload", False):
                    await self.get_model(model_id)
            
            logger.info("模型工厂启动成功")
            
        except Exception as e:
            logger.error(f"模型工厂启动失败: {e}")
            raise ModelException(f"模型工厂启动失败: {e}")
    
    async def stop(self) -> None:
        """停止模型工厂"""
        try:
            # 清理所有模型
            for model in self.models.values():
                await model.cleanup()
            
            self.models.clear()
            logger.info("模型工厂已停止")
            
        except Exception as e:
            logger.error(f"模型工厂停止失败: {e}")
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查所有已加载的模型
            for model_id, model in self.models.items():
                if not await model.health_check():
                    logger.warning(f"模型 {model_id} 健康检查失败")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"模型工厂健康检查失败: {e}")
            return False
    
    async def get_model(self, model_id: str) -> BaseModel:
        """获取模型实例"""
        if model_id in self.models:
            return self.models[model_id]
        
        # 从配置创建模型
        model_config = self._model_configs.get(model_id)
        if not model_config:
            raise ModelException(f"模型配置未找到: {model_id}")
        
        model = await self._create_model(model_id, model_config)
        self.models[model_id] = model
        
        return model
    
    async def _create_model(self, model_id: str, config: Dict[str, Any]) -> BaseModel:
        """创建模型实例"""
        try:
            model_type = ModelType(config.get("type"))
            model_name = config.get("name", model_id)
            
            # 根据类型创建模型
            if model_type == ModelType.CHAT:
                model = ChatModel(model_name, config)
            elif model_type == ModelType.EMBEDDING:
                model = EmbeddingModel(model_name, config)
            elif model_type in [ModelType.CLASSIFICATION, ModelType.SENTIMENT, 
                               ModelType.TCM_DIAGNOSIS, ModelType.HEALTH_ASSESSMENT]:
                model = ClassificationModel(model_name, config)
            else:
                raise ModelException(f"不支持的模型类型: {model_type}")
            
            # 初始化模型
            await model.initialize()
            
            logger.info(f"模型 {model_id} 创建成功")
            return model
            
        except Exception as e:
            logger.error(f"创建模型 {model_id} 失败: {e}")
            raise ModelException(f"创建模型失败: {e}")
    
    async def reload_model(self, model_id: str) -> None:
        """重新加载模型"""
        try:
            # 清理旧模型
            if model_id in self.models:
                await self.models[model_id].cleanup()
                del self.models[model_id]
            
            # 重新创建模型
            await self.get_model(model_id)
            
            logger.info(f"模型 {model_id} 重新加载成功")
            
        except Exception as e:
            logger.error(f"重新加载模型 {model_id} 失败: {e}")
            raise ModelException(f"重新加载模型失败: {e}")
    
    def list_models(self) -> List[str]:
        """列出所有可用模型"""
        return list(self._model_configs.keys())
    
    def list_loaded_models(self) -> List[str]:
        """列出已加载的模型"""
        return list(self.models.keys())
    
    async def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """获取模型信息"""
        config = self._model_configs.get(model_id)
        if not config:
            raise ModelException(f"模型配置未找到: {model_id}")
        
        is_loaded = model_id in self.models
        is_healthy = False
        
        if is_loaded:
            is_healthy = await self.models[model_id].health_check()
        
        return {
            "model_id": model_id,
            "name": config.get("name", model_id),
            "type": config.get("type"),
            "provider": config.get("provider"),
            "is_loaded": is_loaded,
            "is_healthy": is_healthy,
            "config": config
        }

# 全局模型工厂实例
_model_factory: Optional[ModelFactory] = None

def get_model_factory() -> ModelFactory:
    """获取模型工厂实例"""
    global _model_factory
    if _model_factory is None:
        _model_factory = ModelFactory()
    return _model_factory 