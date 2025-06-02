#!/usr/bin/env python3
"""
索克生活 - GPU加速集成模块
支持CUDA、OpenCL等GPU计算加速
"""

import numpy as np
import time
import logging
import platform
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
import psutil

logger = logging.getLogger(__name__)


class GPUBackend(Enum):
    """GPU后端类型"""
    CUDA = "cuda"           # NVIDIA CUDA
    OPENCL = "opencl"       # OpenCL
    METAL = "metal"         # Apple Metal
    VULKAN = "vulkan"       # Vulkan
    CPU_FALLBACK = "cpu"    # CPU回退


class ComputeType(Enum):
    """计算类型"""
    MATRIX_MULTIPLY = "matrix_multiply"
    CONVOLUTION = "convolution"
    FFT = "fft"
    REDUCTION = "reduction"
    ELEMENT_WISE = "element_wise"
    CUSTOM_KERNEL = "custom_kernel"


@dataclass
class GPUDevice:
    """GPU设备信息"""
    device_id: int
    name: str
    backend: GPUBackend
    memory_total: int
    memory_free: int
    compute_capability: Optional[str] = None
    max_threads_per_block: Optional[int] = None
    max_blocks_per_grid: Optional[int] = None
    is_available: bool = True


@dataclass
class GPUConfig:
    """GPU配置"""
    preferred_backend: GPUBackend = GPUBackend.CUDA
    device_id: int = 0
    memory_pool_size: int = 1024 * 1024 * 1024  # 1GB
    enable_memory_pool: bool = True
    enable_profiling: bool = False
    fallback_to_cpu: bool = True
    optimization_level: int = 2


class GPUMemoryManager:
    """GPU内存管理器"""
    
    def __init__(self, backend: GPUBackend, device_id: int = 0):
        self.backend = backend
        self.device_id = device_id
        self.allocated_memory = {}
        self.memory_pool = {}
        self.total_allocated = 0
        self.peak_memory = 0
        
        # 初始化GPU库
        self._initialize_backend()
    
    def _initialize_backend(self):
        """初始化GPU后端"""
        if self.backend == GPUBackend.CUDA:
            try:
                import cupy as cp
                self.cp = cp
                self.device = cp.cuda.Device(self.device_id)
                self.device.use()
                logger.info(f"CUDA设备 {self.device_id} 初始化成功")
            except ImportError:
                logger.warning("CuPy未安装，无法使用CUDA")
                self.backend = GPUBackend.CPU_FALLBACK
        
        elif self.backend == GPUBackend.OPENCL:
            try:
                import pyopencl as cl
                self.cl = cl
                self.context = cl.create_some_context()
                self.queue = cl.CommandQueue(self.context)
                logger.info("OpenCL初始化成功")
            except ImportError:
                logger.warning("PyOpenCL未安装，无法使用OpenCL")
                self.backend = GPUBackend.CPU_FALLBACK
    
    def allocate(self, size: int, dtype=np.float32) -> Any:
        """分配GPU内存"""
        if self.backend == GPUBackend.CUDA:
            array = self.cp.zeros(size, dtype=dtype)
            self.allocated_memory[id(array)] = array.nbytes
            self.total_allocated += array.nbytes
            self.peak_memory = max(self.peak_memory, self.total_allocated)
            return array
        
        elif self.backend == GPUBackend.OPENCL:
            import pyopencl as cl
            buffer = cl.Buffer(
                self.context, 
                cl.mem_flags.READ_WRITE, 
                size * np.dtype(dtype).itemsize
            )
            self.allocated_memory[id(buffer)] = size * np.dtype(dtype).itemsize
            self.total_allocated += size * np.dtype(dtype).itemsize
            return buffer
        
        else:
            # CPU回退
            array = np.zeros(size, dtype=dtype)
            return array
    
    def deallocate(self, array: Any):
        """释放GPU内存"""
        array_id = id(array)
        if array_id in self.allocated_memory:
            self.total_allocated -= self.allocated_memory[array_id]
            del self.allocated_memory[array_id]
    
    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        if self.backend == GPUBackend.CUDA:
            meminfo = self.cp.cuda.runtime.memGetInfo()
            return {
                "backend": self.backend.value,
                "device_id": self.device_id,
                "total_memory": meminfo[1],
                "free_memory": meminfo[0],
                "allocated_by_manager": self.total_allocated,
                "peak_memory": self.peak_memory
            }
        else:
            return {
                "backend": self.backend.value,
                "allocated_by_manager": self.total_allocated,
                "peak_memory": self.peak_memory
            }


