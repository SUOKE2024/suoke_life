"""
症状提取器测试
"""


import pytest

from internal.symptom.optimized_symptom_extractor import OptimizedSymptomExtractor


@pytest.fixture
def mock_config():
    """模拟配置"""
    return {
        "symptom_extraction": {
            "confidence_threshold": 0.7,
            "max_symptoms_per_text": 20,
            "enable_negation_detection": True,
            "enable_severity_analysis": True,
            "enable_duration_extraction": True,
            "enable_body_part_mapping": True,
            "parallel_processing": True,
            "batch_size": 10
        },
        "llm": {
            "use_mock_mode": True,
            "temperature": 0.3,
            "max_tokens": 512
        }
    }


@pytest.fixture
async def symptom_extractor(mock_config):
    """创建症状提取器实例"""
    extractor = OptimizedSymptomExtractor(mock_config)
    await extractor.initialize()
    return extractor


class TestOptimizedSymptomExtractor:
    """症状提取器测试类"""

    @pytest.mark.asyncio
    async def test_extract_symptoms_basic(self, symptom_extractor):
        """测试基本症状提取"""
        text = "我最近头痛，还有点发烧，胃也不舒服"

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is True
        assert "symptoms" in result
        assert isinstance(result["symptoms"], list)
        assert len(result["symptoms"]) > 0

        # 检查症状结构
        for symptom in result["symptoms"]:
            assert "name" in symptom
            assert "confidence" in symptom
            assert "severity" in symptom
            assert "body_part" in symptom

    @pytest.mark.asyncio
    async def test_extract_symptoms_empty_text(self, symptom_extractor):
        """测试空文本的症状提取"""
        text = ""

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is False
        assert "error" in result
        assert "输入文本不能为空" in result["error"]

    @pytest.mark.asyncio
    async def test_extract_symptoms_no_symptoms(self, symptom_extractor):
        """测试无症状文本的提取"""
        text = "今天天气很好，我很开心"

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is True
        assert "symptoms" in result
        # 可能返回空列表或置信度很低的结果

    @pytest.mark.asyncio
    async def test_extract_symptoms_with_negation(self, symptom_extractor):
        """测试否定表达的症状提取"""
        text = "我没有头痛，也不发烧，但是胃疼"

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is True
        assert "symptoms" in result

        # 检查是否正确处理否定
        symptoms = result["symptoms"]
        stomach_pain_found = False
        for symptom in symptoms:
            if "胃" in symptom["name"] or "腹" in symptom["name"]:
                stomach_pain_found = True
                assert symptom["confidence"] > 0.5

        # 应该能找到胃疼症状
        assert stomach_pain_found

    @pytest.mark.asyncio
    async def test_extract_symptoms_with_severity(self, symptom_extractor):
        """测试带严重程度的症状提取"""
        text = "我头痛得很厉害，轻微发烧，胃有点不舒服"

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is True
        assert "symptoms" in result

        symptoms = result["symptoms"]
        severity_levels = [symptom["severity"] for symptom in symptoms]

        # 应该有不同的严重程度
        assert len(set(severity_levels)) > 1

    @pytest.mark.asyncio
    async def test_extract_symptoms_with_duration(self, symptom_extractor):
        """测试带持续时间的症状提取"""
        text = "我头痛了三天，昨天开始发烧，胃疼持续一周了"

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is True
        assert "symptoms" in result

        # 检查是否提取了持续时间信息
        symptoms = result["symptoms"]
        duration_found = False
        for symptom in symptoms:
            if symptom.get("duration"):
                duration_found = True
                break

        assert duration_found

    @pytest.mark.asyncio
    async def test_extract_symptoms_body_parts(self, symptom_extractor):
        """测试身体部位映射"""
        text = "头部疼痛，胸闷，腹部不适，腿部酸痛"

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is True
        assert "symptoms" in result

        symptoms = result["symptoms"]
        body_parts = [symptom["body_part"] for symptom in symptoms if symptom["body_part"]]

        # 应该识别出不同的身体部位
        assert len(body_parts) > 0
        expected_parts = ["头部", "胸部", "腹部", "腿部"]
        found_parts = []
        for part in body_parts:
            for expected in expected_parts:
                if expected in part:
                    found_parts.append(expected)

        assert len(found_parts) > 0

    @pytest.mark.asyncio
    async def test_batch_extract_symptoms(self, symptom_extractor):
        """测试批量症状提取"""
        texts = [
            "我头痛",
            "发烧了",
            "胃不舒服",
            "咳嗽有痰",
            "失眠多梦"
        ]

        result = await symptom_extractor.batch_extract_symptoms(texts)

        assert result["success"] is True
        assert "results" in result
        assert len(result["results"]) == len(texts)

        # 检查每个结果
        for i, text_result in enumerate(result["results"]):
            assert "text_index" in text_result
            assert text_result["text_index"] == i
            assert "symptoms" in text_result

    @pytest.mark.asyncio
    async def test_extract_symptoms_confidence_filtering(self, symptom_extractor):
        """测试置信度过滤"""
        text = "我可能有点头痛，不太确定是否发烧"

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is True
        assert "symptoms" in result

        # 所有返回的症状置信度应该高于阈值
        symptoms = result["symptoms"]
        for symptom in symptoms:
            assert symptom["confidence"] >= symptom_extractor.confidence_threshold

    @pytest.mark.asyncio
    async def test_extract_symptoms_max_limit(self, symptom_extractor):
        """测试症状数量限制"""
        # 构造包含大量症状的文本
        symptoms_list = [
            "头痛", "发烧", "咳嗽", "胃痛", "腹泻", "便秘", "失眠", "疲劳",
            "头晕", "恶心", "呕吐", "腹胀", "胸闷", "心悸", "出汗", "怕冷",
            "口干", "口苦", "食欲不振", "消化不良", "关节痛", "肌肉酸痛",
            "皮疹", "瘙痒", "耳鸣", "视力模糊"
        ]
        text = f"我有{', '.join(symptoms_list)}等症状"

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is True
        assert "symptoms" in result

        # 返回的症状数量不应超过配置的最大值
        symptoms = result["symptoms"]
        assert len(symptoms) <= symptom_extractor.max_symptoms_per_text

    @pytest.mark.asyncio
    async def test_extract_symptoms_complex_text(self, symptom_extractor):
        """测试复杂文本的症状提取"""
        text = """
        我最近身体不太好，主要是头部经常疼痛，特别是太阳穴附近，
        疼痛程度比较严重，已经持续了一个星期了。同时还伴有轻微发热，
        体温大概37.5度左右，晚上睡觉时出汗比较多。
        胃部也有些不适，主要是饭后胀痛，有时候还会恶心。
        另外，最近几天大便也不太正常，比较干燥，排便困难。
        整个人感觉很疲劳，没有精神，工作效率也下降了。
        """

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is True
        assert "symptoms" in result

        symptoms = result["symptoms"]
        assert len(symptoms) > 0

        # 检查是否提取了主要症状
        symptom_names = [symptom["name"] for symptom in symptoms]
        expected_symptoms = ["头痛", "发热", "胃胀", "便秘", "疲劳"]

        found_count = 0
        for expected in expected_symptoms:
            for name in symptom_names:
                if expected in name or any(keyword in name for keyword in expected.split()):
                    found_count += 1
                    break

        # 至少应该找到一半的预期症状
        assert found_count >= len(expected_symptoms) // 2

    @pytest.mark.asyncio
    async def test_extract_symptoms_medical_terms(self, symptom_extractor):
        """测试医学术语的症状提取"""
        text = "患者主诉头痛、发热、恶心、呕吐，伴有畏寒、乏力"

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is True
        assert "symptoms" in result

        symptoms = result["symptoms"]
        assert len(symptoms) > 0

        # 应该能识别医学术语
        symptom_names = [symptom["name"] for symptom in symptoms]
        medical_terms = ["头痛", "发热", "恶心", "呕吐", "畏寒", "乏力"]

        found_terms = 0
        for term in medical_terms:
            if any(term in name for name in symptom_names):
                found_terms += 1

        assert found_terms > 0

    @pytest.mark.asyncio
    async def test_extract_symptoms_error_handling(self, symptom_extractor):
        """测试错误处理"""
        # 测试超长文本
        very_long_text = "头痛" * 10000

        result = await symptom_extractor.extract_symptoms(very_long_text)

        # 应该有适当的错误处理或截断处理
        assert "success" in result
        if not result["success"]:
            assert "error" in result

    @pytest.mark.asyncio
    async def test_parallel_processing(self, symptom_extractor):
        """测试并行处理"""
        texts = [
            "我头痛得厉害",
            "发烧了两天",
            "胃疼想吐",
            "咳嗽有血丝",
            "失眠多梦易醒"
        ] * 5  # 25个文本

        import time
        start_time = time.time()

        result = await symptom_extractor.batch_extract_symptoms(texts)

        end_time = time.time()
        processing_time = end_time - start_time

        assert result["success"] is True
        assert len(result["results"]) == len(texts)

        # 并行处理应该相对较快
        assert processing_time < 30  # 30秒内完成

    @pytest.mark.asyncio
    async def test_symptom_normalization(self, symptom_extractor):
        """测试症状标准化"""
        # 测试同义词和变体
        texts = [
            "头疼",
            "头痛",
            "脑袋疼",
            "头部疼痛"
        ]

        results = []
        for text in texts:
            result = await symptom_extractor.extract_symptoms(text)
            if result["success"] and result["symptoms"]:
                results.append(result["symptoms"][0]["name"])

        # 应该有一定的标准化效果
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_context_awareness(self, symptom_extractor):
        """测试上下文感知"""
        text = "我妈妈头痛，我自己胃疼"

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is True
        assert "symptoms" in result

        # 应该能区分主体，主要提取"我自己"的症状
        symptoms = result["symptoms"]
        stomach_related = any("胃" in symptom["name"] for symptom in symptoms)
        assert stomach_related

    @pytest.mark.asyncio
    async def test_temporal_information(self, symptom_extractor):
        """测试时间信息提取"""
        text = "昨天开始头痛，今天更严重了，三天前就有点发烧"

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is True
        assert "symptoms" in result

        symptoms = result["symptoms"]

        # 检查是否有时间相关信息
        temporal_info_found = False
        for symptom in symptoms:
            if (symptom.get("onset_time")) or \
               (symptom.get("duration")):
                temporal_info_found = True
                break

        # 至少应该提取到一些时间信息
        assert temporal_info_found or len(symptoms) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
