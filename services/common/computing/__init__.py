"""
__init__ - 索克生活项目模块
"""

        import numpy as np
    from .distributed.distributed_computing import (
    from .extensions.c_algorithms import (
    from .gpu.gpu_acceleration import (
    import numpy as np

#!/usr/bin/env python3
"""
索克生活 - 计算模块统一接口
整合分布式计算、C扩展、GPU加速等高性能计算功能
"""

# 分布式计算模块
try:
        DistributedComputeCluster,
        DistributedComputeNode,
        DistributedConfig,
        ComputeMode,
        NodeType,
        TaskStatus,
        create_distributed_cluster
    )
    DISTRIBUTED_AVAILABLE = True
except ImportError as e:
    print(f"分布式计算模块导入失败: {e}")
    DISTRIBUTED_AVAILABLE = False

# C扩展模块
try:
        CAlgorithmExtension,
        CExtensionConfig,
        AlgorithmType,
        get_c_extension,
        tcm_syndrome_analysis_c,
        health_data_normalize_c,
        nutrition_optimization_c,
        biomarker_processing_c,
        pattern_matching_c
    )
    C_EXTENSIONS_AVAILABLE = True
except ImportError as e:
    print(f"C扩展模块导入失败: {e}")
    C_EXTENSIONS_AVAILABLE = False

# GPU加速模块
try:
        GPUAccelerator,
        GPUConfig,
        GPUBackend,
        GPUDevice,
        get_gpu_accelerator,
        tcm_syndrome_analysis_gpu,
        health_data_normalize_gpu,
        nutrition_optimization_gpu
    )
    GPU_ACCELERATION_AVAILABLE = True
except ImportError as e:
    print(f"GPU加速模块导入失败: {e}")
    GPU_ACCELERATION_AVAILABLE = False

# 模块可用性状态
COMPUTING_MODULES_STATUS = {
    'distributed': DISTRIBUTED_AVAILABLE,
    'c_extensions': C_EXTENSIONS_AVAILABLE,
    'gpu_acceleration': GPU_ACCELERATION_AVAILABLE
}


def get_available_computing_modules():
    """获取可用的计算模块列表"""
    return [module for module, available in COMPUTING_MODULES_STATUS.items() if available]


def get_computing_capabilities():
    """获取计算能力信息"""
    capabilities = {
        'modules': COMPUTING_MODULES_STATUS,
        'features': []
    }
    
    if DISTRIBUTED_AVAILABLE:
        capabilities['features'].append('分布式计算')
    
    if C_EXTENSIONS_AVAILABLE:
        capabilities['features'].append('C扩展加速')
    
    if GPU_ACCELERATION_AVAILABLE:
        capabilities['features'].append('GPU加速')
    
    return capabilities


# 统一的高性能计算接口
class SuokeComputingEngine:
    """索克生活统一计算引擎"""
    
    def __init__(self):
        self.distributed_cluster = None
        self.c_extension = None
        self.gpu_accelerator = None
        
        # 初始化可用模块
        self._initialize_modules()
    
    def _initialize_modules(self):
        """初始化计算模块"""
        if C_EXTENSIONS_AVAILABLE:
            try:
                self.c_extension = get_c_extension()
            except Exception as e:
                print(f"C扩展初始化失败: {e}")
        
        if GPU_ACCELERATION_AVAILABLE:
            try:
                self.gpu_accelerator = get_gpu_accelerator()
            except Exception as e:
                print(f"GPU加速器初始化失败: {e}")
    
    async def initialize_distributed_cluster(self, num_workers=2):
        """初始化分布式集群"""
        if DISTRIBUTED_AVAILABLE:
            try:
                self.distributed_cluster = await create_distributed_cluster(num_workers)
                return True
            except Exception as e:
                print(f"分布式集群初始化失败: {e}")
                return False
        return False
    
    def tcm_syndrome_analysis(self, symptoms, weights, patterns, use_gpu=True, use_c=True):
        """中医证候分析 - 自动选择最优计算方式"""
        if use_gpu and GPU_ACCELERATION_AVAILABLE and self.gpu_accelerator:
            try:
                return tcm_syndrome_analysis_gpu(symptoms, weights, patterns)
            except Exception as e:
                print(f"GPU计算失败，回退到C扩展: {e}")
        
        if use_c and C_EXTENSIONS_AVAILABLE and self.c_extension:
            try:
                return tcm_syndrome_analysis_c(symptoms, weights, patterns)
            except Exception as e:
                print(f"C扩展计算失败，回退到Python: {e}")
        
        # Python回退实现
        weighted_symptoms = symptoms * weights
        scores = np.dot(patterns, weighted_symptoms)
        total = np.sum(scores)
        return scores / total if total > 0 else scores
    
    def health_data_normalize(self, data, use_gpu=True, use_c=True):
        """健康数据标准化 - 自动选择最优计算方式"""
        if use_gpu and GPU_ACCELERATION_AVAILABLE and self.gpu_accelerator:
            try:
                return health_data_normalize_gpu(data)
            except Exception as e:
                print(f"GPU计算失败，回退到C扩展: {e}")
        
        if use_c and C_EXTENSIONS_AVAILABLE and self.c_extension:
            try:
                return health_data_normalize_c(data)
            except Exception as e:
                print(f"C扩展计算失败，回退到Python: {e}")
        
        # Python回退实现
        mean = np.mean(data, axis=0)
        std = np.std(data, axis=0)
        std = np.where(std > 1e-8, std, 1.0)
        return (data - mean) / std
    
    def nutrition_optimization(self, user_profile, food_database, use_gpu=True, use_c=True):
        """营养优化 - 自动选择最优计算方式"""
        if use_gpu and GPU_ACCELERATION_AVAILABLE and self.gpu_accelerator:
            try:
                return nutrition_optimization_gpu(user_profile, food_database)
            except Exception as e:
                print(f"GPU计算失败，回退到C扩展: {e}")
        
        if use_c and C_EXTENSIONS_AVAILABLE and self.c_extension:
            try:
                return nutrition_optimization_c(user_profile, food_database)
            except Exception as e:
                print(f"C扩展计算失败，回退到Python: {e}")
        
        # Python回退实现
        user_norm = np.linalg.norm(user_profile)
        food_norms = np.linalg.norm(food_database, axis=1)
        
        if user_norm > 1e-8:
            dot_products = np.dot(food_database, user_profile)
            similarities = dot_products / (user_norm * food_norms + 1e-8)
        else:
            similarities = np.zeros(len(food_database))
        
        return similarities
    
    async def distributed_task_submit(self, task_type, function_name, input_data, **kwargs):
        """提交分布式任务"""
        if self.distributed_cluster:
            try:
                return await self.distributed_cluster.submit_task(
                    task_type, function_name, input_data, **kwargs
                )
            except Exception as e:
                print(f"分布式任务提交失败: {e}")
                return None
        else:
            print("分布式集群未初始化")
            return None
    
    async def distributed_task_result(self, task_id, timeout=300):
        """获取分布式任务结果"""
        if self.distributed_cluster:
            try:
                return await self.distributed_cluster.get_task_result(task_id, timeout)
            except Exception as e:
                print(f"获取分布式任务结果失败: {e}")
                return None
        else:
            print("分布式集群未初始化")
            return None
    
    def get_performance_info(self):
        """获取性能信息"""
        info = {
            'modules_available': COMPUTING_MODULES_STATUS,
            'capabilities': get_computing_capabilities()
        }
        
        if self.c_extension:
            info['c_extension'] = self.c_extension.get_performance_info()
        
        if self.gpu_accelerator:
            info['gpu_accelerator'] = self.gpu_accelerator.get_device_info()
        
        if self.distributed_cluster:
            info['distributed_cluster'] = {
                'master_node': self.distributed_cluster.master_node.node_id if self.distributed_cluster.master_node else None,
                'worker_count': len(self.distributed_cluster.worker_nodes)
            }
        
        return info
    
    async def cleanup(self):
        """清理资源"""
        if self.distributed_cluster:
            await self.distributed_cluster.stop()
        
        if self.gpu_accelerator:
            self.gpu_accelerator.cleanup()


