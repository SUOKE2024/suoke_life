"""
声音分析器 - 处理非语言声音，如咳嗽、呼吸等
"""
import os
import time
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union

import torch
import librosa
from scipy import signal
from scipy.stats import skew, kurtosis

from internal.audio.audio_analyzer import AudioAnalyzer

logger = logging.getLogger(__name__)

class SoundAnalyzer(AudioAnalyzer):
    """声音分析器，用于分析咳嗽、呼吸等非语言声音"""
    
    def __init__(self, config: Dict):
        """
        初始化声音分析器
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        
        # 加载模型配置
        model_config = config.get("models", {}).get("sound_model", {})
        self.model_path = model_config.get("path")
        self.model_name = model_config.get("name", "sound_feature_analyzer")
        self.model_version = model_config.get("version", "1.0.0")
        self.batch_size = model_config.get("batch_size", 8)
        self.device_name = model_config.get("device", "cuda:0" if torch.cuda.is_available() else "cpu")
        self.precision = model_config.get("precision", "fp32")
        self.threshold = model_config.get("threshold", 0.7)
        
        # 是否预加载模型
        self.preload = model_config.get("preload", True)
        self.model = None
        
        # TCM特定配置
        self.tcm_config = config.get("tcm", {})
        
        if self.preload:
            self.load_model()
            
        logger.info(f"声音分析器初始化完成，模型：{self.model_name}, 版本：{self.model_version}")
    
    def load_model(self):
        """加载声音分析模型"""
        if self.model is not None:
            return
            
        try:
            logger.info(f"加载声音分析模型: {self.model_path}")
            start_time = time.time()
            
            # 注意：这里是模型加载的占位代码
            # 实际项目中需要替换为真实的模型加载逻辑
            
            # 使用PyTorch框架示例:
            if os.path.exists(self.model_path):
                self.model = torch.jit.load(self.model_path, map_location=self.device_name)
                self.model.eval()
                if self.precision == "fp16" and "cuda" in self.device_name:
                    self.model = self.model.half()
            else:
                # 开发模式下可以使用模拟模型
                logger.warning(f"模型文件不存在: {self.model_path}，使用模拟模型")
                self.model = DummySoundModel(self.device_name)
            
            load_time = time.time() - start_time
            logger.info(f"模型加载完成，耗时：{load_time:.2f}秒")
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            # 开发模式下使用模拟模型
            self.model = DummySoundModel(self.device_name)
    
    def analyze_sound(self, audio_data: bytes, audio_format: str, 
                     sound_type: str = None, sample_rate: int = None, 
                     apply_preprocessing: bool = True, 
                     **kwargs) -> Dict[str, Any]:
        """
        分析非语言声音，如咳嗽、呼吸等
        
        Args:
            audio_data: 原始音频二进制数据
            audio_format: 音频格式
            sound_type: 声音类型，如"COUGH"，"BREATHING"等
            sample_rate: 音频采样率，如未提供则从音频文件读取
            apply_preprocessing: 是否应用预处理
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        start_time = time.time()
        
        # 加载模型（如果尚未加载）
        if self.model is None:
            self.load_model()
        
        # 加载音频
        target_sr = self.audio_config.get("default_sample_rate", 16000) if sample_rate is None else sample_rate
        audio, sr = self.load_audio(audio_data, audio_format, target_sr=target_sr, convert_to_mono=True)
        
        # 预处理音频
        if apply_preprocessing:
            audio = self.preprocess_audio(audio, sr)
        
        # 提取通用特征
        features = self.extract_features(audio, sr)
        
        # 提取声音特有特征
        sound_features = self.extract_sound_features(audio, sr)
        features.update(sound_features)
        
        # 如果未提供声音类型，则进行分类
        detected_sound_type = sound_type
        if not detected_sound_type:
            detected_sound_type = self.classify_sound_type(audio, sr, features)
        
        # 分析特定类型的声音
        sound_patterns = self.analyze_specific_sound(audio, sr, detected_sound_type, features)
        
        # 生成中医相关性得分
        tcm_relevance = self.generate_tcm_relevance(features, detected_sound_type)
        
        # 计算置信度
        confidence = self.calculate_confidence(features, detected_sound_type)
        
        # 生成诊断提示
        diagnostic_hint = self.generate_diagnostic_hint(features, tcm_relevance, detected_sound_type)
        
        # 构建分析对象
        analysis = {
            "analysis_id": f"sound_{int(time.time()*1000)}",
            "sound_type": detected_sound_type,
            "duration": features.get("duration", 0.0),
            "amplitude": features.get("rms_energy", 0.0),
            "regularity": features.get("regularity", 0.0),
            "moisture": features.get("moisture", 0.5),
            "patterns": sound_patterns,
            "tcm_relevance": tcm_relevance,
            "diagnostic_hint": diagnostic_hint,
            "confidence": confidence,
            "timestamp": int(time.time()),
            "processing_time": time.time() - start_time
        }
        
        return analysis
    
    def extract_sound_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取声音特有的特征
        
        Args:
            audio: 音频数据
            sr: 采样率
            
        Returns:
            Dict[str, Any]: 声音特征
        """
        features = {}
        
        # 计算能量包络
        energy = np.abs(librosa.feature.rms(y=audio)[0])
        
        # 计算声音的规律性
        # 使用能量包络的自相关来估计规律性
        if len(energy) > 1:
            # 计算自相关
            correlation = np.correlate(energy, energy, mode='full')
            correlation = correlation[len(correlation)//2:]
            
            # 寻找自相关中的峰值
            peaks, _ = signal.find_peaks(correlation, height=0.1*np.max(correlation))
            
            if len(peaks) > 1:
                # 计算峰值间距的变异系数，越小越规律
                peak_dists = np.diff(peaks)
                if len(peak_dists) > 0:
                    cv = np.std(peak_dists) / np.mean(peak_dists) if np.mean(peak_dists) > 0 else 1.0
                    features["regularity"] = max(0.0, min(1.0, 1.0 - cv))
                else:
                    features["regularity"] = 0.5
            else:
                features["regularity"] = 0.5
        else:
            features["regularity"] = 0.5
        
        # 计算声音的湿度特征 (干声-湿声 特征)
        # 干声通常高频能量比例更高，湿声低频能量比例高

        # 计算频谱
        D = np.abs(librosa.stft(audio))
        
        # 将频谱分为低频和高频部分
        freq_bins = D.shape[0]
        low_freq_limit = int(freq_bins * 0.3)  # 低频部分约占30%
        
        low_energy = np.sum(D[:low_freq_limit, :])
        high_energy = np.sum(D[low_freq_limit:, :])
        total_energy = low_energy + high_energy
        
        if total_energy > 0:
            # 湿声低频能量占比高，得分越高越湿
            low_freq_ratio = low_energy / total_energy
            features["moisture"] = low_freq_ratio
        else:
            features["moisture"] = 0.5
        
        # 计算频谱特征
        spec_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        spec_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0]
        spec_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
        
        features["spectral_centroid_mean"] = float(np.mean(spec_centroid))
        features["spectral_centroid_std"] = float(np.std(spec_centroid))
        features["spectral_bandwidth_mean"] = float(np.mean(spec_bandwidth))
        features["spectral_rolloff_mean"] = float(np.mean(spec_rolloff))
        
        # 计算统计特征
        if len(audio) > 0:
            features["audio_mean"] = float(np.mean(audio))
            features["audio_std"] = float(np.std(audio))
            features["audio_skewness"] = float(skew(audio))
            features["audio_kurtosis"] = float(kurtosis(audio))
        
        return features
    
    def classify_sound_type(self, audio: np.ndarray, sr: int, features: Dict[str, Any]) -> str:
        """
        对声音类型进行分类
        
        Args:
            audio: 音频数据
            sr: 采样率
            features: 已提取的特征
            
        Returns:
            str: 声音类型枚举值
        """
        try:
            # 使用模型进行分类
            audio_tensor = torch.FloatTensor(audio).to(self.device_name)
            audio_tensor = audio_tensor.unsqueeze(0)  # 添加批次维度
            
            with torch.no_grad():
                prediction = self.model(audio_tensor)
                
            # 假设模型输出是类别的概率分布
            if isinstance(prediction, torch.Tensor):
                if prediction.ndim > 1 and prediction.shape[1] >= 5:
                    # 获取最大概率的类别
                    class_idx = torch.argmax(prediction, dim=1).item()
                    sound_types = ["SOUND_UNKNOWN", "COUGH", "BREATHING", "SNORING", "HEART_SOUND", "OTHER"]
                    
                    # 确保索引在范围内
                    if 0 <= class_idx < len(sound_types):
                        return sound_types[class_idx]
            
            # 如果模型预测失败，使用规则进行分类
            return self._rule_based_classification(features)
            
        except Exception as e:
            logger.error(f"声音类型分类失败: {str(e)}")
            # 失败时使用规则进行分类
            return self._rule_based_classification(features)
    
    def _rule_based_classification(self, features: Dict[str, Any]) -> str:
        """
        使用规则进行声音类型分类
        
        Args:
            features: 已提取的特征
            
        Returns:
            str: 声音类型枚举值
        """
        # 规则基础的分类逻辑，基于特征
        
        # 咳嗽声特征: 高峰值能量, 短持续时间, 高规律性
        if features.get("duration", 0) < 2.0 and features.get("regularity", 0) > 0.7:
            return "COUGH"
        
        # 呼吸声特征: 中等规律性, 持续周期性
        elif 0.4 <= features.get("regularity", 0) <= 0.7 and features.get("duration", 0) > 3.0:
            return "BREATHING"
        
        # 鼾声特征: 高规律性, 低频能量高
        elif features.get("regularity", 0) > 0.6 and features.get("moisture", 0) > 0.7:
            return "SNORING"
        
        # 心音特征: 高规律性, 低频
        elif features.get("regularity", 0) > 0.8 and features.get("spectral_centroid_mean", 1000) < 300:
            return "HEART_SOUND"
        
        # 默认未知
        return "SOUND_UNKNOWN"
    
    def analyze_specific_sound(self, audio: np.ndarray, sr: int, 
                              sound_type: str, 
                              features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        分析特定类型的声音，提取专门特征
        
        Args:
            audio: 音频数据
            sr: 采样率
            sound_type: 声音类型
            features: 已提取的特征
            
        Returns:
            List[Dict[str, Any]]: 声音模式列表
        """
        patterns = []
        
        if sound_type == "COUGH":
            # 分析咳嗽声的特征
            patterns.extend(self._analyze_cough(audio, sr, features))
            
        elif sound_type == "BREATHING":
            # 分析呼吸声的特征
            patterns.extend(self._analyze_breathing(audio, sr, features))
            
        elif sound_type == "SNORING":
            # 分析鼾声的特征
            patterns.extend(self._analyze_snoring(audio, sr, features))
            
        elif sound_type == "HEART_SOUND":
            # 分析心音的特征
            patterns.extend(self._analyze_heart_sound(audio, sr, features))
        
        # 为空时添加默认模式
        if not patterns:
            patterns.append({
                "pattern_name": "未识别模式",
                "score": 0.5,
                "description": "未能识别出明确的声音模式",
                "significance": 0.3
            })
        
        return patterns
    
    def _analyze_cough(self, audio: np.ndarray, sr: int, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析咳嗽声的特性"""
        patterns = []
        
        # 检查干/湿咳嗽
        moisture = features.get("moisture", 0.5)
        if moisture > 0.7:
            patterns.append({
                "pattern_name": "湿咳",
                "score": min(1.0, moisture),
                "description": "咳嗽声中含有明显的湿性成分，可能与痰液分泌过多相关",
                "significance": 0.9
            })
        elif moisture < 0.4:
            patterns.append({
                "pattern_name": "干咳",
                "score": min(1.0, 1.0 - moisture),
                "description": "咳嗽声干燥无痰，可能与气道炎症或刺激相关",
                "significance": 0.9
            })
        
        # 检查咳嗽强度
        energy = features.get("rms_energy", 0)
        if energy > 0.2:
            patterns.append({
                "pattern_name": "强力咳嗽",
                "score": min(1.0, energy/0.3),
                "description": "咳嗽声强度大，显示肺部排痰能力强",
                "significance": 0.7
            })
        elif energy < 0.1:
            patterns.append({
                "pattern_name": "虚弱咳嗽",
                "score": min(1.0, 1.0 - energy/0.1),
                "description": "咳嗽声强度弱，可能与体力不足或肺气亏虚相关",
                "significance": 0.8
            })
        
        # 检查咳嗽规律性
        regularity = features.get("regularity", 0.5)
        if regularity > 0.7:
            patterns.append({
                "pattern_name": "规律性咳嗽",
                "score": regularity,
                "description": "咳嗽声具有明显规律性，可能与慢性呼吸系统疾病相关",
                "significance": 0.6
            })
        
        return patterns
    
    def _analyze_breathing(self, audio: np.ndarray, sr: int, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析呼吸声的特性"""
        patterns = []
        
        # 检查呼吸声湿度
        moisture = features.get("moisture", 0.5)
        if moisture > 0.7:
            patterns.append({
                "pattern_name": "湿性呼吸音",
                "score": min(1.0, moisture),
                "description": "呼吸声中含有明显的湿性成分，可能与气道分泌物增多相关",
                "significance": 0.85
            })
        
        # 检查呼吸频率
        # 通过能量波动估计呼吸频率
        if "regularity" in features and features["regularity"] > 0.5:
            energy = librosa.feature.rms(y=audio)[0]
            peaks, _ = signal.find_peaks(energy, height=0.1*np.max(energy), distance=sr*0.5)
            
            if len(peaks) > 1:
                duration = len(audio) / sr
                breaths_per_minute = len(peaks) / duration * 60
                
                if breaths_per_minute > 20:
                    patterns.append({
                        "pattern_name": "呼吸频率增快",
                        "score": min(1.0, (breaths_per_minute - 20) / 10),
                        "description": f"呼吸频率约为{breaths_per_minute:.1f}次/分钟，高于正常范围",
                        "significance": 0.8
                    })
                elif breaths_per_minute < 12:
                    patterns.append({
                        "pattern_name": "呼吸频率减慢",
                        "score": min(1.0, (12 - breaths_per_minute) / 6),
                        "description": f"呼吸频率约为{breaths_per_minute:.1f}次/分钟，低于正常范围",
                        "significance": 0.75
                    })
        
        # 检查呼吸声强度
        energy = features.get("rms_energy", 0)
        spectral_centroid = features.get("spectral_centroid_mean", 0)
        
        if energy < 0.05:
            patterns.append({
                "pattern_name": "微弱呼吸音",
                "score": min(1.0, 1.0 - energy/0.05),
                "description": "呼吸声强度弱，可能与肺功能减弱或气道通气不畅相关",
                "significance": 0.7
            })
        
        if spectral_centroid > 1000:
            patterns.append({
                "pattern_name": "高频呼吸音",
                "score": min(1.0, (spectral_centroid - 1000) / 1000),
                "description": "呼吸声中高频成分明显，可能与细小气道狭窄相关",
                "significance": 0.65
            })
        
        return patterns
    
    def _analyze_snoring(self, audio: np.ndarray, sr: int, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析鼾声的特性"""
        patterns = []
        
        # 检查鼾声规律性
        regularity = features.get("regularity", 0.5)
        if regularity < 0.4:
            patterns.append({
                "pattern_name": "不规则鼾声",
                "score": min(1.0, 1.0 - regularity/0.4),
                "description": "鼾声呈现不规则模式，可能与呼吸暂停综合征相关",
                "significance": 0.85
            })
        
        # 检查鼾声强度
        energy = features.get("rms_energy", 0)
        if energy > 0.2:
            patterns.append({
                "pattern_name": "高强度鼾声",
                "score": min(1.0, energy/0.3),
                "description": "鼾声强度大，可能与上呼吸道严重阻塞相关",
                "significance": 0.7
            })
        
        # 检查鼾声频谱特性
        spectral_centroid = features.get("spectral_centroid_mean", 0)
        spectral_bandwidth = features.get("spectral_bandwidth_mean", 0)
        
        if spectral_centroid < 500 and spectral_bandwidth < 1000:
            patterns.append({
                "pattern_name": "低频窄谱鼾声",
                "score": min(1.0, (500 - spectral_centroid) / 500),
                "description": "鼾声以低频为主且频带窄，常见于软腭振动引起的鼾声",
                "significance": 0.6
            })
        
        return patterns
    
    def _analyze_heart_sound(self, audio: np.ndarray, sr: int, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析心音的特性"""
        patterns = []
        
        # 检查心音规律性
        regularity = features.get("regularity", 0.5)
        if regularity < 0.6:
            patterns.append({
                "pattern_name": "心律不齐",
                "score": min(1.0, 1.0 - regularity/0.6),
                "description": "心音节律不规则，可能与心律失常相关",
                "significance": 0.9
            })
        
        # 检查是否有杂音
        spectral_bandwidth = features.get("spectral_bandwidth_mean", 0)
        spectral_contrast = np.mean(librosa.feature.spectral_contrast(y=audio, sr=sr)) if len(audio) > 0 else 0
        
        if spectral_bandwidth > 800 and spectral_contrast < 15:
            patterns.append({
                "pattern_name": "心音杂音",
                "score": min(1.0, spectral_bandwidth/1000),
                "description": "心音中可能存在杂音，建议进一步临床检查",
                "significance": 0.85
            })
        
        # 估计心率
        if len(audio) / sr > 5:  # 需要足够长的音频
            energy = librosa.feature.rms(y=audio)[0]
            peaks, _ = signal.find_peaks(energy, height=0.1*np.max(energy), distance=sr*0.3)
            
            if len(peaks) > 1:
                duration = len(audio) / sr
                beats_per_minute = len(peaks) / duration * 60
                
                if beats_per_minute > 100:
                    patterns.append({
                        "pattern_name": "心率增快",
                        "score": min(1.0, (beats_per_minute - 100) / 40),
                        "description": f"预估心率约为{beats_per_minute:.1f}次/分钟，高于正常范围",
                        "significance": 0.8
                    })
                elif beats_per_minute < 60:
                    patterns.append({
                        "pattern_name": "心率减慢",
                        "score": min(1.0, (60 - beats_per_minute) / 20),
                        "description": f"预估心率约为{beats_per_minute:.1f}次/分钟，低于正常范围",
                        "significance": 0.8
                    })
        
        return patterns
    
    def generate_tcm_relevance(self, features: Dict[str, Any], sound_type: str) -> Dict[str, float]:
        """
        生成中医相关性得分
        
        Args:
            features: 提取的特征字典
            sound_type: 声音类型
            
        Returns:
            Dict[str, float]: 中医证型相关性得分
        """
        # 这里是简化的中医相关性推断
        # 实际项目中应使用训练好的模型
        
        # 不同声音类型有不同的中医关联规则
        relevance = {}
        
        if sound_type == "COUGH":
            # 咳嗽与中医证型的关联
            moisture = features.get("moisture", 0.5)
            energy = features.get("rms_energy", 0)
            
            # 湿咳与痰湿证关联
            if moisture > 0.7:
                relevance["痰湿证"] = min(1.0, moisture)
            
            # 干咳与肺阴虚证关联
            if moisture < 0.4:
                relevance["肺阴虚证"] = min(1.0, 1.0 - moisture)
            
            # 弱咳与气虚证关联
            if energy < 0.1:
                relevance["气虚证"] = min(1.0, 1.0 - energy/0.1)
                
        elif sound_type == "BREATHING":
            # 呼吸声与中医证型的关联
            moisture = features.get("moisture", 0.5)
            energy = features.get("rms_energy", 0)
            
            # 湿性呼吸音与痰湿证关联
            if moisture > 0.7:
                relevance["痰湿证"] = min(1.0, moisture)
            
            # 弱呼吸声与气虚证关联
            if energy < 0.05:
                relevance["气虚证"] = min(1.0, 1.0 - energy/0.05)
                
        elif sound_type == "SNORING":
            # 鼾声与中医证型的关联
            moisture = features.get("moisture", 0.5)
            
            # 鼾声与痰湿证、血瘀证关联
            if moisture > 0.6:
                relevance["痰湿证"] = min(1.0, moisture)
                
            # 高强度鼾声与阳亢证关联
            energy = features.get("rms_energy", 0)
            if energy > 0.2:
                relevance["阳亢证"] = min(1.0, energy/0.3)
                
        elif sound_type == "HEART_SOUND":
            # 心音与中医证型的关联
            regularity = features.get("regularity", 0.5)
            
            # 不规则心音与心气虚、心阳虚关联
            if regularity < 0.6:
                relevance["心气虚证"] = min(1.0, 1.0 - regularity/0.6)
            
            # 估计心率相关性
            if "breaths_per_minute" in features:
                bpm = features["breaths_per_minute"]
                if bpm > 100:
                    relevance["心火亢盛"] = min(1.0, (bpm - 100) / 40)
                elif bpm < 60:
                    relevance["心阳虚证"] = min(1.0, (60 - bpm) / 20)
        
        return relevance
    
    def calculate_confidence(self, features: Dict[str, Any], sound_type: str) -> float:
        """
        计算分析结果的置信度
        
        Args:
            features: 提取的特征字典
            sound_type: 声音类型
            
        Returns:
            float: 置信度得分(0-1)
        """
        # 基于特征完整性和质量计算置信度
        if not features:
            return 0.0
            
        # 基础置信度
        base_confidence = 0.5
        
        # 基于声音类型调整
        if sound_type == "SOUND_UNKNOWN":
            base_confidence *= 0.6
        
        # 检查关键特征是否存在
        key_features = ["rms_energy", "spectral_centroid_mean", "regularity", "moisture"]
        feature_presence = sum(1 for f in key_features if f in features) / len(key_features)
        
        # 检查音频质量
        quality_score = 0.0
        if "rms_energy" in features:
            energy_norm = min(1.0, features["rms_energy"] / 0.2)
            quality_score += energy_norm * 0.5
            
        if "regularity" in features:
            quality_score += features["regularity"] * 0.5
        
        # 加权平均
        confidence = 0.3 * base_confidence + 0.4 * feature_presence + 0.3 * quality_score
        
        return min(1.0, max(0.1, confidence))  # 限制在0.1-1.0范围
    
    def generate_diagnostic_hint(self, features: Dict[str, Any], 
                                tcm_relevance: Dict[str, float], 
                                sound_type: str) -> str:
        """
        生成诊断提示文本
        
        Args:
            features: 提取的特征字典
            tcm_relevance: 中医相关性得分
            sound_type: 声音类型
            
        Returns:
            str: 诊断提示文本
        """
        if not features or sound_type == "SOUND_UNKNOWN":
            return "声音类型无法识别或质量不足，无法生成有效诊断提示。"
        
        # 找出最高相关性的证型
        top_pattern = max(tcm_relevance.items(), key=lambda x: x[1], default=(None, 0))
        
        if top_pattern[1] < 0.5:
            return f"根据{self._sound_type_to_chinese(sound_type)}分析，未发现明显中医证型特征。"
        
        # 根据不同声音类型和证型生成不同提示
        hint = f"{self._sound_type_to_chinese(sound_type)}分析提示可能存在{top_pattern[0]}特征"
        
        if sound_type == "COUGH":
            # 咳嗽特征描述
            if features.get("moisture", 0.5) > 0.7:
                hint += "，咳嗽声音湿润有痰"
            elif features.get("moisture", 0.5) < 0.4:
                hint += "，咳嗽声干燥无痰"
                
            if features.get("rms_energy", 0.2) < 0.1:
                hint += "，咳嗽力度较弱"
        
        elif sound_type == "BREATHING":
            # 呼吸特征描述
            if features.get("moisture", 0.5) > 0.7:
                hint += "，呼吸音中含有湿性啰音"
                
            if "breaths_per_minute" in features:
                if features["breaths_per_minute"] > 20:
                    hint += f"，呼吸频率较快(约{features['breaths_per_minute']:.1f}次/分钟)"
                elif features["breaths_per_minute"] < 12:
                    hint += f"，呼吸频率较慢(约{features['breaths_per_minute']:.1f}次/分钟)"
        
        elif sound_type == "SNORING":
            # 鼾声特征描述
            if features.get("regularity", 0.5) < 0.4:
                hint += "，鼾声不规则"
            if features.get("rms_energy", 0.1) > 0.2:
                hint += "，鼾声强度大"
        
        elif sound_type == "HEART_SOUND":
            # 心音特征描述
            if features.get("regularity", 0.7) < 0.6:
                hint += "，心音节律不规则"
                
            if "breaths_per_minute" in features:
                if features["breaths_per_minute"] > 100:
                    hint += f"，心率较快(约{features['breaths_per_minute']:.1f}次/分钟)"
                elif features["breaths_per_minute"] < 60:
                    hint += f"，心率较慢(约{features['breaths_per_minute']:.1f}次/分钟)"
        
        hint += f"，置信度为{top_pattern[1]:.2f}。"
        
        return hint
    
    def _sound_type_to_chinese(self, sound_type: str) -> str:
        """将声音类型枚举转换为中文描述"""
        mapping = {
            "COUGH": "咳嗽声",
            "BREATHING": "呼吸声",
            "SNORING": "鼾声",
            "HEART_SOUND": "心音",
            "SOUND_UNKNOWN": "未知声音",
            "OTHER": "其他声音"
        }
        return mapping.get(sound_type, "声音")


class DummySoundModel:
    """
    模拟声音分析模型，用于开发和测试环境
    """
    def __init__(self, device_name):
        self.device = device_name
        logger.warning("使用模拟声音分析模型")
    
    def eval(self):
        return self
    
    def half(self):
        return self
    
    def __call__(self, audio_tensor):
        # 返回模拟的预测结果
        batch_size = audio_tensor.shape[0]
        # 为每个批次样本生成随机类别分数（模拟）
        # 假设有6个类别：未知、咳嗽、呼吸、鼾声、心音、其他
        dummy_classification = torch.rand((batch_size, 6))
        return dummy_classification 