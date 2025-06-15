"""评测指标测试。"""

import unittest
import numpy as np
from typing import List, Dict, Any
from internal.metrics.tcm_metrics import (
    TongueFeature,
    FaceFeature,
    PulseFeature,
    TongueRecognitionMetric,
    FaceRecognitionMetric,
    PulseRecognitionMetric,
    ConstitutionClassificationMetric
)
from internal.metrics.agent_metrics import (
    DialogueTurn,
    TaskCompletion,
    AgentCollaborationMetric
)
from internal.metrics.privacy_metrics import (
    PrivacyTestCase,
    ZKPTestCase,
    PrivacyTestResult,
    ZKPTestResult,
    PrivacyVerificationMetric
)
from internal.metrics.edge_metrics import (
    DeviceInfo,
    ModelInfo,
    PerformanceMetrics,
    InferenceMetrics,
    EdgePerformanceMetric
)

class TestTCMMetrics(unittest.TestCase):
    """中医四诊指标测试。"""
    
    def setUp(self):
        """测试准备。"""
        # 创建舌象测试数据
        self.tongue_features = [
            TongueFeature(
                color="pale",
                coating="thin_white",
                shape="normal",
                moisture="normal",
                cracks=["central"],
                spots=[{"x": 10, "y": 10, "width": 5, "height": 5}]
            ),
            TongueFeature(
                color="red",
                coating="yellow",
                shape="swollen",
                moisture="dry",
                cracks=["central", "transverse"],
                spots=[{"x": 20, "y": 20, "width": 8, "height": 8}]
            )
        ]
        
        # 创建面色测试数据
        self.face_features = [
            FaceFeature(
                color="normal",
                luster="bright",
                expression="relaxed",
                areas={"forehead": "normal", "cheeks": "rosy"}
            ),
            FaceFeature(
                color="pale",
                luster="dull",
                expression="tired",
                areas={"forehead": "pale", "cheeks": "pale"}
            )
        ]
        
        # 创建脉象测试数据
        self.pulse_features = [
            PulseFeature(
                frequency=72.0,
                strength="moderate",
                rhythm="regular",
                width="normal",
                depth="moderate",
                length="normal"
            ),
            PulseFeature(
                frequency=85.0,
                strength="strong",
                rhythm="irregular",
                width="wide",
                depth="superficial",
                length="long"
            )
        ]
    
    def test_tongue_recognition_metric(self):
        """测试舌象识别指标。"""
        metric = TongueRecognitionMetric()
        result = metric.calculate(self.tongue_features, self.tongue_features)
        
        self.assertGreaterEqual(result.value, 0.0)
        self.assertLessEqual(result.value, 1.0)
        self.assertIn('color_accuracy', result.details)
        self.assertIn('coating_accuracy', result.details)
        self.assertIn('shape_accuracy', result.details)
        self.assertIn('moisture_accuracy', result.details)
        self.assertIn('cracks_f1', result.details)
        self.assertIn('spots_iou', result.details)
    
    def test_face_recognition_metric(self):
        """测试面色识别指标。"""
        metric = FaceRecognitionMetric()
        result = metric.calculate(self.face_features, self.face_features)
        
        self.assertGreaterEqual(result.value, 0.0)
        self.assertLessEqual(result.value, 1.0)
        self.assertIn('color_accuracy', result.details)
        self.assertIn('luster_accuracy', result.details)
        self.assertIn('expression_accuracy', result.details)
        self.assertIn('areas_accuracy', result.details)
    
    def test_pulse_recognition_metric(self):
        """测试脉象识别指标。"""
        metric = PulseRecognitionMetric()
        result = metric.calculate(self.pulse_features, self.pulse_features)
        
        self.assertGreaterEqual(result.value, 0.0)
        self.assertLessEqual(result.value, 1.0)
        self.assertIn('frequency_accuracy', result.details)
        self.assertIn('strength_accuracy', result.details)
        self.assertIn('rhythm_accuracy', result.details)
        self.assertIn('width_accuracy', result.details)
        self.assertIn('depth_accuracy', result.details)
        self.assertIn('length_accuracy', result.details)
    
    def test_constitution_classification_metric(self):
        """测试体质辨识指标。"""
        metric = ConstitutionClassificationMetric()
        predictions = ["balanced", "qi_deficiency"]
        ground_truth = ["balanced", "qi_deficiency"]
        confidences = [0.9, 0.85]
        
        result = metric.calculate(predictions, ground_truth, confidences)
        
        self.assertGreaterEqual(result.value, 0.0)
        self.assertLessEqual(result.value, 1.0)
        self.assertIn('accuracy', result.details)
        self.assertIn('precision', result.details)
        self.assertIn('recall', result.details)
        self.assertIn('f1', result.details)
        self.assertIn('confidence_weighted_accuracy', result.details)

