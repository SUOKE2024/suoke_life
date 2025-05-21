"""
语音特征提取器 - 专注于从人类语音中提取中医诊断相关特征
"""
import os
import time
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union

import torch
import librosa
import parselmouth
from parselmouth.praat import call
from scipy.stats import skew, kurtosis

from internal.audio.audio_analyzer import AudioAnalyzer

logger = logging.getLogger(__name__)

class VoiceFeatureExtractor(AudioAnalyzer):
    """语音特征提取器，从人类语音中提取中医诊断相关特征"""
    
    def __init__(self, config: Dict):
        """
        初始化语音特征提取器
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        
        # 加载模型配置
        model_config = config.get("models", {}).get("voice_model", {})
        self.model_path = model_config.get("path")
        self.model_name = model_config.get("name", "voice_feature_analyzer")
        self.model_version = model_config.get("version", "1.0.0")
        self.batch_size = model_config.get("batch_size", 16)
        self.device_name = model_config.get("device", "cuda:0" if torch.cuda.is_available() else "cpu")
        self.precision = model_config.get("precision", "fp32")
        self.threshold = model_config.get("threshold", 0.65)
        self.sample_rate = model_config.get("sampling_rate", 16000)
        
        # 是否预加载模型
        self.preload = model_config.get("preload", True)
        self.model = None
        
        # TCM特定配置
        self.tcm_config = config.get("tcm", {})
        self.feature_importance_threshold = self.tcm_config.get("syndrome_patterns", {}).get(
            "feature_importance_threshold", 0.3)
        
        # 方言检测选项
        self.dialect_detection = config.get("models", {}).get("dialect_model", {}).get("enabled", True)
        
        if self.preload:
            self.load_model()
            
        logger.info(f"语音特征提取器初始化完成，模型：{self.model_name}, 版本：{self.model_version}")
    
    def load_model(self):
        """加载语音分析模型"""
        if self.model is not None:
            return
            
        try:
            logger.info(f"加载语音分析模型: {self.model_path}")
            start_time = time.time()
            
            # 注意：这里是模型加载的占位代码
            # 实际项目中需要替换为真实的模型加载逻辑
            # 例如使用 PyTorch, TensorFlow 或其他框架加载模型
            
            # 使用PyTorch框架示例:
            if os.path.exists(self.model_path):
                self.model = torch.jit.load(self.model_path, map_location=self.device_name)
                self.model.eval()
                if self.precision == "fp16" and "cuda" in self.device_name:
                    self.model = self.model.half()
            else:
                # 开发模式下可以使用模拟模型
                logger.warning(f"模型文件不存在: {self.model_path}，使用模拟模型")
                self.model = DummyVoiceModel(self.device_name)
            
            load_time = time.time() - start_time
            logger.info(f"模型加载完成，耗时：{load_time:.2f}秒")
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            # 开发模式下使用模拟模型
            self.model = DummyVoiceModel(self.device_name)
    
    def analyze_voice(self, audio_data: bytes, audio_format: str, 
                     sample_rate: int = None, apply_preprocessing: bool = True,
                     **kwargs) -> Dict[str, Any]:
        """
        分析语音，提取中医相关特征
        
        Args:
            audio_data: 原始音频二进制数据
            audio_format: 音频格式
            sample_rate: 音频采样率，如未提供则从音频文件读取
            apply_preprocessing: 是否应用预处理
            
        Returns:
            Dict[str, Any]: 分析结果，包含各种语音特征和中医相关性
        """
        start_time = time.time()
        
        # 加载模型（如果尚未加载）
        if self.model is None:
            self.load_model()
        
        # 加载音频
        target_sr = self.sample_rate if sample_rate is None else sample_rate
        audio, sr = self.load_audio(audio_data, audio_format, target_sr=target_sr, convert_to_mono=True)
        
        # 预处理音频
        if apply_preprocessing:
            audio = self.preprocess_audio(audio, sr)
        
        # 提取通用特征
        features = self.extract_features(audio, sr)
        
        # 提取语音特有特征
        voice_features = self.extract_voice_features(audio, sr)
        features.update(voice_features)
        
        # 生成中医相关性得分
        tcm_relevance = self.generate_tcm_relevance(features)
        
        # 计算置信度
        confidence = self.calculate_confidence(features)
        
        # 生成分析摘要和诊断提示
        diagnostic_hint = self.generate_diagnostic_hint(features, tcm_relevance)
        
        # 构建分析对象
        analysis = {
            "analysis_id": f"voice_{int(time.time()*1000)}",
            "speech_rate": features.get("speech_rate", 0.0),
            "pitch_avg": features.get("f0_mean", 0.0),
            "pitch_range": features.get("f0_range", 0.0),
            "volume_avg": features.get("volume_avg", 0.0),
            "voice_stability": features.get("voice_stability", 0.0),
            "breathiness": features.get("breathiness", 0.0),
            "features": self.format_voice_features(features),
            "tcm_relevance": tcm_relevance,
            "diagnostic_hint": diagnostic_hint,
            "confidence": confidence,
            "timestamp": int(time.time()),
            "processing_time": time.time() - start_time
        }
        
        return analysis
    
    def extract_voice_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取语音特有的特征
        
        Args:
            audio: 音频数据
            sr: 采样率
            
        Returns:
            Dict[str, Any]: 语音特征
        """
        features = {}
        
        # 使用Praat库提取语音特征
        try:
            # 转换为Praat Sound对象
            sound = parselmouth.Sound(audio, sr)
            
            # 提取基频特征
            pitch = call(sound, "To Pitch", 0.0, 75, 500)
            features["f0_mean"] = call(pitch, "Get mean", 0, 0, "Hertz")
            features["f0_std"] = call(pitch, "Get standard deviation", 0, 0, "Hertz")
            f0_min = call(pitch, "Get minimum", 0, 0, "Hertz", "Parabolic")
            f0_max = call(pitch, "Get maximum", 0, 0, "Hertz", "Parabolic")
            features["f0_min"] = f0_min if f0_min > 0 else 0
            features["f0_max"] = f0_max if f0_max > 0 else 0
            features["f0_range"] = f0_max - f0_min if f0_max > 0 and f0_min > 0 else 0
            
            # 计算抖动和颤音
            point_process = call(sound, "To PointProcess (periodic, cc)", 75, 500)
            features["jitter_local"] = call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
            features["jitter_rap"] = call(point_process, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
            features["shimmer_local"] = call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
            features["shimmer_apq5"] = call([sound, point_process], "Get shimmer (apq5)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
            
            # 谐噪比，评估声音质量
            harmonicity = call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
            features["hnr"] = call(harmonicity, "Get mean", 0, 0)
            
            # 共振峰分析，评估声道特性
            formant = call(sound, "To Formant (burg)", 0.0025, 5, 5000, 0.025, 50)
            features["formant1_mean"] = call(formant, "Get mean", 1, 0, 0, "Hertz")
            features["formant2_mean"] = call(formant, "Get mean", 2, 0, 0, "Hertz")
            features["formant3_mean"] = call(formant, "Get mean", 3, 0, 0, "Hertz")
            
            # 计算气息性参数（基于谐噪比的倒数）
            if features["hnr"] > 0:
                features["breathiness"] = 1.0 / (1.0 + features["hnr"] / 10.0)  # 标准化到0-1
            else:
                features["breathiness"] = 1.0
            
            # 计算声音稳定性（基于抖动和颤音的组合）
            jitter_norm = min(1.0, features["jitter_local"] / 0.01)  # 标准抖动阈值约为1%
            shimmer_norm = min(1.0, features["shimmer_local"] / 0.06)  # 标准颤音阈值约为6%
            features["voice_stability"] = 1.0 - (jitter_norm + shimmer_norm) / 2.0
            
        except Exception as e:
            logger.error(f"Praat特征提取失败: {str(e)}")
            # 设置默认值
            features["f0_mean"] = 0.0
            features["f0_std"] = 0.0
            features["f0_min"] = 0.0
            features["f0_max"] = 0.0
            features["f0_range"] = 0.0
            features["jitter_local"] = 0.0
            features["jitter_rap"] = 0.0
            features["shimmer_local"] = 0.0
            features["shimmer_apq5"] = 0.0
            features["hnr"] = 0.0
            features["formant1_mean"] = 0.0
            features["formant2_mean"] = 0.0
            features["formant3_mean"] = 0.0
            features["breathiness"] = 0.5
            features["voice_stability"] = 0.5
        
        # 计算语速（基于音节检测）
        try:
            # 一个简单的语速估计
            energy = librosa.feature.rms(y=audio)[0]
            peaks = librosa.util.peak_pick(energy, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.1, wait=10)
            
            # 假设每个峰值大致对应一个音节
            if len(audio) / sr > 0.5:  # 只处理长度超过0.5秒的音频
                duration = len(audio) / sr
                syllable_count = len(peaks)
                features["speech_rate"] = syllable_count / (duration / 60.0)  # 音节/分钟
            else:
                features["speech_rate"] = 0.0
                
        except Exception as e:
            logger.error(f"语速计算失败: {str(e)}")
            features["speech_rate"] = 0.0
        
        # 计算音量特征
        features["volume_avg"] = np.mean(np.abs(audio)) * 100  # 标准化到更可读的范围
        features["volume_std"] = np.std(np.abs(audio)) * 100
        
        return features
    
    def format_voice_features(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        格式化语音特征为前端可用的结构
        
        Args:
            features: 提取的特征字典
            
        Returns:
            List[Dict[str, Any]]: 格式化的特征列表
        """
        formatted_features = []
        
        # 定义要包含的特征及其描述
        feature_definitions = {
            "f0_mean": {
                "name": "平均音调",
                "unit": "Hz",
                "description": "说话者的平均音调频率",
                "significance": 0.9
            },
            "f0_range": {
                "name": "音调范围",
                "unit": "Hz", 
                "description": "说话者音调的变化范围",
                "significance": 0.8
            },
            "speech_rate": {
                "name": "语速",
                "unit": "音节/分钟",
                "description": "说话速度",
                "significance": 0.7
            },
            "jitter_local": {
                "name": "音调微扰",
                "unit": "",
                "description": "音调的短期波动，反映声带稳定性",
                "significance": 0.75
            },
            "shimmer_local": {
                "name": "振幅微扰",
                "unit": "",
                "description": "音量的短期波动，反映发声稳定性",
                "significance": 0.7
            },
            "hnr": {
                "name": "谐噪比",
                "unit": "dB",
                "description": "声音中谐波与噪声的比例，反映声音质量",
                "significance": 0.8
            },
            "breathiness": {
                "name": "气息音特征",
                "unit": "",
                "description": "声音中气息成分的占比",
                "significance": 0.85
            },
            "formant1_mean": {
                "name": "第一共振峰",
                "unit": "Hz",
                "description": "与口腔开合度相关的声学特征",
                "significance": 0.65
            },
            "formant2_mean": {
                "name": "第二共振峰",
                "unit": "Hz",
                "description": "与舌位前后位置相关的声学特征",
                "significance": 0.6
            },
            "voice_stability": {
                "name": "声音稳定性",
                "unit": "",
                "description": "声音保持稳定的程度",
                "significance": 0.85
            }
        }
        
        # 添加存在于特征字典中的项目
        for feature_key, definition in feature_definitions.items():
            if feature_key in features:
                formatted_features.append({
                    "feature_name": definition["name"],
                    "value": float(features[feature_key]),
                    "unit": definition["unit"],
                    "description": definition["description"],
                    "significance": definition["significance"]
                })
        
        return formatted_features
    
    def generate_tcm_relevance(self, features: Dict[str, Any]) -> Dict[str, float]:
        """
        生成中医相关性得分
        
        Args:
            features: 提取的特征字典
            
        Returns:
            Dict[str, float]: 中医证型相关性得分
        """
        # 这里是简化的中医相关性推断
        # 实际项目中应使用训练好的模型
        
        # 注意：这些关联是示例性的，实际应基于中医理论和数据分析
        relevance = {}
        
        # 气虚证相关特征
        if "breathiness" in features and "voice_stability" in features and "hnr" in features:
            qi_xu_score = 0.0
            if features["breathiness"] > 0.6:  # 气息音高
                qi_xu_score += 0.4
            if features["voice_stability"] < 0.5:  # 声音不稳
                qi_xu_score += 0.3
            if features["hnr"] < 10:  # 谐噪比低
                qi_xu_score += 0.3
                
            relevance["气虚证"] = min(1.0, qi_xu_score)
        
        # 阴虚证相关特征
        if "f0_mean" in features and "shimmer_local" in features:
            yin_xu_score = 0.0
            if features.get("f0_mean", 0) > 150:  # 音调偏高
                yin_xu_score += 0.4
            if features.get("speech_rate", 0) > 240:  # 语速快
                yin_xu_score += 0.3
            if features.get("shimmer_local", 0) > 0.05:  # 振幅不稳
                yin_xu_score += 0.3
                
            relevance["阴虚证"] = min(1.0, yin_xu_score)
        
        # 痰湿证相关特征
        if "formant1_mean" in features and "formant2_mean" in features:
            tan_shi_score = 0.0
            if features.get("breathiness", 0) > 0.7:  # 明显气息音
                tan_shi_score += 0.3
            if features.get("formant1_mean", 0) < 500:  # 第一共振峰低
                tan_shi_score += 0.3
            if features.get("speech_rate", 0) < 150:  # 语速慢
                tan_shi_score += 0.4
                
            relevance["痰湿证"] = min(1.0, tan_shi_score)
        
        # 其他证型...
        
        # 添加中医五音关联（宫商角徵羽）
        if "f0_mean" in features:
            pitch = features["f0_mean"]
            if 65 <= pitch < 130:  # 宫音范围（示例值）
                relevance["宫音"] = 0.8
            elif 130 <= pitch < 195:  # 商音范围
                relevance["商音"] = 0.8
            elif 195 <= pitch < 260:  # 角音范围
                relevance["角音"] = 0.8
            elif 260 <= pitch < 325:  # 徵音范围
                relevance["徵音"] = 0.8
            elif pitch >= 325:  # 羽音范围
                relevance["羽音"] = 0.8
        
        return relevance
    
    def calculate_confidence(self, features: Dict[str, Any]) -> float:
        """
        计算分析结果的置信度
        
        Args:
            features: 提取的特征字典
            
        Returns:
            float: 置信度得分(0-1)
        """
        # 基于特征完整性和质量计算置信度
        if not features:
            return 0.0
            
        # 检查关键特征是否存在
        key_features = ["f0_mean", "jitter_local", "shimmer_local", "hnr", "voice_stability"]
        feature_presence = sum(1 for f in key_features if f in features and features[f] > 0) / len(key_features)
        
        # 检查音频质量
        quality_score = 0.0
        if "voice_stability" in features:
            quality_score += features["voice_stability"] * 0.5
        if "hnr" in features:
            hnr_norm = min(1.0, features["hnr"] / 20.0)  # 规范化，20dB是较好的谐噪比
            quality_score += hnr_norm * 0.5
        
        # 加权平均
        confidence = 0.7 * feature_presence + 0.3 * quality_score
        
        return min(1.0, max(0.1, confidence))  # 限制在0.1-1.0范围
    
    def generate_diagnostic_hint(self, features: Dict[str, Any], tcm_relevance: Dict[str, float]) -> str:
        """
        生成诊断提示文本
        
        Args:
            features: 提取的特征字典
            tcm_relevance: 中医相关性得分
            
        Returns:
            str: 诊断提示文本
        """
        if not features or not tcm_relevance:
            return "音频质量不足，无法生成有效诊断提示。"
        
        # 找出最高相关性的证型
        top_pattern = max(tcm_relevance.items(), key=lambda x: x[1], default=(None, 0))
        
        if top_pattern[1] < 0.5:
            return "根据语音特征，未发现明显中医证型特征。"
        
        # 根据不同证型生成不同提示
        hint = f"语音分析提示可能存在{top_pattern[0]}特征"
        
        # 添加具体特征描述
        if top_pattern[0] == "气虚证":
            if features.get("breathiness", 0) > 0.6:
                hint += "，语音气息偏弱"
            if features.get("voice_stability", 0) < 0.5:
                hint += "，声音不稳"
        
        elif top_pattern[0] == "阴虚证":
            if features.get("f0_mean", 0) > 150:
                hint += "，音调偏高"
            if features.get("speech_rate", 0) > 240:
                hint += "，语速较快"
        
        elif top_pattern[0] == "痰湿证":
            if features.get("speech_rate", 0) < 150:
                hint += "，语速偏缓"
            if features.get("breathiness", 0) > 0.7:
                hint += "，存在明显气息音"
        
        hint += f"，置信度为{top_pattern[1]:.2f}。"
        
        return hint


class DummyVoiceModel:
    """
    模拟语音分析模型，用于开发和测试环境
    """
    def __init__(self, device_name):
        self.device = device_name
        logger.warning("使用模拟语音分析模型")
    
    def eval(self):
        return self
    
    def half(self):
        return self
    
    def __call__(self, audio_tensor):
        # 返回模拟的预测结果
        batch_size = audio_tensor.shape[0]
        # 为每个批次样本生成随机特征（模拟）
        dummy_features = torch.rand((batch_size, 10))
        return dummy_features 