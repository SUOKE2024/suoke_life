#!/usr/bin/env python3
"""
模型优化器

提供深度学习模型的性能优化功能，包括模型量化、模型剪枝、批量推理和
硬件加速支持等，以提高望诊服务中视觉模型的推理效率。
"""

import os
import time
import logging
import threading
import numpy as np
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple, Union, Callable

import cv2
import torch
import onnx
import onnxruntime as ort
from torch.utils.data import DataLoader

# 配置日志
logger = logging.getLogger(__name__)

# 定义优化类型枚举
class OptimizationType(Enum):
    """模型优化类型枚举"""
    NONE = "none"                   # 不进行优化
    QUANTIZATION = "quantization"   # 量化优化
    PRUNING = "pruning"             # 剪枝优化
    DISTILLATION = "distillation"   # 知识蒸馏
    FUSION = "fusion"               # 算子融合


class ModelOptimizer:
    """
    模型优化器，用于优化深度学习模型的推理性能
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化模型优化器
        
        Args:
            config: 配置字典，包含优化参数
        """
        self.config = config
        self.device = self._get_device()
        self.optimization_enabled = config.get('optimization_enabled', True)
        self.optimization_type = OptimizationType(config.get('optimization_type', 'quantization'))
        self.batch_size = config.get('batch_size', 1)
        self.enable_gpu = config.get('enable_gpu', True)
        self.fp16_enabled = config.get('fp16_enabled', False)
        self.thread_pool_size = config.get('thread_pool_size', 4)
        
        # 初始化性能计数器
        self.inference_times: List[float] = []
        
        # 初始化推理会话选项
        self.session_options = ort.SessionOptions()
        self.session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        # 设置线程数
        self.session_options.intra_op_num_threads = self.thread_pool_size
        self.session_options.inter_op_num_threads = 1
        
        # 初始化批处理队列和锁
        self._batch_queue: List[Dict[str, Any]] = []
        self._batch_lock = threading.Lock()
        self._batch_timer: Optional[threading.Timer] = None
        
        logger.info(f"模型优化器初始化完成，设备: {self.device}, 优化类型: {self.optimization_type.value}")
    
    def _get_device(self) -> str:
        """
        确定可用的计算设备
        
        Returns:
            str: 计算设备名称，'cuda' 或 'cpu'
        """
        if torch.cuda.is_available() and self.config.get('enable_gpu', True):
            device = 'cuda'
            logger.info(f"使用GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = 'cpu'
            logger.info("GPU不可用，使用CPU")
        return device
    
    def optimize_model(self, model_path: str, input_shape: List[int]) -> str:
        """
        根据配置优化模型
        
        Args:
            model_path: 原始模型路径
            input_shape: 输入张量形状
            
        Returns:
            str: 优化后的模型路径
        """
        if not self.optimization_enabled:
            logger.info(f"模型优化已禁用，使用原始模型: {model_path}")
            return model_path
        
        # 获取模型文件扩展名和文件名
        _, ext = os.path.splitext(model_path)
        model_dir = os.path.dirname(model_path)
        model_name = os.path.basename(model_path).replace(ext, '')
        
        # 根据优化类型生成输出路径
        optimized_name = f"{model_name}_{self.optimization_type.value}"
        if self.fp16_enabled:
            optimized_name += "_fp16"
        optimized_path = os.path.join(model_dir, f"{optimized_name}{ext}")
        
        # 如果优化后的模型已存在，直接返回
        if os.path.exists(optimized_path):
            logger.info(f"使用现有优化模型: {optimized_path}")
            return optimized_path
        
        # 根据模型类型和优化类型执行优化
        try:
            logger.info(f"开始优化模型: {model_path} -> {optimized_path}")
            
            if ext.lower() == '.onnx':
                # ONNX模型优化
                if self.optimization_type == OptimizationType.QUANTIZATION:
                    optimized_path = self._quantize_onnx_model(model_path, optimized_path, input_shape)
                elif self.optimization_type == OptimizationType.FUSION:
                    optimized_path = self._fuse_onnx_model(model_path, optimized_path)
                else:
                    logger.warning(f"ONNX模型不支持{self.optimization_type.value}优化，使用原始模型")
                    return model_path
            
            elif ext.lower() == '.pt' or ext.lower() == '.pth':
                # PyTorch模型优化
                if self.optimization_type == OptimizationType.QUANTIZATION:
                    optimized_path = self._quantize_torch_model(model_path, optimized_path)
                elif self.optimization_type == OptimizationType.PRUNING:
                    optimized_path = self._prune_torch_model(model_path, optimized_path)
                else:
                    logger.warning(f"PyTorch模型不支持{self.optimization_type.value}优化，使用原始模型")
                    return model_path
            
            else:
                logger.warning(f"不支持的模型格式: {ext}，使用原始模型")
                return model_path
            
            logger.info(f"模型优化成功: {optimized_path}")
            return optimized_path
        
        except Exception as e:
            logger.error(f"模型优化失败: {str(e)}", exc_info=True)
            return model_path
    
    def _quantize_onnx_model(self, input_path: str, output_path: str, input_shape: List[int]) -> str:
        """
        量化ONNX模型
        
        Args:
            input_path: 输入模型路径
            output_path: 输出模型路径
            input_shape: 输入张量形状
            
        Returns:
            str: 量化后的模型路径
        """
        from onnxruntime.quantization import quantize_dynamic, QuantType
        
        try:
            # 动态量化模型
            quantize_dynamic(
                model_input=input_path,
                model_output=output_path,
                weight_type=QuantType.QInt8,
                optimize_model=True
            )
            logger.info(f"ONNX模型动态量化完成: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"ONNX模型量化失败: {str(e)}", exc_info=True)
            return input_path
    
    def _fuse_onnx_model(self, input_path: str, output_path: str) -> str:
        """
        融合ONNX模型中的运算符，减少计算图节点
        
        Args:
            input_path: 输入模型路径
            output_path: 输出模型路径
            
        Returns:
            str: 融合后的模型路径
        """
        try:
            import onnxoptimizer
            
            # 加载模型
            model = onnx.load(input_path)
            
            # 应用融合优化
            passes = ["fuse_bn_into_conv", "fuse_add_bias_into_conv"]
            optimized_model = onnxoptimizer.optimize(model, passes)
            
            # 保存优化后的模型
            onnx.save(optimized_model, output_path)
            logger.info(f"ONNX模型算子融合完成: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"ONNX模型融合失败: {str(e)}", exc_info=True)
            return input_path
    
    def _quantize_torch_model(self, input_path: str, output_path: str) -> str:
        """
        量化PyTorch模型
        
        Args:
            input_path: 输入模型路径
            output_path: 输出模型路径
            
        Returns:
            str: 量化后的模型路径
        """
        try:
            # 加载模型
            model = torch.load(input_path, map_location=self.device)
            
            # 应用量化
            quantized_model = torch.quantization.quantize_dynamic(
                model, {torch.nn.Linear, torch.nn.Conv2d}, dtype=torch.qint8
            )
            
            # 保存量化后的模型
            torch.save(quantized_model.state_dict(), output_path)
            logger.info(f"PyTorch模型量化完成: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"PyTorch模型量化失败: {str(e)}", exc_info=True)
            return input_path
    
    def _prune_torch_model(self, input_path: str, output_path: str) -> str:
        """
        剪枝PyTorch模型
        
        Args:
            input_path: 输入模型路径
            output_path: 输出模型路径
            
        Returns:
            str: 剪枝后的模型路径
        """
        try:
            # 此处实现模型剪枝逻辑
            # 注意：实际剪枝需要有训练数据和评估指标
            logger.warning("PyTorch模型剪枝功能尚未完全实现")
            return input_path
        except Exception as e:
            logger.error(f"PyTorch模型剪枝失败: {str(e)}", exc_info=True)
            return input_path
    
    def create_inference_session(self, model_path: str) -> ort.InferenceSession:
        """
        创建推理会话
        
        Args:
            model_path: 模型路径
            
        Returns:
            ort.InferenceSession: 推理会话对象
        """
        # 优化模型路径
        providers = []
        if self.device == 'cuda' and self.enable_gpu:
            providers.append('CUDAExecutionProvider')
        providers.append('CPUExecutionProvider')
        
        # 创建推理会话
        session = ort.InferenceSession(
            model_path, 
            sess_options=self.session_options,
            providers=providers
        )
        logger.info(f"创建推理会话: {model_path}, 提供程序: {providers}")
        
        return session
    
    def preprocess_image(self, image: np.ndarray, target_size: Tuple[int, int], 
                        normalize: bool = True, mean: List[float] = None, 
                        std: List[float] = None) -> np.ndarray:
        """
        预处理图像
        
        Args:
            image: 输入图像
            target_size: 目标尺寸 (height, width)
            normalize: 是否归一化
            mean: 归一化均值，默认为 [0.485, 0.456, 0.406]
            std: 归一化标准差，默认为 [0.229, 0.224, 0.225]
            
        Returns:
            np.ndarray: 预处理后的图像张量
        """
        if mean is None:
            mean = [0.485, 0.456, 0.406]
        if std is None:
            std = [0.229, 0.224, 0.225]
        
        # 调整图像大小
        resized = cv2.resize(image, (target_size[1], target_size[0]))
        
        # 转换为RGB（如果是BGR）
        if image.shape[2] == 3:
            resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # 转换为浮点数并归一化
        processed = resized.astype(np.float32) / 255.0
        
        # 应用均值和标准差归一化
        if normalize:
            mean = np.array(mean, dtype=np.float32)
            std = np.array(std, dtype=np.float32)
            processed = (processed - mean) / std
        
        # 转换为NCHW格式 (批次大小, 通道数, 高度, 宽度)
        processed = processed.transpose(2, 0, 1)[np.newaxis, ...]
        
        return processed
    
    def infer(self, session: ort.InferenceSession, input_data: np.ndarray, 
             input_name: Optional[str] = None) -> np.ndarray:
        """
        执行模型推理
        
        Args:
            session: 推理会话
            input_data: 输入数据
            input_name: 输入名称，如果为None，则使用会话的第一个输入名称
            
        Returns:
            np.ndarray: 推理结果
        """
        # 获取输入名称
        if input_name is None:
            input_name = session.get_inputs()[0].name
        
        # 记录开始时间
        start_time = time.time()
        
        # 执行推理
        outputs = session.run(None, {input_name: input_data})
        
        # 记录推理时间
        inference_time = time.time() - start_time
        self.inference_times.append(inference_time)
        
        # 如果有过多的记录，保留最近的100个
        if len(self.inference_times) > 100:
            self.inference_times = self.inference_times[-100:]
        
        # 记录平均推理时间
        avg_time = sum(self.inference_times) / len(self.inference_times)
        logger.debug(f"推理时间: {inference_time*1000:.2f}ms, 平均: {avg_time*1000:.2f}ms")
        
        return outputs[0]
    
    def batch_infer(self, session: ort.InferenceSession, input_data_list: List[np.ndarray], 
                   input_name: Optional[str] = None) -> List[np.ndarray]:
        """
        批量执行模型推理
        
        Args:
            session: 推理会话
            input_data_list: 输入数据列表
            input_name: 输入名称，如果为None，则使用会话的第一个输入名称
            
        Returns:
            List[np.ndarray]: 推理结果列表
        """
        if not input_data_list:
            return []
        
        # 获取输入名称
        if input_name is None:
            input_name = session.get_inputs()[0].name
        
        # 合并为批处理
        if isinstance(input_data_list[0], np.ndarray):
            # 确保所有输入具有相同的形状
            same_shape = all(data.shape == input_data_list[0].shape for data in input_data_list)
            if same_shape:
                batched_input = np.vstack(input_data_list)
            else:
                # 如果形状不同，则单独推理
                logger.warning("批处理输入形状不一致，将逐个推理")
                return [self.infer(session, data, input_name) for data in input_data_list]
        else:
            logger.warning("输入类型不是numpy数组，将逐个推理")
            return [self.infer(session, data, input_name) for data in input_data_list]
        
        # 记录开始时间
        start_time = time.time()
        
        # 执行批量推理
        outputs = session.run(None, {input_name: batched_input})
        
        # 记录推理时间
        inference_time = time.time() - start_time
        avg_time_per_sample = inference_time / len(input_data_list)
        self.inference_times.append(avg_time_per_sample)
        
        # 如果有过多的记录，保留最近的100个
        if len(self.inference_times) > 100:
            self.inference_times = self.inference_times[-100:]
        
        # 记录平均推理时间
        avg_time = sum(self.inference_times) / len(self.inference_times)
        logger.debug(f"批量推理 ({len(input_data_list)}个样本): {inference_time*1000:.2f}ms, "
                    f"每样本平均: {avg_time_per_sample*1000:.2f}ms, 总平均: {avg_time*1000:.2f}ms")
        
        # 分割批处理结果
        return np.split(outputs[0], len(input_data_list))
    
    def enqueue_for_batch(self, input_data: np.ndarray, callback: Callable[[np.ndarray], None], 
                         session: ort.InferenceSession, input_name: Optional[str] = None,
                         max_wait_time: float = 0.1) -> None:
        """
        将输入数据加入批处理队列
        
        Args:
            input_data: 输入数据
            callback: 回调函数，处理推理结果
            session: 推理会话
            input_name: 输入名称
            max_wait_time: 最大等待时间（秒）
        """
        with self._batch_lock:
            # 添加到队列
            self._batch_queue.append({
                'input_data': input_data,
                'callback': callback
            })
            
            # 如果队列长度达到批处理大小，立即处理
            if len(self._batch_queue) >= self.batch_size:
                self._process_batch(session, input_name)
            elif len(self._batch_queue) == 1:
                # 如果是队列中的第一个元素，启动计时器
                if self._batch_timer is not None:
                    self._batch_timer.cancel()
                
                self._batch_timer = threading.Timer(
                    max_wait_time, 
                    self._process_batch_timeout,
                    args=[session, input_name]
                )
                self._batch_timer.daemon = True
                self._batch_timer.start()
    
    def _process_batch(self, session: ort.InferenceSession, input_name: Optional[str] = None) -> None:
        """
        处理当前批次队列
        
        Args:
            session: 推理会话
            input_name: 输入名称
        """
        # 取出当前批次
        current_batch = self._batch_queue.copy()
        self._batch_queue.clear()
        
        # 取消计时器
        if self._batch_timer is not None:
            self._batch_timer.cancel()
            self._batch_timer = None
        
        # 释放锁后进行批处理，避免阻塞其他请求
        input_data_list = [item['input_data'] for item in current_batch]
        callbacks = [item['callback'] for item in current_batch]
        
        # 执行批量推理
        results = self.batch_infer(session, input_data_list, input_name)
        
        # 调用回调函数
        for i, result in enumerate(results):
            try:
                callbacks[i](result)
            except Exception as e:
                logger.error(f"回调函数执行失败: {str(e)}", exc_info=True)
    
    def _process_batch_timeout(self, session: ort.InferenceSession, input_name: Optional[str] = None) -> None:
        """
        批处理超时处理函数
        
        Args:
            session: 推理会话
            input_name: 输入名称
        """
        with self._batch_lock:
            if self._batch_queue:
                logger.debug(f"批处理超时，处理{len(self._batch_queue)}个样本")
                self._process_batch(session, input_name)
    
    def get_performance_stats(self) -> Dict[str, float]:
        """
        获取性能统计数据
        
        Returns:
            Dict[str, float]: 性能统计指标
        """
        if not self.inference_times:
            return {
                'avg_inference_time_ms': 0,
                'min_inference_time_ms': 0,
                'max_inference_time_ms': 0,
                'p90_inference_time_ms': 0,
                'p95_inference_time_ms': 0,
                'p99_inference_time_ms': 0,
                'samples_count': 0
            }
        
        times = sorted(self.inference_times)
        n = len(times)
        return {
            'avg_inference_time_ms': (sum(times) / n) * 1000,
            'min_inference_time_ms': min(times) * 1000,
            'max_inference_time_ms': max(times) * 1000,
            'p90_inference_time_ms': times[int(n * 0.9)] * 1000,
            'p95_inference_time_ms': times[int(n * 0.95)] * 1000,
            'p99_inference_time_ms': times[int(n * 0.99)] * 1000,
            'samples_count': n
        }


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 配置示例
    config = {
        'optimization_enabled': True,
        'optimization_type': 'quantization',
        'batch_size': 4,
        'enable_gpu': True,
        'fp16_enabled': False,
        'thread_pool_size': 4
    }
    
    # 创建优化器
    optimizer = ModelOptimizer(config)
    
    # 优化模型示例
    model_path = 'models/face_detection.onnx'
    input_shape = [1, 3, 416, 416]  # 批次大小，通道数，高度，宽度
    
    # 模拟优化过程，实际使用时需要真实模型文件
    print(f"优化模型: {model_path}")
    print(f"设备: {optimizer.device}")
    print(f"优化类型: {optimizer.optimization_type.value}")
    
    # 模拟批量推理过程
    def process_result(result):
        print(f"处理结果: {result.shape if isinstance(result, np.ndarray) else result}")
    
    # 创建随机输入数据
    input_data = np.random.rand(1, 3, 416, 416).astype(np.float32)
    
    print("模拟批量推理...")
    print(f"批量大小: {optimizer.batch_size}")
    
    # 在实际使用中，这里会创建真正的推理会话和执行推理
    # session = optimizer.create_inference_session(optimized_model_path)
    # 模拟推理结果
    mock_result = np.random.rand(1, 80, 80, 5).astype(np.float32)
    
    # 打印性能统计数据
    # 模拟一些推理时间
    for _ in range(20):
        optimizer.inference_times.append(np.random.uniform(0.01, 0.05))
    
    stats = optimizer.get_performance_stats()
    print("\n性能统计:")
    for k, v in stats.items():
        print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}") 