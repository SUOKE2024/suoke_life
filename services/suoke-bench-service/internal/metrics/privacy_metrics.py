"""隐私安全评测指标实现。"""

from dataclasses import dataclass
from typing import Any

from .agent_metrics import MetricResult
from .metrics import Metric

@dataclass
class PrivacyTestCase:
    """隐私测试用例数据类。"""

    case_id: str  # 测试用例ID
    data_type: str  # 数据类型
    privacy_level: int  # 隐私等级(1-5)
    test_type: str  # 测试类型
    input_data: dict[str, Any]  # 输入数据
    expected_output: dict[str, Any]  # 期望输出
    attack_vectors: list[str]  # 攻击向量

@dataclass
class ZKPTestCase:
    """零知识证明测试用例数据类。"""

    case_id: str  # 测试用例ID
    proof_type: str  # 证明类型
    public_input: dict[str, Any]  # 公开输入
    private_input: dict[str, Any]  # 私密输入
    expected_result: bool  # 期望结果
    verification_time: float  # 验证时间(ms)

@dataclass
class PrivacyTestResult:
    """隐私测试结果数据类。"""

    case_id: str  # 测试用例ID
    success: bool  # 是否成功
    leakage_detected: bool  # 是否检测到泄露
    leakage_type: str | None  # 泄露类型
    leakage_severity: float | None  # 泄露严重程度
    mitigation_success: bool | None  # 缓解措施是否成功
    execution_time: float  # 执行时间(ms)

@dataclass
class ZKPTestResult:
    """零知识证明测试结果数据类。"""

    case_id: str  # 测试用例ID
    proof_generated: bool  # 是否生成证明
    proof_verified: bool  # 是否验证成功
    generation_time: float  # 生成时间(ms)
    verification_time: float  # 验证时间(ms)
    proof_size: int  # 证明大小(bytes)

