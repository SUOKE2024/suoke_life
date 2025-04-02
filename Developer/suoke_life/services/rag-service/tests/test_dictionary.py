import pytest
import tempfile
import os
from pathlib import Path

from src.utils.dictionary import Dictionary

@pytest.fixture
def test_dict_path(tmp_path):
    """创建测试字典文件"""
    dict_path = tmp_path / "test_dict.txt"
    with open(dict_path, "w", encoding="utf-8") as f:
        f.write("气虚质|体质|气虚体质,气虚症\n")
        f.write("人参|药材|\n")
        f.write("补气|治法|\n")
        f.write("脉诊|诊法|\n")
    return dict_path

@pytest.fixture
def dict(test_dict_path):
    """创建字典实例"""
    return Dictionary(str(test_dict_path))

def test_load_dictionary(dict):
    """测试加载字典"""
    assert len(dict.terms) == 4
    assert len(dict.categories) == 4
    assert "体质" in dict.categories
    assert "治法" in dict.categories
    assert "药材" in dict.categories
    assert "诊法" in dict.categories

def test_get_term_info(dict):
    """测试获取术语信息"""
    info = dict.get_term_info("气虚质")
    assert info is not None
    assert info["category"] == "体质"
    assert "气虚体质" in info["synonyms"]
    
    info = dict.get_term_info("气虚体质")
    assert info is not None
    assert info["term"] == "气虚质"
    
    assert dict.get_term_info("不存在") is None

def test_get_category(dict):
    """测试获取术语类别"""
    assert dict.get_category("气虚质") == "体质"
    assert dict.get_category("人参") == "药材"
    assert dict.get_category("不存在") is None

def test_get_synonyms(dict):
    """测试获取同义词"""
    synonyms = dict.get_synonyms("气虚质")
    assert "气虚体质" in synonyms
    assert "气虚症" in synonyms
    assert len(dict.get_synonyms("不存在")) == 0

def test_is_term(dict):
    """测试是否为术语"""
    assert dict.is_term("气虚质") is True
    assert dict.is_term("气虚体质") is True
    assert dict.is_term("不存在") is False

def test_extract_terms(dict):
    """测试提取术语"""
    text = "气虚质的患者可以服用人参进行补气治疗。"
    terms = dict.extract_terms(text)
    assert len(terms) >= 3  # 应至少包含"气虚质"、"人参"和"补气"三个术语

def test_add_term(dict):
    """测试添加术语"""
    success = dict.add_term(
        "白芍",
        "药材",
        ["芍药", "白芍药"]
    )
    assert success is True
    info = dict.get_term_info("白芍")
    assert info is not None
    assert info["category"] == "药材"
    assert "芍药" in info["synonyms"]
    
    # 测试添加已存在术语
    success = dict.add_term("气虚质", "体质")
    assert success is True

def test_remove_term(dict):
    """测试删除术语"""
    success = dict.remove_term("气虚质")
    assert success is True
    assert dict.get_term_info("气虚质") is None
    
    # 测试删除不存在术语
    success = dict.remove_term("不存在")
    assert success is False

def test_save_dictionary(dict, tmp_path):
    """测试保存字典"""
    # 添加一个新术语
    dict.add_term("白芍", "药材", ["芍药", "白芍药"])
    
    # 保存到新路径
    new_path = tmp_path / "new_dict.txt"
    dict.dictionary_path = str(new_path)
    dict.save_dictionary()
    
    # 检查文件是否存在
    assert new_path.exists()
    
    # 加载新字典并验证内容
    new_dict = Dictionary(str(new_path))
    assert len(new_dict.terms) == 5  # 4个原始术语加1个新术语
    assert "白芍" in new_dict.terms