# 全局计算引擎实例
_computing_engine = None

def get_computing_engine():
    """获取全局计算引擎实例"""
    global _computing_engine
    if _computing_engine is None:
        _computing_engine = SuokeComputingEngine()
    return _computing_engine


# 便捷函数
def smart_tcm_analysis(symptoms, weights, patterns):
    """智能中医证候分析"""
    engine = get_computing_engine()
    return engine.tcm_syndrome_analysis(symptoms, weights, patterns)


def smart_health_normalize(data):
    """智能健康数据标准化"""
    engine = get_computing_engine()
    return engine.health_data_normalize(data)


def smart_nutrition_optimize(user_profile, food_database):
    """智能营养优化"""
    engine = get_computing_engine()
    return engine.nutrition_optimization(user_profile, food_database)


__all__ = [
    # 模块状态
    'COMPUTING_MODULES_STATUS',
    'get_available_computing_modules',
    'get_computing_capabilities',
    
    # 统一计算引擎
    'SuokeComputingEngine',
    'get_computing_engine',
    
    # 便捷函数
    'smart_tcm_analysis',
    'smart_health_normalize',
    'smart_nutrition_optimize',
    
    # 分布式计算（如果可用）
    'DistributedComputeCluster',
    'DistributedComputeNode',
    'DistributedConfig',
    'ComputeMode',
    'NodeType',
    'TaskStatus',
    'create_distributed_cluster',
    
    # C扩展（如果可用）
    'CAlgorithmExtension',
    'CExtensionConfig',
    'AlgorithmType',
    'get_c_extension',
    'tcm_syndrome_analysis_c',
    'health_data_normalize_c',
    'nutrition_optimization_c',
    'biomarker_processing_c',
    'pattern_matching_c',
    
    # GPU加速（如果可用）
    'GPUAccelerator',
    'GPUConfig',
    'GPUBackend',
    'GPUDevice',
    'get_gpu_accelerator',
    'tcm_syndrome_analysis_gpu',
    'health_data_normalize_gpu',
    'nutrition_optimization_gpu'
]


if __name__ == "__main__":
    # 测试计算模块
    print("索克生活 - 计算模块测试")
    print("=" * 50)
    
    # 显示可用模块
    capabilities = get_computing_capabilities()
    print(f"可用模块: {capabilities['modules']}")
    print(f"可用功能: {capabilities['features']}")
    
    # 测试统一计算引擎
    engine = get_computing_engine()
    perf_info = engine.get_performance_info()
    print(f"性能信息: {perf_info}")
    
    # 测试智能计算函数
    
    # 测试数据
    symptoms = np.random.rand(20).astype(np.float32)
    weights = np.random.rand(20).astype(np.float32)
    patterns = np.random.rand(4, 20).astype(np.float32)
    health_data = np.random.rand(100, 30).astype(np.float32)
    
    # 智能中医分析
    tcm_scores = smart_tcm_analysis(symptoms, weights, patterns)
    print(f"中医证候评分: {tcm_scores}")
    
    # 智能健康数据标准化
    normalized_data = smart_health_normalize(health_data)
    print(f"标准化数据形状: {normalized_data.shape}")
    
    print("计算模块测试完成") 