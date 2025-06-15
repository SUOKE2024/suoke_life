"""
模型集成接口

提供统一的接口连接不同类型的模型，支持本地模型和远程API模型的集成。
"""

import json
import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

import aiohttp
import numpy as np
import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ModelRequest(BaseModel):
    """模型请求参数"""
    inputs: Any
    parameters: Optional[Dict[str, Any]] = None


class ModelResponse(BaseModel):
    """模型响应结果"""
    outputs: Any
    model_id: str
    model_version: str
    latency_ms: float


class ModelInterface(ABC):
    """模型接口基类"""

    @abstractmethod
    def predict(self, inputs: Any, parameters: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """
        模型预测接口
        
        Args:
            inputs: 输入数据
            parameters: 预测参数
            
        Returns:
            模型响应
        """
        pass

    @abstractmethod
    async def predict_async(self, inputs: Any, parameters: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """
        异步模型预测接口
        
        Args:
            inputs: 输入数据
            parameters: 预测参数
            
        Returns:
            模型响应
        """
        pass


class LocalModel(ModelInterface):
    """本地模型接口"""

    def __init__(
        self,
        model_id: str,
        model_version: str,
        model_path: str,
        device: str = "cpu",
        **kwargs
    ):
        """
        初始化本地模型
        
        Args:
            model_id: 模型ID
            model_version: 模型版本
            model_path: 模型路径
            device: 运行设备
            **kwargs: 其他参数
        """
        self.model_id = model_id
        self.model_version = model_version
        self.model_path = model_path
        self.device = device
        self.model = None
        self.preprocessor = None
        
        # 记录模型加载时间
        start_time = time.time()
        self._load_model()
        load_time = time.time() - start_time
        logger.info(f"模型 {model_id}:{model_version} 加载完成，耗时 {load_time:.2f} 秒")

    def _load_model(self):
        """加载模型"""
        # 在实际实现中，根据模型类型加载不同的模型
        # 例如PyTorch、TensorFlow或其他框架的模型
        # 这里仅做示例，实际项目中需根据具体需求实现
        try:
            # 根据模型ID和路径判断模型类型并加载
            if "torch" in self.model_id.lower() or self.model_path.endswith(".pt"):
                self._load_pytorch_model()
            elif "tf" in self.model_id.lower() or self.model_path.endswith(".pb"):
                self._load_tensorflow_model()
            elif "onnx" in self.model_id.lower() or self.model_path.endswith(".onnx"):
                self._load_onnx_model()
            else:
                # 默认处理
                logger.warning(f"未知模型类型: {self.model_id}, 将使用通用加载方式")
                self.model = {"dummy": "model"}  # 仅作示例
                
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise RuntimeError(f"模型加载失败: {str(e)}")

    def _load_pytorch_model(self):
        """加载PyTorch模型"""
        try:
            import torch
            
            logger.info(f"加载PyTorch模型: {self.model_path}")
            self.model = torch.load(self.model_path, map_location=self.device)
            self.model.eval()  # 设置为评估模式
            
        except ImportError:
            logger.error("无法导入PyTorch，请确保已安装")
            raise RuntimeError("无法导入PyTorch，请确保已安装")
        except Exception as e:
            logger.error(f"PyTorch模型加载失败: {str(e)}")
            raise RuntimeError(f"PyTorch模型加载失败: {str(e)}")

    def _load_tensorflow_model(self):
        """加载TensorFlow模型"""
        try:
            import tensorflow as tf
            
            logger.info(f"加载TensorFlow模型: {self.model_path}")
            self.model = tf.saved_model.load(self.model_path)
            
        except ImportError:
            logger.error("无法导入TensorFlow，请确保已安装")
            raise RuntimeError("无法导入TensorFlow，请确保已安装")
        except Exception as e:
            logger.error(f"TensorFlow模型加载失败: {str(e)}")
            raise RuntimeError(f"TensorFlow模型加载失败: {str(e)}")

    def _load_onnx_model(self):
        """加载ONNX模型"""
        try:
            import onnxruntime as ort
            
            logger.info(f"加载ONNX模型: {self.model_path}")
            self.model = ort.InferenceSession(self.model_path)
            
        except ImportError:
            logger.error("无法导入ONNX Runtime，请确保已安装")
            raise RuntimeError("无法导入ONNX Runtime，请确保已安装")
        except Exception as e:
            logger.error(f"ONNX模型加载失败: {str(e)}")
            raise RuntimeError(f"ONNX模型加载失败: {str(e)}")

    def predict(self, inputs: Any, parameters: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """
        模型预测
        
        Args:
            inputs: 输入数据
            parameters: 预测参数
            
        Returns:
            模型响应
        """
        if self.model is None:
            raise RuntimeError("模型未加载")
            
        # 记录预测时间
        start_time = time.time()
        
        try:
            # 预处理
            processed_inputs = self._preprocess(inputs)
            
            # 根据模型类型进行不同的预测调用
            if hasattr(self.model, "forward") and callable(self.model.forward):
                # PyTorch模型
                import torch
                with torch.no_grad():
                    outputs = self.model(processed_inputs)
            elif hasattr(self.model, "predict") and callable(self.model.predict):
                # TensorFlow、Scikit-learn等
                outputs = self.model.predict(processed_inputs)
            elif hasattr(self.model, "run") and callable(self.model.run):
                # ONNX模型
                outputs = self.model.run(None, {"input": processed_inputs})[0]
            else:
                # 通用情况，模拟预测
                logger.warning("使用模拟预测")
                outputs = {"result": "模拟预测结果", "confidence": 0.95}
            
            # 后处理
            final_outputs = self._postprocess(outputs)
            
            latency_ms = (time.time() - start_time) * 1000
            
            return ModelResponse(
                outputs=final_outputs,
                model_id=self.model_id,
                model_version=self.model_version,
                latency_ms=latency_ms
            )
            
        except Exception as e:
            logger.error(f"预测失败: {str(e)}")
            raise RuntimeError(f"预测失败: {str(e)}")

    async def predict_async(self, inputs: Any, parameters: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """
        异步模型预测
        
        Args:
            inputs: 输入数据
            parameters: 预测参数
            
        Returns:
            模型响应
        """
        # 由于本地模型预测通常是同步的，这里简单地将同步方法包装为异步方法
        # 在实际项目中，可以使用线程池进行优化
        return self.predict(inputs, parameters)

    def _preprocess(self, inputs: Any) -> Any:
        """
        预处理输入数据
        
        Args:
            inputs: 原始输入
            
        Returns:
            处理后的输入
        """
        # 实际项目中应根据模型类型实现具体的预处理逻辑
        # 这里仅做简单示例
        if self.preprocessor:
            return self.preprocessor(inputs)
        return inputs

    def _postprocess(self, outputs: Any) -> Any:
        """
        后处理模型输出
        
        Args:
            outputs: 模型原始输出
            
        Returns:
            处理后的输出
        """
        # 实际项目中应根据模型类型实现具体的后处理逻辑
        # 这里仅做简单示例
        return outputs


class RemoteAPIModel(ModelInterface):
    """远程API模型接口"""

    def __init__(
        self,
        model_id: str,
        model_version: str,
        api_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        初始化远程API模型
        
        Args:
            model_id: 模型ID
            model_version: 模型版本
            api_url: API地址
            api_key: API密钥
            timeout: 超时时间（秒）
            **kwargs: 其他参数
        """
        self.model_id = model_id
        self.model_version = model_version
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {
            "Content-Type": "application/json",
        }
        
        # 如果提供了API密钥，添加到请求头
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        
        logger.info(f"远程API模型 {model_id}:{model_version} 初始化完成，API地址: {api_url}")

    def predict(self, inputs: Any, parameters: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """
        同步模型预测
        
        Args:
            inputs: 输入数据
            parameters: 预测参数
            
        Returns:
            模型响应
        """
        # 准备请求数据
        request_data = {
            "inputs": inputs,
        }
        if parameters:
            request_data["parameters"] = parameters
            
        # 记录请求开始时间
        start_time = time.time()
        
        try:
            # 发送API请求
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=request_data,
                timeout=self.timeout
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应数据
            result = response.json()
            
            # 计算延迟
            latency_ms = (time.time() - start_time) * 1000
            
            return ModelResponse(
                outputs=result.get("outputs", result),  # 兼容不同API格式
                model_id=self.model_id,
                model_version=self.model_version,
                latency_ms=latency_ms
            )
            
        except requests.RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            raise RuntimeError(f"API请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"API响应解析失败: {str(e)}")
            raise RuntimeError(f"API响应解析失败: {str(e)}")
        except Exception as e:
            logger.error(f"调用API模型失败: {str(e)}")
            raise RuntimeError(f"调用API模型失败: {str(e)}")

    async def predict_async(self, inputs: Any, parameters: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """
        异步模型预测
        
        Args:
            inputs: 输入数据
            parameters: 预测参数
            
        Returns:
            模型响应
        """
        # 准备请求数据
        request_data = {
            "inputs": inputs,
        }
        if parameters:
            request_data["parameters"] = parameters
            
        # 记录请求开始时间
        start_time = time.time()
        
        try:
            # 使用aiohttp发送异步请求
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=request_data,
                    timeout=self.timeout
                ) as response:
                    # 检查响应状态
                    response.raise_for_status()
                    
                    # 异步解析响应内容
                    result = await response.json()
                    
                    # 计算延迟
                    latency_ms = (time.time() - start_time) * 1000
                    
                    return ModelResponse(
                        outputs=result.get("outputs", result),  # 兼容不同API格式
                        model_id=self.model_id,
                        model_version=self.model_version,
                        latency_ms=latency_ms
                    )
                    
        except aiohttp.ClientError as e:
            logger.error(f"异步API请求失败: {str(e)}")
            raise RuntimeError(f"异步API请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"异步API响应解析失败: {str(e)}")
            raise RuntimeError(f"异步API响应解析失败: {str(e)}")
        except Exception as e:
            logger.error(f"异步调用API模型失败: {str(e)}")
            raise RuntimeError(f"异步调用API模型失败: {str(e)}")


def create_model(
    model_id: str,
    model_version: str,
    model_type: str,
    model_config: Dict[str, Any]
) -> ModelInterface:
    """
    工厂函数：创建模型接口实例
    
    Args:
        model_id: 模型ID
        model_version: 模型版本
        model_type: 模型类型 (local, remote_api)
        model_config: 模型配置
        
    Returns:
        模型接口实例
    """
    if model_type == "local":
        # 本地模型
        model_path = model_config.get("model_path")
        if not model_path:
            raise ValueError("本地模型必须提供model_path")
            
        # 检查模型文件是否存在
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
            
        return LocalModel(
            model_id=model_id,
            model_version=model_version,
            model_path=model_path,
            device=model_config.get("device", "cpu"),
            **model_config
        )
    elif model_type == "remote_api":
        # 远程API模型
        api_url = model_config.get("api_url")
        if not api_url:
            raise ValueError("远程API模型必须提供api_url")
            
        return RemoteAPIModel(
            model_id=model_id,
            model_version=model_version,
            api_url=api_url,
            api_key=model_config.get("api_key"),
            timeout=model_config.get("timeout", 30),
            **model_config
        )
    else:
        # 未知模型类型
        raise ValueError(f"不支持的模型类型: {model_type}")


class ModelRegistry:
    """模型注册表"""
    
    def __init__(self):
        """初始化模型注册表"""
        self.models: Dict[str, ModelInterface] = {}
        
    def register_model(
        self,
        model_id: str,
        model_version: str,
        model_type: str,
        model_config: Dict[str, Any]
    ) -> ModelInterface:
        """
        注册模型
        
        Args:
            model_id: 模型ID
            model_version: 模型版本
            model_type: 模型类型
            model_config: 模型配置
            
        Returns:
            模型接口实例
        """
        # 创建模型实例
        model = create_model(model_id, model_version, model_type, model_config)
        
        # 生成唯一模型标识
        model_key = f"{model_id}:{model_version}"
        
        # 注册模型
        self.models[model_key] = model
        logger.info(f"模型注册成功: {model_key}")
        
        return model
        
    def get_model(self, model_id: str, model_version: str) -> Optional[ModelInterface]:
        """
        获取模型
        
        Args:
            model_id: 模型ID
            model_version: 模型版本
            
        Returns:
            模型接口实例，如果不存在则返回None
        """
        model_key = f"{model_id}:{model_version}"
        return self.models.get(model_key)
        
    def unregister_model(self, model_id: str, model_version: str) -> bool:
        """
        注销模型
        
        Args:
            model_id: 模型ID
            model_version: 模型版本
            
        Returns:
            是否成功注销
        """
        model_key = f"{model_id}:{model_version}"
        if model_key in self.models:
            del self.models[model_key]
            logger.info(f"模型注销成功: {model_key}")
            return True
        return False
        
    def list_models(self) -> List[Dict[str, str]]:
        """
        列出所有已注册模型
        
        Returns:
            模型列表
        """
        return [
            {"model_id": key.split(":")[0], "model_version": key.split(":")[1]}
            for key in self.models.keys()
        ]


# 全局模型注册表实例
model_registry = ModelRegistry() 