from typing import Dict, List, Any, Optional, Union

"""
test_pulse_processor - 索克生活项目模块
"""

from internal.signal.pulse_processor import PulseProcessor
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import sys

#! / usr / bin / env python
# - * - coding: utf - 8 - * -
"""
脉诊处理器单元测试
"""



# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# 测试数据
SAMPLE_RATE = 1000
TEST_CONFIG = {
    'sampling_rate': SAMPLE_RATE,
    'filter': {
        'low_cutoff': 0.5,
        'high_cutoff': 20.0
    },
    'wavelet': {
        'wavelet_type': 'db4',
        'decomposition_level': 5
    }
}

# 生成测试用的脉搏数据 - 模拟5个脉搏波
def generate_test_pulse_data(n_samples = 5000):
    """TODO: 添加文档字符串"""
    # 生成模拟的脉搏波数据，包含主波和重搏波
    t = np.linspace(0, n_samples / SAMPLE_RATE, n_samples)
    # 基线波动
    baseline = np.sin(2 * np.pi * 0.1 * t) * 10
    # 主波
    main_wave = np.zeros_like(t)

    # 生成几个脉搏波
    for i in range(5):
        center = i * 1.0 + 0.5
        # 主波 - 高斯脉冲
        main_pulse = 100 * np.exp( - ((t - center) * * 2) / (2 * 0.1 * * 2))
        # 重搏波 - 较小的高斯脉冲，延迟一点
        dicrotic_pulse = 30 * np.exp( - ((t - (center + 0.3)) * * 2) / (2 * 0.1 * * 2))
        main_wave + = main_pulse + dicrotic_pulse

    # 添加一些噪声
    noise = np.random.normal(0, 5, n_samples)

    # 组合所有信号
    signal = baseline + main_wave + noise
    return signal.tolist()

class TestPulseProcessor:
    """脉诊处理器测试类"""

    @pytest.fixture
    def processor(self) - > None:
        """创建处理器实例"""
        return PulseProcessor(TEST_CONFIG)

    @pytest.fixture
    def sample_pulse_data(self) - > None:
        """生成样本脉搏数据"""
        return generate_test_pulse_data()

    def test_initialization(self, processor):
        """测试初始化"""
        assert processor.sampling_rate == TEST_CONFIG['sampling_rate']
        assert processor.filter_low == TEST_CONFIG['filter']['low_cutoff']
        assert processor.filter_high == TEST_CONFIG['filter']['high_cutoff']
        assert processor.wavelet_type == TEST_CONFIG['wavelet']['wavelet_type']
        assert processor.decomposition_level == TEST_CONFIG['wavelet']['decomposition_level']

    def test_preprocess(self, processor, sample_pulse_data):
        """测试预处理功能"""
        processed_data = processor.preprocess(sample_pulse_data)

        # 检查数据类型和长度
        assert isinstance(processed_data, np.ndarray)
        assert len(processed_data) == len(sample_pulse_data)

        # 检查数据被归一化
        assert - 1.0 < = np.max(processed_data) < = 1.0
        assert - 1.0 < = np.min(processed_data) < = 1.0

    def test_segment_pulse_waves(self, processor, sample_pulse_data):
        """测试脉搏波分割功能"""
        processed_data = processor.preprocess(sample_pulse_data)
        segments = processor.segment_pulse_waves(processed_data)

        # 检查是否检测到脉搏波
        assert len(segments) > 0

        # 检查每个段的长度是否合理
        for segment in segments:
            assert len(segment) > 0
            assert len(segment) < len(sample_pulse_data)

    def test_extract_features(self, processor, sample_pulse_data):
        """测试特征提取功能"""
        processed_data = processor.preprocess(sample_pulse_data)
        features = processor.extract_features(processed_data)

        # 检查特征结构
        assert 'time_domain' in features
        assert 'frequency_domain' in features
        assert 'wavelet' in features

        # 检查时域特征
        time_features = features['time_domain']
        assert 'mean' in time_features
        assert 'std' in time_features
        assert 'max_amplitude' in time_features

        # 检查频域特征
        freq_features = features['frequency_domain']
        assert 'main_frequency' in freq_features
        assert 'energy_ratio' in freq_features

        # 检查小波特征
        wavelet_features = features['wavelet']
        assert len(wavelet_features) > 0

    def test_quality_assessment(self, processor, sample_pulse_data):
        """测试信号质量评估功能"""
        processed_data = processor.preprocess(sample_pulse_data)
        quality_score = processor.assess_quality(processed_data)

        # 检查质量分数范围
        assert 0.0 < = quality_score < = 1.0

    def test_classify_pulse(self, processor, sample_pulse_data):
        """测试脉象分类功能"""
        # 模拟模型预测
        with patch.object(processor, '_load_model', return_value = MagicMock()):
            with patch.object(processor, '_model', return_value = MagicMock()):
                # 设置模型预测结果
                processor._model.predict_proba = MagicMock(return_value = np.array([[0.1, 0.2, 0.7]]))
                processor.pulse_types = ['normal', 'slippery', 'wiry']

                processed_data = processor.preprocess(sample_pulse_data)
                features = processor.extract_features(processed_data)
                result = processor.classify_pulse(features)

                # 检查分类结果
                assert 'pulse_type' in result
                assert 'confidence' in result
                assert result['pulse_type'] == 'wiry'
                assert 0.0 < = result['confidence'] < = 1.0