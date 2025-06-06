"""
__init__ - 索克生活项目模块
"""

from .distributed_computing import (

#!/usr/bin/env python3
"""
索克生活 - 分布式计算模块
支持多节点计算、任务分发、结果聚合等功能
"""

    DistributedComputeCluster,
    DistributedComputeNode,
    DistributedConfig,
    ComputeMode,
    NodeType,
    TaskStatus,
    DistributedTask,
    NodeInfo,
    create_distributed_cluster
)

__all__ = [
    'DistributedComputeCluster',
    'DistributedComputeNode',
    'DistributedConfig',
    'ComputeMode',
    'NodeType',
    'TaskStatus',
    'DistributedTask',
    'NodeInfo',
    'create_distributed_cluster'
] 