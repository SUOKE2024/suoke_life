"""
计算优化模块

提供高性能计算功能，包括：
- GPU加速计算
- 分布式计算
- C扩展算法
- 数值计算优化
"""

from typing import Dict, List, Any, Optional, Union

try:
    import numpy as np
    
    from .gpu.gpu_acceleration import GPUAccelerator, CUDAManager
    from .distributed.distributed_computing import DistributedComputer, TaskScheduler
    from .extensions.c_algorithms import CAlgorithms, OptimizedMath
    
    __all__ = [
        "GPUAccelerator",
        "CUDAManager",
        "DistributedComputer", 
        "TaskScheduler",
        "CAlgorithms",
        "OptimizedMath",
    ]
    
except ImportError as e:
    import logging
    logging.warning(f"计算模块导入失败: {e}")
    __all__ = []


def main() -> None:
    """主函数 - 用于测试计算功能"""
    try:
        print("计算模块测试开始...")
        
        # 测试GPU加速（如果可用）
        try:
            gpu_accelerator = GPUAccelerator()
            print("GPU加速器初始化成功")
        except Exception as e:
            print(f"GPU加速器不可用: {e}")
        
        # 测试分布式计算
        try:
            distributed_computer = DistributedComputer()
            print("分布式计算器初始化成功")
        except Exception as e:
            print(f"分布式计算器不可用: {e}")
        
        print("计算模块测试完成")
        
    except Exception as e:
        print(f"计算模块测试失败: {e}")


if __name__=="__main__":
    main()