class GPUKernelManager:
    """GPU内核管理器"""
    
    def __init__(self, backend: GPUBackend, memory_manager: GPUMemoryManager):
        self.backend = backend
        self.memory_manager = memory_manager
        self.compiled_kernels = {}
        
        # 预定义内核
        self._load_builtin_kernels()
    
    def _load_builtin_kernels(self):
        """加载内置内核"""
        if self.backend == GPUBackend.CUDA:
            self._load_cuda_kernels()
        elif self.backend == GPUBackend.OPENCL:
            self._load_opencl_kernels()
    
    def _load_cuda_kernels(self):
        """加载CUDA内核"""
        # 中医证候分析内核
        tcm_kernel_code = '''
        extern "C" __global__
        void tcm_syndrome_analysis(
            const float* symptoms,
            const float* weights,
            const float* patterns,
            float* scores,
            int n_symptoms,
            int n_patterns
        ) {
            int pattern_id = blockIdx.x * blockDim.x + threadIdx.x;
            
            if (pattern_id < n_patterns) {
                float score = 0.0f;
                
                for (int i = 0; i < n_symptoms; i++) {
                    float weighted_symptom = symptoms[i] * weights[i];
                    score += weighted_symptom * patterns[pattern_id * n_symptoms + i];
                }
                
                scores[pattern_id] = score;
            }
        }
        '''
        
        # 健康数据标准化内核
        normalize_kernel_code = '''
        extern "C" __global__
        void health_data_normalize(
            const float* input,
            float* output,
            const float* means,
            const float* stds,
            int n_samples,
            int n_features
        ) {
            int idx = blockIdx.x * blockDim.x + threadIdx.x;
            int total_elements = n_samples * n_features;
            
            if (idx < total_elements) {
                int feature_idx = idx % n_features;
                float std_val = stds[feature_idx];
                
                if (std_val > 1e-8f) {
                    output[idx] = (input[idx] - means[feature_idx]) / std_val;
                } else {
                    output[idx] = 0.0f;
                }
            }
        }
        '''
        
        # 营养优化内核
        nutrition_kernel_code = '''
        extern "C" __global__
        void nutrition_optimization(
            const float* user_profile,
            const float* food_database,
            float* similarity_scores,
            int n_foods,
            int n_nutrients
        ) {
            int food_id = blockIdx.x * blockDim.x + threadIdx.x;
            
            if (food_id < n_foods) {
                float dot_product = 0.0f;
                float user_norm = 0.0f;
                float food_norm = 0.0f;
                
                for (int i = 0; i < n_nutrients; i++) {
                    float user_val = user_profile[i];
                    float food_val = food_database[food_id * n_nutrients + i];
                    
                    dot_product += user_val * food_val;
                    user_norm += user_val * user_val;
                    food_norm += food_val * food_val;
                }
                
                user_norm = sqrtf(user_norm);
                food_norm = sqrtf(food_norm);
                
                if (user_norm > 1e-8f && food_norm > 1e-8f) {
                    similarity_scores[food_id] = dot_product / (user_norm * food_norm);
                } else {
                    similarity_scores[food_id] = 0.0f;
                }
            }
        }
        '''
        
        try:
            import cupy as cp
            
            # 编译内核
            self.compiled_kernels['tcm_syndrome_analysis'] = cp.RawKernel(
                tcm_kernel_code, 'tcm_syndrome_analysis'
            )
            
            self.compiled_kernels['health_data_normalize'] = cp.RawKernel(
                normalize_kernel_code, 'health_data_normalize'
            )
            
            self.compiled_kernels['nutrition_optimization'] = cp.RawKernel(
                nutrition_kernel_code, 'nutrition_optimization'
            )
            
            logger.info("CUDA内核编译完成")
            
        except Exception as e:
            logger.error(f"CUDA内核编译失败: {e}")
    
    def _load_opencl_kernels(self):
        """加载OpenCL内核"""
        # OpenCL内核代码
        opencl_kernel_code = '''
        __kernel void tcm_syndrome_analysis(
            __global const float* symptoms,
            __global const float* weights,
            __global const float* patterns,
            __global float* scores,
            int n_symptoms,
            int n_patterns
        ) {
            int pattern_id = get_global_id(0);
            
            if (pattern_id < n_patterns) {
                float score = 0.0f;
                
                for (int i = 0; i < n_symptoms; i++) {
                    float weighted_symptom = symptoms[i] * weights[i];
                    score += weighted_symptom * patterns[pattern_id * n_symptoms + i];
                }
                
                scores[pattern_id] = score;
            }
        }
        
        __kernel void health_data_normalize(
            __global const float* input,
            __global float* output,
            __global const float* means,
            __global const float* stds,
            int n_samples,
            int n_features
        ) {
            int idx = get_global_id(0);
            int total_elements = n_samples * n_features;
            
            if (idx < total_elements) {
                int feature_idx = idx % n_features;
                float std_val = stds[feature_idx];
                
                if (std_val > 1e-8f) {
                    output[idx] = (input[idx] - means[feature_idx]) / std_val;
                } else {
                    output[idx] = 0.0f;
                }
            }
        }
        '''
        
        try:
            import pyopencl as cl
            
            program = cl.Program(self.memory_manager.context, opencl_kernel_code).build()
            
            self.compiled_kernels['tcm_syndrome_analysis'] = program.tcm_syndrome_analysis
            self.compiled_kernels['health_data_normalize'] = program.health_data_normalize
            
            logger.info("OpenCL内核编译完成")
            
        except Exception as e:
            logger.error(f"OpenCL内核编译失败: {e}")
    
    def execute_kernel(self, kernel_name: str, *args, **kwargs) -> Any:
        """执行GPU内核"""
        if kernel_name not in self.compiled_kernels:
            raise ValueError(f"未找到内核: {kernel_name}")
        
        kernel = self.compiled_kernels[kernel_name]
        
        if self.backend == GPUBackend.CUDA:
            return self._execute_cuda_kernel(kernel, *args, **kwargs)
        elif self.backend == GPUBackend.OPENCL:
            return self._execute_opencl_kernel(kernel, *args, **kwargs)
        else:
            raise RuntimeError(f"不支持的后端: {self.backend}")
    
    def _execute_cuda_kernel(self, kernel, *args, **kwargs):
        """执行CUDA内核"""
        grid_size = kwargs.get('grid_size', (1,))
        block_size = kwargs.get('block_size', (256,))
        
        kernel(grid_size, block_size, args)
        
        # 同步等待完成
        import cupy as cp
        cp.cuda.Stream.null.synchronize()
    
    def _execute_opencl_kernel(self, kernel, *args, **kwargs):
        """执行OpenCL内核"""
        global_size = kwargs.get('global_size', (1,))
        local_size = kwargs.get('local_size', None)
        
        kernel(self.memory_manager.queue, global_size, local_size, *args)
        self.memory_manager.queue.finish()


