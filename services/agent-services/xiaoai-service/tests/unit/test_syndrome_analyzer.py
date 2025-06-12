"""
中医辨证分析器单元测试
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from xiaoai.core.syndrome_analyzer import (
    AnalysisMethod,
    SyndromeAnalyzer,
    SyndromePattern,
    SyndromeResult,
    SyndromeType,
)
from xiaoai.models.diagnosis import DiagnosisData


class TestSyndromeAnalyzer:
    """中医辨证分析器测试类"""

    @pytest.fixture
    async def analyzer(self):
        """创建分析器实例"""
        analyzer = SyndromeAnalyzer()
        await analyzer.initialize()
        yield analyzer

    @pytest.fixture
    def sample_diagnosis_data(self):
        """样本诊断数据"""
        return DiagnosisData(
            user_id="test_user",
            session_id="test_session",
            symptoms=["头痛", "失眠", "心悸", "口干"],
            tongue_data={"color": "红", "coating": "厚", "texture": "干"},
            pulse_data={"type": "弦数", "rate": 90, "strength": "有力"},
            complexion="面红",
            voice_data={"tone": "高亢", "volume": "大声"},
            emotional_state="烦躁",
            sleep_pattern="难入睡",
            appetite="食欲不振",
            stool="便秘",
            urine="尿黄",
            temperature_preference="喜冷",
            created_at=datetime.now(),
        )

    @pytest.fixture
    def yang_excess_data(self):
        """阳盛实热证数据"""
        return DiagnosisData(
            user_id="test_user",
            session_id="test_session",
            symptoms=["发热", "头痛", "烦躁", "口渴"],
            tongue_data={"color": "红", "coating": "黄厚"},
            pulse_data={"type": "洪数", "rate": 100},
            complexion="面红",
            temperature_preference="喜冷",
            stool="便秘",
            urine="尿黄",
            created_at=datetime.now(),
        )

    @pytest.fixture
    def yin_deficiency_data(self):
        """阴虚证数据"""
        return DiagnosisData(
            user_id="test_user",
            session_id="test_session",
            symptoms=["潮热", "盗汗", "失眠", "心烦"],
            tongue_data={"color": "红", "coating": "少苔"},
            pulse_data={"type": "细数", "rate": 85},
            complexion="颧红",
            temperature_preference="喜凉",
            created_at=datetime.now(),
        )

    @pytest.fixture
    def qi_deficiency_data(self):
        """气虚证数据"""
        return DiagnosisData(
            user_id="test_user",
            session_id="test_session",
            symptoms=["乏力", "气短", "懒言", "自汗"],
            tongue_data={"color": "淡", "coating": "白"},
            pulse_data={"type": "虚弱", "rate": 65},
            complexion="面色萎黄",
            voice_data={"tone": "低沉", "volume": "小声"},
            created_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_analyzer_initialization(self, analyzer):
        """测试分析器初始化"""
        assert analyzer is not None
        assert hasattr(analyzer, "syndrome_patterns")
        assert hasattr(analyzer, "analysis_methods")
        assert len(analyzer.syndrome_patterns) > 0

    @pytest.mark.asyncio
    async def test_eight_principles_analysis(self, analyzer, yang_excess_data):
        """测试八纲辨证"""
        result = await analyzer._eight_principles_analysis(yang_excess_data)

        assert isinstance(result, SyndromeResult)
        assert result.method == AnalysisMethod.EIGHT_PRINCIPLES
        assert len(result.patterns) > 0

        # 检查是否识别出阳证、热证、实证
        pattern_names = [p.name for p in result.patterns]
        assert any("阳" in name for name in pattern_names)
        assert any("热" in name for name in pattern_names)
        assert any("实" in name for name in pattern_names)

    @pytest.mark.asyncio
    async def test_qi_blood_analysis(self, analyzer, qi_deficiency_data):
        """测试气血津液辨证"""
        result = await analyzer._qi_blood_analysis(qi_deficiency_data)

        assert isinstance(result, SyndromeResult)
        assert result.method == AnalysisMethod.QI_BLOOD
        assert len(result.patterns) > 0

        # 检查是否识别出气虚证
        pattern_names = [p.name for p in result.patterns]
        assert any("气虚" in name for name in pattern_names)

    @pytest.mark.asyncio
    async def test_organ_analysis(self, analyzer, sample_diagnosis_data):
        """测试脏腑辨证"""
        result = await analyzer._organ_analysis(sample_diagnosis_data)

        assert isinstance(result, SyndromeResult)
        assert result.method == AnalysisMethod.ORGAN
        assert len(result.patterns) > 0

        # 根据症状应该识别出心相关证型
        pattern_names = [p.name for p in result.patterns]
        assert any("心" in name for name in pattern_names)

    @pytest.mark.asyncio
    async def test_six_channels_analysis(self, analyzer, yang_excess_data):
        """测试六经辨证"""
        result = await analyzer._six_channels_analysis(yang_excess_data)

        assert isinstance(result, SyndromeResult)
        assert result.method == AnalysisMethod.SIX_CHANNELS
        assert len(result.patterns) > 0

        # 根据症状应该识别出阳明经证
        pattern_names = [p.name for p in result.patterns]
        assert any("阳明" in name for name in pattern_names)

    @pytest.mark.asyncio
    async def test_triple_burner_analysis(self, analyzer, sample_diagnosis_data):
        """测试三焦辨证"""
        result = await analyzer._triple_burner_analysis(sample_diagnosis_data)

        assert isinstance(result, SyndromeResult)
        assert result.method == AnalysisMethod.TRIPLE_BURNER
        assert len(result.patterns) > 0

    @pytest.mark.asyncio
    async def test_comprehensive_analysis(self, analyzer, sample_diagnosis_data):
        """测试综合辨证分析"""
        result = await analyzer.analyze_syndrome(sample_diagnosis_data)

        assert isinstance(result, SyndromeResult)
        assert len(result.patterns) > 0
        assert result.confidence > 0
        assert result.primary_pattern is not None
        assert result.analysis_summary is not None

    @pytest.mark.asyncio
    async def test_pattern_matching(self, analyzer):
        """测试证型模式匹配"""
        # 测试阳盛实热证模式
        symptoms = ["发热", "头痛", "烦躁", "口渴", "便秘"]
        tongue = {"color": "红", "coating": "黄厚"}
        pulse = {"type": "洪数"}

        patterns = await analyzer._match_patterns(symptoms, tongue, pulse)

        assert len(patterns) > 0
        pattern_names = [p.name for p in patterns]
        assert any("实热" in name or "阳盛" in name for name in pattern_names)

    @pytest.mark.asyncio
    async def test_symptom_weight_calculation(self, analyzer):
        """测试症状权重计算"""
        symptoms = ["头痛", "失眠", "心悸", "口干"]

        weights = analyzer._calculate_symptom_weights(symptoms)

        assert len(weights) == len(symptoms)
        assert all(0 <= weight <= 1 for weight in weights.values())

        # 主症应该有更高权重
        assert weights.get("头痛", 0) > 0.5
        assert weights.get("失眠", 0) > 0.5

    @pytest.mark.asyncio
    async def test_tongue_analysis(self, analyzer):
        """测试舌象分析"""
        # 测试红舌黄苔
        tongue_data = {"color": "红", "coating": "黄厚", "texture": "干"}
        analysis = analyzer._analyze_tongue(tongue_data)

        assert "heat_score" in analysis
        assert "dryness_score" in analysis
        assert analysis["heat_score"] > 0.5  # 红舌黄苔提示热证

        # 测试淡舌白苔
        tongue_data = {"color": "淡", "coating": "白", "texture": "润"}
        analysis = analyzer._analyze_tongue(tongue_data)

        assert analysis["cold_score"] > 0.5  # 淡舌白苔提示寒证

    @pytest.mark.asyncio
    async def test_pulse_analysis(self, analyzer):
        """测试脉象分析"""
        # 测试洪数脉
        pulse_data = {"type": "洪数", "rate": 100, "strength": "有力"}
        analysis = analyzer._analyze_pulse(pulse_data)

        assert "heat_score" in analysis
        assert "excess_score" in analysis
        assert analysis["heat_score"] > 0.5
        assert analysis["excess_score"] > 0.5

        # 测试细弱脉
        pulse_data = {"type": "细弱", "rate": 60, "strength": "无力"}
        analysis = analyzer._analyze_pulse(pulse_data)

        assert analysis["deficiency_score"] > 0.5

    @pytest.mark.asyncio
    async def test_confidence_calculation(self, analyzer, sample_diagnosis_data):
        """测试置信度计算"""
        patterns = [
            SyndromePattern(
                name="心火亢盛",
                type=SyndromeType.EXCESS_HEAT,
                symptoms=["心悸", "失眠", "口干"],
                tongue_signs=["红", "黄苔"],
                pulse_signs=["数"],
                confidence=0.8,
            ),
            SyndromePattern(
                name="肝阳上亢",
                type=SyndromeType.YANG_EXCESS,
                symptoms=["头痛", "烦躁"],
                tongue_signs=["红"],
                pulse_signs=["弦"],
                confidence=0.7,
            ),
        ]

        confidence = analyzer._calculate_overall_confidence(patterns, sample_diagnosis_data)

        assert 0 <= confidence <= 1
        assert confidence > 0.5  # 应该有合理的置信度

    @pytest.mark.asyncio
    async def test_pattern_combination_analysis(self, analyzer):
        """测试证型组合分析"""
        patterns = [
            SyndromePattern(name="气虚", type=SyndromeType.QI_DEFICIENCY, confidence=0.8),
            SyndromePattern(name="血瘀", type=SyndromeType.BLOOD_STASIS, confidence=0.7),
        ]

        combinations = analyzer._analyze_pattern_combinations(patterns)

        assert len(combinations) > 0
        # 应该识别出气虚血瘀的组合
        combination_names = [c["name"] for c in combinations]
        assert any("气虚血瘀" in name for name in combination_names)

    @pytest.mark.asyncio
    async def test_syndrome_evolution_analysis(self, analyzer):
        """测试证型演变分析"""
        current_patterns = [
            SyndromePattern(name="外感风寒", type=SyndromeType.EXTERIOR_COLD, confidence=0.8)
        ]

        evolution = analyzer._analyze_syndrome_evolution(current_patterns)

        assert "possible_developments" in evolution
        assert "prevention_suggestions" in evolution
        assert len(evolution["possible_developments"]) > 0

    @pytest.mark.asyncio
    async def test_differential_diagnosis(self, analyzer):
        """测试鉴别诊断"""
        primary_pattern = SyndromePattern(
            name="心火亢盛",
            type=SyndromeType.EXCESS_HEAT,
            symptoms=["心悸", "失眠", "口干"],
            confidence=0.8,
        )

        differential = analyzer._perform_differential_diagnosis(primary_pattern)

        assert "similar_patterns" in differential
        assert "distinguishing_features" in differential
        assert len(differential["similar_patterns"]) > 0

    @pytest.mark.asyncio
    async def test_treatment_principle_generation(self, analyzer):
        """测试治疗原则生成"""
        patterns = [SyndromePattern(name="心火亢盛", type=SyndromeType.EXCESS_HEAT, confidence=0.8)]

        principles = analyzer._generate_treatment_principles(patterns)

        assert "primary_principle" in principles
        assert "secondary_principles" in principles
        assert "contraindications" in principles

        # 心火亢盛应该清心泻火
        assert any("清心" in p or "泻火" in p for p in principles["primary_principle"])

    @pytest.mark.asyncio
    async def test_error_handling(self, analyzer):
        """测试错误处理"""
        # 测试空数据
        empty_data = DiagnosisData(
            user_id="test_user",
            session_id="test_session",
            symptoms=[],
            created_at=datetime.now(),
        )

        result = await analyzer.analyze_syndrome(empty_data)

        # 应该返回默认结果而不是抛出异常
        assert isinstance(result, SyndromeResult)
        assert result.confidence == 0

    @pytest.mark.asyncio
    async def test_multiple_syndrome_analysis(self, analyzer):
        """测试多证型分析"""
        # 创建复杂症状的数据
        complex_data = DiagnosisData(
            user_id="test_user",
            session_id="test_session",
            symptoms=["头痛", "失眠", "心悸", "乏力", "气短", "腰酸"],
            tongue_data={"color": "淡红", "coating": "薄白"},
            pulse_data={"type": "细弱", "rate": 70},
            created_at=datetime.now(),
        )

        result = await analyzer.analyze_syndrome(complex_data)

        assert len(result.patterns) >= 2  # 应该识别出多个证型
        assert result.primary_pattern is not None
        assert len(result.secondary_patterns) > 0

    @pytest.mark.asyncio
    async def test_seasonal_adjustment(self, analyzer):
        """测试季节性调整"""
        # 夏季数据
        summer_data = DiagnosisData(
            user_id="test_user",
            session_id="test_session",
            symptoms=["烦热", "汗出", "口渴"],
            created_at=datetime(2023, 7, 15),  # 夏季
        )

        result = await analyzer.analyze_syndrome(summer_data)

        # 夏季应该更容易诊断为热证
        pattern_names = [p.name for p in result.patterns]
        assert any("热" in name for name in pattern_names)

    @pytest.mark.asyncio
    async def test_age_gender_adjustment(self, analyzer):
        """测试年龄性别调整"""
        # 老年女性数据
        elderly_female_data = DiagnosisData(
            user_id="test_user",
            session_id="test_session",
            symptoms=["潮热", "盗汗", "失眠"],
            patient_info={"age": 55, "gender": "female"},
            created_at=datetime.now(),
        )

        result = await analyzer.analyze_syndrome(elderly_female_data)

        # 应该考虑更年期相关证型
        pattern_names = [p.name for p in result.patterns]
        assert any("肾阴虚" in name or "阴虚" in name for name in pattern_names)

    def test_syndrome_type_enum(self):
        """测试证型枚举"""
        assert SyndromeType.YIN_DEFICIENCY.value == "yin_deficiency"
        assert SyndromeType.YANG_DEFICIENCY.value == "yang_deficiency"
        assert SyndromeType.QI_DEFICIENCY.value == "qi_deficiency"
        assert SyndromeType.BLOOD_DEFICIENCY.value == "blood_deficiency"

    def test_analysis_method_enum(self):
        """测试分析方法枚举"""
        assert AnalysisMethod.EIGHT_PRINCIPLES.value == "eight_principles"
        assert AnalysisMethod.QI_BLOOD.value == "qi_blood"
        assert AnalysisMethod.ORGAN.value == "organ"
        assert AnalysisMethod.SIX_CHANNELS.value == "six_channels"
