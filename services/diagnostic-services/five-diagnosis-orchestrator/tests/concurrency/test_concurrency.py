"""
并发测试

测试五诊协同诊断系统的并发处理能力和线程安全性
"""

import asyncio
import random
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import pytest
from five_diagnosis_orchestrator.core.orchestrator import (
    FiveDiagnosisOrchestrator,
    OrchestrationConfig,
    OrchestrationMode,
)
from five_diagnosis_orchestrator.models.diagnosis_models import (
    DiagnosisInput,
    DiagnosisType,
    PatientInfo,
    SessionStatus,
)


@pytest.fixture
async def orchestrator():
    """创建编排器实例"""
    orchestrator = FiveDiagnosisOrchestrator()
    await orchestrator.initialize()
    yield orchestrator
    await orchestrator.close()


@pytest.fixture
def concurrency_patient_info():
    """并发测试用患者信息"""
    return PatientInfo(
        patient_id=str(uuid.uuid4()),
        name="并发测试患者",
        age=30,
        gender="男",
        height=175.0,
        weight=70.0,
    )


@pytest.fixture
def concurrency_diagnosis_inputs():
    """并发测试用诊断输入"""
    return [
        DiagnosisInput(
            diagnosis_type=DiagnosisType.INQUIRY,
            data={"symptoms": {"头痛": 0.8, "失眠": 0.6}},
        ),
        DiagnosisInput(
            diagnosis_type=DiagnosisType.LOOK,
            data={"tongue": {"color": "淡红", "coating": "薄白"}},
        ),
        DiagnosisInput(
            diagnosis_type=DiagnosisType.LISTEN,
            data={"voice": {"tone": "正常", "volume": "正常"}},
        ),
        DiagnosisInput(
            diagnosis_type=DiagnosisType.PALPATION,
            data={"pulse": {"rate": 72, "rhythm": "规律"}},
        ),
        DiagnosisInput(
            diagnosis_type=DiagnosisType.CALCULATION,
            data={"constitution_scores": {"气虚质": 0.3, "阴虚质": 0.4}},
        ),
    ]


