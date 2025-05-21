#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模型工厂模块

负责创建、加载和管理不同类型的模型，支持多种深度学习框架
"""

import os
import logging
from enum import Enum
from typing import Dict, Any, Optional, Union, List

import cv2
import numpy as np
from structlog import get_logger

from pkg.utils.exceptions import ModelLoadingError, ConfigurationError


# 设置日志
logger = get_logger()


class ModelType(str, Enum):
    """模型类型枚举"""
    FACE_ANALYSIS = "face_analysis"
    BODY_ANALYSIS = "body_analysis"
    TONGUE_ANALYSIS = "tongue_analysis"
    FEATURE_EXTRACTION = "feature_extraction"
    IMAGE_SEGMENTATION = "image_segmentation"


class ModelBackend(str, Enum):
    """模型后端枚举"""
    OPENCV = "opencv"
    ONNX = "onnx"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    CUSTOM = "custom"


class BaseModel:
    """模型基类，定义所有模型的通用接口"""
    
    def __init__(self, model_path: str, config: Dict[str, Any] = None):
        """
        初始化模型
        
        Args:
            model_path: 模型文件路径
            config: 模型配置
        """
        self.model_path = model_path
        self.config = config or {}
        self.model = None
        self.input_shape = None
        self.is_loaded = False
        
    def load(self) -> bool:
        """
        加载模型
        
        Returns:
            加载是否成功
        """
        raise NotImplementedError("子类必须实现load方法")
        
    def predict(self, input_data: np.ndarray) -> Any:
        """
        使用模型进行预测
        
        Args:
            input_data: 输入数据
            
        Returns:
            预测结果
        """
        raise NotImplementedError("子类必须实现predict方法")
    
    def preprocess(self, input_data: np.ndarray) -> np.ndarray:
        """
        预处理输入数据
        
        Args:
            input_data: 原始输入数据
            
        Returns:
            预处理后的数据
        """
        raise NotImplementedError("子类必须实现preprocess方法")
    
    def postprocess(self, model_output: Any) -> Any:
        """
        后处理模型输出
        
        Args:
            model_output: 模型原始输出
            
        Returns:
            后处理后的结果
        """
        raise NotImplementedError("子类必须实现postprocess方法")


class OpenCVModel(BaseModel):
    """基于OpenCV DNN的模型实现"""
    
    def __init__(self, model_path: str, config: Dict[str, Any] = None):
        """
        初始化OpenCV模型
        
        Args:
            model_path: 模型文件路径
            config: 模型配置
        """
        super().__init__(model_path, config)
        self.input_size = self.config.get("input_size", (224, 224))
        self.mean = self.config.get("mean", [0.485, 0.456, 0.406])
        self.std = self.config.get("std", [0.229, 0.224, 0.225])
        self.scale = self.config.get("scale", 1.0)
        self.swap_rb = self.config.get("swap_rb", True)
        self.is_tensorflow = self.config.get("is_tensorflow", False)
        
    def load(self) -> bool:
        """
        加载OpenCV DNN模型
        
        Returns:
            加载是否成功
        """
        try:
            # 检查文件存在
            if not os.path.exists(self.model_path):
                raise ModelLoadingError(f"模型文件不存在: {self.model_path}")
            
            # 根据文件扩展名选择加载方法
            ext = os.path.splitext(self.model_path)[1].lower()
            
            if ext == ".onnx":
                self.model = cv2.dnn.readNetFromONNX(self.model_path)
            elif ext in [".pb", ".pbtxt"]:
                if self.config.get("config_path"):
                    self.model = cv2.dnn.readNetFromTensorflow(
                        self.model_path, 
                        self.config.get("config_path")
                    )
                else:
                    self.model = cv2.dnn.readNetFromTensorflow(self.model_path)
            elif ext in [".caffemodel", ".prototxt"]:
                if self.config.get("config_path"):
                    self.model = cv2.dnn.readNetFromCaffe(
                        self.config.get("config_path"),
                        self.model_path
                    )
                else:
                    raise ConfigurationError("Caffe模型需要提供prototxt配置文件路径")
            else:
                raise ModelLoadingError(f"不支持的模型格式: {ext}")
            
            # 设置计算后端
            if self.config.get("use_cuda", False) and cv2.cuda.getCudaEnabledDeviceCount() > 0:
                self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                logger.info("使用CUDA加速OpenCV DNN模型")
            else:
                self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                logger.info("使用CPU运行OpenCV DNN模型")
            
            self.is_loaded = True
            logger.info("OpenCV DNN模型加载成功", model_path=self.model_path)
            return True
            
        except Exception as e:
            logger.error("OpenCV DNN模型加载失败", error=str(e), model_path=self.model_path)
            raise ModelLoadingError(f"加载OpenCV DNN模型失败: {str(e)}")
    
    def preprocess(self, input_data: np.ndarray) -> np.ndarray:
        """
        预处理输入数据
        
        Args:
            input_data: 原始输入图像
            
        Returns:
            预处理后的blob数据
        """
        if input_data.shape[0] != self.input_size[1] or input_data.shape[1] != self.input_size[0]:
            input_data = cv2.resize(input_data, self.input_size)
            
        # 创建blob
        blob = cv2.dnn.blobFromImage(
            input_data, 
            scalefactor=self.scale,
            size=self.input_size,
            mean=self.mean,
            swapRB=self.swap_rb,
            crop=False
        )
        
        return blob
    
    def predict(self, input_data: np.ndarray) -> Any:
        """
        使用模型进行预测
        
        Args:
            input_data: 输入图像
            
        Returns:
            模型输出
        """
        if not self.is_loaded:
            self.load()
            
        # 预处理
        blob = self.preprocess(input_data)
        
        # 设置输入
        self.model.setInput(blob)
        
        # 获取输出层名称
        output_names = self.model.getUnconnectedOutLayersNames() if self.config.get("use_output_names", False) else []
        
        # 执行前向传播
        if output_names:
            outputs = self.model.forward(output_names)
        else:
            outputs = self.model.forward()
            
        # 后处理
        result = self.postprocess(outputs)
        
        return result
        
    def postprocess(self, model_output: Any) -> Any:
        """
        后处理模型输出
        
        Args:
            model_output: 模型原始输出
            
        Returns:
            后处理后的结果
        """
        # 默认实现直接返回模型输出
        # 具体的后处理逻辑应该由子类实现
        return model_output


class ONNXModel(BaseModel):
    """基于ONNX Runtime的模型实现"""
    
    def __init__(self, model_path: str, config: Dict[str, Any] = None):
        """
        初始化ONNX模型
        
        Args:
            model_path: 模型文件路径
            config: 模型配置
        """
        super().__init__(model_path, config)
        # 推迟导入，以避免强制依赖
        import onnxruntime as ort
        self.ort = ort
        
        self.input_size = self.config.get("input_size", (224, 224))
        self.input_name = self.config.get("input_name", None)
        self.output_names = self.config.get("output_names", None)
        self.providers = self.config.get("providers", None)
        
    def load(self) -> bool:
        """
        加载ONNX模型
        
        Returns:
            加载是否成功
        """
        try:
            # 检查文件存在
            if not os.path.exists(self.model_path):
                raise ModelLoadingError(f"模型文件不存在: {self.model_path}")
            
            # 设置运行时选项
            if self.providers is None:
                # 如果没有指定providers，则尝试使用CUDA，如果可用
                available_providers = self.ort.get_available_providers()
                if 'CUDAExecutionProvider' in available_providers and self.config.get("use_cuda", True):
                    self.providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                    logger.info("使用CUDA加速ONNX模型")
                else:
                    self.providers = ['CPUExecutionProvider']
                    logger.info("使用CPU运行ONNX模型")
            
            # 创建推理会话
            sess_options = self.ort.SessionOptions()
            sess_options.graph_optimization_level = self.ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            
            # 设置线程数
            if "num_threads" in self.config:
                sess_options.intra_op_num_threads = self.config["num_threads"]
                
            # 加载模型
            self.model = self.ort.InferenceSession(
                self.model_path, 
                sess_options=sess_options,
                providers=self.providers
            )
            
            # 获取模型输入输出信息
            model_inputs = self.model.get_inputs()
            model_outputs = self.model.get_outputs()
            
            if not self.input_name and model_inputs:
                self.input_name = model_inputs[0].name
                
            if not self.output_names and model_outputs:
                self.output_names = [output.name for output in model_outputs]
                
            # 获取输入形状
            if model_inputs:
                input_shape = model_inputs[0].shape
                # 通常为[batch_size, channels, height, width]或[batch_size, height, width, channels]
                if len(input_shape) == 4:
                    # 假设输入形状为NCHW或NHWC
                    if input_shape[1] == 3 or input_shape[1] in [1, 3]:  # NCHW
                        self.input_shape = (int(input_shape[2]), int(input_shape[3]))
                    elif input_shape[3] == 3 or input_shape[3] in [1, 3]:  # NHWC
                        self.input_shape = (int(input_shape[1]), int(input_shape[2]))
                        
                    # 如果模型输入形状有明确尺寸（非符号尺寸），则使用它
                    if self.input_shape[0] > 0 and self.input_shape[1] > 0:
                        self.input_size = self.input_shape
            
            self.is_loaded = True
            logger.info("ONNX模型加载成功", 
                      model_path=self.model_path, 
                      input_name=self.input_name,
                      output_names=self.output_names)
            return True
            
        except Exception as e:
            logger.error("ONNX模型加载失败", error=str(e), model_path=self.model_path)
            raise ModelLoadingError(f"加载ONNX模型失败: {str(e)}")
    
    def preprocess(self, input_data: np.ndarray) -> np.ndarray:
        """
        预处理输入数据
        
        Args:
            input_data: 原始输入图像
            
        Returns:
            预处理后的数据
        """
        # 调整图像大小
        if input_data.shape[0] != self.input_size[1] or input_data.shape[1] != self.input_size[0]:
            input_data = cv2.resize(input_data, self.input_size)
            
        # 标准化
        input_data = input_data.astype(np.float32) / 255.0
        
        # 处理通道
        if self.config.get("channel_first", True):
            # NHWC -> NCHW
            input_data = input_data.transpose(2, 0, 1)
            
        # 添加批次维度
        input_data = np.expand_dims(input_data, axis=0)
        
        return input_data
    
    def predict(self, input_data: np.ndarray) -> Any:
        """
        使用模型进行预测
        
        Args:
            input_data: 输入图像
            
        Returns:
            模型输出
        """
        if not self.is_loaded:
            self.load()
            
        # 预处理
        processed_input = self.preprocess(input_data)
        
        # 准备输入
        inputs = {self.input_name: processed_input}
        
        # 执行推理
        outputs = self.model.run(self.output_names, inputs)
        
        # 后处理
        result = self.postprocess(outputs)
        
        return result
        
    def postprocess(self, model_output: Any) -> Any:
        """
        后处理模型输出
        
        Args:
            model_output: 模型原始输出
            
        Returns:
            后处理后的结果
        """
        # 默认实现直接返回模型输出
        # 具体的后处理逻辑应该由子类实现
        return model_output


class TensorFlowModel(BaseModel):
    """基于TensorFlow的模型实现"""
    
    def __init__(self, model_path: str, config: Dict[str, Any] = None):
        """
        初始化TensorFlow模型
        
        Args:
            model_path: 模型文件路径
            config: 模型配置
        """
        super().__init__(model_path, config)
        # 推迟导入，以避免强制依赖
        import tensorflow as tf
        self.tf = tf
        
        self.input_size = self.config.get("input_size", (224, 224))
        self.input_name = self.config.get("input_name", None)
        self.output_names = self.config.get("output_names", None)
        
        # 设置GPU内存增长
        gpus = self.tf.config.experimental.list_physical_devices('GPU')
        if gpus and self.config.get("use_gpu", True):
            try:
                for gpu in gpus:
                    self.tf.config.experimental.set_memory_growth(gpu, True)
                logger.info(f"设置TensorFlow GPU内存增长，可用GPU数量: {len(gpus)}")
            except RuntimeError as e:
                logger.warning(f"设置TensorFlow GPU内存增长失败: {str(e)}")
        
    def load(self) -> bool:
        """
        加载TensorFlow模型
        
        Returns:
            加载是否成功
        """
        try:
            # 检查文件存在
            if not os.path.exists(self.model_path):
                raise ModelLoadingError(f"模型文件不存在: {self.model_path}")
            
            # 加载模型
            self.model = self.tf.saved_model.load(self.model_path)
            
            # 获取签名
            if hasattr(self.model, 'signatures'):
                self.model_func = self.model.signatures["serving_default"]
                
                # 获取输入输出信息
                input_desc = list(self.model_func.structured_input_signature[1].items())
                if input_desc and not self.input_name:
                    self.input_name = input_desc[0][0]
                    
                output_desc = list(self.model_func.structured_outputs.items())
                if output_desc and not self.output_names:
                    self.output_names = [desc[0] for desc in output_desc]
            else:
                # 对于自定义模型，可能需要在配置中指定callable的属性名
                if "model_func_name" in self.config:
                    self.model_func = getattr(self.model, self.config["model_func_name"])
                else:
                    # 默认使用模型本身作为callable
                    self.model_func = self.model
            
            self.is_loaded = True
            logger.info("TensorFlow模型加载成功", 
                      model_path=self.model_path, 
                      input_name=self.input_name,
                      output_names=self.output_names)
            return True
            
        except Exception as e:
            logger.error("TensorFlow模型加载失败", error=str(e), model_path=self.model_path)
            raise ModelLoadingError(f"加载TensorFlow模型失败: {str(e)}")
    
    def preprocess(self, input_data: np.ndarray) -> np.ndarray:
        """
        预处理输入数据
        
        Args:
            input_data: 原始输入图像
            
        Returns:
            预处理后的数据
        """
        # 调整图像大小
        if input_data.shape[0] != self.input_size[1] or input_data.shape[1] != self.input_size[0]:
            input_data = cv2.resize(input_data, self.input_size)
            
        # 转换为RGB（如果输入是BGR）
        if self.config.get("convert_to_rgb", True) and input_data.shape[2] == 3:
            input_data = cv2.cvtColor(input_data, cv2.COLOR_BGR2RGB)
            
        # 标准化
        input_data = input_data.astype(np.float32) / 255.0
        
        # 添加批次维度
        input_data = np.expand_dims(input_data, axis=0)
        
        return input_data
    
    def predict(self, input_data: np.ndarray) -> Any:
        """
        使用模型进行预测
        
        Args:
            input_data: 输入图像
            
        Returns:
            模型输出
        """
        if not self.is_loaded:
            self.load()
            
        # 预处理
        processed_input = self.preprocess(input_data)
        
        # 转换为TensorFlow张量
        input_tensor = self.tf.convert_to_tensor(processed_input)
        
        # 执行推理
        if hasattr(self.model, 'signatures'):
            # 使用签名函数
            outputs = self.model_func(**{self.input_name: input_tensor})
            # 转换为NumPy数组
            outputs = {key: value.numpy() for key, value in outputs.items()}
        else:
            # 直接调用模型
            outputs = self.model_func(input_tensor)
            if isinstance(outputs, self.tf.Tensor):
                outputs = outputs.numpy()
            elif isinstance(outputs, dict):
                outputs = {key: value.numpy() if hasattr(value, 'numpy') else value 
                         for key, value in outputs.items()}
        
        # 后处理
        result = self.postprocess(outputs)
        
        return result
        
    def postprocess(self, model_output: Any) -> Any:
        """
        后处理模型输出
        
        Args:
            model_output: 模型原始输出
            
        Returns:
            后处理后的结果
        """
        # 默认实现直接返回模型输出
        # 具体的后处理逻辑应该由子类实现
        return model_output


class ModelFactory:
    """模型工厂类，负责创建和管理不同类型的模型"""
    
    # 模型缓存，避免重复加载
    _model_cache: Dict[str, BaseModel] = {}
    
    @classmethod
    def get_model(cls, 
                 model_type: Union[str, ModelType], 
                 model_path: str, 
                 device: str = "cpu", 
                 **kwargs) -> BaseModel:
        """
        获取模型实例，如果已存在则返回缓存的实例
        
        Args:
            model_type: 模型类型，可以是ModelType枚举或字符串
            model_path: 模型文件路径
            device: 设备类型，'cpu'或'cuda'/'gpu'
            **kwargs: 其他模型配置参数
            
        Returns:
            模型实例
            
        Raises:
            ModelLoadingError: 当模型加载失败时
            ValueError: 当参数无效时
        """
        # 创建模型缓存键
        cache_key = f"{model_type}_{model_path}_{device}"
        
        # 检查缓存
        if cache_key in cls._model_cache:
            logger.debug("使用缓存模型", model_type=model_type, model_path=model_path)
            return cls._model_cache[cache_key]
        
        # 确保model_type是字符串
        if isinstance(model_type, ModelType):
            model_type = model_type.value
            
        # 创建模型配置
        config = kwargs.copy()
        config["device"] = device
        config["use_cuda"] = device.lower() in ["cuda", "gpu"]
        
        # 根据文件扩展名确定模型后端
        ext = os.path.splitext(model_path)[1].lower()
        backend = kwargs.get("backend", None)
        
        if backend is None:
            # 自动检测后端
            if ext == ".onnx":
                backend = ModelBackend.ONNX
            elif ext in [".pb", ".pbtxt", ".tf", ".tflite", ""]:
                # 空扩展名可能是SavedModel目录
                backend = ModelBackend.TENSORFLOW
            else:
                # 默认使用OpenCV
                backend = ModelBackend.OPENCV
        
        # 创建模型实例
        try:
            if backend == ModelBackend.ONNX:
                try:
                    import onnxruntime
                    model = ONNXModel(model_path, config)
                except ImportError:
                    logger.warning("ONNX Runtime未安装，回退到OpenCV DNN")
                    model = OpenCVModel(model_path, config)
            elif backend == ModelBackend.TENSORFLOW:
                try:
                    import tensorflow
                    model = TensorFlowModel(model_path, config)
                except ImportError:
                    logger.warning("TensorFlow未安装，回退到OpenCV DNN")
                    model = OpenCVModel(model_path, config)
            else:
                model = OpenCVModel(model_path, config)
            
            # 加载模型
            model.load()
            
            # 缓存模型
            cls._model_cache[cache_key] = model
            
            return model
            
        except Exception as e:
            logger.error("创建模型失败", error=str(e), model_type=model_type, model_path=model_path)
            raise ModelLoadingError(f"创建模型失败: {str(e)}")
    
    @classmethod
    def clear_cache(cls, model_type: str = None, model_path: str = None):
        """
        清除模型缓存
        
        Args:
            model_type: 要清除的模型类型，如果为None则清除所有类型
            model_path: 要清除的模型路径，如果为None则清除所有路径
        """
        if model_type is None and model_path is None:
            # 清除所有缓存
            cls._model_cache.clear()
            logger.info("已清除所有模型缓存")
        else:
            # 清除特定模型的缓存
            keys_to_remove = []
            for key in cls._model_cache.keys():
                parts = key.split('_')
                if (model_type is None or parts[0] == model_type) and \
                   (model_path is None or model_path in key):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del cls._model_cache[key]
            
            logger.info("已清除特定模型缓存", 
                      model_type=model_type, 
                      model_path=model_path, 
                      count=len(keys_to_remove)) 