class TestAgentMetrics(unittest.TestCase):
    """智能体协作指标测试。"""
    
    def setUp(self):
        """测试准备。"""
        # 创建对话轮次测试数据
        self.dialogue_turns = [
            DialogueTurn(
                agent_id="xiaoai",
                role="leader",
                content="您好，我是小艾，请问有什么可以帮您？",
                intent="greeting",
                entities=[],
                confidence=0.95,
                response_time=100.0,
                context_relevance=1.0
            ),
            DialogueTurn(
                agent_id="xiaoke",
                role="assistant",
                content="我注意到您最近的睡眠质量不太好。",
                intent="information",
                entities=[{"type": "symptom", "value": "poor_sleep", "confidence": 0.9}],
                confidence=0.88,
                response_time=150.0,
                context_relevance=0.92
            )
        ]
        
        # 创建任务完成情况测试数据
        self.task_completion = TaskCompletion(
            task_id="health_consultation_001",
            status="completed",
            duration=280.0,
            steps=["greeting", "information_gathering", "analysis", "suggestion"],
            agent_contributions={
                "xiaoai": 0.4,
                "xiaoke": 0.3,
                "laoke": 0.2,
                "soer": 0.1
            },
            user_satisfaction=0.9
        )
    
    def test_agent_collaboration_metric(self):
        """测试智能体协作指标。"""
        metric = AgentCollaborationMetric()
        result = metric.calculate(self.dialogue_turns, self.task_completion)
        
        self.assertGreaterEqual(result.value, 0.0)
        self.assertLessEqual(result.value, 1.0)
        self.assertIn('dialogue_quality', result.details)
        self.assertIn('task_success', result.details)
        self.assertIn('collaboration_efficiency', result.details)
        self.assertIn('performance', result.details)

class TestPrivacyMetrics(unittest.TestCase):
    """隐私安全指标测试。"""
    
    def setUp(self):
        """测试准备。"""
        # 创建隐私测试用例数据
        self.privacy_cases = [
            PrivacyTestCase(
                case_id="privacy_001",
                data_type="health_record",
                privacy_level=4,
                test_type="data_access",
                input_data={"user_id": "123", "record_type": "medical"},
                expected_output={"status": "authorized"},
                attack_vectors=["unauthorized_access", "data_inference"]
            )
        ]
        
        # 创建隐私测试结果数据
        self.privacy_results = [
            PrivacyTestResult(
                case_id="privacy_001",
                success=True,
                leakage_detected=False,
                leakage_type=None,
                leakage_severity=None,
                mitigation_success=None,
                execution_time=150.0
            )
        ]
        
        # 创建ZKP测试用例数据
        self.zkp_cases = [
            ZKPTestCase(
                case_id="zkp_001",
                proof_type="groth16",
                public_input={"commitment": "0x123..."},
                private_input={"secret": "0x456..."},
                expected_result=True,
                verification_time=100.0
            )
        ]
        
        # 创建ZKP测试结果数据
        self.zkp_results = [
            ZKPTestResult(
                case_id="zkp_001",
                proof_generated=True,
                proof_verified=True,
                generation_time=200.0,
                verification_time=50.0,
                proof_size=1024
            )
        ]
    
    def test_privacy_verification_metric(self):
        """测试隐私验证指标。"""
        metric = PrivacyVerificationMetric()
        result = metric.calculate(
            self.privacy_cases,
            self.privacy_results,
            self.zkp_cases,
            self.zkp_results
        )
        
        self.assertGreaterEqual(result.value, 0.0)
        self.assertLessEqual(result.value, 1.0)
        self.assertIn('privacy_protection', result.details)
        self.assertIn('zero_knowledge_proof', result.details)
        self.assertIn('performance', result.details)

class TestEdgeMetrics(unittest.TestCase):
    """端侧性能指标测试。"""
    
    def setUp(self):
        """测试准备。"""
        # 创建设备信息测试数据
        self.device_info = DeviceInfo(
            device_id="device_001",
            model="iPhone 13",
            os="iOS",
            os_version="15.0",
            cpu_info={"cores": 6, "frequency": "2.4GHz"},
            memory_size=4096,
            storage_size=128000,
            battery_capacity=3000
        )
        
        # 创建模型信息测试数据
        self.model_info = ModelInfo(
            model_id="tcm_diagnosis_001",
            version="1.0.0",
            task_type="classification",
            model_size=50,
            quantization="int8",
            optimization=["pruning", "distillation"]
        )
        
        # 创建性能指标测试数据
        self.perf_metrics = [
            PerformanceMetrics(
                cpu_usage=30.0,
                memory_usage=200.0,
                power_usage=500.0,
                battery_impact=50.0,
                storage_io=5.0,
                network_io=1.0,
                temperature=35.0
            ),
            PerformanceMetrics(
                cpu_usage=35.0,
                memory_usage=220.0,
                power_usage=550.0,
                battery_impact=55.0,
                storage_io=6.0,
                network_io=1.2,
                temperature=36.0
            )
        ]
        
        # 创建推理性能测试数据
        self.infer_metrics = [
            InferenceMetrics(
                latency=50.0,
                throughput=20.0,
                accuracy=0.92,
                initialization_time=500.0,
                memory_footprint=100.0
            ),
            InferenceMetrics(
                latency=55.0,
                throughput=18.0,
                accuracy=0.91,
                initialization_time=520.0,
                memory_footprint=105.0
            )
        ]
    
    def test_edge_performance_metric(self):
        """测试端侧性能指标。"""
        metric = EdgePerformanceMetric()
        result = metric.calculate(
            self.device_info,
            self.model_info,
            self.perf_metrics,
            self.infer_metrics
        )
        
        self.assertGreaterEqual(result.value, 0.0)
        self.assertLessEqual(result.value, 1.0)
        self.assertIn('resource_usage', result.details)
        self.assertIn('inference_performance', result.details)
        self.assertIn('energy_efficiency', result.details)
        self.assertIn('stability', result.details)

if __name__ == '__main__':
    unittest.main() 