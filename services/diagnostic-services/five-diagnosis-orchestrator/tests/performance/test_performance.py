"""
性能测试

测试五诊协同诊断系统的性能表现
"""

import pytest
import asyncio
import time
import statistics
from datetime import datetime, timezone
from typing import List, Dict, Any
import uuid

from five_diagnosis_orchestrator.core.orchestrator import FiveDiagnosisOrchestrator, OrchestrationConfig, OrchestrationMode
from five_diagnosis_orchestrator.models.diagnosis_models import (
    PatientInfo, DiagnosisInput, DiagnosisType, SessionStatus
)


@pytest.fixture
async def orchestrator():
    """创建编排器实例"""
    orchestrator = FiveDiagnosisOrchestrator()
    await orchestrator.initialize()
    yield orchestrator
    await orchestrator.close()


@pytest.fixture
def performance_patient_info():
    """性能测试用患者信息"""
    return PatientInfo(
        patient_id=str(uuid.uuid4()),
        name="性能测试患者",
        age=30,
        gender="男",
        height=175.0,
        weight=70.0
    )


@pytest.fixture
def performance_diagnosis_inputs():
    """性能测试用诊断输入"""
    return [
        DiagnosisInput(
            diagnosis_type=DiagnosisType.INQUIRY,
            data={"symptoms": {"头痛": 0.8, "失眠": 0.6}}
        ),
        DiagnosisInput(
            diagnosis_type=DiagnosisType.LOOK,
            data={"tongue": {"color": "淡红", "coating": "薄白"}}
        ),
        DiagnosisInput(
            diagnosis_type=DiagnosisType.LISTEN,
            data={"voice": {"tone": "正常", "volume": "正常"}}
        ),
        DiagnosisInput(
            diagnosis_type=DiagnosisType.PALPATION,
            data={"pulse": {"rate": 72, "rhythm": "规律"}}
        ),
        DiagnosisInput(
            diagnosis_type=DiagnosisType.CALCULATION,
            data={"constitution_scores": {"气虚质": 0.3, "阴虚质": 0.4}}
        )
    ]


