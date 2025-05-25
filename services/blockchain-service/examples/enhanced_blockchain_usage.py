#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版区块链服务使用示例

该示例展示了如何使用增强版区块链服务的各种功能，包括：
- 基础区块链操作
- 优化配置管理
- 性能监控
- 智能批量处理
- 自动优化
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Any

# 导入必要的模块
from internal.model.config import AppConfig
from internal.model.entities import DataType, TaskPriority
from internal.service.enhanced_blockchain_service import EnhancedBlockchainService
from internal.service.smart_batch_processor import BatchStrategy, RetryStrategy


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BlockchainServiceDemo:
    """区块链服务演示类"""

    def __init__(self):
        """初始化演示"""
        # 创建配置对象
        self.config = AppConfig()
        
        # 创建增强版区块链服务
        self.blockchain_service = EnhancedBlockchainService(self.config)
        
        # 演示数据
        self.demo_users = ["user_001", "user_002", "user_003"]
        self.demo_data_types = [DataType.VITAL_SIGNS, DataType.LAB_RESULTS, DataType.MEDICAL_IMAGES]
    
    async def run_demo(self):
        """运行完整演示"""
        logger.info("开始增强版区块链服务演示")
        
        try:
            # 1. 启动服务
            await self.demo_service_startup()
            
            # 2. 基础功能演示
            await self.demo_basic_operations()
            
            # 3. 优化功能演示
            await self.demo_optimization_features()
            
            # 4. 批量处理演示
            await self.demo_batch_processing()
            
            # 5. 监控和告警演示
            await self.demo_monitoring_features()
            
            # 6. 性能调优演示
            await self.demo_performance_tuning()
            
            # 7. 服务管理演示
            await self.demo_service_management()
            
        except Exception as e:
            logger.error(f"演示过程中发生错误: {str(e)}")
        
        finally:
            # 停止服务
            await self.blockchain_service.stop_service()
            logger.info("增强版区块链服务演示完成")
    
    async def demo_service_startup(self):
        """演示服务启动"""
        logger.info("=== 服务启动演示 ===")
        
        # 使用标准优化配置启动服务
        await self.blockchain_service.start_service(
            optimization_profile="standard",
            enable_auto_optimization=True
        )
        
        # 获取服务状态
        status = await self.blockchain_service.get_service_status()
        logger.info(f"服务状态: {status}")
        
        # 等待服务完全启动
        await asyncio.sleep(2)
    
    async def demo_basic_operations(self):
        """演示基础操作"""
        logger.info("=== 基础操作演示 ===")
        
        # 存储健康数据
        user_id = self.demo_users[0]
        data_type = DataType.VITAL_SIGNS
        data_hash = b"sample_health_data_hash_001"
        metadata = {
            "device_id": "device_001",
            "timestamp": datetime.now().isoformat(),
            "data_size": "1024"
        }
        
        logger.info(f"存储健康数据: 用户={user_id}, 类型={data_type.value}")
        
        result = await self.blockchain_service.store_health_data(
            user_id=user_id,
            data_type=data_type,
            data_hash=data_hash,
            metadata=metadata
        )
        
        if result[0]:
            logger.info(f"存储成功: {result[1]}")
            transaction_id = result[2].transaction_id
            
            # 验证数据
            logger.info(f"验证健康数据: 交易ID={transaction_id}")
            verify_result = await self.blockchain_service.verify_health_data(
                transaction_id=transaction_id,
                data_hash=data_hash
            )
            
            if verify_result[0]:
                logger.info(f"验证成功: {verify_result[1]}")
            else:
                logger.error(f"验证失败: {verify_result[1]}")
        else:
            logger.error(f"存储失败: {result[1]}")
    
    async def demo_optimization_features(self):
        """演示优化功能"""
        logger.info("=== 优化功能演示 ===")
        
        # 获取优化配置文件
        profiles = self.blockchain_service.optimization_service.get_optimization_profiles()
        logger.info(f"可用优化配置: {list(profiles.keys())}")
        
        # 使用增强版存储方法
        user_id = self.demo_users[1]
        data_type = DataType.LAB_RESULTS
        data_hash = b"enhanced_health_data_hash_002"
        
        logger.info("使用增强版存储方法")
        
        result = await self.blockchain_service.store_health_data_enhanced(
            user_id=user_id,
            data_type=data_type,
            data_hash=data_hash,
            use_batch=False,
            priority=TaskPriority.HIGH
        )
        
        if result[0]:
            logger.info(f"增强版存储成功: {result[1]}")
        
        # 获取性能摘要
        performance_summary = await self.blockchain_service.get_performance_summary()
        logger.info(f"性能摘要: {performance_summary}")
    
    async def demo_batch_processing(self):
        """演示批量处理"""
        logger.info("=== 批量处理演示 ===")
        
        # 准备批量数据
        batch_data = []
        for i, user_id in enumerate(self.demo_users):
            for j, data_type in enumerate(self.demo_data_types):
                batch_data.append({
                    "user_id": user_id,
                    "data_type": data_type.value,
                    "data_hash": f"batch_data_hash_{i}_{j}".encode().hex(),
                    "metadata": {
                        "batch_id": f"batch_{i}_{j}",
                        "timestamp": datetime.now().isoformat()
                    },
                    "priority": 2
                })
        
        logger.info(f"准备批量处理 {len(batch_data)} 个项目")
        
        # 使用智能批量处理
        batch_result = await self.blockchain_service.batch_store_health_data_smart(
            batch_data=batch_data,
            strategy=BatchStrategy.ADAPTIVE,
            retry_strategy=RetryStrategy.ADAPTIVE
        )
        
        logger.info(f"批量处理结果: {batch_result}")
        
        # 使用基础批量处理作为对比
        logger.info("使用基础批量处理")
        basic_batch_result = await self.blockchain_service.batch_store_health_data(
            batch_data=batch_data[:3]  # 只处理前3个项目
        )
        
        logger.info(f"基础批量处理结果: {basic_batch_result}")
    
    async def demo_monitoring_features(self):
        """演示监控功能"""
        logger.info("=== 监控功能演示 ===")
        
        # 获取全面状态
        comprehensive_status = await self.blockchain_service.get_comprehensive_status()
        logger.info(f"全面状态信息:")
        logger.info(f"  服务状态: {comprehensive_status['service']}")
        logger.info(f"  性能统计: {comprehensive_status['performance']}")
        
        if comprehensive_status.get('system_health'):
            health = comprehensive_status['system_health']
            logger.info(f"  系统健康: 总分={health['overall_score']:.2f}")
            logger.info(f"  活跃告警: {health['active_alerts']}")
            logger.info(f"  严重告警: {health['critical_alerts']}")
        
        # 获取组件状态
        components = comprehensive_status.get('components', {})
        for component_name, component_status in components.items():
            logger.info(f"  {component_name}: {type(component_status).__name__}")
    
    async def demo_performance_tuning(self):
        """演示性能调优"""
        logger.info("=== 性能调优演示 ===")
        
        # 执行手动优化
        logger.info("执行手动优化")
        optimization_result = await self.blockchain_service.manual_optimization()
        logger.info(f"手动优化结果: {optimization_result}")
        
        # 执行全面优化
        logger.info("执行全面优化")
        comprehensive_optimization = await self.blockchain_service.comprehensive_optimization()
        logger.info(f"全面优化结果: {comprehensive_optimization}")
        
        # 性能优化
        logger.info("执行性能优化")
        performance_optimization = await self.blockchain_service.optimize_performance()
        logger.info(f"性能优化结果: {performance_optimization}")
    
    async def demo_service_management(self):
        """演示服务管理"""
        logger.info("=== 服务管理演示 ===")
        
        # 切换优化配置文件
        logger.info("切换到高级优化配置")
        await self.blockchain_service.switch_optimization_profile("advanced")
        
        # 等待配置生效
        await asyncio.sleep(2)
        
        # 获取更新后的状态
        status = await self.blockchain_service.get_service_status()
        logger.info(f"切换后的服务状态: {status}")
        
        # 清理缓存
        logger.info("清理缓存")
        cache_result = await self.blockchain_service.clear_cache()
        logger.info(f"缓存清理结果: {cache_result}")
        
        # 切换回标准配置
        logger.info("切换回标准优化配置")
        await self.blockchain_service.switch_optimization_profile("standard")