class GPUAccelerator:
    """GPU加速器主类"""
    
    def __init__(self, config: Optional[GPUConfig] = None):
        self.config = config or GPUConfig()
        self.available_devices = []
        self.current_device = None
        self.memory_manager = None
        self.kernel_manager = None
        self.performance_stats = {
            'total_operations': 0,
            'total_gpu_time': 0.0,
            'total_cpu_time': 0.0,
            'gpu_speedup': 1.0
        }
        
        # 检测可用设备
        self._detect_devices()
        
        # 初始化GPU
        self._initialize_gpu()
    
    def _detect_devices(self):
        """检测可用的GPU设备"""
        # 检测CUDA设备
        try:
            import cupy as cp
            device_count = cp.cuda.runtime.getDeviceCount()
            
            for i in range(device_count):
                with cp.cuda.Device(i):
                    props = cp.cuda.runtime.getDeviceProperties(i)
                    meminfo = cp.cuda.runtime.memGetInfo()
                    
                    device = GPUDevice(
                        device_id=i,
                        name=props['name'].decode('utf-8'),
                        backend=GPUBackend.CUDA,
                        memory_total=meminfo[1],
                        memory_free=meminfo[0],
                        compute_capability=f"{props['major']}.{props['minor']}",
                        max_threads_per_block=props['maxThreadsPerBlock'],
                        max_blocks_per_grid=props['maxGridSize'][0]
                    )
                    
                    self.available_devices.append(device)
                    
            logger.info(f"检测到 {device_count} 个CUDA设备")
            
        except ImportError:
            logger.info("未检测到CUDA支持")
        
        # 检测OpenCL设备
        try:
            import pyopencl as cl
            
            platforms = cl.get_platforms()
            device_id = 0
            
            for platform in platforms:
                devices = platform.get_devices()
                
                for device in devices:
                    gpu_device = GPUDevice(
                        device_id=device_id,
                        name=device.name,
                        backend=GPUBackend.OPENCL,
                        memory_total=device.global_mem_size,
                        memory_free=device.global_mem_size,  # OpenCL无法直接获取空闲内存
                        max_threads_per_block=device.max_work_group_size
                    )
                    
                    self.available_devices.append(gpu_device)
                    device_id += 1
                    
            logger.info(f"检测到 {device_id} 个OpenCL设备")
            
        except ImportError:
            logger.info("未检测到OpenCL支持")
        
        # 如果没有GPU设备，添加CPU回退
        if not self.available_devices:
            cpu_device = GPUDevice(
                device_id=0,
                name="CPU Fallback",
                backend=GPUBackend.CPU_FALLBACK,
                memory_total=psutil.virtual_memory().total,
                memory_free=psutil.virtual_memory().available
            )
            self.available_devices.append(cpu_device)
    
    def _initialize_gpu(self):
        """初始化GPU"""
        # 选择设备
        preferred_devices = [
            d for d in self.available_devices 
            if d.backend == self.config.preferred_backend
        ]
        
        if preferred_devices:
            self.current_device = preferred_devices[self.config.device_id % len(preferred_devices)]
        else:
            # 回退到第一个可用设备
            self.current_device = self.available_devices[0] if self.available_devices else None
        
        if not self.current_device:
            raise RuntimeError("没有可用的计算设备")
        
        # 初始化内存管理器
        self.memory_manager = GPUMemoryManager(
            self.current_device.backend,
            self.current_device.device_id
        )
        
        # 初始化内核管理器
        self.kernel_manager = GPUKernelManager(
            self.current_device.backend,
            self.memory_manager
        )
        
        logger.info(f"使用设备: {self.current_device.name} ({self.current_device.backend.value})")
    
    def tcm_syndrome_analysis_gpu(self, symptoms: np.ndarray, weights: np.ndarray, 
                                 patterns: np.ndarray) -> np.ndarray:
        """GPU加速的中医证候分析"""
        start_time = time.time()
        
        try:
            if self.current_device.backend == GPUBackend.CUDA:
                return self._tcm_syndrome_analysis_cuda(symptoms, weights, patterns)
            elif self.current_device.backend == GPUBackend.OPENCL:
                return self._tcm_syndrome_analysis_opencl(symptoms, weights, patterns)
            else:
                return self._tcm_syndrome_analysis_cpu(symptoms, weights, patterns)
        
        finally:
            gpu_time = time.time() - start_time
            self.performance_stats['total_operations'] += 1
            self.performance_stats['total_gpu_time'] += gpu_time
    
    def _tcm_syndrome_analysis_cuda(self, symptoms: np.ndarray, weights: np.ndarray, 
                                   patterns: np.ndarray) -> np.ndarray:
        """CUDA版本的中医证候分析"""
        import cupy as cp
        
        # 转换到GPU
        symptoms_gpu = cp.asarray(symptoms, dtype=cp.float32)
        weights_gpu = cp.asarray(weights, dtype=cp.float32)
        patterns_gpu = cp.asarray(patterns, dtype=cp.float32)
        
        n_symptoms = len(symptoms)
        n_patterns = patterns.shape[0]
        
        # 分配输出内存
        scores_gpu = cp.zeros(n_patterns, dtype=cp.float32)
        
        # 执行内核
        block_size = (256,)
        grid_size = ((n_patterns + block_size[0] - 1) // block_size[0],)
        
        self.kernel_manager.execute_kernel(
            'tcm_syndrome_analysis',
            symptoms_gpu, weights_gpu, patterns_gpu, scores_gpu,
            cp.int32(n_symptoms), cp.int32(n_patterns),
            grid_size=grid_size, block_size=block_size
        )
        
        # 归一化
        total = cp.sum(scores_gpu)
        if total > 0:
            scores_gpu /= total
        
        # 转换回CPU
        return cp.asnumpy(scores_gpu)
    
    def _tcm_syndrome_analysis_opencl(self, symptoms: np.ndarray, weights: np.ndarray, 
                                     patterns: np.ndarray) -> np.ndarray:
        """OpenCL版本的中医证候分析"""
        import pyopencl as cl
        
        # 创建缓冲区
        symptoms_buf = cl.Buffer(
            self.memory_manager.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=symptoms.astype(np.float32)
        )
        
        weights_buf = cl.Buffer(
            self.memory_manager.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=weights.astype(np.float32)
        )
        
        patterns_buf = cl.Buffer(
            self.memory_manager.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=patterns.astype(np.float32)
        )
        
        n_patterns = patterns.shape[0]
        scores = np.zeros(n_patterns, dtype=np.float32)
        scores_buf = cl.Buffer(
            self.memory_manager.context,
            cl.mem_flags.WRITE_ONLY,
            scores.nbytes
        )
        
        # 执行内核
        self.kernel_manager.execute_kernel(
            'tcm_syndrome_analysis',
            symptoms_buf, weights_buf, patterns_buf, scores_buf,
            np.int32(len(symptoms)), np.int32(n_patterns),
            global_size=(n_patterns,)
        )
        
        # 读取结果
        cl.enqueue_copy(self.memory_manager.queue, scores, scores_buf)
        
        # 归一化
        total = np.sum(scores)
        if total > 0:
            scores /= total
        
        return scores
    
    def _tcm_syndrome_analysis_cpu(self, symptoms: np.ndarray, weights: np.ndarray, 
                                  patterns: np.ndarray) -> np.ndarray:
        """CPU回退版本的中医证候分析"""
        weighted_symptoms = symptoms * weights
        scores = np.dot(patterns, weighted_symptoms)
        total = np.sum(scores)
        return scores / total if total > 0 else scores
    
    def health_data_normalize_gpu(self, data: np.ndarray) -> np.ndarray:
        """GPU加速的健康数据标准化"""
        start_time = time.time()
        
        try:
            if self.current_device.backend == GPUBackend.CUDA:
                return self._health_data_normalize_cuda(data)
            elif self.current_device.backend == GPUBackend.OPENCL:
                return self._health_data_normalize_opencl(data)
            else:
                return self._health_data_normalize_cpu(data)
        
        finally:
            gpu_time = time.time() - start_time
            self.performance_stats['total_operations'] += 1
            self.performance_stats['total_gpu_time'] += gpu_time
    
    def _health_data_normalize_cuda(self, data: np.ndarray) -> np.ndarray:
        """CUDA版本的健康数据标准化"""
        import cupy as cp
        
        # 转换到GPU
        data_gpu = cp.asarray(data, dtype=cp.float32)
        n_samples, n_features = data.shape
        
        # 计算均值和标准差
        means_gpu = cp.mean(data_gpu, axis=0)
        stds_gpu = cp.std(data_gpu, axis=0)
        
        # 分配输出内存
        output_gpu = cp.zeros_like(data_gpu)
        
        # 执行标准化内核
        total_elements = n_samples * n_features
        block_size = (256,)
        grid_size = ((total_elements + block_size[0] - 1) // block_size[0],)
        
        self.kernel_manager.execute_kernel(
            'health_data_normalize',
            data_gpu, output_gpu, means_gpu, stds_gpu,
            cp.int32(n_samples), cp.int32(n_features),
            grid_size=grid_size, block_size=block_size
        )
        
        return cp.asnumpy(output_gpu)
    
    def _health_data_normalize_opencl(self, data: np.ndarray) -> np.ndarray:
        """OpenCL版本的健康数据标准化"""
        # 计算均值和标准差
        means = np.mean(data, axis=0).astype(np.float32)
        stds = np.std(data, axis=0).astype(np.float32)
        
        # 创建缓冲区
        import pyopencl as cl
        
        data_buf = cl.Buffer(
            self.memory_manager.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=data.astype(np.float32)
        )
        
        means_buf = cl.Buffer(
            self.memory_manager.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=means
        )
        
        stds_buf = cl.Buffer(
            self.memory_manager.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=stds
        )
        
        output = np.zeros_like(data, dtype=np.float32)
        output_buf = cl.Buffer(
            self.memory_manager.context,
            cl.mem_flags.WRITE_ONLY,
            output.nbytes
        )
        
        # 执行内核
        total_elements = data.size
        self.kernel_manager.execute_kernel(
            'health_data_normalize',
            data_buf, output_buf, means_buf, stds_buf,
            np.int32(data.shape[0]), np.int32(data.shape[1]),
            global_size=(total_elements,)
        )
        
        # 读取结果
        cl.enqueue_copy(self.memory_manager.queue, output, output_buf)
        
        return output
    
    def _health_data_normalize_cpu(self, data: np.ndarray) -> np.ndarray:
        """CPU回退版本的健康数据标准化"""
        mean = np.mean(data, axis=0)
        std = np.std(data, axis=0)
        std = np.where(std > 1e-8, std, 1.0)
        return (data - mean) / std
    
    def nutrition_optimization_gpu(self, user_profile: np.ndarray, 
                                  food_database: np.ndarray) -> np.ndarray:
        """GPU加速的营养优化"""
        start_time = time.time()
        
        try:
            if self.current_device.backend == GPUBackend.CUDA:
                return self._nutrition_optimization_cuda(user_profile, food_database)
            else:
                return self._nutrition_optimization_cpu(user_profile, food_database)
        
        finally:
            gpu_time = time.time() - start_time
            self.performance_stats['total_operations'] += 1
            self.performance_stats['total_gpu_time'] += gpu_time
    
    def _nutrition_optimization_cuda(self, user_profile: np.ndarray, 
                                    food_database: np.ndarray) -> np.ndarray:
        """CUDA版本的营养优化"""
        import cupy as cp
        
        # 转换到GPU
        user_profile_gpu = cp.asarray(user_profile, dtype=cp.float32)
        food_database_gpu = cp.asarray(food_database, dtype=cp.float32)
        
        n_foods, n_nutrients = food_database.shape
        
        # 分配输出内存
        scores_gpu = cp.zeros(n_foods, dtype=cp.float32)
        
        # 执行内核
        block_size = (256,)
        grid_size = ((n_foods + block_size[0] - 1) // block_size[0],)
        
        self.kernel_manager.execute_kernel(
            'nutrition_optimization',
            user_profile_gpu, food_database_gpu, scores_gpu,
            cp.int32(n_foods), cp.int32(n_nutrients),
            grid_size=grid_size, block_size=block_size
        )
        
        return cp.asnumpy(scores_gpu)
    
    def _nutrition_optimization_cpu(self, user_profile: np.ndarray, 
                                   food_database: np.ndarray) -> np.ndarray:
        """CPU回退版本的营养优化"""
        user_norm = np.linalg.norm(user_profile)
        food_norms = np.linalg.norm(food_database, axis=1)
        
        if user_norm > 1e-8:
            dot_products = np.dot(food_database, user_profile)
            similarities = dot_products / (user_norm * food_norms + 1e-8)
        else:
            similarities = np.zeros(len(food_database))
        
        return similarities
    
    def benchmark_performance(self, data_sizes: List[int] = None) -> Dict[str, Any]:
        """性能基准测试"""
        if data_sizes is None:
            data_sizes = [100, 500, 1000, 2000]
        
        results = {}
        
        for size in data_sizes:
            # 生成测试数据
            symptoms = np.random.rand(20).astype(np.float32)
            weights = np.random.rand(20).astype(np.float32)
            patterns = np.random.rand(4, 20).astype(np.float32)
            health_data = np.random.rand(size, 50).astype(np.float32)
            
            # GPU测试
            start_time = time.time()
            for _ in range(10):
                self.tcm_syndrome_analysis_gpu(symptoms, weights, patterns)
                self.health_data_normalize_gpu(health_data)
            gpu_time = time.time() - start_time
            
            # CPU测试
            start_time = time.time()
            for _ in range(10):
                self._tcm_syndrome_analysis_cpu(symptoms, weights, patterns)
                self._health_data_normalize_cpu(health_data)
            cpu_time = time.time() - start_time
            
            speedup = cpu_time / gpu_time if gpu_time > 0 else 1.0
            
            results[f"size_{size}"] = {
                "gpu_time": gpu_time,
                "cpu_time": cpu_time,
                "speedup": speedup,
                "backend": self.current_device.backend.value
            }
        
        return results
    
    def get_device_info(self) -> Dict[str, Any]:
        """获取设备信息"""
        return {
            "current_device": {
                "name": self.current_device.name,
                "backend": self.current_device.backend.value,
                "device_id": self.current_device.device_id,
                "memory_total": self.current_device.memory_total,
                "memory_free": self.current_device.memory_free
            },
            "available_devices": [
                {
                    "name": device.name,
                    "backend": device.backend.value,
                    "device_id": device.device_id
                }
                for device in self.available_devices
            ],
            "memory_info": self.memory_manager.get_memory_info(),
            "performance_stats": self.performance_stats.copy()
        }
    
    def cleanup(self):
        """清理资源"""
        if self.memory_manager:
            # 清理分配的内存
            for array_id in list(self.memory_manager.allocated_memory.keys()):
                self.memory_manager.deallocate(array_id)
        
        logger.info("GPU资源已清理")


# 全局GPU加速器实例
_gpu_accelerator = None

def get_gpu_accelerator(config: Optional[GPUConfig] = None) -> GPUAccelerator:
    """获取GPU加速器实例（单例模式）"""
    global _gpu_accelerator
    if _gpu_accelerator is None:
        _gpu_accelerator = GPUAccelerator(config)
    return _gpu_accelerator


# 便捷函数接口
def tcm_syndrome_analysis_gpu(symptoms: np.ndarray, weights: np.ndarray, 
                             patterns: np.ndarray) -> np.ndarray:
    """GPU加速的中医证候分析"""
    accelerator = get_gpu_accelerator()
    return accelerator.tcm_syndrome_analysis_gpu(symptoms, weights, patterns)


def health_data_normalize_gpu(data: np.ndarray) -> np.ndarray:
    """GPU加速的健康数据标准化"""
    accelerator = get_gpu_accelerator()
    return accelerator.health_data_normalize_gpu(data)


def nutrition_optimization_gpu(user_profile: np.ndarray, 
                              food_database: np.ndarray) -> np.ndarray:
    """GPU加速的营养优化"""
    accelerator = get_gpu_accelerator()
    return accelerator.nutrition_optimization_gpu(user_profile, food_database)


if __name__ == "__main__":
    # 测试GPU加速
    print("索克生活 - GPU加速测试")
    
    try:
        # 创建GPU加速器
        accelerator = get_gpu_accelerator()
        
        # 获取设备信息
        device_info = accelerator.get_device_info()
        print(f"当前设备: {device_info['current_device']['name']}")
        print(f"后端: {device_info['current_device']['backend']}")
        
        # 测试中医证候分析
        symptoms = np.random.rand(20).astype(np.float32)
        weights = np.random.rand(20).astype(np.float32)
        patterns = np.random.rand(4, 20).astype(np.float32)
        
        scores = tcm_syndrome_analysis_gpu(symptoms, weights, patterns)
        print(f"证候评分: {scores}")
        
        # 测试健康数据标准化
        health_data = np.random.rand(1000, 50).astype(np.float32)
        normalized = health_data_normalize_gpu(health_data)
        print(f"标准化数据形状: {normalized.shape}")
        
        # 性能基准测试
        benchmark_results = accelerator.benchmark_performance([500, 1000])
        print(f"性能基准测试: {benchmark_results}")
        
        # 清理资源
        accelerator.cleanup()
        
    except Exception as e:
        print(f"GPU测试失败: {e}")
        print("将使用CPU回退模式") 