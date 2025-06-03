#!/usr/bin/env python3
"""
索克生活 - 中期实施任务集成测试
测试智能任务调度器、共享内存大数据处理和混合架构设计
"""

import asyncio
import time
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# 导入测试模块
from services.common.intelligent_task_scheduler import (
    IntelligentTaskScheduler, AgentInfo, AgentType, TaskPriority,
    initialize_scheduler
)
from services.common.shared_memory_processor import (
    SharedMemoryDataPipeline, initialize_shared_memory_system
)
from services.common.hybrid_architecture import (
    HybridArchitecture, TaskType, ProcessingMode, Priority,
    initialize_hybrid_architecture
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MidTermImplementationTester:
    """中期实施任务测试器"""

    def __init__(self):
        self.test_results = []
        self.scheduler = None
        self.shared_memory_pipeline = None
        self.hybrid_architecture = None

    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("🚀 开始中期实施任务集成测试")

        try:
            # 初始化系统
            await self.initialize_systems()

            # 测试智能任务调度器
            await self.test_intelligent_task_scheduler()

            # 测试共享内存大数据处理
            await self.test_shared_memory_processing()

            # 测试混合架构设计
            await self.test_hybrid_architecture()

            # 测试系统集成
            await self.test_system_integration()

            # 生成测试报告
            self.generate_test_report()

        except Exception as e:
            logger.error(f"测试过程中出现错误: {e}")
            raise
        finally:
            await self.cleanup_systems()

    async def initialize_systems(self):
        """初始化测试系统"""
        logger.info("📋 初始化测试系统...")

        # 初始化智能任务调度器
        self.scheduler = await initialize_scheduler()

        # 注册测试智能体
        test_agents = [
            AgentInfo(
                agent_id="xiaoai_test_001",
                agent_type=AgentType.XIAOAI,
                endpoint="http://localhost:8001",
                max_capacity=5,
                capabilities=["ai_inference", "data_analysis"]
            ),
            AgentInfo(
                agent_id="xiaoke_test_001",
                agent_type=AgentType.XIAOKE,
                endpoint="http://localhost:8002",
                max_capacity=8,
                capabilities=["health_monitoring", "biomarker_analysis"]
            ),
            AgentInfo(
                agent_id="laoke_test_001",
                agent_type=AgentType.LAOKE,
                endpoint="http://localhost:8003",
                max_capacity=6,
                capabilities=["tcm_diagnosis", "syndrome_analysis"]
            ),
            AgentInfo(
                agent_id="soer_test_001",
                agent_type=AgentType.SOER,
                endpoint="http://localhost:8004",
                max_capacity=10,
                capabilities=["lifestyle_planning", "nutrition_optimization"]
            )
        ]

        for agent in test_agents:
            self.scheduler.register_agent(agent)

        # 初始化共享内存系统
        self.shared_memory_pipeline = await initialize_shared_memory_system(
            max_memory_gb=2.0, max_workers=4
        )

        # 初始化混合架构
        self.hybrid_architecture = await initialize_hybrid_architecture(
            max_threads=4, max_processes=2, enable_distributed=False
        )

        logger.info("✅ 系统初始化完成")

    async def test_intelligent_task_scheduler(self):
        """测试智能任务调度器"""
        logger.info("🧠 测试智能任务调度器...")

        test_start = time.time()

        try:
            # 测试1: 任务提交和调度
            task_ids = []
            for i in range(20):
                task_id = await self.scheduler.submit_task(
                    task_type=f"test_task_{i}",
                    agent_type=AgentType.XIAOAI if i % 4 == 0 else
                              AgentType.XIAOKE if i % 4 == 1 else
                              AgentType.LAOKE if i % 4 == 2 else AgentType.SOER,
                    input_data={"test_data": f"data_{i}"},
                    priority=TaskPriority.HIGH if i < 5 else TaskPriority.NORMAL
                )
                task_ids.append(task_id)

            # 等待任务处理
            await asyncio.sleep(2)

            # 测试2: 获取任务状态
            completed_tasks = 0
            for task_id in task_ids:
                status = await self.scheduler.get_task_status(task_id)
                if status and status.get("status") == "completed":
                    completed_tasks += 1

            # 测试3: 获取调度器统计
            stats = self.scheduler.get_scheduler_stats()

            test_duration = time.time() - test_start

            # 记录测试结果
            self.test_results.append({
                "test_name": "智能任务调度器",
                "success": True,
                "duration": test_duration,
                "metrics": {
                    "submitted_tasks": len(task_ids),
                    "completed_tasks": completed_tasks,
                    "completion_rate": completed_tasks / len(task_ids) * 100,
                    "scheduler_stats": stats
                }
            })

            logger.info(f"✅ 智能任务调度器测试完成 - 完成率: {completed_tasks}/{len(task_ids)}")

        except Exception as e:
            self.test_results.append({
                "test_name": "智能任务调度器",
                "success": False,
                "error": str(e),
                "duration": time.time() - test_start
            })
            logger.error(f"❌ 智能任务调度器测试失败: {e}")

    async def test_shared_memory_processing(self):
        """测试共享内存大数据处理"""
        logger.info("💾 测试共享内存大数据处理...")

        test_start = time.time()

        try:
            # 测试1: 创建大型数据集
            health_data = np.random.rand(1000, 50).astype(np.float32)  # 1000个样本，50个特征
            symptoms_data = np.random.rand(100, 20).astype(np.float32)  # 100个症状，20个特征
            weights_data = np.random.rand(20).astype(np.float32)  # 权重向量
            nutrition_data = np.random.rand(500, 30).astype(np.float32)  # 500种食物，30个营养成分
            user_profile = np.random.rand(30).astype(np.float32)  # 用户营养需求

            # 测试2: 健康数据批处理
            health_input_id = "health_test_input"
            health_output_id = "health_test_output"

            health_array = self.shared_memory_pipeline.memory_manager.create_shared_array(
                health_input_id, health_data.shape, health_data.dtype
            )
            health_array[:] = health_data

            health_task_id = await self.shared_memory_pipeline.processor.process_health_data_batch(
                health_input_id, health_output_id, "normalize"
            )

            # 测试3: 中医证候分析
            symptoms_id = "symptoms_test"
            weights_id = "weights_test"
            syndrome_result_id = "syndrome_result"

            symptoms_array = self.shared_memory_pipeline.memory_manager.create_shared_array(
                symptoms_id, symptoms_data.shape, symptoms_data.dtype
            )
            symptoms_array[:] = symptoms_data

            weights_array = self.shared_memory_pipeline.memory_manager.create_shared_array(
                weights_id, weights_data.shape, weights_data.dtype
            )
            weights_array[:] = weights_data

            syndrome_task_id = await self.shared_memory_pipeline.processor.process_tcm_syndrome_analysis(
                symptoms_id, weights_id, syndrome_result_id
            )

            # 测试4: 营养优化处理
            user_data_id = "user_nutrition"
            nutrition_db_id = "nutrition_database"
            nutrition_result_id = "nutrition_optimization"

            user_array = self.shared_memory_pipeline.memory_manager.create_shared_array(
                user_data_id, user_profile.shape, user_profile.dtype
            )
            user_array[:] = user_profile

            nutrition_array = self.shared_memory_pipeline.memory_manager.create_shared_array(
                nutrition_db_id, nutrition_data.shape, nutrition_data.dtype
            )
            nutrition_array[:] = nutrition_data

            nutrition_task_id = await self.shared_memory_pipeline.processor.process_nutrition_optimization(
                user_data_id, nutrition_db_id, nutrition_result_id
            )

            # 测试5: 数据管道处理
            pipeline_result_id = await self.shared_memory_pipeline.health_data_analysis_pipeline(
                health_data
            )

            # 获取内存统计
            memory_stats = self.shared_memory_pipeline.memory_manager.get_memory_stats()
            processing_stats = self.shared_memory_pipeline.processor.get_processing_stats()

            test_duration = time.time() - test_start

            # 记录测试结果
            self.test_results.append({
                "test_name": "共享内存大数据处理",
                "success": True,
                "duration": test_duration,
                "metrics": {
                    "health_data_shape": health_data.shape,
                    "symptoms_data_shape": symptoms_data.shape,
                    "nutrition_data_shape": nutrition_data.shape,
                    "memory_stats": memory_stats,
                    "processing_stats": processing_stats,
                    "completed_tasks": [
                        health_task_id, syndrome_task_id,
                        nutrition_task_id, pipeline_result_id
                    ]
                }
            })

            logger.info(f"✅ 共享内存大数据处理测试完成 - 内存使用: {memory_stats['total_allocated_mb']:.2f}MB")

        except Exception as e:
            self.test_results.append({
                "test_name": "共享内存大数据处理",
                "success": False,
                "error": str(e),
                "duration": time.time() - test_start
            })
            logger.error(f"❌ 共享内存大数据处理测试失败: {e}")

    async def test_hybrid_architecture(self):
        """测试混合架构设计"""
        logger.info("🏗️ 测试混合架构设计...")

        test_start = time.time()

        try:
            # 定义测试函数
            def cpu_intensive_task(n: int) -> int:
                """CPU密集型任务"""
                result = 0
                for i in range(n):
                    result += i * i
                return result

            async def io_intensive_task(delay: float) -> str:
                """I/O密集型任务"""
                await asyncio.sleep(delay)
                return f"IO task completed after {delay}s"

            def memory_intensive_task(size: int) -> int:
                """内存密集型任务"""
                data = np.random.rand(size, size)
                return int(np.sum(data))

            # 测试1: 同步本地处理
            sync_local_tasks = []
            for i in range(5):
                task_id = await self.hybrid_architecture.submit_task(
                    function=cpu_intensive_task,
                    args=(10000,),
                    task_type=TaskType.CPU_INTENSIVE,
                    processing_mode=ProcessingMode.SYNC_LOCAL,
                    priority=Priority.NORMAL
                )
                sync_local_tasks.append(task_id)

            # 测试2: 异步本地处理
            async_local_tasks = []
            for i in range(5):
                task_id = await self.hybrid_architecture.submit_task(
                    function=io_intensive_task,
                    args=(0.1,),
                    task_type=TaskType.IO_INTENSIVE,
                    processing_mode=ProcessingMode.ASYNC_LOCAL,
                    priority=Priority.HIGH
                )
                async_local_tasks.append(task_id)

            # 测试3: 混合模式处理
            hybrid_tasks = []
            for i in range(10):
                if i % 3 == 0:
                    func, args, task_type = cpu_intensive_task, (5000,), TaskType.CPU_INTENSIVE
                elif i % 3 == 1:
                    func, args, task_type = io_intensive_task, (0.05,), TaskType.IO_INTENSIVE
                else:
                    func, args, task_type = memory_intensive_task, (100,), TaskType.MEMORY_INTENSIVE

                task_id = await self.hybrid_architecture.submit_task(
                    function=func,
                    args=args,
                    task_type=task_type,
                    processing_mode=ProcessingMode.HYBRID,
                    priority=Priority.NORMAL
                )
                hybrid_tasks.append(task_id)

            # 等待任务完成
            await asyncio.sleep(3)

            # 收集结果
            completed_sync = 0
            completed_async = 0
            completed_hybrid = 0

            for task_id in sync_local_tasks:
                try:
                    result = await self.hybrid_architecture.get_task_result(task_id, timeout=1)
                    if result is not None:
                        completed_sync += 1
                except:
                    pass

            for task_id in async_local_tasks:
                try:
                    result = await self.hybrid_architecture.get_task_result(task_id, timeout=1)
                    if result is not None:
                        completed_async += 1
                except:
                    pass

            for task_id in hybrid_tasks:
                try:
                    result = await self.hybrid_architecture.get_task_result(task_id, timeout=1)
                    if result is not None:
                        completed_hybrid += 1
                except:
                    pass

            # 获取架构统计
            arch_stats = self.hybrid_architecture.get_architecture_stats()

            test_duration = time.time() - test_start

            # 记录测试结果
            self.test_results.append({
                "test_name": "混合架构设计",
                "success": True,
                "duration": test_duration,
                "metrics": {
                    "sync_local_completion": f"{completed_sync}/{len(sync_local_tasks)}",
                    "async_local_completion": f"{completed_async}/{len(async_local_tasks)}",
                    "hybrid_completion": f"{completed_hybrid}/{len(hybrid_tasks)}",
                    "total_completion_rate": (
                        (completed_sync + completed_async + completed_hybrid) /
                        (len(sync_local_tasks) + len(async_local_tasks) + len(hybrid_tasks)) * 100
                    ),
                    "architecture_stats": arch_stats
                }
            })

            logger.info(f"✅ 混合架构设计测试完成 - 总完成率: {completed_sync + completed_async + completed_hybrid}/{len(sync_local_tasks) + len(async_local_tasks) + len(hybrid_tasks)}")

        except Exception as e:
            self.test_results.append({
                "test_name": "混合架构设计",
                "success": False,
                "error": str(e),
                "duration": time.time() - test_start
            })
            logger.error(f"❌ 混合架构设计测试失败: {e}")

    async def test_system_integration(self):
        """测试系统集成"""
        logger.info("🔗 测试系统集成...")

        test_start = time.time()

        try:
            # 集成测试场景：健康数据分析流程

            # 1. 生成测试数据
            user_health_data = np.random.rand(500, 40).astype(np.float32)

            # 2. 通过调度器提交健康数据处理任务
            health_analysis_task = await self.scheduler.submit_task(
                task_type="health_data_analysis",
                agent_type=AgentType.XIAOKE,
                input_data={
                    "data_shape": user_health_data.shape,
                    "data_type": "health_monitoring"
                },
                priority=TaskPriority.HIGH
            )

            # 3. 使用共享内存处理大数据
            shared_data_id = "integration_test_data"
            shared_array = self.shared_memory_pipeline.memory_manager.create_shared_array(
                shared_data_id, user_health_data.shape, user_health_data.dtype
            )
            shared_array[:] = user_health_data

            # 4. 通过混合架构执行数据处理
            def process_health_data(data_id: str) -> Dict[str, Any]:
                # 模拟健康数据处理
                return {
                    "processed_data_id": data_id,
                    "analysis_result": "健康状态良好",
                    "risk_score": 0.15,
                    "recommendations": ["保持运动", "均衡饮食", "充足睡眠"]
                }

            hybrid_task_id = await self.hybrid_architecture.submit_task(
                function=process_health_data,
                args=(shared_data_id,),
                task_type=TaskType.MIXED,
                processing_mode=ProcessingMode.HYBRID,
                priority=Priority.HIGH
            )

            # 5. 等待所有任务完成
            await asyncio.sleep(2)

            # 6. 收集结果
            scheduler_status = await self.scheduler.get_task_status(health_analysis_task)
            hybrid_result = await self.hybrid_architecture.get_task_result(hybrid_task_id, timeout=5)

            # 7. 获取系统统计
            scheduler_stats = self.scheduler.get_scheduler_stats()
            memory_stats = self.shared_memory_pipeline.memory_manager.get_memory_stats()
            arch_stats = self.hybrid_architecture.get_architecture_stats()

            test_duration = time.time() - test_start

            # 记录测试结果
            self.test_results.append({
                "test_name": "系统集成",
                "success": True,
                "duration": test_duration,
                "metrics": {
                    "scheduler_task_status": scheduler_status.get("status") if scheduler_status else "unknown",
                    "hybrid_task_result": hybrid_result is not None,
                    "data_processing_successful": shared_data_id in self.shared_memory_pipeline.memory_manager.blocks,
                    "system_stats": {
                        "scheduler": scheduler_stats,
                        "memory": memory_stats,
                        "architecture": arch_stats
                    }
                }
            })

            logger.info("✅ 系统集成测试完成")

        except Exception as e:
            self.test_results.append({
                "test_name": "系统集成",
                "success": False,
                "error": str(e),
                "duration": time.time() - test_start
            })
            logger.error(f"❌ 系统集成测试失败: {e}")

    def generate_test_report(self):
        """生成测试报告"""
        logger.info("📊 生成测试报告...")

        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["success"]])
        total_duration = sum(r["duration"] for r in self.test_results)

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration,
                "timestamp": datetime.now().isoformat()
            },
            "test_details": self.test_results
        }

        # 保存报告
        report_file = f"mid_term_implementation_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"📄 测试报告已保存: {report_file}")
        except Exception as e:
            logger.error(f"保存测试报告失败: {e}")

        # 打印摘要
        print("\n" + "="*80)
        print("🎯 中期实施任务测试报告摘要")
        print("="*80)
        print(f"总测试数: {total_tests}")
        print(f"成功测试: {successful_tests}")
        print(f"失败测试: {total_tests - successful_tests}")
        print(f"成功率: {successful_tests / total_tests * 100:.1f}%")
        print(f"总耗时: {total_duration:.2f}秒")
        print("\n测试详情:")

        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test_name']}: {result['duration']:.2f}s")
            if not result["success"]:
                print(f"   错误: {result.get('error', '未知错误')}")

        print("="*80)

    async def cleanup_systems(self):
        """清理测试系统"""
        logger.info("🧹 清理测试系统...")

        try:
            # 停止调度器
            if self.scheduler:
                await self.scheduler.stop_scheduler()

            # 清理共享内存
            if self.shared_memory_pipeline:
                self.shared_memory_pipeline.cleanup_all()

            # 停止混合架构
            if self.hybrid_architecture:
                await self.hybrid_architecture.performance_monitor.stop()

            logger.info("✅ 系统清理完成")

        except Exception as e:
            logger.error(f"系统清理失败: {e}")

async def main():
    """主函数"""
    tester = MidTermImplementationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())