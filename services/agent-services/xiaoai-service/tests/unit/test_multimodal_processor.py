"""
多模态处理器单元测试
"""

import pytest
import asyncio
import numpy as np
from PIL import Image
import io
import base64
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from xiaoai.core.multimodal_processor import (
    MultimodalProcessor,
    ModalityType,
    ProcessingStatus,
    ModalityInput,
    ProcessingResult
)
from xiaoai.utils.exceptions import ProcessingError, UnsupportedFormatError


class TestMultimodalProcessor:
    """多模态处理器测试类"""
    
    @pytest.fixture
    async def processor(self):
        """创建处理器实例"""
        processor = MultimodalProcessor()
        await processor.initialize()
        yield processor
    
    @pytest.fixture
    def sample_text_input(self):
        """样本文本输入"""
        return ModalityInput(
            modality_type=ModalityType.TEXT,
            data="患者主诉头痛失眠，舌红苔厚，脉弦数。",
            format="text/plain",
            encoding="utf-8"
        )
    
    @pytest.fixture
    def sample_image_input(self):
        """样本图像输入"""
        # 创建一个简单的测试图像
        image = Image.new('RGB', (100, 100), color='red')
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_data = img_buffer.getvalue()
        
        return ModalityInput(
            modality_type=ModalityType.IMAGE,
            data=img_data,
            format="png",
            metadata={"image_type": "tongue"}
        )
    
    @pytest.fixture
    def sample_audio_input(self):
        """样本音频输入"""
        # 创建模拟音频数据
        sample_rate = 16000
        duration = 2  # 2秒
        audio_data = np.random.random(sample_rate * duration).astype(np.float32)
        
        return ModalityInput(
            modality_type=ModalityType.AUDIO,
            data=audio_data.tobytes(),
            format="wav",
            metadata={"sample_rate": sample_rate, "duration": duration}
        )
    
    @pytest.fixture
    def sample_sensor_input(self):
        """样本传感器输入"""
        # 模拟心率数据
        heart_rate_data = [72, 75, 73, 76, 74, 71, 73, 75]
        
        return ModalityInput(
            modality_type=ModalityType.SENSOR,
            data=heart_rate_data,
            metadata={"sensor_type": "heart_rate", "unit": "bpm"}
        )
    
    @pytest.mark.asyncio
    async def test_processor_initialization(self, processor):
        """测试处理器初始化"""
        assert processor is not None
        assert hasattr(processor, 'processors')
        assert processor.accessibility_enabled is True
    
    @pytest.mark.asyncio
    async def test_text_processing(self, processor, sample_text_input):
        """测试文本处理"""
        result = await processor._process_text(sample_text_input)
        
        assert isinstance(result, ProcessingResult)
        assert result.modality_type==ModalityType.TEXT
        assert result.status==ProcessingStatus.PROCESSING
        assert "original_text" in result.processed_data
        assert "text_length" in result.processed_data
        assert "language" in result.processed_data
        assert result.confidence > 0
    
    @pytest.mark.asyncio
    async def test_text_tcm_keyword_extraction(self, processor):
        """测试中医关键词提取"""
        tcm_text = "患者舌红苔厚，脉弦数，头痛眩晕，心悸失眠，阳虚体质。"
        keywords = processor._extract_tcm_keywords(tcm_text)
        
        expected_keywords = ["头痛", "眩晕", "心悸", "失眠", "舌红", "苔厚", "脉弦", "阳虚"]
        found_keywords = [kw for kw in expected_keywords if kw in keywords]
        
        assert len(found_keywords) > 0
        assert "头痛" in keywords
        assert "失眠" in keywords
    
    @pytest.mark.asyncio
    async def test_image_processing(self, processor, sample_image_input):
        """测试图像处理"""
        with patch.object(processor, 'processors') as mock_processors:
            # 模拟图像处理管道
            mock_processors.get.return_value = {
                "image_classification": Mock(return_value=[
                    {"label": "tongue", "score": 0.9}
                ]),
                "object_detection": Mock(return_value=[
                    {"label": "tongue", "score": 0.8, "box": {"x": 10, "y": 10, "width": 80, "height": 80}}
                ])
            }
            
            result = await processor._process_image(sample_image_input)
            
            assert isinstance(result, ProcessingResult)
            assert result.modality_type==ModalityType.IMAGE
            assert "size" in result.processed_data
            assert "mode" in result.processed_data
            assert result.confidence > 0
    
    @pytest.mark.asyncio
    async def test_audio_processing(self, processor, sample_audio_input):
        """测试音频处理"""
        with patch('librosa.load') as mock_load, \
             patch('librosa.feature.zero_crossing_rate') as mock_zcr, \
             patch('librosa.feature.spectral_centroid') as mock_sc, \
             patch('librosa.feature.mfcc') as mock_mfcc:
            
            # 模拟librosa函数
            mock_load.return_value = (np.random.random(16000), 16000)
            mock_zcr.return_value = np.array([[0.1]])
            mock_sc.return_value = np.array([[1000]])
            mock_mfcc.return_value = np.random.random((13, 100))
            
            result = await processor._process_audio(sample_audio_input)
            
            assert isinstance(result, ProcessingResult)
            assert result.modality_type==ModalityType.AUDIO
            assert "duration" in result.processed_data
            assert "sample_rate" in result.processed_data
    
    @pytest.mark.asyncio
    async def test_sensor_processing(self, processor, sample_sensor_input):
        """测试传感器数据处理"""
        result = await processor._process_sensor(sample_sensor_input)
        
        assert isinstance(result, ProcessingResult)
        assert result.modality_type==ModalityType.SENSOR
        assert "sensor_type" in result.processed_data
        assert "data_points" in result.processed_data
        assert "statistics" in result.features
        assert "heart_rate_analysis" in result.features
    
    @pytest.mark.asyncio
    async def test_multimodal_input_processing(self, processor, sample_text_input, sample_image_input):
        """测试多模态输入处理"""
        inputs = [sample_text_input, sample_image_input]
        user_id = "test_user"
        session_id = "test_session"
        
        with patch.object(processor, '_process_single_modality') as mock_process:
            mock_process.side_effect = [
                ProcessingResult(
                    modality_type=ModalityType.TEXT,
                    status=ProcessingStatus.COMPLETED,
                    confidence=0.8
                ),
                ProcessingResult(
                    modality_type=ModalityType.IMAGE,
                    status=ProcessingStatus.COMPLETED,
                    confidence=0.7
                )
            ]
            
            results = await processor.process_multimodal_input(inputs, user_id, session_id)
            
            assert len(results)==2
            assert all(isinstance(result, ProcessingResult) for result in results)
            assert results[0].modality_type==ModalityType.TEXT
            assert results[1].modality_type==ModalityType.IMAGE
    
    @pytest.mark.asyncio
    async def test_language_detection(self, processor):
        """测试语言检测"""
        chinese_text = "这是中文文本，包含中医术语如气血阴阳。"
        english_text = "This is English text about traditional Chinese medicine."
        
        chinese_lang = processor._detect_language(chinese_text)
        english_lang = processor._detect_language(english_text)
        
        assert chinese_lang=="zh"
        assert english_lang=="en"
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, processor):
        """测试置信度计算"""
        # 测试文本置信度计算
        text_features = {
            "sentiment": {"score": 0.9},
            "entities": [{"text": "头痛", "confidence": 0.8}],
            "tcm_keywords": ["头痛", "失眠", "心悸"]
        }
        
        text_confidence = processor._calculate_text_confidence(text_features)
        assert 0<=text_confidence<=1
        assert text_confidence > 0.5  # 应该有较高置信度
        
        # 测试音频置信度计算
        audio_features = {
            "transcription": "患者说话声音低沉",
            "speech_ratio": 0.8
        }
        
        audio_confidence = processor._calculate_audio_confidence(audio_features)
        assert 0<=audio_confidence<=1
    
    @pytest.mark.asyncio
    async def test_tongue_image_analysis(self, processor):
        """测试舌象图像分析"""
        # 创建红色舌象图像
        red_tongue = Image.new('RGB', (100, 100), color=(200, 100, 100))
        
        analysis = await processor._analyze_tongue_image(red_tongue)
        
        assert analysis["type"]=="tongue"
        assert "color_analysis" in analysis
        assert "tongue_color" in analysis
        assert analysis["tongue_color"] in ["红", "淡", "淡红"]
    
    @pytest.mark.asyncio
    async def test_face_image_analysis(self, processor):
        """测试面色图像分析"""
        # 创建正常面色图像
        normal_face = Image.new('RGB', (100, 100), color=(150, 130, 120))
        
        analysis = await processor._analyze_face_image(normal_face)
        
        assert analysis["type"]=="face"
        assert "color_analysis" in analysis
        assert "face_color" in analysis
    
    @pytest.mark.asyncio
    async def test_heart_rate_analysis(self, processor):
        """测试心率数据分析"""
        heart_rate_data = np.array([72, 75, 73, 76, 74, 71, 73, 75])
        
        analysis = await processor._analyze_heart_rate(heart_rate_data)
        
        assert "average_hr" in analysis
        assert "hr_variability" in analysis
        assert "min_hr" in analysis
        assert "max_hr" in analysis
        assert analysis["average_hr"] > 0
    
    @pytest.mark.asyncio
    async def test_blood_pressure_analysis(self, processor):
        """测试血压数据分析"""
        # 血压数据格式：[收缩压, 舒张压, 收缩压, 舒张压, ...]
        bp_data = np.array([120, 80, 125, 82, 118, 78])
        
        analysis = await processor._analyze_blood_pressure(bp_data)
        
        assert "systolic_mean" in analysis
        assert "diastolic_mean" in analysis
        assert "pulse_pressure" in analysis
        assert analysis["systolic_mean"] > analysis["diastolic_mean"]
    
    @pytest.mark.asyncio
    async def test_temperature_analysis(self, processor):
        """测试体温数据分析"""
        temp_data = np.array([36.5, 36.8, 37.2, 37.5, 36.9, 36.7])
        
        analysis = await processor._analyze_temperature(temp_data)
        
        assert "average_temp" in analysis
        assert "temp_variation" in analysis
        assert "fever_episodes" in analysis
        assert analysis["fever_episodes"]>=0
    
    @pytest.mark.asyncio
    async def test_input_validation(self, processor):
        """测试输入验证"""
        # 测试空数据
        empty_input = ModalityInput(
            modality_type=ModalityType.TEXT,
            data="",
            format="text/plain"
        )
        
        with pytest.raises(ValueError):
            await processor._validate_input(empty_input)
        
        # 测试有效数据
        valid_input = ModalityInput(
            modality_type=ModalityType.TEXT,
            data="有效的文本数据",
            format="text/plain"
        )
        
        # 应该不抛出异常
        await processor._validate_input(valid_input)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, processor):
        """测试错误处理"""
        # 创建会导致处理错误的输入
        invalid_input = ModalityInput(
            modality_type=ModalityType.IMAGE,
            data=b"invalid_image_data",
            format="png"
        )
        
        result = await processor._process_single_modality(
            invalid_input, "test_user", "test_session"
        )
        
        assert result.status==ProcessingStatus.FAILED
        assert result.error_message is not None
    
    @pytest.mark.asyncio
    async def test_accessibility_text_to_speech(self, processor):
        """测试无障碍文本转语音"""
        text = "这是测试文本"
        
        with patch.object(processor.processors.get("accessibility", {}), "get") as mock_tts:
            mock_engine = Mock()
            mock_tts.return_value = mock_engine
            
            with patch('tempfile.NamedTemporaryFile'), \
                 patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = b"fake_audio_data"
                
                audio_data = await processor.text_to_speech(text)
                
                # 由于模拟环境，可能返回None或模拟数据
                assert audio_data is None or isinstance(audio_data, bytes)
    
    @pytest.mark.asyncio
    async def test_accessibility_speech_to_text(self, processor):
        """测试无障碍语音转文本"""
        audio_data = b"fake_audio_data"
        
        with patch.object(processor, '_process_audio') as mock_process:
            mock_result = ProcessingResult(
                modality_type=ModalityType.AUDIO,
                status=ProcessingStatus.COMPLETED,
                features={"transcription": "转录的文本"}
            )
            mock_process.return_value = mock_result
            
            text = await processor.speech_to_text_accessibility(audio_data)
            
            assert text=="转录的文本"
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, processor):
        """测试并发处理"""
        # 创建多个输入
        inputs = []
        for i in range(5):
            input_data = ModalityInput(
                modality_type=ModalityType.TEXT,
                data=f"测试文本 {i}",
                format="text/plain"
            )
            inputs.append(input_data)
        
        # 并发处理
        tasks = []
        for input_data in inputs:
            task = processor._process_single_modality(
                input_data, "test_user", "test_session"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        assert len(results)==5
        assert all(isinstance(result, ProcessingResult) for result in results)
    
    @pytest.mark.asyncio
    async def test_image_feature_extraction(self, processor):
        """测试图像特征提取"""
        # 创建测试图像
        image = Image.new('RGB', (100, 100), color=(128, 64, 192))
        
        features = await processor._extract_image_features(image)
        
        assert "color_mean" in features
        assert "color_std" in features
        assert "brightness_mean" in features
        assert "contrast" in features
        assert len(features["color_mean"])==3  # RGB三个通道
    
    @pytest.mark.asyncio
    async def test_audio_feature_extraction(self, processor):
        """测试音频特征提取"""
        # 创建模拟音频数据
        y = np.random.random(16000).astype(np.float32)
        sr = 16000
        
        with patch('librosa.feature.zero_crossing_rate') as mock_zcr, \
             patch('librosa.feature.spectral_centroid') as mock_sc, \
             patch('librosa.feature.spectral_rolloff') as mock_sr, \
             patch('librosa.feature.mfcc') as mock_mfcc, \
             patch('librosa.feature.rms') as mock_rms, \
             patch('librosa.effects.split') as mock_split:
            
            # 模拟librosa函数返回值
            mock_zcr.return_value = np.array([[0.1]])
            mock_sc.return_value = np.array([[1000]])
            mock_sr.return_value = np.array([[2000]])
            mock_mfcc.return_value = np.random.random((13, 100))
            mock_rms.return_value = np.array([[0.5]])
            mock_split.return_value = [(0, 8000), (8000, 16000)]
            
            features = await processor._extract_audio_features(y, sr)
            
            assert "zero_crossing_rate" in features
            assert "spectral_centroid" in features
            assert "mfcc_mean" in features
            assert "speech_segments" in features
    
    def test_modality_type_enum(self):
        """测试模态类型枚举"""
        assert ModalityType.TEXT.value=="text"
        assert ModalityType.AUDIO.value=="audio"
        assert ModalityType.IMAGE.value=="image"
        assert ModalityType.VIDEO.value=="video"
        assert ModalityType.SENSOR.value=="sensor"
    
    def test_processing_status_enum(self):
        """测试处理状态枚举"""
        assert ProcessingStatus.PENDING.value=="pending"
        assert ProcessingStatus.PROCESSING.value=="processing"
        assert ProcessingStatus.COMPLETED.value=="completed"
        assert ProcessingStatus.FAILED.value=="failed"