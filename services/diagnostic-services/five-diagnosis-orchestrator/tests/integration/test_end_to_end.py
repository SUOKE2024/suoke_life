"""
端到端集成测试

测试完整的五诊协同诊断流程
"""

import asyncio
import uuid
from datetime import datetime, timezone
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
def sample_patient_info():
    """示例患者信息"""
    return PatientInfo(
        patient_id=str(uuid.uuid4()),
        name="张三",
        age=35,
        gender="男",
        height=175.0,
        weight=70.0,
        occupation="程序员",
        location="北京",
        medical_history=["高血压家族史"],
        current_medications=[],
        allergies=["青霉素"],
    )


@pytest.fixture
def sample_diagnosis_inputs():
    """示例诊断输入"""
    return [
        DiagnosisInput(
            diagnosis_type=DiagnosisType.INQUIRY,
            data={
                "symptoms": {"头痛": 0.8, "失眠": 0.6, "疲劳": 0.7},
                "duration": "2周",
                "severity": "中度",
            },
        ),
        DiagnosisInput(
            diagnosis_type=DiagnosisType.LOOK,
            data={
                "tongue": {"color": "淡红", "coating": "薄白", "texture": "正常"},
                "face": {"complexion": "略显疲惫", "eyes": "略显干涩"},
            },
        ),
        DiagnosisInput(
            diagnosis_type=DiagnosisType.LISTEN,
            data={
                "voice": {"tone": "略显低沉", "volume": "正常", "clarity": "清晰"},
                "breathing": {"rhythm": "正常", "depth": "正常"},
            },
        ),
        DiagnosisInput(
            diagnosis_type=DiagnosisType.PALPATION,
            data={
                "pulse": {
                    "rate": 72,
                    "rhythm": "规律",
                    "strength": "中等",
                    "quality": "弦脉",
                }
            },
        ),
        DiagnosisInput(
            diagnosis_type=DiagnosisType.CALCULATION,
            data={
                "constitution_scores": {
                    "气虚质": 0.3,
                    "阳虚质": 0.2,
                    "阴虚质": 0.4,
                    "痰湿质": 0.1,
                    "湿热质": 0.0,
                    "血瘀质": 0.2,
                    "气郁质": 0.5,
                    "特禀质": 0.1,
                    "平和质": 0.2,
                }
            },
        ),
    ]


