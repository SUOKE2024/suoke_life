#!/usr/bin/env python3

"""
xiaoai-service性能测试脚本
测试服务在不同负载下的性能表现
"""

import argparse
import asyncio
import json
import logging
import statistics
import sys
import time
import uuid
from pathlib import Path
from unittest.mock import MagicMock

import matplotlib.pyplot as plt

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入需要测试的服务和模块
from internal.four_diagnosis.feature_extractor import FeatureExtractor
from internal.four_diagnosis.multimodal_fusion import MultimodalFusion
from internal.four_diagnosis.recommendation.health_advisor import HealthAdvisor
from internal.four_diagnosis.syndrome_analyzer import SyndromeAnalyzer
from internal.orchestrator.four_diagnosis_coordinator import FourDiagnosisCoordinator
from xiaoai_service.protos import four_diagnosis_pb2 as diagnosis_pb

logging.basicConfig(level=logging.INFO)
# 使用loguru logger

# 测试数据路径
TEST_DATA_DIR = Path(__file__).parent / 'data'

class PerformanceTester:
    """xiaoai-service性能测试器"""

    def __init__(self, use_mock=True, server_address=None):
        """
        初始化性能测试器

        Args:
            use_mock: 是否使用模拟服务
            server_address: 服务器地址(如果不使用模拟)
        """
        self.use_mock = use_mock
        self.server_address = server_address
        self.results = {
            'full_flow': [],
            'syndrome_analysis': [],
            'health_recommendations': []
        }

        self._setup_test_environment()

    def _setup_test_environment(self):
        """设置测试环境"""
        if self.use_mock:
            # 模拟服务客户端
            self.look_client = self._create_mock_look_client()
            self.listen_client = self._create_mock_listen_client()
            self.inquiry_client = self._create_mock_inquiry_client()
            self.palpation_client = self._create_mock_palpation_client()

            self.feature_extractor = FeatureExtractor()
            self.multimodal_fusion = MultimodalFusion()
            self.syndrome_analyzer = SyndromeAnalyzer()
            self.health_advisor = HealthAdvisor()

            self.coordinator = FourDiagnosisCoordinator(
                look_client=self.look_client,
                listen_client=self.listen_client,
                inquiry_client=self.inquiry_client,
                palpation_client=self.palpation_client,
                feature_extractor=self.feature_extractor,
                multimodal_fusion=self.multimodal_fusion,
                syndrome_analyzer=self.syndrome_analyzer,
                health_advisor=self.health_advisor
            )
        else:
            # 使用实际服务地址
            # 这部分需要根据实际部署情况进行实现
            pass

    def _create_mock_look_client(self):
        """创建模拟望诊服务客户端"""
        mock_client = MagicMock()

        look_response = MagicMock()
        look_response.features = [
            diagnosis_pb.DiagnosisFeature(
                feature_name="舌质",
                feature_value="淡红",
                confidence=0.92,
                category="tongue"
            ),
            diagnosis_pb.DiagnosisFeature(
                feature_name="舌苔",
                feature_value="薄白",
                confidence=0.88,
                category="tongue"
            ),
            diagnosis_pb.DiagnosisFeature(
                feature_name="面色",
                feature_value="偏白",
                confidence=0.85,
                category="face"
            )
        ]
        mock_client.analyze_tongue_image = lambda x: look_response
        mock_client.analyze_face_image = lambda x: look_response

        return mock_client

    def _create_mock_listen_client(self):
        """创建模拟闻诊服务客户端"""
        mock_client = MagicMock()

        listen_response = MagicMock()
        listen_response.features = [
            diagnosis_pb.DiagnosisFeature(
                feature_name="语音",
                feature_value="语速缓慢",
                confidence=0.82,
                category="voice"
            ),
            diagnosis_pb.DiagnosisFeature(
                feature_name="气息",
                feature_value="气短",
                confidence=0.75,
                category="voice"
            )
        ]
        mock_client.analyze_voice = lambda x: listen_response

        return mock_client

    def _create_mock_inquiry_client(self):
        """创建模拟问诊服务客户端"""
        mock_client = MagicMock()

        inquiry_response = MagicMock()
        inquiry_response.features = [
            diagnosis_pb.DiagnosisFeature(
                feature_name="主诉",
                feature_value="疲乏无力",
                confidence=0.95,
                category="symptom"
            ),
            diagnosis_pb.DiagnosisFeature(
                feature_name="食欲",
                feature_value="食欲不振",
                confidence=0.88,
                category="symptom"
            ),
            diagnosis_pb.DiagnosisFeature(
                feature_name="睡眠",
                feature_value="睡眠欠佳",
                confidence=0.80,
                category="symptom"
            )
        ]
        mock_client.analyze_inquiry = lambda x: inquiry_response

        return mock_client

    def _create_mock_palpation_client(self):
        """创建模拟切诊服务客户端"""
        mock_client = MagicMock()

        palpation_response = MagicMock()
        palpation_response.features = [
            diagnosis_pb.DiagnosisFeature(
                feature_name="脉象",
                feature_value="沉细",
                confidence=0.87,
                category="pulse"
            )
        ]
        mock_client.analyze_pulse = lambda x: palpation_response

        return mock_client

    async def test_full_flow_performance(self, num_requests):
        """
        测试完整流程的性能

        Args:
            num_requests: 请求数量
        """
        logger.info(f"开始测试完整流程性能 ({num_requests} 个请求)...")

        requests = []
        for _ in range(num_requests):
            request = diagnosis_pb.DiagnosisCoordinationRequest(
                user_id=f"perf_test_user_{i}",
                session_id=str(uuid.uuid4()),
                include_looking=True,
                include_listening=True,
                include_inquiry=True,
                include_palpation=True,
                looking_data=b'mock_image_data',
                listening_data=b'mock_audio_data',
                inquiry_data=json.dumps({
                    "chief_complaint": "疲乏无力,食欲不振",
                    "symptoms": ["疲乏", "食欲不振", "睡眠欠佳"],
                    "duration": "两周",
                    "history": "无特殊病史"
                }),
                palpation_data=b'mock_pulse_data',
                settings={"mode": "comprehensive"}
            )
            requests.append(request)

        times = []
        for i, _ in enumerate(requests):
            start_time = time.time()
            response = await self.coordinator.coordinate_diagnosis(request)
            end_time = time.time()
            elapsed_time = (end_time - start_time) * 1000  # 毫秒
            times.append(elapsed_time)

            # 验证响应是否有效
            if not response or not response.coordination_id:
                logger.warning(f"请求 {i} 返回无效响应")
                continue

            logger.info(f"请求 {i}: {elapsed_time:.2f} ms")

        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        p95_time = np.percentile(times, 95)

        # 记录结果
        self.results['full_flow'] = {
            'num_requests': num_requests,
            'avg_time': avg_time,
            'median_time': median_time,
            'min_time': min_time,
            'max_time': max_time,
            'p95_time': p95_time,
            'all_times': times
        }

        logger.info("完整流程性能测试结果:")
        logger.info(f"  平均时间: {avg_time:.2f} ms")
        logger.info(f"  中位数时间: {median_time:.2f} ms")
        logger.info(f"  最小时间: {min_time:.2f} ms")
        logger.info(f"  最大时间: {max_time:.2f} ms")
        logger.info(f"  95百分位时间: {p95_time:.2f} ms")

        return self.results['full_flow']

    async def test_syndrome_analysis_performance(self, num_requests):
        """
        测试证型分析性能

        Args:
            num_requests: 请求数量
        """
        logger.info(f"开始测试证型分析性能 ({num_requests} 个请求)...")

        fusion_results = []
        for _ in range(num_requests):
            fusion_result = diagnosis_pb.FusionResult(
                fusion_id=str(uuid.uuid4()),
                user_id=f"perf_test_user_{i}",
                session_id=str(uuid.uuid4()),
                created_at=int(time.time())
            )

            # 添加融合特征
            fused_features = diagnosis_pb.FusedFeatures()
            for feature_data in [
                ("舌质", "淡红", 0.92, "tongue"),
                ("舌苔", "薄白", 0.88, "tongue"),
                ("面色", "偏白", 0.85, "face"),
                ("语音", "语速缓慢", 0.82, "voice"),
                ("气息", "气短", 0.75, "voice"),
                ("主诉", "疲乏无力", 0.95, "symptom"),
                ("食欲", "食欲不振", 0.88, "symptom"),
                ("睡眠", "睡眠欠佳", 0.80, "symptom"),
                ("脉象", "沉细", 0.87, "pulse")
            ]:
                feature = fused_features.features.add()
                feature.feature_name = feature_data[0]
                feature.feature_value = feature_data[1]
                feature.confidence = feature_data[2]
                feature.category = feature_data[3]

            fusion_result.fused_features.CopyFrom(fused_features)
            fusion_results.append(fusion_result)

        times = []
        for i, _ in enumerate(fusion_results):
            start_time = time.time()
            response = await self.syndrome_analyzer.analyze_syndromes(fusion_result)
            end_time = time.time()
            elapsed_time = (end_time - start_time) * 1000  # 毫秒
            times.append(elapsed_time)

            # 验证响应是否有效
            if not response or not response.analysis_id:
                logger.warning(f"请求 {i} 返回无效响应")
                continue

            logger.info(f"请求 {i}: {elapsed_time:.2f} ms")

        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        p95_time = np.percentile(times, 95)

        # 记录结果
        self.results['syndrome_analysis'] = {
            'num_requests': num_requests,
            'avg_time': avg_time,
            'median_time': median_time,
            'min_time': min_time,
            'max_time': max_time,
            'p95_time': p95_time,
            'all_times': times
        }

        logger.info("证型分析性能测试结果:")
        logger.info(f"  平均时间: {avg_time:.2f} ms")
        logger.info(f"  中位数时间: {median_time:.2f} ms")
        logger.info(f"  最小时间: {min_time:.2f} ms")
        logger.info(f"  最大时间: {max_time:.2f} ms")
        logger.info(f"  95百分位时间: {p95_time:.2f} ms")

        return self.results['syndrome_analysis']

    async def test_health_recommendations_performance(self, num_requests):
        """
        测试健康建议生成性能

        Args:
            num_requests: 请求数量
        """
        logger.info(f"开始测试健康建议生成性能 ({num_requests} 个请求)...")

        analysis_results = []
        for _ in range(num_requests):
            analysis_result = diagnosis_pb.SyndromeAnalysisResult(
                analysis_id=str(uuid.uuid4()),
                user_id=f"perf_test_user_{i}",
                session_id=str(uuid.uuid4()),
                created_at=int(time.time()),
                fusion_id=str(uuid.uuid4()),
                analysis_confidence=0.85
            )

            # 添加证型
            syndrome = analysis_result.syndromes.add()
            syndrome.syndrome_id = "syndrome_001"
            syndrome.syndrome_name = "脾气虚证"
            syndrome.confidence = 0.9
            syndrome.description = "脾气虚弱,运化功能减退"
            syndrome.category = "脏腑辨证"

            # 添加证据
            evidence = syndrome.evidences.add()
            evidence.feature_name = "疲乏"
            evidence.feature_value = "疲乏无力"
            evidence.weight = 1.0

            # 添加体质评估
            analysis_result.constitution_assessment.dominant_type = "气虚质"
            analysis_result.constitution_assessment.assessment_confidence = 0.85

            # 添加第二个体质类型
            constitution = analysis_result.constitution_assessment.constitutions.add()
            constitution.type_name = "气虚质"
            constitution.score = 0.85
            constitution.description = "气虚质以疲乏、气短、易感冒为主要特征"

            constitution = analysis_result.constitution_assessment.constitutions.add()
            constitution.type_name = "湿热质"
            constitution.score = 0.35
            constitution.description = "湿热质以口苦、身重、油腻为主要特征"

            analysis_results.append(analysis_result)

        times = []
        for i, _ in enumerate(analysis_results):
            start_time = time.time()
            response = await self.health_advisor.generate_recommendations(analysis_result)
            end_time = time.time()
            elapsed_time = (end_time - start_time) * 1000  # 毫秒
            times.append(elapsed_time)

            # 验证响应是否有效
            if not response or not response.recommendations:
                logger.warning(f"请求 {i} 返回无效响应")
                continue

            logger.info(f"请求 {i}: {elapsed_time:.2f} ms")

        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        p95_time = np.percentile(times, 95)

        # 记录结果
        self.results['health_recommendations'] = {
            'num_requests': num_requests,
            'avg_time': avg_time,
            'median_time': median_time,
            'min_time': min_time,
            'max_time': max_time,
            'p95_time': p95_time,
            'all_times': times
        }

        logger.info("健康建议生成性能测试结果:")
        logger.info(f"  平均时间: {avg_time:.2f} ms")
        logger.info(f"  中位数时间: {median_time:.2f} ms")
        logger.info(f"  最小时间: {min_time:.2f} ms")
        logger.info(f"  最大时间: {max_time:.2f} ms")
        logger.info(f"  95百分位时间: {p95_time:.2f} ms")

        return self.results['health_recommendations']

    async def run_performance_tests(self, request_counts=None):
        """
        运行所有性能测试

        Args:
            request_counts: 要测试的请求数量列表
        """
        if request_counts is None:
            request_counts = [1, 5, 10, 20]
        logger.info("开始运行性能测试...")

        all_results = {}

        for count in request_counts:
            logger.info(f"\n=== 测试 {count} 个并发请求 ===")

            # 测试完整流程
            full_flow_results = await self.test_full_flow_performance(count)

            # 测试证型分析
            syndrome_analysis_results = await self.test_syndrome_analysis_performance(count)

            health_recommendations_results = await self.test_health_recommendations_performance(count)

            # 记录此并发级别的结果
            all_results[count] = {
                'full_flow': full_flow_results,
                'syndrome_analysis': syndrome_analysis_results,
                'health_recommendations': health_recommendations_results
            }

        self._generate_performance_report(all_results, request_counts)

        return all_results

    def _generate_performance_report(self, all_results, request_counts):
        """
        生成性能测试报告

        Args:
            all_results: 所有测试结果
            request_counts: 请求数量列表
        """
        logger.info("\n=== 生成性能测试报告 ===")

        # 准备数据
        avg_times_full_flow = [all_results[count]['full_flow']['avg_time'] for count in request_counts]
        avg_times_syndrome = [all_results[count]['syndrome_analysis']['avg_time'] for count in request_counts]
        avg_times_recommendations = [all_results[count]['health_recommendations']['avg_time'] for count in request_counts]

        p95_times_full_flow = [all_results[count]['full_flow']['p95_time'] for count in request_counts]
        p95_times_syndrome = [all_results[count]['syndrome_analysis']['p95_time'] for count in request_counts]
        p95_times_recommendations = [all_results[count]['health_recommendations']['p95_time'] for count in request_counts]

        plt.figure(figsize=(12, 10))

        # 平均响应时间图表
        plt.subplot(2, 1, 1)
        plt.plot(request_counts, avg_times_full_flow, 'o-', label='完整流程')
        plt.plot(request_counts, avg_times_syndrome, 's-', label='证型分析')
        plt.plot(request_counts, avg_times_recommendations, '^-', label='健康建议')
        plt.title('平均响应时间 (毫秒)')
        plt.xlabel('并发请求数')
        plt.ylabel('响应时间 (ms)')
        plt.grid(True)
        plt.legend()

        # P95响应时间图表
        plt.subplot(2, 1, 2)
        plt.plot(request_counts, p95_times_full_flow, 'o-', label='完整流程')
        plt.plot(request_counts, p95_times_syndrome, 's-', label='证型分析')
        plt.plot(request_counts, p95_times_recommendations, '^-', label='健康建议')
        plt.title('P95响应时间 (毫秒)')
        plt.xlabel('并发请求数')
        plt.ylabel('响应时间 (ms)')
        plt.grid(True)
        plt.legend()

        plt.tight_layout()

        # 保存图表
        report_dir = Path(__file__).parent / '../reports'
        Path(report_dir).mkdir(parents=True, exist_ok=True)
        plt.savefig(Path(report_dir) / f'performance_report_{time.strftime("%Y%m%d_%H%M%S")}.png')

        report_text = "# 小艾服务性能测试报告\n\n"
        report_text += f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report_text += "## 测试配置\n\n"
        report_text += f"- 测试环境: {'模拟环境' if self.use_mock else '实际服务'}\n"
        report_text += f"- 测试请求数: {request_counts}\n\n"

        report_text += "## 测试结果摘要\n\n"
        report_text += "### 平均响应时间 (毫秒)\n\n"
        report_text += "| 并发请求数 | 完整流程 | 证型分析 | 健康建议 |\n"
        report_text += "|------------|----------|----------|----------|\n"

        for count in request_counts:
            report_text += f"| {count} | {all_results[count]['full_flow']['avg_time']:.2f} | {all_results[count]['syndrome_analysis']['avg_time']:.2f} | {all_results[count]['health_recommendations']['avg_time']:.2f} |\n"

        report_text += "\n### P95响应时间 (毫秒)\n\n"
        report_text += "| 并发请求数 | 完整流程 | 证型分析 | 健康建议 |\n"
        report_text += "|------------|----------|----------|----------|\n"

        for count in request_counts:
            report_text += f"| {count} | {all_results[count]['full_flow']['p95_time']:.2f} | {all_results[count]['syndrome_analysis']['p95_time']:.2f} | {all_results[count]['health_recommendations']['p95_time']:.2f} |\n"

        # 保存报告文本
        with Path(Path(report_dir) / f'performance_report_{time.strftime("%Y%m%d_%H%M%S")}.md').open('w', encoding='utf-8') as f:
            f.write(report_text)

        logger.info(f"性能测试报告已生成: {report_dir}")

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='小艾服务性能测试工具')
    parser.add_argument('--real', action='store_true', help='使用实际服务而非模拟')
    parser.add_argument('--server', type=str, default='localhost:50051', help='服务器地址 (例如: localhost:50051)')
    parser.add_argument('--counts', type=str, default='1,5,10,20', help='测试请求数量,逗号分隔 (例如: 1,5,10,20)')

    args = parser.parse_args()

    # 解析请求数量
    request_counts = [int(x) for x in args.counts.split(',')]

    tester = PerformanceTester(use_mock=not args.real, server_address=args.server)

    # 运行测试
    await tester.run_performance_tests(request_counts=request_counts)

if __name__ == "__main__":
    asyncio.run(main())
