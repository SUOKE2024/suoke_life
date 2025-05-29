#!/usr/bin/env python3
"""
四诊合参流程集成测试
测试从数据输入到健康建议输出的完整流程
"""

import json
import logging
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# 将项目根目录添加到Python路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入测试目标模块
from internal.four_diagnosis.fusion.multimodal_fusion import MultimodalFusionEngine
from internal.four_diagnosis.reasoning.syndrome_differentiation import (
    SyndromeDifferentiationEngine,
)
from internal.four_diagnosis.recommendation.health_advisor import HealthAdvisor
from internal.orchestrator.diagnosis_coordinator import DiagnosisCoordinator

# 配置日志
logging.basicConfig(level=logging.INFO)
# 使用loguru logger

class TestFourDiagnosisIntegration(unittest.TestCase):
    """四诊合参流程集成测试"""

    def setUp(self):
        """测试前初始化"""
        self.fusion_engine = MultimodalFusionEngine({
            "algorithm": "weighted",
            "confidence_threshold": 0.6,
            "weights": {
                "looking": 1.0,
                "listening": 1.0,
                "inquiry": 1.5,
                "palpation": 1.2
            }
        })

        self.differentiation_engine = SyndromeDifferentiationEngine({
            "methods": [
                "eight_principles",
                "zang_fu",
                "qi_blood_fluid"
            ],
            "confidence_threshold": 0.6
        })

        self.health_advisor = HealthAdvisor({
            "max_recommendations": 10,
            "min_confidence": 0.6
        })

        # 准备测试数据
        self.prepare_test_data()

    def prepare_test_data(self):
        """准备测试数据"""
        # 读取测试数据
        self.looking_data = self._load_test_data("looking_data.json")
        self.listening_data = self._load_test_data("listening_data.json")
        self.inquiry_data = self._load_test_data("inquiry_data.json")
        self.palpation_data = self._load_test_data("palpation_data.json")

        if not all([self.looking_data, self.listening_data, self.inquiry_data, self.palpation_data]):
            logger.info("未找到测试数据文件,使用模拟数据...")

            self.looking_data = {
                "type": "LOOKING",
                "diagnosis_id": "look-12345",
                "source_service": "look-service",
                "confidence": 0.85,
                "features": [
                    {
                        "name": "舌淡",
                        "value": 0.8,
                        "confidence": 0.85,
                        "category": "tongue_color"
                    },
                    {
                        "name": "舌苔薄白",
                        "value": 0.75,
                        "confidence": 0.8,
                        "category": "tongue_coating"
                    },
                    {
                        "name": "面色萎黄",
                        "value": 0.7,
                        "confidence": 0.75,
                        "category": "face_color"
                    }
                ],
                "detailed_result": json.dumps({"tongue_color": "pale", "tongue_coating": "thin_white"}),
                "timestamp": int(time.time())
            }

            # 闻诊数据
            self.listening_data = {
                "type": "LISTENING",
                "diagnosis_id": "listen-12345",
                "source_service": "listen-service",
                "confidence": 0.8,
                "features": [
                    {
                        "name": "声音低弱",
                        "value": 0.7,
                        "confidence": 0.75,
                        "category": "voice_strength"
                    },
                    {
                        "name": "气短",
                        "value": 0.75,
                        "confidence": 0.8,
                        "category": "breath"
                    }
                ],
                "detailed_result": json.dumps({"voice_analysis": "weak"}),
                "timestamp": int(time.time())
            }

            # 问诊数据
            self.inquiry_data = {
                "type": "INQUIRY",
                "diagnosis_id": "inquiry-12345",
                "source_service": "inquiry-service",
                "confidence": 0.9,
                "features": [
                    {
                        "name": "乏力",
                        "value": 0.85,
                        "confidence": 0.9,
                        "category": "symptoms"
                    },
                    {
                        "name": "食欲不振",
                        "value": 0.8,
                        "confidence": 0.85,
                        "category": "symptoms"
                    },
                    {
                        "name": "腹胀",
                        "value": 0.75,
                        "confidence": 0.8,
                        "category": "symptoms"
                    },
                    {
                        "name": "大便溏薄",
                        "value": 0.7,
                        "confidence": 0.75,
                        "category": "symptoms"
                    }
                ],
                "detailed_result": json.dumps({"chief_complaint": "乏力,食欲不振"}),
                "timestamp": int(time.time())
            }

            # 切诊数据
            self.palpation_data = {
                "type": "PALPATION",
                "diagnosis_id": "palpation-12345",
                "source_service": "palpation-service",
                "confidence": 0.75,
                "features": [
                    {
                        "name": "脉缓弱",
                        "value": 0.7,
                        "confidence": 0.75,
                        "category": "pulse"
                    }
                ],
                "detailed_result": json.dumps({"pulse_type": "slow_weak"}),
                "timestamp": int(time.time())
            }

    def _load_test_data(self, filename):
        """从测试数据文件加载数据"""
        try:
            file_path = Path(Path(__file__).parent, "data", filename)
            if Path(file_path).exists():
                with Path(file_path).open(encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.warning(f"加载测试数据文件 {filename} 失败: {e!s}")
            return None

    def test_full_diagnosis_flow(self):
        """测试完整的四诊合参流程"""
        # 步骤1: 模拟四诊数据
        diagnosis_results = [
            self.looking_data,
            self.listening_data,
            self.inquiry_data,
            self.palpation_data
        ]

        fusion_result = self.fusion_engine.fuse_diagnosis_data(diagnosis_results)

        # 验证融合结果
        self.assertTrue(fusion_result["success"])
        self.assertIsInstance(fusion_result["syndromes"], list)
        self.assertGreater(len(fusion_result["syndromes"]), 0)

        differentiation_result = self.differentiation_engine.analyze_syndromes(fusion_result)

        # 验证辨证结果
        self.assertTrue(differentiation_result["success"])
        self.assertIsInstance(differentiation_result["syndromes"], list)
        self.assertGreater(len(differentiation_result["syndromes"]), 0)
        self.assertIsNotNone(differentiation_result["constitution"])

        health_recommendations = self.health_advisor.generate_recommendations(differentiation_result)

        # 验证健康建议
        self.assertTrue(health_recommendations["success"])
        self.assertIsInstance(health_recommendations["recommendations"], list)
        self.assertGreater(len(health_recommendations["recommendations"]), 0)

        has_spleen_qi_deficiency = False
        for syndrome in differentiation_result["syndromes"]:
            if syndrome["name"] == "脾气虚":
                has_spleen_qi_deficiency = True
                break

        self.assertTrue(has_spleen_qi_deficiency, "应该识别出脾气虚证候")

        # 检查是否有针对性健康建议
        has_relevant_recommendations = False
        for rec in health_recommendations["recommendations"]:
            if "山药" in rec["content"] or "大枣" in rec["content"] or "健脾" in rec["content"]:
                has_relevant_recommendations = True
                break

        self.assertTrue(has_relevant_recommendations, "应该有针对脾气虚的健康建议")

        # 打印主要结果
        logger.info(f"四诊合参完整流程测试通过,识别出 {len(differentiation_result['syndromes'])} 个证候")
        logger.info(f"体质类型: {differentiation_result['constitution']['name']}")
        logger.info(f"生成健康建议数量: {len(health_recommendations['recommendations'])}")

    @patch('internal.four_diagnosis.fusion.multimodal_fusion.MultimodalFusionEngine._compute_syndrome_scores')
    def test_fallback_mechanism(self, mock_compute_scores):
        """测试异常情况下的降级机制"""
        mock_compute_scores.side_effect = Exception("模拟计算失败")

        fusion_result = self.fusion_engine.fuse_diagnosis_data([
            self.looking_data,
            self.inquiry_data
        ])

        # 验证结果
        self.assertFalse(fusion_result["success"])
        self.assertIn("error", fusion_result)

    def test_missing_modality(self):
        """测试缺少某个模态数据的情况"""
        # 只提供两个模态数据
        partial_results = [
            self.inquiry_data,
            self.palpation_data
        ]

        fusion_result = self.fusion_engine.fuse_diagnosis_data(partial_results)

        # 验证融合结果
        self.assertTrue(fusion_result["success"])
        self.assertIsInstance(fusion_result["syndromes"], list)

        differentiation_result = self.differentiation_engine.analyze_syndromes(fusion_result)
        health_recommendations = self.health_advisor.generate_recommendations(differentiation_result)

        # 验证结果
        self.assertTrue(differentiation_result["success"])
        self.assertTrue(health_recommendations["success"])

    def test_contradictory_data(self):
        """测试矛盾数据处理"""
        contradictory_looking = self.looking_data.copy()
        contradictory_looking["features"].append({
            "name": "舌红",
            "value": 0.9,
            "confidence": 0.85,
            "category": "tongue_color"
        })

        results = [
            contradictory_looking,
            self.listening_data,
            self.inquiry_data,
            self.palpation_data
        ]

        fusion_result = self.fusion_engine.fuse_diagnosis_data(results)
        differentiation_result = self.differentiation_engine.analyze_syndromes(fusion_result)

        syndrome_names = [s["name"] for s in differentiation_result["syndromes"]]

        # 检查是否同时出现矛盾证候
        not_both_hot_cold = not ("寒证" in syndrome_names and "热证" in syndrome_names)
        self.assertTrue(not_both_hot_cold, "不应同时出现寒证和热证")

    @unittest.skip("需要模拟四诊服务,跳过此测试")
    async def test_diagnosis_coordinator(self):
        """测试四诊协调引擎 (需要模拟四诊服务)"""
        coordinator = DiagnosisCoordinator()

        # 模拟请求
        request = MagicMock()
        request.user_id = "test_user"
        request.session_id = "test_session"
        request.looking_data = b'binary_image_data'
        request.listening_data = b'binary_audio_data'
        request.inquiry_data = json.dumps({
            "symptoms": ["乏力", "食欲不振"],
            "duration": "三天"
        })
        request.palpation_data = json.dumps({
            "pulse_data": [0.5, 0.6, 0.7]
        })

        # 启用所有诊断
        request.include_looking = True
        request.include_listening = True
        request.include_inquiry = True
        request.include_palpation = True

        # 模拟四诊服务客户端
        coordinator.grpc_clients = {
            "looking": MagicMock(),
            "listening": MagicMock(),
            "inquiry": MagicMock(),
            "palpation": MagicMock()
        }

        coordinator.grpc_clients["looking"].AnalyzeImage = MagicMock(return_value=MagicMock(
            diagnosis_id="look-12345",
            confidence=0.85,
            features=[MagicMock(name="舌淡", value=0.8, confidence=0.85, category="tongue_color")]
        ))

        response = await coordinator.coordinate_diagnosis(request)

        # 验证结果
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.coordination_id)

    def test_performance_end_to_end(self):
        """测试端到端性能"""
        start_time = time.time()

        for _ in range(10):
            # 步骤1: 多模态融合
            fusion_result = self.fusion_engine.fuse_diagnosis_data([
                self.looking_data,
                self.listening_data,
                self.inquiry_data,
                self.palpation_data
            ])

            # 步骤2: 辨证分析
            differentiation_result = self.differentiation_engine.analyze_syndromes(fusion_result)

            self.health_advisor.generate_recommendations(differentiation_result)

        elapsed_time = time.time() - start_time

        # 打印性能结果
        logger.info(f"端到端性能测试: 10次完整流程耗时 {elapsed_time:.2f} 秒, 平均每次 {elapsed_time/10*1000:.2f} 毫秒")

        self.assertLess(elapsed_time/10, 0.2, "端到端性能不达标")

    def load_test_data(self, filename: str) -> bytes:
        """加载测试数据文件"""
        file_path = Path(__file__).parent / "data" / filename
        with open(file_path, 'rb') as f:
            return f.read()

if __name__ == '__main__':
    unittest.main()