class TestEndToEndDiagnosis:
    """端到端诊断测试"""

    @pytest.mark.asyncio
    async def test_complete_diagnosis_workflow(
        self, orchestrator, sample_patient_info, sample_diagnosis_inputs
    ):
        """测试完整诊断工作流程"""
        # 1. 创建诊断会话
        enabled_diagnoses = [
            DiagnosisType.INQUIRY,
            DiagnosisType.LOOK,
            DiagnosisType.CALCULATION,
        ]
        session_id = await orchestrator.create_diagnosis_session(
            patient_info=sample_patient_info, enabled_diagnoses=enabled_diagnoses
        )

        assert session_id is not None
        assert len(session_id) > 0

        # 2. 检查会话状态
        status = await orchestrator.get_session_status(session_id)
        assert status["status"] == SessionStatus.CREATED.value
        assert status["progress"] == 0.0
        assert len(status["enabled_diagnoses"]) == 3

        # 3. 启动诊断
        filtered_inputs = [
            inp
            for inp in sample_diagnosis_inputs
            if inp.diagnosis_type in enabled_diagnoses
        ]

        await orchestrator.start_diagnosis(session_id, filtered_inputs)

        # 4. 等待诊断完成
        max_wait_time = 30  # 最大等待30秒
        wait_interval = 1  # 每秒检查一次

        for _ in range(max_wait_time):
            status = await orchestrator.get_session_status(session_id)
            if status["status"] == SessionStatus.COMPLETED.value:
                break
            elif status["status"] == SessionStatus.FAILED.value:
                pytest.fail(f"诊断失败: {status['errors']}")
            await asyncio.sleep(wait_interval)
        else:
            pytest.fail("诊断超时")

        # 5. 验证最终状态
        final_status = await orchestrator.get_session_status(session_id)
        assert final_status["status"] == SessionStatus.COMPLETED.value
        assert final_status["progress"] == 1.0
        assert final_status["total_duration"] is not None
        assert final_status["total_duration"] > 0

        # 6. 获取诊断结果
        result = await orchestrator.get_session_result(session_id)
        assert result is not None
        assert result.session_id == session_id
        assert result.overall_confidence > 0
        assert result.consistency_score >= 0
        assert result.completeness_score > 0

        # 7. 验证融合结果
        assert len(result.individual_results) == len(enabled_diagnoses)
        for diagnosis_type in enabled_diagnoses:
            assert diagnosis_type in result.individual_results
            individual_result = result.individual_results[diagnosis_type]
            assert individual_result.confidence > 0
            assert individual_result.status == "completed"

        # 8. 验证建议
        assert (
            len(result.treatment_recommendations) > 0
            or len(result.lifestyle_recommendations) > 0
        )

    @pytest.mark.asyncio
    async def test_parallel_execution_mode(
        self, orchestrator, sample_patient_info, sample_diagnosis_inputs
    ):
        """测试并行执行模式"""
        config = OrchestrationConfig(mode=OrchestrationMode.PARALLEL)

        # 创建会话
        enabled_diagnoses = [
            DiagnosisType.INQUIRY,
            DiagnosisType.LOOK,
            DiagnosisType.LISTEN,
        ]
        session_id = await orchestrator.create_diagnosis_session(
            patient_info=sample_patient_info,
            enabled_diagnoses=enabled_diagnoses,
            config=config,
        )

        # 记录开始时间
        start_time = datetime.now()

        # 启动诊断
        filtered_inputs = [
            inp
            for inp in sample_diagnosis_inputs
            if inp.diagnosis_type in enabled_diagnoses
        ]
        await orchestrator.start_diagnosis(session_id, filtered_inputs)

        # 等待完成
        for _ in range(30):
            status = await orchestrator.get_session_status(session_id)
            if status["status"] == SessionStatus.COMPLETED.value:
                break
            await asyncio.sleep(1)

        # 验证并行执行的性能优势
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        # 并行执行应该比顺序执行快
        assert total_time < 15  # 假设并行执行应在15秒内完成

        # 验证结果
        result = await orchestrator.get_session_result(session_id)
        assert result is not None
        assert len(result.individual_results) == len(enabled_diagnoses)

    @pytest.mark.asyncio
    async def test_sequential_execution_mode(
        self, orchestrator, sample_patient_info, sample_diagnosis_inputs
    ):
        """测试顺序执行模式"""
        config = OrchestrationConfig(mode=OrchestrationMode.SEQUENTIAL)

        # 创建会话
        enabled_diagnoses = [
            DiagnosisType.INQUIRY,
            DiagnosisType.LOOK,
            DiagnosisType.CALCULATION,
        ]
        session_id = await orchestrator.create_diagnosis_session(
            patient_info=sample_patient_info,
            enabled_diagnoses=enabled_diagnoses,
            config=config,
        )

        # 启动诊断
        filtered_inputs = [
            inp
            for inp in sample_diagnosis_inputs
            if inp.diagnosis_type in enabled_diagnoses
        ]
        await orchestrator.start_diagnosis(session_id, filtered_inputs)

        # 等待完成
        for _ in range(30):
            status = await orchestrator.get_session_status(session_id)
            if status["status"] == SessionStatus.COMPLETED.value:
                break
            await asyncio.sleep(1)

        # 验证结果
        result = await orchestrator.get_session_result(session_id)
        assert result is not None
        assert len(result.individual_results) == len(enabled_diagnoses)

    @pytest.mark.asyncio
    async def test_priority_based_execution(
        self, orchestrator, sample_patient_info, sample_diagnosis_inputs
    ):
        """测试基于优先级的执行"""
        config = OrchestrationConfig(mode=OrchestrationMode.PRIORITY_BASED)

        # 创建会话
        enabled_diagnoses = list(DiagnosisType)  # 启用所有诊断类型
        session_id = await orchestrator.create_diagnosis_session(
            patient_info=sample_patient_info,
            enabled_diagnoses=enabled_diagnoses,
            config=config,
        )

        # 启动诊断
        await orchestrator.start_diagnosis(session_id, sample_diagnosis_inputs)

        # 等待完成
        for _ in range(30):
            status = await orchestrator.get_session_status(session_id)
            if status["status"] == SessionStatus.COMPLETED.value:
                break
            await asyncio.sleep(1)

        # 验证结果
        result = await orchestrator.get_session_result(session_id)
        assert result is not None
        assert len(result.individual_results) == len(enabled_diagnoses)

        # 验证问诊结果存在（优先级最高）
        assert DiagnosisType.INQUIRY in result.individual_results

    @pytest.mark.asyncio
    async def test_adaptive_execution_mode(
        self, orchestrator, sample_patient_info, sample_diagnosis_inputs
    ):
        """测试自适应执行模式"""
        config = OrchestrationConfig(mode=OrchestrationMode.ADAPTIVE)

        # 创建会话
        enabled_diagnoses = [
            DiagnosisType.INQUIRY,
            DiagnosisType.LOOK,
            DiagnosisType.CALCULATION,
        ]
        session_id = await orchestrator.create_diagnosis_session(
            patient_info=sample_patient_info,
            enabled_diagnoses=enabled_diagnoses,
            config=config,
        )

        # 启动诊断
        filtered_inputs = [
            inp
            for inp in sample_diagnosis_inputs
            if inp.diagnosis_type in enabled_diagnoses
        ]
        await orchestrator.start_diagnosis(session_id, filtered_inputs)

        # 等待完成
        for _ in range(30):
            status = await orchestrator.get_session_status(session_id)
            if status["status"] == SessionStatus.COMPLETED.value:
                break
            await asyncio.sleep(1)

        # 验证结果
        result = await orchestrator.get_session_result(session_id)
        assert result is not None
        assert len(result.individual_results) == len(enabled_diagnoses)

    @pytest.mark.asyncio
    async def test_session_cancellation(
        self, orchestrator, sample_patient_info, sample_diagnosis_inputs
    ):
        """测试会话取消"""
        # 创建会话
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK]
        session_id = await orchestrator.create_diagnosis_session(
            patient_info=sample_patient_info, enabled_diagnoses=enabled_diagnoses
        )

        # 启动诊断
        filtered_inputs = [
            inp
            for inp in sample_diagnosis_inputs
            if inp.diagnosis_type in enabled_diagnoses
        ]
        await orchestrator.start_diagnosis(session_id, filtered_inputs)

        # 等待一小段时间后取消
        await asyncio.sleep(1)
        await orchestrator.cancel_session(session_id)

        # 验证会话状态
        status = await orchestrator.get_session_status(session_id)
        assert status["status"] == SessionStatus.CANCELLED.value

    @pytest.mark.asyncio
    async def test_error_handling(self, orchestrator, sample_patient_info):
        """测试错误处理"""
        # 测试无效的诊断输入
        with pytest.raises(Exception):
            await orchestrator.create_diagnosis_session(
                patient_info=sample_patient_info,
                enabled_diagnoses=[],  # 空的诊断类型列表
            )

        # 测试不存在的会话
        with pytest.raises(Exception):
            await orchestrator.get_session_status("non-existent-session")

    @pytest.mark.asyncio
    async def test_multiple_concurrent_sessions(
        self, orchestrator, sample_patient_info, sample_diagnosis_inputs
    ):
        """测试多个并发会话"""
        session_count = 3
        sessions = []

        # 创建多个会话
        for i in range(session_count):
            patient_info = PatientInfo(
                patient_id=f"patient_{i}",
                name=f"患者{i}",
                age=30 + i,
                gender="男" if i % 2 == 0 else "女",
            )

            enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK]
            session_id = await orchestrator.create_diagnosis_session(
                patient_info=patient_info, enabled_diagnoses=enabled_diagnoses
            )
            sessions.append(session_id)

        # 并发启动所有诊断
        tasks = []
        for session_id in sessions:
            filtered_inputs = [
                inp
                for inp in sample_diagnosis_inputs
                if inp.diagnosis_type in [DiagnosisType.INQUIRY, DiagnosisType.LOOK]
            ]
            task = asyncio.create_task(
                orchestrator.start_diagnosis(session_id, filtered_inputs)
            )
            tasks.append(task)

        # 等待所有任务完成
        await asyncio.gather(*tasks)

        # 等待所有会话完成
        for session_id in sessions:
            for _ in range(30):
                status = await orchestrator.get_session_status(session_id)
                if status["status"] in [
                    SessionStatus.COMPLETED.value,
                    SessionStatus.FAILED.value,
                ]:
                    break
                await asyncio.sleep(1)

        # 验证所有会话都完成了
        for session_id in sessions:
            status = await orchestrator.get_session_status(session_id)
            assert status["status"] == SessionStatus.COMPLETED.value

            result = await orchestrator.get_session_result(session_id)
            assert result is not None

    @pytest.mark.asyncio
    async def test_system_metrics(
        self, orchestrator, sample_patient_info, sample_diagnosis_inputs
    ):
        """测试系统指标"""
        # 执行一个完整的诊断流程
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.LOOK]
        session_id = await orchestrator.create_diagnosis_session(
            patient_info=sample_patient_info, enabled_diagnoses=enabled_diagnoses
        )

        filtered_inputs = [
            inp
            for inp in sample_diagnosis_inputs
            if inp.diagnosis_type in enabled_diagnoses
        ]
        await orchestrator.start_diagnosis(session_id, filtered_inputs)

        # 等待完成
        for _ in range(30):
            status = await orchestrator.get_session_status(session_id)
            if status["status"] == SessionStatus.COMPLETED.value:
                break
            await asyncio.sleep(1)

        # 获取系统指标
        metrics = await orchestrator.get_system_metrics()

        # 验证指标
        assert metrics["total_sessions"] >= 1
        assert metrics["successful_sessions"] >= 1
        assert metrics["success_rate"] > 0
        assert metrics["average_processing_time"] > 0
        assert "service_availability" in metrics

    @pytest.mark.asyncio
    async def test_diagnosis_quality_assessment(
        self, orchestrator, sample_patient_info, sample_diagnosis_inputs
    ):
        """测试诊断质量评估"""
        # 创建高质量的诊断会话（启用所有诊断类型）
        enabled_diagnoses = list(DiagnosisType)
        session_id = await orchestrator.create_diagnosis_session(
            patient_info=sample_patient_info, enabled_diagnoses=enabled_diagnoses
        )

        # 启动诊断
        await orchestrator.start_diagnosis(session_id, sample_diagnosis_inputs)

        # 等待完成
        for _ in range(30):
            status = await orchestrator.get_session_status(session_id)
            if status["status"] == SessionStatus.COMPLETED.value:
                break
            await asyncio.sleep(1)

        # 获取结果并评估质量
        result = await orchestrator.get_session_result(session_id)
        assert result is not None

        # 验证质量指标
        assert result.overall_confidence > 0
        assert result.consistency_score >= 0
        assert result.completeness_score > 0

        # 验证质量等级
        quality_grade = result.quality_grade
        assert quality_grade in ["优秀", "良好", "一般", "较差"]

        # 如果启用了所有诊断类型，完整性分数应该是1.0
        assert result.completeness_score == 1.0

    @pytest.mark.asyncio
    async def test_recommendation_generation(
        self, orchestrator, sample_patient_info, sample_diagnosis_inputs
    ):
        """测试建议生成"""
        # 创建会话
        enabled_diagnoses = [DiagnosisType.INQUIRY, DiagnosisType.CALCULATION]
        session_id = await orchestrator.create_diagnosis_session(
            patient_info=sample_patient_info, enabled_diagnoses=enabled_diagnoses
        )

        # 启动诊断
        filtered_inputs = [
            inp
            for inp in sample_diagnosis_inputs
            if inp.diagnosis_type in enabled_diagnoses
        ]
        await orchestrator.start_diagnosis(session_id, filtered_inputs)

        # 等待完成
        for _ in range(30):
            status = await orchestrator.get_session_status(session_id)
            if status["status"] == SessionStatus.COMPLETED.value:
                break
            await asyncio.sleep(1)

        # 验证建议生成
        result = await orchestrator.get_session_result(session_id)
        assert result is not None

        # 至少应该有一种类型的建议
        total_recommendations = (
            len(result.treatment_recommendations)
            + len(result.lifestyle_recommendations)
            + len(result.follow_up_recommendations)
        )
        assert total_recommendations > 0

        # 验证建议内容不为空
        for recommendation in result.treatment_recommendations:
            assert len(recommendation.strip()) > 0

        for recommendation in result.lifestyle_recommendations:
            assert len(recommendation.strip()) > 0

        for recommendation in result.follow_up_recommendations:
            assert len(recommendation.strip()) > 0
