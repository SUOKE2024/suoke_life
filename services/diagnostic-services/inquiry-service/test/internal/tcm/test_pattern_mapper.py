"""
test_pattern_mapper - 索克生活项目模块
"""

from internal.tcm import pattern_mapper
import json
import os
import pytest

#!/usr/bin/env python

"""
证型映射器单元测试
"""





# 测试配置
@pytest.fixture
def test_config():
    return {
        "tcm_knowledge": {
            "patterns_db_path": "./tests/data/test_patterns.json",
            "symptoms_mapping_path": "./tests/data/test_symptoms_mapping.json",
            "confidence_threshold": 0.6,
        }
    }


# 测试数据
@pytest.fixture
def test_symptoms():
    return ["头痛", "失眠", "五心烦热", "口干", "舌红少苔"]


@pytest.fixture
def test_tongue_features():
    return ["舌红", "少苔", "舌尖红"]


@pytest.fixture
def test_pulse_features():
    return ["脉细数"]


# 测试映射器初始化
def test_pattern_mapper_init(test_config):
    # 确保测试文件存在
    os.makedirs("./tests/data", exist_ok=True)

    # 创建测试证型数据
    with open("./tests/data/test_patterns.json", "w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "id": "P001",
                    "name": "阴虚证",
                    "english_name": "Yin Deficiency",
                    "category": "虚证",
                    "description": "阴虚证是指人体阴液亏损所导致的一系列症状",
                }
            ],
            f,
        )

    # 创建测试症状映射数据
    with open("./tests/data/test_symptoms_mapping.json", "w", encoding="utf-8") as f:
        json.dump(
            [
                {"symptom_name": "头痛", "pattern_associations": {"阴虚证": 0.7}},
                {"symptom_name": "口干", "pattern_associations": {"阴虚证": 0.9}},
            ],
            f,
        )

    # 创建测试规则数据
    with open("./tests/data/test_rules.json", "w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "rule_id": "R001",
                    "pattern_name": "阴虚证",
                    "required_symptoms": ["口干", "五心烦热"],
                    "supporting_symptoms": {"失眠": 0.7, "舌红少苔": 0.6},
                    "minimum_required_count": 1,
                    "minimum_supporting_score": 0.5,
                    "tongue_rules": "舌红少苔",
                    "pulse_rules": "脉细数",
                }
            ],
            f,
        )

    # 初始化映射器
    mapper = pattern_mapper.PatternMapper(test_config)

    # 验证数据加载
    assert len(mapper.patterns) == 1
    assert len(mapper.symptoms_mapping) == 2
    assert len(mapper.rules) == 1


# 测试规则匹配
@pytest.mark.asyncio
async def test_match_by_rules(
    test_config, test_symptoms, test_tongue_features, test_pulse_features
):
    mapper = pattern_mapper.PatternMapper(test_config)

    # 私有方法测试，直接调用
    matched_patterns = mapper._match_by_rules(
        test_symptoms, test_tongue_features, test_pulse_features
    )

    # 验证结果
    assert len(matched_patterns) == 1
    assert matched_patterns[0]["pattern_name"] == "阴虚证"
    assert matched_patterns[0]["confidence"] > 0.6
    assert len(matched_patterns[0]["matched_symptoms"]) >= 2


# 测试症状关联匹配
@pytest.mark.asyncio
async def test_match_by_associations(test_config, test_symptoms):
    mapper = pattern_mapper.PatternMapper(test_config)

    # 私有方法测试，直接调用
    matched_patterns = mapper._match_by_associations(test_symptoms)

    # 验证结果
    assert len(matched_patterns) == 1
    assert matched_patterns[0]["pattern_name"] == "阴虚证"
    assert matched_patterns[0]["confidence"] > 0.5
    assert len(matched_patterns[0]["matched_symptoms"]) >= 1


# 测试完整映射流程
@pytest.mark.asyncio
async def test_map_symptoms_to_patterns(
    test_config, test_symptoms, test_tongue_features, test_pulse_features
):
    mapper = pattern_mapper.PatternMapper(test_config)

    # 调用公共方法
    result = await mapper.map_symptoms_to_patterns(
        test_symptoms,
        tongue_features=test_tongue_features,
        pulse_features=test_pulse_features,
    )

    # 验证结果
    assert len(result) == 1
    assert result[0]["pattern_name"] == "阴虚证"
    assert result[0]["confidence"] > 0.7
    assert len(result[0]["matched_symptoms"]) >= 3


# 主函数
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