class TestConcurrency:
    """并发测试类"""

    @pytest.mark.asyncio
    async def test_concurrent_session_creation(self, orchestrator):
        """测试并发会话创建"""
        concurrent_count = 10
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK]

        # 并发创建会话
        tasks = []
        for i in range(concurrent_count):
            patient_info = PatientInfo(
                patient_id=f"concurrent_patient_{i}",
                name=f"并发患者{i}",
                age=30 + i,
                gender="男" if i % 2 == 0 else "女",
            )

            task = asyncio.create_task(
                orchestrator.create_diagnosis_session(
                    patient_info=patient_info, enabled_diagnoses=enabled_diagnoses
                )
            )
            tasks.append(task)

        # 等待所有会话创建完成
        session_ids = await asyncio.gather(*tasks)

        # 验证结果
        assert len(session_ids) == concurrent_count
        assert len(set(session_ids)) == concurrent_count  # 所有会话ID应该唯一

        # 验证每个会话都能正常获取状态
        for session_id in session_ids:
            status = await orchestrator.get_session_status(session_id)
            assert status["status"] == SessionStatus.CREATED.value

    @pytest.mark.asyncio
    async def test_concurrent_diagnosis_execution(
        self, orchestrator, concurrency_diagnosis_inputs
    ):
        """测试并发诊断执行"""
        concurrent_count = 8
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK]

        # 创建多个会话
        session_ids = []
        for i in range(concurrent_count):
            patient_info = PatientInfo(
                patient_id=f"exec_patient_{i}",
                name=f"执行测试患者{i}",
                age=25 + i,
                gender="男" if i % 2 == 0 else "女",
            )

            session_id = await orchestrator.create_diagnosis_session(
                patient_info=patient_info, enabled_diagnoses=enabled_diagnoses
            )
            session_ids.append(session_id)

        # 并发启动诊断
        tasks = []
        for session_id in session_ids:
            filtered_inputs = [
                inp
                for inp in concurrency_diagnosis_inputs
                if inp.diagnosis_type in enabled_diagnoses
            ]
            task = asyncio.create_task(
                orchestrator.start_diagnosis(session_id, filtered_inputs)
            )
            tasks.append(task)

        # 等待所有诊断启动
        await asyncio.gather(*tasks)

        # 等待所有诊断完成
        completed_sessions = []
        max_wait_time = 30

        for _ in range(max_wait_time * 10):
            current_completed = []
            for session_id in session_ids:
                status = await orchestrator.get_session_status(session_id)
                if status["status"] == SessionStatus.COMPLETED.value:
                    current_completed.append(session_id)

            completed_sessions = current_completed
            if len(completed_sessions) == concurrent_count:
                break

            await asyncio.sleep(0.1)

        # 验证结果
        assert len(completed_sessions) == concurrent_count

        # 验证每个会话的结果
        for session_id in completed_sessions:
            result = await orchestrator.get_session_result(session_id)
            assert result is not None
            assert result.overall_confidence > 0

    @pytest.mark.asyncio
    async def test_mixed_concurrent_operations(
        self, orchestrator, concurrency_diagnosis_inputs
    ):
        """测试混合并发操作"""
        # 同时进行会话创建、诊断执行、状态查询等操作

        # 任务1: 创建新会话
        create_tasks = []
        for i in range(5):
            patient_info = PatientInfo(
                patient_id=f"mixed_patient_{i}",
                name=f"混合测试患者{i}",
                age=30 + i,
                gender="男" if i % 2 == 0 else "女",
            )

            task = asyncio.create_task(
                orchestrator.create_diagnosis_session(
                    patient_info=patient_info,
                    enabled_diagnoses=[DiagnosisType.INQUIRY, DiagnosisType.LOOK],
                )
            )
            create_tasks.append(task)

        # 等待会话创建完成
        new_session_ids = await asyncio.gather(*create_tasks)

        # 任务2: 启动诊断
        diagnosis_tasks = []
        for session_id in new_session_ids:
            filtered_inputs = [
                inp
                for inp in concurrency_diagnosis_inputs
                if inp.diagnosis_type in [DiagnosisType.INQUIRY, DiagnosisType.LOOK]
            ]
            task = asyncio.create_task(
                orchestrator.start_diagnosis(session_id, filtered_inputs)
            )
            diagnosis_tasks.append(task)

        # 任务3: 并发状态查询
        status_tasks = []
        for session_id in new_session_ids:
            for _ in range(3):  # 每个会话查询3次
                task = asyncio.create_task(orchestrator.get_session_status(session_id))
                status_tasks.append(task)

        # 任务4: 系统指标查询
        metrics_tasks = []
        for _ in range(5):
            task = asyncio.create_task(orchestrator.get_system_metrics())
            metrics_tasks.append(task)

        # 并发执行所有任务
        all_tasks = diagnosis_tasks + status_tasks + metrics_tasks
        results = await asyncio.gather(*all_tasks, return_exceptions=True)

        # 验证没有异常
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) == 0, f"发现异常: {exceptions}"

        # 等待诊断完成
        for session_id in new_session_ids:
            for _ in range(30):
                status = await orchestrator.get_session_status(session_id)
                if status["status"] == SessionStatus.COMPLETED.value:
                    break
                await asyncio.sleep(0.1)

    @pytest.mark.asyncio
    async def test_concurrent_session_cancellation(
        self, orchestrator, concurrency_diagnosis_inputs
    ):
        """测试并发会话取消"""
        session_count = 6
        enabled_diagnoses = [
            DiagnosisType.INQUIRY,
            DiagnosisType.LOOK,
            DiagnosisType.CALCULATION,
        ]

        # 创建多个会话
        session_ids = []
        for i in range(session_count):
            patient_info = PatientInfo(
                patient_id=f"cancel_patient_{i}",
                name=f"取消测试患者{i}",
                age=30 + i,
                gender="男" if i % 2 == 0 else "女",
            )

            session_id = await orchestrator.create_diagnosis_session(
                patient_info=patient_info, enabled_diagnoses=enabled_diagnoses
            )
            session_ids.append(session_id)

        # 启动所有诊断
        for session_id in session_ids:
            filtered_inputs = [
                inp
                for inp in concurrency_diagnosis_inputs
                if inp.diagnosis_type in enabled_diagnoses
            ]
            await orchestrator.start_diagnosis(session_id, filtered_inputs)

        # 等待一小段时间
        await asyncio.sleep(1)

        # 并发取消一半的会话
        cancel_count = session_count // 2
        cancel_tasks = []

        for i in range(cancel_count):
            task = asyncio.create_task(orchestrator.cancel_session(session_ids[i]))
            cancel_tasks.append(task)

        # 等待取消操作完成
        await asyncio.gather(*cancel_tasks)

        # 验证取消状态
        for i in range(cancel_count):
            status = await orchestrator.get_session_status(session_ids[i])
            assert status["status"] == SessionStatus.CANCELLED.value

        # 等待剩余会话完成
        for i in range(cancel_count, session_count):
            for _ in range(30):
                status = await orchestrator.get_session_status(session_ids[i])
                if status["status"] in [
                    SessionStatus.COMPLETED.value,
                    SessionStatus.FAILED.value,
                ]:
                    break
                await asyncio.sleep(0.1)

    @pytest.mark.asyncio
    async def test_concurrent_result_retrieval(
        self, orchestrator, concurrency_diagnosis_inputs
    ):
        """测试并发结果获取"""
        session_count = 5
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK]

        # 创建并完成多个会话
        session_ids = []
        for i in range(session_count):
            patient_info = PatientInfo(
                patient_id=f"result_patient_{i}",
                name=f"结果测试患者{i}",
                age=30 + i,
                gender="男" if i % 2 == 0 else "女",
            )

            session_id = await orchestrator.create_diagnosis_session(
                patient_info=patient_info, enabled_diagnoses=enabled_diagnoses
            )
            session_ids.append(session_id)

            filtered_inputs = [
                inp
                for inp in concurrency_diagnosis_inputs
                if inp.diagnosis_type in enabled_diagnoses
            ]
            await orchestrator.start_diagnosis(session_id, filtered_inputs)

        # 等待所有会话完成
        for session_id in session_ids:
            for _ in range(30):
                status = await orchestrator.get_session_status(session_id)
                if status["status"] == SessionStatus.COMPLETED.value:
                    break
                await asyncio.sleep(0.1)

        # 并发获取结果（每个会话获取多次）
        result_tasks = []
        for session_id in session_ids:
            for _ in range(3):  # 每个会话获取3次结果
                task = asyncio.create_task(orchestrator.get_session_result(session_id))
                result_tasks.append(task)

        # 等待所有结果获取完成
        results = await asyncio.gather(*result_tasks)

        # 验证结果
        assert len(results) == session_count * 3
        for result in results:
            assert result is not None
            assert result.overall_confidence > 0

    @pytest.mark.asyncio
    async def test_race_condition_protection(
        self, orchestrator, concurrency_diagnosis_inputs
    ):
        """测试竞态条件保护"""
        patient_info = PatientInfo(
            patient_id="race_condition_patient",
            name="竞态条件测试患者",
            age=30,
            gender="男",
        )

        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK]

        # 创建会话
        session_id = await orchestrator.create_diagnosis_session(
            patient_info=patient_info, enabled_diagnoses=enabled_diagnoses
        )

        # 并发执行可能产生竞态条件的操作
        tasks = []

        # 多次启动诊断（应该只有第一次成功）
        for _ in range(5):
            filtered_inputs = [
                inp
                for inp in concurrency_diagnosis_inputs
                if inp.diagnosis_type in enabled_diagnoses
            ]
            task = asyncio.create_task(
                orchestrator.start_diagnosis(session_id, filtered_inputs)
            )
            tasks.append(task)

        # 多次获取状态
        for _ in range(10):
            task = asyncio.create_task(orchestrator.get_session_status(session_id))
            tasks.append(task)

        # 尝试取消会话
        task = asyncio.create_task(orchestrator.cancel_session(session_id))
        tasks.append(task)

        # 执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 验证没有严重错误（允许一些预期的异常，如重复启动诊断）
        serious_exceptions = [
            r
            for r in results
            if isinstance(r, Exception)
            and not isinstance(r, (ValueError, RuntimeError))
        ]
        assert len(serious_exceptions) == 0, f"发现严重异常: {serious_exceptions}"

    @pytest.mark.asyncio
    async def test_resource_contention(
        self, orchestrator, concurrency_diagnosis_inputs
    ):
        """测试资源竞争"""
        concurrent_count = 15  # 较高的并发数
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK]

        # 创建大量并发会话
        session_creation_tasks = []
        for i in range(concurrent_count):
            patient_info = PatientInfo(
                patient_id=f"contention_patient_{i}",
                name=f"资源竞争测试患者{i}",
                age=20 + (i % 50),
                gender="男" if i % 2 == 0 else "女",
            )

            task = asyncio.create_task(
                orchestrator.create_diagnosis_session(
                    patient_info=patient_info, enabled_diagnoses=enabled_diagnoses
                )
            )
            session_creation_tasks.append(task)

        # 等待会话创建
        session_ids = await asyncio.gather(*session_creation_tasks)

        # 并发启动所有诊断
        diagnosis_tasks = []
        for session_id in session_ids:
            filtered_inputs = [
                inp
                for inp in concurrency_diagnosis_inputs
                if inp.diagnosis_type in enabled_diagnoses
            ]
            task = asyncio.create_task(
                orchestrator.start_diagnosis(session_id, filtered_inputs)
            )
            diagnosis_tasks.append(task)

        # 同时进行状态查询
        status_tasks = []
        for session_id in session_ids:
            task = asyncio.create_task(orchestrator.get_session_status(session_id))
            status_tasks.append(task)

        # 执行所有任务
        all_tasks = diagnosis_tasks + status_tasks
        results = await asyncio.gather(*all_tasks, return_exceptions=True)

        # 验证结果
        exceptions = [r for r in results if isinstance(r, Exception)]
        success_rate = (len(results) - len(exceptions)) / len(results) * 100

        print(f"资源竞争测试结果:")
        print(f"  并发数: {concurrent_count}")
        print(f"  总任务数: {len(all_tasks)}")
        print(f"  成功任务数: {len(results) - len(exceptions)}")
        print(f"  异常数: {len(exceptions)}")
        print(f"  成功率: {success_rate:.1f}%")

        # 成功率应该较高
        assert success_rate > 80.0

        # 等待诊断完成
        completed_count = 0
        for session_id in session_ids:
            for _ in range(50):  # 增加等待时间
                try:
                    status = await orchestrator.get_session_status(session_id)
                    if status["status"] == SessionStatus.COMPLETED.value:
                        completed_count += 1
                        break
                except Exception:
                    pass
                await asyncio.sleep(0.1)

        completion_rate = completed_count / concurrent_count * 100
        print(f"  完成率: {completion_rate:.1f}%")

        # 大部分会话应该能完成
        assert completion_rate > 70.0

    @pytest.mark.asyncio
    async def test_deadlock_prevention(
        self, orchestrator, concurrency_diagnosis_inputs
    ):
        """测试死锁预防"""
        session_count = 8
        enabled_diagnoses = [
            DiagnosisType.INQUIRY,
            DiagnosisType.LOOK,
            DiagnosisType.CALCULATION,
        ]

        # 创建多个会话
        session_ids = []
        for i in range(session_count):
            patient_info = PatientInfo(
                patient_id=f"deadlock_patient_{i}",
                name=f"死锁测试患者{i}",
                age=30 + i,
                gender="男" if i % 2 == 0 else "女",
            )

            session_id = await orchestrator.create_diagnosis_session(
                patient_info=patient_info, enabled_diagnoses=enabled_diagnoses
            )
            session_ids.append(session_id)

        # 创建可能导致死锁的操作模式
        async def complex_operations(session_id: str, operation_id: int):
            """复杂操作，可能导致死锁"""
            try:
                # 启动诊断
                filtered_inputs = [
                    inp
                    for inp in concurrency_diagnosis_inputs
                    if inp.diagnosis_type in enabled_diagnoses
                ]
                await orchestrator.start_diagnosis(session_id, filtered_inputs)

                # 随机延迟
                await asyncio.sleep(random.uniform(0.1, 0.5))

                # 获取状态
                await orchestrator.get_session_status(session_id)

                # 再次随机延迟
                await asyncio.sleep(random.uniform(0.1, 0.3))

                # 尝试获取结果（可能还未完成）
                try:
                    await orchestrator.get_session_result(session_id)
                except Exception:
                    pass  # 预期可能失败

                return f"操作{operation_id}完成"

            except Exception as e:
                return f"操作{operation_id}异常: {e}"

        # 并发执行复杂操作
        operation_tasks = []
        for i, session_id in enumerate(session_ids):
            task = asyncio.create_task(complex_operations(session_id, i))
            operation_tasks.append(task)

        # 设置超时以检测死锁
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*operation_tasks, return_exceptions=True),
                timeout=60.0,  # 60秒超时
            )

            # 验证没有死锁
            print("死锁预防测试结果:")
            for i, result in enumerate(results):
                print(f"  操作{i}: {result}")

            # 所有操作都应该完成（成功或失败）
            assert len(results) == session_count

        except asyncio.TimeoutError:
            pytest.fail("检测到可能的死锁 - 操作超时")

    @pytest.mark.asyncio
    async def test_memory_consistency(self, orchestrator, concurrency_diagnosis_inputs):
        """测试内存一致性"""
        session_count = 10
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK]

        # 创建多个会话
        session_ids = []
        for i in range(session_count):
            patient_info = PatientInfo(
                patient_id=f"consistency_patient_{i}",
                name=f"一致性测试患者{i}",
                age=30 + i,
                gender="男" if i % 2 == 0 else "女",
            )

            session_id = await orchestrator.create_diagnosis_session(
                patient_info=patient_info, enabled_diagnoses=enabled_diagnoses
            )
            session_ids.append(session_id)

        # 并发启动诊断
        for session_id in session_ids:
            filtered_inputs = [
                inp
                for inp in concurrency_diagnosis_inputs
                if inp.diagnosis_type in enabled_diagnoses
            ]
            await orchestrator.start_diagnosis(session_id, filtered_inputs)

        # 并发多次读取状态，验证一致性
        consistency_tasks = []
        for session_id in session_ids:
            for _ in range(5):  # 每个会话读取5次
                task = asyncio.create_task(orchestrator.get_session_status(session_id))
                consistency_tasks.append(task)

        # 执行所有读取操作
        status_results = await asyncio.gather(*consistency_tasks)

        # 验证同一会话的状态读取一致性
        session_status_map = {}
        for i, result in enumerate(status_results):
            session_index = i // 5  # 每5个结果对应一个会话
            session_id = session_ids[session_index]

            if session_id not in session_status_map:
                session_status_map[session_id] = []
            session_status_map[session_id].append(result["status"])

        # 验证每个会话的状态读取是一致的或者是合理的状态转换
        valid_transitions = {
            SessionStatus.CREATED.value: [SessionStatus.RUNNING.value],
            SessionStatus.RUNNING.value: [
                SessionStatus.COMPLETED.value,
                SessionStatus.FAILED.value,
            ],
            SessionStatus.COMPLETED.value: [],
            SessionStatus.FAILED.value: [],
        }

        for session_id, statuses in session_status_map.items():
            # 验证状态转换的合理性
            for i in range(len(statuses) - 1):
                current_status = statuses[i]
                next_status = statuses[i + 1]

                # 状态应该保持不变或者按照有效转换进行
                assert (
                    current_status == next_status
                    or next_status in valid_transitions.get(current_status, [])
                )

        print("内存一致性测试通过 - 所有状态转换都是有效的")
