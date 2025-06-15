#!/usr/bin/env python
"""
症状提取器单元测试
"""

from unittest.mock import AsyncMock

import pytest

from internal.symptom.optimized_symptom_extractor import OptimizedSymptomExtractor


class TestOptimizedSymptomExtractor:
    """症状提取器测试类"""

    @pytest.fixture
    def symptom_extractor(self) -> OptimizedSymptomExtractor:
        """创建症状提取器实例"""
        config = {
            "llm": {
                "model": "test-model",
                "max_tokens": 1000,
                "temperature": 0.7,
                "timeout": 30,
            },
            "symptom_extraction": {
                "confidence_threshold": 0.6,
                "max_symptoms_per_text": 10,
                "enable_negation_detection": True,
                "enable_severity_analysis": True,
                "enable_duration_extraction": True,
                "enable_context_analysis": True,
            },
        }

        # 创建模拟的LLM客户端
        mock_llm_client = AsyncMock()

        # 模拟症状提取响应
        mock_llm_client.extract_symptoms.return_value = {
            "symptoms": [
                {
                    "name": "头痛",
                    "confidence": 0.9,
                    "severity": "中度",
                    "duration": "3天",
                    "location": "太阳穴",
                    "is_negated": False,
                    "context": "工作压力大时加重",
                },
                {
                    "name": "失眠",
                    "confidence": 0.8,
                    "severity": "轻度",
                    "duration": "1周",
                    "location": "",
                    "is_negated": False,
                    "context": "入睡困难",
                },
            ],
            "extracted_count": 2,
            "processing_time": 0.5,
        }

        extractor = OptimizedSymptomExtractor(config)
        extractor.llm_client = mock_llm_client

        return extractor

    @pytest.mark.asyncio
    async def test_extract_symptoms_basic(self, symptom_extractor):
        """测试基本症状提取"""
        text = "我最近总是头痛，特别是太阳穴位置，已经持续3天了。晚上也睡不好，入睡困难。"

        result = await symptom_extractor.extract_symptoms(text)

        # 验证结果
        assert "symptoms" in result
        assert len(result["symptoms"]) == 2
        assert result["symptoms"][0]["name"] == "头痛"
        assert result["symptoms"][0]["confidence"] == 0.9
        assert result["symptoms"][1]["name"] == "失眠"
        assert result["extracted_count"] == 2

    @pytest.mark.asyncio
    async def test_extract_symptoms_with_negation(self, symptom_extractor):
        """测试否定症状检测"""
        # 修改模拟响应以包含否定症状
        symptom_extractor.llm_client.extract_symptoms.return_value = {
            "symptoms": [
                {
                    "name": "发热",
                    "confidence": 0.8,
                    "severity": "",
                    "duration": "",
                    "location": "",
                    "is_negated": True,
                    "context": "明确否认发热",
                },
                {
                    "name": "咳嗽",
                    "confidence": 0.9,
                    "severity": "轻度",
                    "duration": "2天",
                    "location": "",
                    "is_negated": False,
                    "context": "干咳",
                },
            ],
            "extracted_count": 2,
            "processing_time": 0.3,
        }

        text = "我有点咳嗽，但是没有发热。"

        result = await symptom_extractor.extract_symptoms(text)

        # 验证结果
        assert len(result["symptoms"]) == 2
        assert result["symptoms"][0]["is_negated"] is True
        assert result["symptoms"][1]["is_negated"] is False

    @pytest.mark.asyncio
    async def test_extract_symptoms_batch(self, symptom_extractor):
        """测试批量症状提取"""
        texts = [
            "我头痛得厉害",
            "最近失眠严重",
            "胃部不适，食欲不振",
        ]

        # 为批量处理设置不同的模拟响应
        responses = [
            {
                "symptoms": [{"name": "头痛", "confidence": 0.9, "severity": "重度", "duration": "", "location": "", "is_negated": False, "context": ""}],
                "extracted_count": 1,
                "processing_time": 0.2,
            },
            {
                "symptoms": [{"name": "失眠", "confidence": 0.8, "severity": "重度", "duration": "", "location": "", "is_negated": False, "context": ""}],
                "extracted_count": 1,
                "processing_time": 0.2,
            },
            {
                "symptoms": [
                    {"name": "胃部不适", "confidence": 0.9, "severity": "中度", "duration": "", "location": "胃部", "is_negated": False, "context": ""},
                    {"name": "食欲不振", "confidence": 0.8, "severity": "中度", "duration": "", "location": "", "is_negated": False, "context": ""},
                ],
                "extracted_count": 2,
                "processing_time": 0.3,
            },
        ]

        symptom_extractor.llm_client.extract_symptoms.side_effect = responses

        results = await symptom_extractor.extract_symptoms_batch(texts)

        # 验证结果
        assert len(results) == 3
        assert results[0]["extracted_count"] == 1
        assert results[1]["extracted_count"] == 1
        assert results[2]["extracted_count"] == 2

    @pytest.mark.asyncio
    async def test_extract_symptoms_empty_text(self, symptom_extractor):
        """测试空文本处理"""
        result = await symptom_extractor.extract_symptoms("")

        # 验证结果
        assert result["symptoms"] == []
        assert result["extracted_count"] == 0

    @pytest.mark.asyncio
    async def test_extract_symptoms_error_handling(self, symptom_extractor):
        """测试错误处理"""
        # 模拟LLM客户端抛出异常
        symptom_extractor.llm_client.extract_symptoms.side_effect = Exception("LLM服务不可用")

        text = "我头痛"

        with pytest.raises(Exception, match="LLM服务不可用"):
            await symptom_extractor.extract_symptoms(text)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