class TestPerformance:
    """性能测试类"""
    
    @pytest.mark.asyncio
    async def test_single_session_performance(self, orchestrator, performance_patient_info, performance_diagnosis_inputs):
        """测试单个会话的性能"""
        # 记录开始时间
        start_time = time.time()
        
        # 创建会话
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK, DiagnosisType.CALCULATION]
        session_id = await orchestrator.create_diagnosis_session(
            patient_info=performance_patient_info,
            enabled_diagnoses=enabled_diagnoses
        )
        
        session_creation_time = time.time() - start_time
        
        # 启动诊断
        diagnosis_start_time = time.time()
        filtered_inputs = [
            inp for inp in performance_diagnosis_inputs 
            if inp.diagnosis_type in enabled_diagnoses
        ]
        await orchestrator.start_diagnosis(session_id, filtered_inputs)
        
        # 等待完成
        for _ in range(30):
            status = await orchestrator.get_session_status(session_id)
            if status["status"]==SessionStatus.COMPLETED.value:
                break
            await asyncio.sleep(0.1)
        
        total_time = time.time() - start_time
        diagnosis_time = time.time() - diagnosis_start_time
        
        # 获取结果
        result = await orchestrator.get_session_result(session_id)
        
        # 性能断言
        assert session_creation_time < 1.0  # 会话创建应在1秒内完成
        assert diagnosis_time < 10.0  # 诊断应在10秒内完成
        assert total_time < 15.0  # 总时间应在15秒内
        
        # 验证结果质量
        assert result is not None
        assert result.overall_confidence > 0
        
        print(f"性能指标:")
        print(f"  会话创建时间: {session_creation_time:.3f}秒")
        print(f"  诊断执行时间: {diagnosis_time:.3f}秒")
        print(f"  总执行时间: {total_time:.3f}秒")
        print(f"  整体置信度: {result.overall_confidence:.3f}")
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions_performance(self, orchestrator, performance_patient_info, performance_diagnosis_inputs):
        """测试并发会话性能"""
        concurrent_count = 5
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK]
        
        # 记录开始时间
        start_time = time.time()
        
        # 创建多个并发会话
        session_ids = []
        for i in range(concurrent_count):
            patient_info = PatientInfo(
                patient_id=f"perf_patient_{i}",
                name=f"并发测试患者{i}",
                age=30 + i,
                gender="男" if i % 2==0 else "女"
            )
            
            session_id = await orchestrator.create_diagnosis_session(
                patient_info=patient_info,
                enabled_diagnoses=enabled_diagnoses
            )
            session_ids.append(session_id)
        
        session_creation_time = time.time() - start_time
        
        # 并发启动所有诊断
        diagnosis_start_time = time.time()
        tasks = []
        
        for session_id in session_ids:
            filtered_inputs = [
                inp for inp in performance_diagnosis_inputs 
                if inp.diagnosis_type in enabled_diagnoses
            ]
            task = asyncio.create_task(
                orchestrator.start_diagnosis(session_id, filtered_inputs)
            )
            tasks.append(task)
        
        # 等待所有诊断启动
        await asyncio.gather(*tasks)
        
        # 等待所有会话完成
        completed_sessions = 0
        max_wait_time = 30
        
        for _ in range(max_wait_time * 10):  # 每0.1秒检查一次
            completed_count = 0
            for session_id in session_ids:
                status = await orchestrator.get_session_status(session_id)
                if status["status"]==SessionStatus.COMPLETED.value:
                    completed_count+=1
            
            if completed_count==concurrent_count:
                completed_sessions = completed_count
                break
            
            await asyncio.sleep(0.1)
        
        total_time = time.time() - start_time
        diagnosis_time = time.time() - diagnosis_start_time
        
        # 性能断言
        assert completed_sessions==concurrent_count  # 所有会话都应该完成
        assert session_creation_time < 5.0  # 创建5个会话应在5秒内完成
        assert diagnosis_time < 20.0  # 并发诊断应在20秒内完成
        assert total_time < 30.0  # 总时间应在30秒内
        
        # 计算平均性能
        avg_time_per_session = total_time / concurrent_count
        assert avg_time_per_session < 10.0  # 平均每个会话应在10秒内完成
        
        print(f"并发性能指标 (并发数: {concurrent_count}):")
        print(f"  会话创建总时间: {session_creation_time:.3f}秒")
        print(f"  诊断执行总时间: {diagnosis_time:.3f}秒")
        print(f"  总执行时间: {total_time:.3f}秒")
        print(f"  平均每会话时间: {avg_time_per_session:.3f}秒")
        print(f"  完成会话数: {completed_sessions}/{concurrent_count}")
    
    @pytest.mark.asyncio
    async def test_parallel_vs_sequential_performance(self, orchestrator, performance_patient_info, performance_diagnosis_inputs):
        """测试并行vs顺序执行性能对比"""
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK, DiagnosisType.LISTEN]
        
        # 测试并行执行
        parallel_config = OrchestrationConfig(mode=OrchestrationMode.PARALLEL)
        parallel_start_time = time.time()
        
        parallel_session_id = await orchestrator.create_diagnosis_session(
            patient_info=performance_patient_info,
            enabled_diagnoses=enabled_diagnoses,
            config=parallel_config
        )
        
        filtered_inputs = [
            inp for inp in performance_diagnosis_inputs 
            if inp.diagnosis_type in enabled_diagnoses
        ]
        await orchestrator.start_diagnosis(parallel_session_id, filtered_inputs)
        
        # 等待并行执行完成
        for _ in range(30):
            status = await orchestrator.get_session_status(parallel_session_id)
            if status["status"]==SessionStatus.COMPLETED.value:
                break
            await asyncio.sleep(0.1)
        
        parallel_time = time.time() - parallel_start_time
        
        # 测试顺序执行
        sequential_config = OrchestrationConfig(mode=OrchestrationMode.SEQUENTIAL)
        sequential_start_time = time.time()
        
        # 创建新的患者信息避免冲突
        sequential_patient_info = PatientInfo(
            patient_id=str(uuid.uuid4()),
            name="顺序测试患者",
            age=30,
            gender="女"
        )
        
        sequential_session_id = await orchestrator.create_diagnosis_session(
            patient_info=sequential_patient_info,
            enabled_diagnoses=enabled_diagnoses,
            config=sequential_config
        )
        
        await orchestrator.start_diagnosis(sequential_session_id, filtered_inputs)
        
        # 等待顺序执行完成
        for _ in range(30):
            status = await orchestrator.get_session_status(sequential_session_id)
            if status["status"]==SessionStatus.COMPLETED.value:
                break
            await asyncio.sleep(0.1)
        
        sequential_time = time.time() - sequential_start_time
        
        # 性能对比
        performance_improvement = (sequential_time - parallel_time) / sequential_time * 100
        
        print(f"执行模式性能对比:")
        print(f"  并行执行时间: {parallel_time:.3f}秒")
        print(f"  顺序执行时间: {sequential_time:.3f}秒")
        print(f"  性能提升: {performance_improvement:.1f}%")
        
        # 并行执行应该更快（至少快10%）
        assert parallel_time < sequential_time
        assert performance_improvement > 10.0
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, orchestrator, performance_patient_info, performance_diagnosis_inputs):
        """测试内存使用稳定性"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        session_count = 10
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK]
        
        memory_measurements = [initial_memory]
        
        # 执行多个会话
        for i in range(session_count):
            patient_info = PatientInfo(
                patient_id=f"memory_test_patient_{i}",
                name=f"内存测试患者{i}",
                age=30 + i,
                gender="男" if i % 2==0 else "女"
            )
            
            session_id = await orchestrator.create_diagnosis_session(
                patient_info=patient_info,
                enabled_diagnoses=enabled_diagnoses
            )
            
            filtered_inputs = [
                inp for inp in performance_diagnosis_inputs 
                if inp.diagnosis_type in enabled_diagnoses
            ]
            await orchestrator.start_diagnosis(session_id, filtered_inputs)
            
            # 等待完成
            for _ in range(30):
                status = await orchestrator.get_session_status(session_id)
                if status["status"]==SessionStatus.COMPLETED.value:
                    break
                await asyncio.sleep(0.1)
            
            # 记录内存使用
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_measurements.append(current_memory)
            
            # 强制垃圾回收
            import gc
            gc.collect()
        
        final_memory = memory_measurements[-1]
        memory_increase = final_memory - initial_memory
        max_memory = max(memory_measurements)
        
        print(f"内存使用情况:")
        print(f"  初始内存: {initial_memory:.1f} MB")
        print(f"  最终内存: {final_memory:.1f} MB")
        print(f"  最大内存: {max_memory:.1f} MB")
        print(f"  内存增长: {memory_increase:.1f} MB")
        print(f"  平均每会话内存增长: {memory_increase/session_count:.1f} MB")
        
        # 内存增长应该在合理范围内
        assert memory_increase < 100  # 总内存增长不应超过100MB
        assert memory_increase / session_count < 10  # 平均每会话内存增长不应超过10MB
    
    @pytest.mark.asyncio
    async def test_throughput_performance(self, orchestrator, performance_patient_info, performance_diagnosis_inputs):
        """测试吞吐量性能"""
        test_duration = 30  # 测试30秒
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK]
        
        start_time = time.time()
        completed_sessions = 0
        session_times = []
        
        session_counter = 0
        
        while time.time() - start_time < test_duration:
            session_start_time = time.time()
            
            # 创建患者信息
            patient_info = PatientInfo(
                patient_id=f"throughput_patient_{session_counter}",
                name=f"吞吐量测试患者{session_counter}",
                age=30 + (session_counter % 50),
                gender="男" if session_counter % 2==0 else "女"
            )
            
            # 创建会话
            session_id = await orchestrator.create_diagnosis_session(
                patient_info=patient_info,
                enabled_diagnoses=enabled_diagnoses
            )
            
            # 启动诊断
            filtered_inputs = [
                inp for inp in performance_diagnosis_inputs 
                if inp.diagnosis_type in enabled_diagnoses
            ]
            await orchestrator.start_diagnosis(session_id, filtered_inputs)
            
            # 等待完成（设置较短的超时时间）
            session_completed = False
            for _ in range(100):  # 最多等待10秒
                status = await orchestrator.get_session_status(session_id)
                if status["status"]==SessionStatus.COMPLETED.value:
                    session_completed = True
                    break
                await asyncio.sleep(0.1)
            
            if session_completed:
                session_time = time.time() - session_start_time
                session_times.append(session_time)
                completed_sessions+=1
            
            session_counter+=1
            
            # 避免过度负载
            await asyncio.sleep(0.1)
        
        total_time = time.time() - start_time
        throughput = completed_sessions / total_time  # 每秒完成的会话数
        
        if session_times:
            avg_session_time = statistics.mean(session_times)
            min_session_time = min(session_times)
            max_session_time = max(session_times)
        else:
            avg_session_time = min_session_time = max_session_time = 0
        
        print(f"吞吐量性能指标 (测试时长: {test_duration}秒):")
        print(f"  总启动会话数: {session_counter}")
        print(f"  完成会话数: {completed_sessions}")
        print(f"  完成率: {completed_sessions/session_counter*100:.1f}%")
        print(f"  吞吐量: {throughput:.2f} 会话/秒")
        print(f"  平均会话时间: {avg_session_time:.3f}秒")
        print(f"  最快会话时间: {min_session_time:.3f}秒")
        print(f"  最慢会话时间: {max_session_time:.3f}秒")
        
        # 性能断言
        assert completed_sessions > 0  # 至少完成一个会话
        assert throughput > 0.1  # 吞吐量至少0.1会话/秒
        assert completed_sessions / session_counter > 0.5  # 完成率至少50%
    
    @pytest.mark.asyncio
    async def test_stress_test(self, orchestrator, performance_patient_info, performance_diagnosis_inputs):
        """压力测试"""
        stress_session_count = 20
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.CALCULATION]
        
        start_time = time.time()
        
        # 创建大量并发会话
        session_ids = []
        for i in range(stress_session_count):
            patient_info = PatientInfo(
                patient_id=f"stress_patient_{i}",
                name=f"压力测试患者{i}",
                age=20 + (i % 60),
                gender="男" if i % 2==0 else "女"
            )
            
            session_id = await orchestrator.create_diagnosis_session(
                patient_info=patient_info,
                enabled_diagnoses=enabled_diagnoses
            )
            session_ids.append(session_id)
        
        # 并发启动所有诊断
        tasks = []
        for session_id in session_ids:
            filtered_inputs = [
                inp for inp in performance_diagnosis_inputs 
                if inp.diagnosis_type in enabled_diagnoses
            ]
            task = asyncio.create_task(
                orchestrator.start_diagnosis(session_id, filtered_inputs)
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # 等待所有会话完成
        completed_count = 0
        failed_count = 0
        max_wait_time = 60  # 最多等待60秒
        
        for _ in range(max_wait_time * 10):
            current_completed = 0
            current_failed = 0
            
            for session_id in session_ids:
                status = await orchestrator.get_session_status(session_id)
                if status["status"]==SessionStatus.COMPLETED.value:
                    current_completed+=1
                elif status["status"]==SessionStatus.FAILED.value:
                    current_failed+=1
            
            completed_count = current_completed
            failed_count = current_failed
            
            if completed_count + failed_count==stress_session_count:
                break
            
            await asyncio.sleep(0.1)
        
        total_time = time.time() - start_time
        success_rate = completed_count / stress_session_count * 100
        
        print(f"压力测试结果 (会话数: {stress_session_count}):")
        print(f"  总执行时间: {total_time:.3f}秒")
        print(f"  成功完成: {completed_count}")
        print(f"  失败: {failed_count}")
        print(f"  未完成: {stress_session_count - completed_count - failed_count}")
        print(f"  成功率: {success_rate:.1f}%")
        print(f"  平均每会话时间: {total_time/stress_session_count:.3f}秒")
        
        # 压力测试断言
        assert success_rate > 80.0  # 成功率应该超过80%
        assert total_time < 120.0  # 总时间应在2分钟内
        assert completed_count > stress_session_count * 0.8  # 至少80%的会话成功完成
    
    @pytest.mark.asyncio
    async def test_resource_cleanup_performance(self, orchestrator, performance_patient_info, performance_diagnosis_inputs):
        """测试资源清理性能"""
        session_count = 10
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK]
        
        # 创建并完成多个会话
        session_ids = []
        for i in range(session_count):
            patient_info = PatientInfo(
                patient_id=f"cleanup_patient_{i}",
                name=f"清理测试患者{i}",
                age=30 + i,
                gender="男" if i % 2==0 else "女"
            )
            
            session_id = await orchestrator.create_diagnosis_session(
                patient_info=patient_info,
                enabled_diagnoses=enabled_diagnoses
            )
            session_ids.append(session_id)
            
            filtered_inputs = [
                inp for inp in performance_diagnosis_inputs 
                if inp.diagnosis_type in enabled_diagnoses
            ]
            await orchestrator.start_diagnosis(session_id, filtered_inputs)
            
            # 等待完成
            for _ in range(30):
                status = await orchestrator.get_session_status(session_id)
                if status["status"]==SessionStatus.COMPLETED.value:
                    break
                await asyncio.sleep(0.1)
        
        # 测试资源清理性能
        cleanup_start_time = time.time()
        
        # 清理所有会话
        for session_id in session_ids:
            await orchestrator.cleanup_session(session_id)
        
        cleanup_time = time.time() - cleanup_start_time
        
        print(f"资源清理性能:")
        print(f"  清理会话数: {session_count}")
        print(f"  清理总时间: {cleanup_time:.3f}秒")
        print(f"  平均每会话清理时间: {cleanup_time/session_count:.3f}秒")
        
        # 清理性能断言
        assert cleanup_time < 5.0  # 清理应在5秒内完成
        assert cleanup_time / session_count < 1.0  # 平均每会话清理时间应少于1秒