class PrivacyVerificationMetric(Metric):
    """隐私验证评测指标。"""

    def __init__(self, threshold: float = 0.95):
        super().__init__("privacy_verification", threshold, "", True)
        self.description = "评估隐私保护机制的有效性"

    def calculate(
        self,
        privacy_cases: list[PrivacyTestCase],
        privacy_results: list[PrivacyTestResult],
        zkp_cases: list[ZKPTestCase],
        zkp_results: list[ZKPTestResult],
    ) -> MetricResult:
        """计算隐私验证的评测指标。"""

        # 计算隐私保护指标
        privacy_score = self._calculate_privacy_score(privacy_cases, privacy_results)

        # 计算零知识证明指标
        zkp_score = self._calculate_zkp_score(zkp_cases, zkp_results)

        # 计算性能指标
        performance = self._calculate_performance_metrics(privacy_results, zkp_results)

        # 计算加权总分
        weights = {"privacy": 0.4, "zkp": 0.4, "performance": 0.2}

        total_score = (
            weights["privacy"] * privacy_score["overall"]
            + weights["zkp"] * zkp_score["overall"]
            + weights["performance"] * performance["overall"]
        )

        return MetricResult(
            name=self.name,
            value=total_score,
            threshold=self.threshold,
            details={
                "privacy_protection": privacy_score,
                "zero_knowledge_proof": zkp_score,
                "performance": performance,
            },
        )

    def _calculate_privacy_score(
        self, cases: list[PrivacyTestCase], results: list[PrivacyTestResult]
    ) -> dict[str, float]:
        """计算隐私保护指标。"""

        # 计算基本成功率
        success_rate = sum(1 for r in results if r.success) / len(results)

        # 计算泄露检测率
        leakage_detection_rate = sum(1 for r in results if r.leakage_detected) / len(
            results
        )

        # 计算泄露严重程度
        severity_scores = [
            r.leakage_severity for r in results if r.leakage_severity is not None
        ]
        avg_severity = np.mean(severity_scores) if severity_scores else 0.0

        # 计算缓解成功率
        mitigation_results = [
            r.mitigation_success for r in results if r.mitigation_success is not None
        ]
        mitigation_rate = (
            sum(1 for m in mitigation_results if m) / len(mitigation_results)
            if mitigation_results
            else 0.0
        )

        # 计算隐私等级覆盖度
        privacy_levels = {case.privacy_level for case in cases}
        level_coverage = len(privacy_levels) / 5  # 假设最高隐私等级为5

        # 计算整体隐私保护分数
        weights = {
            "success_rate": 0.3,
            "leakage_detection": 0.2,
            "severity": 0.2,
            "mitigation": 0.2,
            "coverage": 0.1,
        }

        # 注意：泄露检测率和严重程度是负向指标
        leakage_score = 1.0 - (leakage_detection_rate * avg_severity)

        overall = (
            weights["success_rate"] * success_rate
            + weights["leakage_detection"] * leakage_score
            + weights["severity"] * (1.0 - avg_severity)
            + weights["mitigation"] * mitigation_rate
            + weights["coverage"] * level_coverage
        )

        return {
            "overall": overall,
            "success_rate": success_rate,
            "leakage_detection_rate": leakage_detection_rate,
            "average_severity": avg_severity,
            "mitigation_rate": mitigation_rate,
            "level_coverage": level_coverage,
        }

    def _calculate_zkp_score(
        self, cases: list[ZKPTestCase], results: list[ZKPTestResult]
    ) -> dict[str, float]:
        """计算零知识证明指标。"""

        # 计算证明生成成功率
        generation_rate = sum(1 for r in results if r.proof_generated) / len(results)

        # 计算验证成功率
        verification_rate = sum(1 for r in results if r.proof_verified) / len(results)

        # 计算时间效率得分
        generation_times = [r.generation_time for r in results]
        verification_times = [r.verification_time for r in results]

        # 假设基准时间为1000ms
        gen_time_score = np.mean([max(0, 1 - (t / 1000)) for t in generation_times])
        ver_time_score = np.mean([max(0, 1 - (t / 1000)) for t in verification_times])

        # 计算证明大小得分
        # 假设基准大小为10KB
        size_scores = [max(0, 1 - (r.proof_size / 10240)) for r in results]
        size_score = np.mean(size_scores)

        # 计算整体零知识证明分数
        weights = {
            "generation": 0.25,
            "verification": 0.25,
            "gen_time": 0.2,
            "ver_time": 0.2,
            "size": 0.1,
        }

        overall = (
            weights["generation"] * generation_rate
            + weights["verification"] * verification_rate
            + weights["gen_time"] * gen_time_score
            + weights["ver_time"] * ver_time_score
            + weights["size"] * size_score
        )

        return {
            "overall": overall,
            "generation_success_rate": generation_rate,
            "verification_success_rate": verification_rate,
            "generation_time_score": gen_time_score,
            "verification_time_score": ver_time_score,
            "proof_size_score": size_score,
        }

    def _calculate_performance_metrics(
        self, privacy_results: list[PrivacyTestResult], zkp_results: list[ZKPTestResult]
    ) -> dict[str, float]:
        """计算性能指标。"""

        # 计算隐私测试执行时间得分
        privacy_times = [r.execution_time for r in privacy_results]
        avg_privacy_time = np.mean(privacy_times)
        privacy_time_score = max(0, 1 - (avg_privacy_time / 1000))  # 基准1000ms

        # 计算ZKP执行时间得分
        zkp_times = [r.generation_time + r.verification_time for r in zkp_results]
        avg_zkp_time = np.mean(zkp_times)
        zkp_time_score = max(0, 1 - (avg_zkp_time / 2000))  # 基准2000ms

        # 计算时间稳定性
        privacy_time_std = np.std(privacy_times)
        zkp_time_std = np.std(zkp_times)

        privacy_stability = max(0, 1 - (privacy_time_std / 500))  # 基准500ms
        zkp_stability = max(0, 1 - (zkp_time_std / 1000))  # 基准1000ms

        # 计算整体性能分数
        weights = {
            "privacy_time": 0.3,
            "zkp_time": 0.3,
            "privacy_stability": 0.2,
            "zkp_stability": 0.2,
        }

        overall = (
            weights["privacy_time"] * privacy_time_score
            + weights["zkp_time"] * zkp_time_score
            + weights["privacy_stability"] * privacy_stability
            + weights["zkp_stability"] * zkp_stability
        )

        return {
            "overall": overall,
            "privacy_time_score": privacy_time_score,
            "zkp_time_score": zkp_time_score,
            "privacy_stability": privacy_stability,
            "zkp_stability": zkp_stability,
            "avg_privacy_time": avg_privacy_time,
            "avg_zkp_time": avg_zkp_time,
        }
