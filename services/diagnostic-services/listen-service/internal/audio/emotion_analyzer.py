"""
情绪分析器 - 从语音中提取情绪特征，支持中医五志（喜、怒、忧、思、恐）分析
"""
import os
import time
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union

import torch
import librosa
from scipy import signal

from internal.audio.audio_analyzer import AudioAnalyzer

logger = logging.getLogger(__name__)

class EmotionAnalyzer(AudioAnalyzer):
    """情绪分析器，从语音中提取情绪特征"""
    
    def __init__(self, config: Dict):
        """
        初始化情绪分析器
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        
        # 加载模型配置
        model_config = config.get("models", {}).get("emotion_model", {})
        self.model_path = model_config.get("path")
        self.model_name = model_config.get("name", "emotion_detector")
        self.model_version = model_config.get("version", "1.0.0")
        self.batch_size = model_config.get("batch_size", 16)
        self.device_name = model_config.get("device", "cuda:0" if torch.cuda.is_available() else "cpu")
        self.precision = model_config.get("precision", "fp32")
        self.threshold = model_config.get("threshold", 0.6)
        
        # 是否预加载模型
        self.preload = model_config.get("preload", True)
        self.model = None
        
        # 情绪类别
        self.emotion_classes = [
            "neutral", "happy", "sad", "angry", "fearful", 
            "disgust", "surprised", "calm", "anxiety", "stress"
        ]
        
        # 中医五志
        self.tcm_emotions = ["喜", "怒", "忧", "思", "恐"]
        
        # TCM特定配置
        self.tcm_config = config.get("tcm", {})
        
        if self.preload:
            self.load_model()
            
        logger.info(f"情绪分析器初始化完成，模型：{self.model_name}, 版本：{self.model_version}")
    
    def load_model(self):
        """加载情绪分析模型"""
        if self.model is not None:
            return
            
        try:
            logger.info(f"加载情绪分析模型: {self.model_path}")
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
                self.model = DummyEmotionModel(self.device_name, len(self.emotion_classes))
            
            load_time = time.time() - start_time
            logger.info(f"模型加载完成，耗时：{load_time:.2f}秒")
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            # 开发模式下使用模拟模型
            self.model = DummyEmotionModel(self.device_name, len(self.emotion_classes))
    
    def analyze_emotion(self, audio_data: bytes, audio_format: str, 
                      sample_rate: int = None, text_transcript: str = None,
                      apply_preprocessing: bool = True, 
                      **kwargs) -> Dict[str, Any]:
        """
        分析语音中的情绪
        
        Args:
            audio_data: 原始音频二进制数据
            audio_format: 音频格式
            sample_rate: 音频采样率，如未提供则从音频文件读取
            text_transcript: 可选的文本记录，用于增强情绪分析
            apply_preprocessing: 是否应用预处理
            
        Returns:
            Dict[str, Any]: 情绪分析结果
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
        
        # 提取情绪特征
        emotion_features = self.extract_emotion_features(audio, sr)
        
        # 预测情绪
        emotions = self.predict_emotions(audio, sr, emotion_features)
        
        # 如果提供了文本记录，结合文本和音频分析
        if text_transcript:
            text_emotions = self.analyze_text_emotion(text_transcript)
            # 融合文本和音频情绪分析结果
            emotions = self.fusion_emotions(emotions, text_emotions)
        
        # 生成中医五志相关性
        tcm_emotions = self.map_to_tcm_emotions(emotions)
        
        # 分析情绪变化趋势
        trend = self.analyze_emotion_trend(audio, sr, emotion_features)
        
        # 计算情绪稳定性
        emotional_stability = self.calculate_emotional_stability(emotions, emotion_features)
        
        # 计算置信度
        confidence = self.calculate_confidence(emotions, emotion_features)
        
        # 生成诊断提示
        diagnostic_hint = self.generate_diagnostic_hint(emotions, tcm_emotions, trend, emotional_stability)
        
        # 构建分析对象
        analysis = {
            "analysis_id": f"emotion_{int(time.time()*1000)}",
            "emotions": emotions,
            "emotional_stability": emotional_stability,
            "tcm_emotions": tcm_emotions,
            "trend": trend,
            "diagnostic_hint": diagnostic_hint,
            "confidence": confidence,
            "timestamp": int(time.time()),
            "processing_time": time.time() - start_time
        }
        
        return analysis
    
    def extract_emotion_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取情绪相关的音频特征
        
        Args:
            audio: 音频数据
            sr: 采样率
            
        Returns:
            Dict[str, Any]: 特征字典
        """
        features = {}
        
        # 跳过静音音频
        if np.max(np.abs(audio)) < 1e-10:
            logger.warning("音频为静音，无法提取情绪特征")
            return features
        
        # 提取基础音频特征
        features["duration"] = len(audio) / sr
        features["rms_energy"] = np.sqrt(np.mean(audio**2))
        
        # 提取MFCC特征（用于情绪分析的重要特征）
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20)
        features["mfccs_mean"] = np.mean(mfccs, axis=1).tolist()
        features["mfccs_std"] = np.std(mfccs, axis=1).tolist()
        
        # 色谱图特征（用于表示声音的时频特性）
        chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
        features["chroma_mean"] = np.mean(chroma, axis=1).tolist()
        
        # 梅尔频谱特征（表示能量分布）
        mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        features["mel_spec_mean"] = np.mean(mel_spec_db, axis=1).tolist()
        
        # 节奏和速度特征
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
        features["tempo"] = float(tempo)
        
        # 声音强度变化（表达情绪的重要指标）
        rms = librosa.feature.rms(y=audio)[0]
        features["rms_mean"] = float(np.mean(rms))
        features["rms_std"] = float(np.std(rms))
        features["rms_max"] = float(np.max(rms))
        
        # 提取声音的基频F0特征（用于判断情绪）
        if len(audio) / sr > 0.5:  # 只处理长度超过0.5秒的音频
            try:
                f0, voiced_flag, _ = librosa.pyin(audio, 
                                                fmin=librosa.note_to_hz('C2'), 
                                                fmax=librosa.note_to_hz('C7'),
                                                sr=sr)
                # 去除NaN值
                f0 = f0[~np.isnan(f0)] if f0 is not None else np.array([])
                
                if len(f0) > 0:
                    features["f0_mean"] = float(np.mean(f0))
                    features["f0_std"] = float(np.std(f0))
                    features["f0_range"] = float(np.max(f0) - np.min(f0)) if len(f0) > 1 else 0.0
                    
                    # 计算音调的变化率（情绪变化的指标）
                    if len(f0) > 1:
                        f0_diff = np.diff(f0)
                        features["f0_derivative_mean"] = float(np.mean(np.abs(f0_diff)))
            except Exception as e:
                logger.error(f"F0提取失败: {str(e)}")
        
        # 音量包络的变化率（表情绪强度）
        if len(rms) > 1:
            rms_diff = np.diff(rms)
            features["rms_derivative_mean"] = float(np.mean(np.abs(rms_diff)))
        
        return features
    
    def predict_emotions(self, audio: np.ndarray, sr: int, features: Dict[str, Any]) -> Dict[str, float]:
        """
        预测音频中的情绪概率分布
        
        Args:
            audio: 音频数据
            sr: 采样率
            features: 已提取的特征
            
        Returns:
            Dict[str, float]: 情绪概率分布
        """
        try:
            # 音频处理：提取适合模型的特征
            # 这里是一个简化的示例，实际项目中需要根据模型的具体需求进行特征提取
            
            # 例如，将音频转换为梅尔频谱图作为模型输入
            mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128, fmax=8000)
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # 对梅尔频谱图进行规范化
            mel_spec_db_norm = (mel_spec_db - np.mean(mel_spec_db)) / (np.std(mel_spec_db) + 1e-10)
            
            # 转换为模型输入格式
            # 例如，调整为固定长度，增加批次和通道维度
            input_length = 128  # 假设模型接受128帧
            if mel_spec_db_norm.shape[1] > input_length:
                mel_input = mel_spec_db_norm[:, :input_length]
            else:
                # 如果不够长，则进行填充
                padding = np.zeros((mel_spec_db_norm.shape[0], input_length - mel_spec_db_norm.shape[1]))
                mel_input = np.concatenate([mel_spec_db_norm, padding], axis=1)
            
            # 添加批次和通道维度
            mel_input = np.expand_dims(np.expand_dims(mel_input, 0), 0)
            
            # 转换为PyTorch张量
            input_tensor = torch.FloatTensor(mel_input).to(self.device_name)
            
            # 模型推理
            with torch.no_grad():
                output = self.model(input_tensor)
                
            # 处理模型输出
            if isinstance(output, torch.Tensor):
                # 应用softmax获取概率
                probabilities = torch.nn.functional.softmax(output, dim=1)[0].cpu().numpy()
                
                # 映射到情绪标签
                emotions = {}
                for i, emotion in enumerate(self.emotion_classes):
                    if i < len(probabilities):
                        emotions[emotion] = float(probabilities[i])
                
                return emotions
            
            # 如果模型输出不是张量，返回空结果
            logger.error("模型输出格式无效")
            return self._generate_default_emotions()
            
        except Exception as e:
            logger.error(f"情绪预测失败: {str(e)}")
            # 返回默认情绪分布
            return self._generate_default_emotions()
    
    def _generate_default_emotions(self) -> Dict[str, float]:
        """生成默认的情绪分布"""
        emotions = {}
        for emotion in self.emotion_classes:
            emotions[emotion] = 0.0
        emotions["neutral"] = 1.0
        return emotions
    
    def analyze_text_emotion(self, text: str) -> Dict[str, float]:
        """
        分析文本中的情绪（简化实现）
        
        Args:
            text: 文本内容
            
        Returns:
            Dict[str, float]: 情绪概率分布
        """
        # 注意：这是一个非常简化的文本情绪分析示例
        # 实际项目中应该使用NLP模型或情感分析API
        
        emotions = self._generate_default_emotions()
        
        # 简单的关键词匹配
        happy_keywords = ["高兴", "开心", "快乐", "欢喜", "愉快", "开心", "哈哈"]
        sad_keywords = ["伤心", "难过", "悲伤", "痛苦", "遗憾", "哭", "叹气"]
        angry_keywords = ["生气", "愤怒", "恼火", "发火", "气愤", "怒", "烦", "讨厌"]
        fearful_keywords = ["害怕", "恐惧", "担心", "紧张", "焦虑", "怕", "惊"]
        
        # 检查关键词出现
        for keyword in happy_keywords:
            if keyword in text:
                emotions["happy"] += 0.2
                
        for keyword in sad_keywords:
            if keyword in text:
                emotions["sad"] += 0.2
                
        for keyword in angry_keywords:
            if keyword in text:
                emotions["angry"] += 0.2
                
        for keyword in fearful_keywords:
            if keyword in text:
                emotions["fearful"] += 0.2
        
        # 规范化情绪分数总和为1
        total = sum(emotions.values())
        if total > 0:
            for emotion in emotions:
                emotions[emotion] /= total
        else:
            emotions["neutral"] = 1.0
        
        return emotions
    
    def fusion_emotions(self, audio_emotions: Dict[str, float], 
                       text_emotions: Dict[str, float]) -> Dict[str, float]:
        """
        融合音频和文本的情绪分析结果
        
        Args:
            audio_emotions: 音频情绪概率分布
            text_emotions: 文本情绪概率分布
            
        Returns:
            Dict[str, float]: 融合后的情绪概率分布
        """
        # 加权融合
        audio_weight = 0.7  # 音频权重更高
        text_weight = 0.3
        
        combined_emotions = {}
        
        # 合并两个字典中的所有情绪类别
        all_emotions = set(audio_emotions.keys()).union(set(text_emotions.keys()))
        
        for emotion in all_emotions:
            audio_prob = audio_emotions.get(emotion, 0.0)
            text_prob = text_emotions.get(emotion, 0.0)
            
            # 加权融合
            combined_emotions[emotion] = audio_prob * audio_weight + text_prob * text_weight
        
        # 规范化概率总和为1
        total = sum(combined_emotions.values())
        if total > 0:
            for emotion in combined_emotions:
                combined_emotions[emotion] /= total
        
        return combined_emotions
    
    def map_to_tcm_emotions(self, emotions: Dict[str, float]) -> Dict[str, float]:
        """
        将现代情绪分类映射到中医五志（喜、怒、忧、思、恐）
        
        Args:
            emotions: 现代情绪概率分布
            
        Returns:
            Dict[str, float]: 中医五志概率分布
        """
        # 中医五志映射关系
        mapping = {
            "喜": {"happy": 0.9, "calm": 0.3, "surprised": 0.5, "neutral": 0.1},
            "怒": {"angry": 0.9, "disgust": 0.6, "stress": 0.4},
            "忧": {"sad": 0.8, "stress": 0.5, "anxiety": 0.6},
            "思": {"neutral": 0.3, "calm": 0.3, "anxiety": 0.3},
            "恐": {"fearful": 0.9, "anxiety": 0.7, "surprised": 0.4}
        }
        
        tcm_scores = {}
        
        # 计算每种中医情志的得分
        for tcm_emotion, modern_mapping in mapping.items():
            score = 0.0
            for modern_emotion, weight in modern_mapping.items():
                if modern_emotion in emotions:
                    score += emotions[modern_emotion] * weight
            
            tcm_scores[tcm_emotion] = min(1.0, score)  # 限制最大值为1.0
        
        return tcm_scores
    
    def analyze_emotion_trend(self, audio: np.ndarray, sr: int, 
                            features: Dict[str, Any]) -> str:
        """
        分析情绪变化趋势
        
        Args:
            audio: 音频数据
            sr: 采样率
            features: 已提取的特征
            
        Returns:
            str: 趋势枚举值 (STABLE, RISING, FALLING, FLUCTUATING)
        """
        # 分析情绪变化需要时间序列数据
        # 我们可以通过分析音高、音量等特征随时间的变化来估计
        
        # 默认趋势为稳定
        trend = "STABLE"
        
        # 分析音量变化 (RMS能量)
        if "rms_derivative_mean" in features and "rms_std" in features and "rms_mean" in features:
            rms_derivative = features["rms_derivative_mean"]
            rms_std = features["rms_std"]
            rms_mean = features["rms_mean"]
            
            # 计算变化率相对于平均值的比例
            if rms_mean > 0:
                relative_change_rate = rms_derivative / rms_mean
                
                # 基于变化率和标准差判断趋势
                if relative_change_rate > 0.3:  # 有显著变化
                    # 将音频分为前后两部分
                    half_point = len(audio) // 2
                    first_half = audio[:half_point]
                    second_half = audio[half_point:]
                    
                    # 计算两部分的RMS能量
                    first_half_rms = np.sqrt(np.mean(first_half**2))
                    second_half_rms = np.sqrt(np.mean(second_half**2))
                    
                    # 比较前后两部分确定趋势
                    if second_half_rms > first_half_rms * 1.3:
                        trend = "RISING"
                    elif first_half_rms > second_half_rms * 1.3:
                        trend = "FALLING"
                    elif rms_std / rms_mean > 0.4:  # 波动较大
                        trend = "FLUCTUATING"
        
        # 分析音高变化 (F0)
        if "f0_derivative_mean" in features and "f0_std" in features and "f0_mean" in features:
            f0_derivative = features["f0_derivative_mean"]
            f0_std = features["f0_std"]
            f0_mean = features["f0_mean"]
            
            # 计算变化率相对于平均值的比例
            if f0_mean > 0:
                relative_f0_change = f0_derivative / f0_mean
                
                # 如果音高变化显著
                if relative_f0_change > 0.1:  # 音高变化通常较小
                    # 提取足够长的音频的F0时间序列
                    if len(audio) / sr > 1.0:
                        f0, voiced_flag, _ = librosa.pyin(audio, 
                                                        fmin=librosa.note_to_hz('C2'), 
                                                        fmax=librosa.note_to_hz('C7'),
                                                        sr=sr)
                        f0 = f0[~np.isnan(f0)] if f0 is not None else np.array([])
                        
                        if len(f0) > 10:  # 需要足够多的F0采样点
                            # 平滑F0曲线
                            f0_smoothed = signal.savgol_filter(f0, window_length=min(5, len(f0) // 2 * 2 + 1), polyorder=2)
                            
                            # 分为前后两部分
                            half_point = len(f0_smoothed) // 2
                            first_half_f0 = f0_smoothed[:half_point]
                            second_half_f0 = f0_smoothed[half_point:]
                            
                            # 计算前后两部分的平均F0
                            if len(first_half_f0) > 0 and len(second_half_f0) > 0:
                                first_mean = np.mean(first_half_f0)
                                second_mean = np.mean(second_half_f0)
                                
                                # 比较前后两部分确定趋势
                                if second_mean > first_mean * 1.1:
                                    if trend == "RISING":  # 音量和音高趋势一致
                                        trend = "RISING"
                                    elif trend != "STABLE":  # 音量和音高趋势不一致
                                        trend = "FLUCTUATING"
                                    else:
                                        trend = "RISING"
                                elif first_mean > second_mean * 1.1:
                                    if trend == "FALLING":  # 趋势一致
                                        trend = "FALLING"
                                    elif trend != "STABLE":  # 趋势不一致
                                        trend = "FLUCTUATING"
                                    else:
                                        trend = "FALLING"
                                elif f0_std / f0_mean > 0.3:  # 波动较大
                                    trend = "FLUCTUATING"
        
        return trend
    
    def calculate_emotional_stability(self, emotions: Dict[str, float], 
                                    features: Dict[str, Any]) -> float:
        """
        计算情绪稳定性得分
        
        Args:
            emotions: 情绪概率分布
            features: 已提取的特征
            
        Returns:
            float: 情绪稳定性得分(0-1)，1表示最稳定
        """
        # 情绪稳定性综合考虑情绪分布的集中程度和音频特征的变化
        
        # 1. 情绪分布的集中程度
        # 如果某个情绪占主导，表示情绪更加明确，可能更稳定
        max_emotion_score = max(emotions.values()) if emotions else 0
        emotion_concentration = max_emotion_score
        
        # 2. 特征的变化程度
        feature_stability = 1.0  # 默认最稳定
        
        # 音量变化
        if "rms_std" in features and "rms_mean" in features and features["rms_mean"] > 0:
            rms_variation = features["rms_std"] / features["rms_mean"]
            feature_stability -= min(0.5, rms_variation)  # 最多减0.5
            
        # 音高变化
        if "f0_std" in features and "f0_mean" in features and features["f0_mean"] > 0:
            f0_variation = features["f0_std"] / features["f0_mean"]
            feature_stability -= min(0.5, f0_variation)  # 最多减0.5
        
        # 综合评分
        stability = 0.5 * emotion_concentration + 0.5 * feature_stability
        
        # 额外调整：某些情绪本身表示不稳定
        if "anxiety" in emotions and emotions["anxiety"] > 0.3:
            stability *= (1.0 - 0.5 * emotions["anxiety"])  # 焦虑降低稳定性
            
        if "stress" in emotions and emotions["stress"] > 0.3:
            stability *= (1.0 - 0.4 * emotions["stress"])  # 压力降低稳定性
        
        return max(0.0, min(1.0, stability))  # 限制在0-1范围
    
    def calculate_confidence(self, emotions: Dict[str, float], 
                           features: Dict[str, Any]) -> float:
        """
        计算分析结果的置信度
        
        Args:
            emotions: 情绪概率分布
            features: 已提取的特征
            
        Returns:
            float: 置信度得分(0-1)
        """
        # 如果没有情绪数据
        if not emotions:
            return 0.0
            
        # 1. 基于主要情绪的概率值
        max_emotion_prob = max(emotions.values())
        
        # 2. 基于特征的完整性
        feature_presence = 0.0
        key_features = ["f0_mean", "rms_mean", "mfccs_mean"]
        if features:
            feature_presence = sum(1 for f in key_features if f in features) / len(key_features)
        
        # 3. 音频质量评估
        audio_quality = 0.5  # 默认中等质量
        if "rms_mean" in features:
            audio_quality = min(1.0, features["rms_mean"] / 0.1)  # 音量太小可能影响质量
        
        # 加权平均
        confidence = 0.5 * max_emotion_prob + 0.3 * feature_presence + 0.2 * audio_quality
        
        return min(1.0, max(0.1, confidence))  # 限制在0.1-1.0范围
    
    def generate_diagnostic_hint(self, emotions: Dict[str, float], 
                               tcm_emotions: Dict[str, float], 
                               trend: str, 
                               emotional_stability: float) -> str:
        """
        生成诊断提示文本
        
        Args:
            emotions: 情绪概率分布
            tcm_emotions: 中医五志概率分布
            trend: 情绪变化趋势
            emotional_stability: 情绪稳定性得分
            
        Returns:
            str: 诊断提示文本
        """
        if not emotions or not tcm_emotions:
            return "音频质量不足，无法生成有效情绪诊断提示。"
        
        # 找出最主要的情绪
        main_emotion = max(emotions.items(), key=lambda x: x[1], default=(None, 0))
        
        # 找出最主要的中医情志
        main_tcm_emotion = max(tcm_emotions.items(), key=lambda x: x[1], default=(None, 0))
        
        # 生成基础提示
        hint = f"语音情绪分析显示，"
        
        # 添加情绪描述
        emotion_description = self._emotion_to_chinese(main_emotion[0])
        hint += f"主要呈现{emotion_description}情绪"
        
        # 添加中医五志关联
        if main_tcm_emotion[1] > 0.5:
            hint += f"，对应中医五志中的「{main_tcm_emotion[0]}」"
        
        # 添加情绪稳定性描述
        if emotional_stability < 0.4:
            hint += "，情绪波动明显"
        elif emotional_stability > 0.7:
            hint += "，情绪较为稳定"
        
        # 添加情绪趋势描述
        if trend != "STABLE":
            trend_description = {
                "RISING": "情绪逐渐增强",
                "FALLING": "情绪逐渐缓和",
                "FLUCTUATING": "情绪起伏波动"
            }.get(trend, "")
            
            if trend_description:
                hint += f"，{trend_description}"
        
        # 添加中医诊断相关性
        if main_tcm_emotion[0] == "怒" and main_tcm_emotion[1] > 0.7:
            hint += "，情绪易激动，可能与肝气郁结相关"
        elif main_tcm_emotion[0] == "喜" and main_tcm_emotion[1] > 0.7:
            hint += "，情绪愉悦，气血运行通畅"
        elif main_tcm_emotion[0] == "忧" and main_tcm_emotion[1] > 0.7:
            hint += "，情绪低落，可能与气郁相关"
        elif main_tcm_emotion[0] == "思" and main_tcm_emotion[1] > 0.7:
            hint += "，思虑较多，可能导致气机郁滞"
        elif main_tcm_emotion[0] == "恐" and main_tcm_emotion[1] > 0.7:
            hint += "，存在明显的恐惧情绪，可能与肾气不足相关"
        
        hint += "。"
        
        return hint
    
    def _emotion_to_chinese(self, emotion: str) -> str:
        """将情绪标签转换为中文描述"""
        mapping = {
            "neutral": "平静",
            "happy": "愉悦",
            "sad": "悲伤",
            "angry": "愤怒",
            "fearful": "恐惧",
            "disgust": "厌恶",
            "surprised": "惊讶",
            "calm": "安静",
            "anxiety": "焦虑",
            "stress": "压力"
        }
        return mapping.get(emotion, emotion)


class DummyEmotionModel:
    """
    模拟情绪分析模型，用于开发和测试环境
    """
    def __init__(self, device_name, num_emotions):
        self.device = device_name
        self.num_emotions = num_emotions
        logger.warning("使用模拟情绪分析模型")
    
    def eval(self):
        return self
    
    def half(self):
        return self
    
    def __call__(self, audio_tensor):
        # 返回模拟的预测结果
        batch_size = audio_tensor.shape[0]
        # 为每个批次样本生成随机情绪分数（模拟）
        dummy_emotions = torch.rand((batch_size, self.num_emotions))
        return dummy_emotions 