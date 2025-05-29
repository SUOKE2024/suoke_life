#!/usr/bin/env python

"""
症状提取器测试
"""

import json
from unittest.mock import patch

import pytest

from internal.llm.symptom_extractor import SymptomExtractor

# 测试数据
TEST_TEXT = """
最近一周我总是感到头痛，尤其是右侧太阳穴位置。疼痛通常在下午开始，到晚上会加重。
我还注意到有轻微的恶心感，有时候会觉得眼睛疲劳。睡眠也不是很好，经常醒来。
这种情况持续大概一周了，我有点担心是不是工作压力太大导致的。
"""

MOCK_SYMPTOMS_RESPONSE = {
    "symptoms": [
        {
            "symptom_name": "头痛",
            "severity": "MODERATE",
            "onset_time": 1615000000,
            "duration": 604800,  # 一周，以秒为单位
            "description": "右侧太阳穴位置疼痛，下午开始，晚上加重",
            "confidence": 0.95,
        },
        {
            "symptom_name": "恶心",
            "severity": "MILD",
            "onset_time": 1615000000,
            "duration": 604800,
            "description": "轻微恶心感",
            "confidence": 0.85,
        },
        {
            "symptom_name": "眼睛疲劳",
            "severity": "MILD",
            "onset_time": 1615000000,
            "duration": 604800,
            "description": "眼睛疲劳感",
            "confidence": 0.80,
        },
        {
            "symptom_name": "睡眠障碍",
            "severity": "MODERATE",
            "onset_time": 1615000000,
            "duration": 604800,
            "description": "睡眠质量差，经常醒来",
            "confidence": 0.90,
        },
    ],
    "body_locations": [
        {"location_name": "头部", "associated_symptoms": ["头痛"], "side": "right"},
        {
            "location_name": "眼睛",
            "associated_symptoms": ["眼睛疲劳"],
            "side": "bilateral",
        },
    ],
    "temporal_factors": [
        {
            "factor_type": "diurnal",
            "description": "下午开始，晚上加重",
            "symptoms_affected": ["头痛"],
        }
    ],
    "confidence_score": 0.88,
}


class TestSymptomExtractor:
    """症状提取器测试类"""

    @pytest.fixture
    def symptom_extractor(self):
        """创建症状提取器实例"""
        config = {
            "llm": {"use_mock_mode": True, "model_type": "test", "timeout_seconds": 10},
            "symptom_extraction": {"confidence_threshold": 0.6, "max_symptoms": 10},
        }
        return SymptomExtractor(config)

    @pytest.mark.asyncio
    @patch("internal.llm.llm_client.LLMClient.generate")
    async def test_extract_symptoms(self, mock_generate, symptom_extractor):
        """测试症状提取功能"""
        # 模拟LLM响应
        mock_generate.return_value = json.dumps(MOCK_SYMPTOMS_RESPONSE)

        # 执行测试
        result = await symptom_extractor.extract_symptoms(TEST_TEXT)

        # 验证结果
        assert isinstance(result, dict)
        assert "symptoms" in result
        assert len(result["symptoms"]) == 4
        assert result["symptoms"][0]["symptom_name"] == "头痛"
        assert result["symptoms"][0]["severity"] == "MODERATE"
        assert "body_locations" in result
        assert len(result["body_locations"]) == 2
        assert "temporal_factors" in result
        assert result["confidence_score"] == 0.88

        # 验证LLM调用
        mock_generate.assert_called_once()

    @pytest.mark.asyncio
    @patch("internal.llm.llm_client.LLMClient.generate")
    async def test_extract_symptoms_with_empty_text(
        self, mock_generate, symptom_extractor
    ):
        """测试空文本情况"""
        # 模拟LLM响应
        mock_generate.return_value = json.dumps(
            {
                "symptoms": [],
                "body_locations": [],
                "temporal_factors": [],
                "confidence_score": 0.0,
            }
        )

        # 执行测试
        result = await symptom_extractor.extract_symptoms("")

        # 验证结果
        assert isinstance(result, dict)
        assert "symptoms" in result
        assert len(result["symptoms"]) == 0
        assert "confidence_score" in result
        assert result["confidence_score"] == 0.0

    @pytest.mark.asyncio
    @patch("internal.llm.llm_client.LLMClient.generate")
    async def test_extract_symptoms_with_llm_error(
        self, mock_generate, symptom_extractor
    ):
        """测试LLM错误情况"""
        # 模拟LLM错误
        mock_generate.side_effect = Exception("LLM调用失败")

        # 执行测试
        with pytest.raises(Exception) as exc_info:
            await symptom_extractor.extract_symptoms(TEST_TEXT)

        # 验证异常
        assert "LLM调用失败" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_symptom_extraction_e2e(self, symptom_extractor):
        """端到端测试症状提取"""
        # 这是一个完整的端到端测试，需要实际的LLM环境
        # 在CI环境中，会跳过这个测试
        pytest.skip("需要实际的LLM环境，跳过CI测试")

        # 实际提取
        result = await symptom_extractor.extract_symptoms(TEST_TEXT)

        # 验证基本结构
        assert isinstance(result, dict)
        assert "symptoms" in result
        assert "body_locations" in result
        assert "confidence_score" in result


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