class PerformanceTestDemo:
    """性能测试演示"""

    def __init__(self, blockchain_service: EnhancedBlockchainService):
        self.blockchain_service = blockchain_service
    
    async def run_performance_test(self, num_operations: int = 100):
        """运行性能测试"""
        logger.info(f"=== 性能测试演示 ({num_operations} 次操作) ===")
        
        start_time = time.time()
        successful_operations = 0
        failed_operations = 0
        
        # 并发执行操作
        tasks = []
        for i in range(num_operations):
            task = self._single_operation(f"perf_user_{i % 10}", i)
            tasks.append(task)
        
        # 等待所有操作完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        for result in results:
            if isinstance(result, Exception):
                failed_operations += 1
            elif result and result[0]:
                successful_operations += 1
            else:
                failed_operations += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 输出性能统计
        logger.info(f"性能测试结果:")
        logger.info(f"  总操作数: {num_operations}")
        logger.info(f"  成功操作: {successful_operations}")
        logger.info(f"  失败操作: {failed_operations}")
        logger.info(f"  总耗时: {total_time:.2f} 秒")
        logger.info(f"  平均耗时: {total_time / num_operations:.3f} 秒/操作")
        logger.info(f"  吞吐量: {num_operations / total_time:.2f} 操作/秒")
        
        # 获取服务性能统计
        comprehensive_status = await self.blockchain_service.get_comprehensive_status()
        performance_stats = comprehensive_status.get('performance', {})
        logger.info(f"  服务统计: {performance_stats}")
    
    async def _single_operation(self, user_id: str, operation_id: int):
        """单个操作"""
        try:
            data_hash = f"perf_test_data_{operation_id}".encode()
            
            result = await self.blockchain_service.store_health_data_enhanced(
                user_id=user_id,
                data_type=DataType.VITAL_SIGNS,
                data_hash=data_hash,
                metadata={"test_id": str(operation_id)},
                use_batch=operation_id % 5 == 0,  # 每5个操作使用一次批量处理
                priority=TaskPriority.NORMAL
            )
            
            return result
            
        except Exception as e:
            logger.error(f"操作 {operation_id} 失败: {str(e)}")
            return None


async def main():
    """主函数"""
    logger.info("启动增强版区块链服务完整演示")
    
    # 创建演示实例
    demo = BlockchainServiceDemo()
    
    try:
        # 运行基础演示
        await demo.run_demo()
        
        # 运行性能测试
        performance_demo = PerformanceTestDemo(demo.blockchain_service)
        await performance_demo.run_performance_test(50)
        
    except Exception as e:
        logger.error(f"演示失败: {str(e)}")
    
    logger.info("演示完成")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main()) 