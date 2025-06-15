#!/usr/bin/env python

"""
前沿技术服务测试
测试脑机接口、高级触觉反馈和空间音频处理服务
"""


import pytest

from internal.service.implementations.bci_impl import BCIServiceImpl
from internal.service.implementations.haptic_feedback_impl import (
    HapticFeedbackServiceImpl,
)
from internal.service.implementations.spatial_audio_impl import SpatialAudioServiceImpl
from internal.service.interfaces.bci_interface import (
    BCICommand,
    BCIDeviceType,
    SignalType,
)
from internal.service.interfaces.haptic_feedback_interface import (
    HapticDeviceType,
    HapticModality,
    HapticPattern,
)
from internal.service.interfaces.spatial_audio_interface import (
    AudioRenderingEngine,
    RoomAcoustics,
    SpatialAudioFormat,
)


class TestBCIService:
    """脑机接口服务测试"""

    @pytest.fixture
    async def bci_service(self):
        """创建BCI服务实例"""
        service = BCIServiceImpl()
        await service.initialize()
        yield service
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_bci_initialization(self, bci_service):
        """测试BCI服务初始化"""
        assert bci_service.is_initialized
        status = await bci_service.get_service_status()
        assert status["service_name"] == "Brain-Computer Interface Service"
        assert status["status"] == "running"

    @pytest.mark.asyncio
    async def test_detect_bci_devices(self, bci_service):
        """测试BCI设备检测"""
        result = await bci_service.detect_bci_devices()

        assert result["success"]
        assert "devices" in result
        assert result["count"] > 0

        # 验证设备信息
        devices = result["devices"]
        assert any(
            device["device_type"] == BCIDeviceType.EEG.value for device in devices
        )
        assert any(
            device["device_type"] == BCIDeviceType.FNIRS.value for device in devices
        )

    @pytest.mark.asyncio
    async def test_connect_bci_device(self, bci_service):
        """测试BCI设备连接"""
        device_id = "eeg_device_001"
        device_type = BCIDeviceType.EEG

        result = await bci_service.connect_bci_device(device_id, device_type)

        assert result["success"]
        assert result["device_id"] == device_id
        assert result["device_type"] == device_type.value
        assert "connection_time" in result

    @pytest.mark.asyncio
    async def test_calibrate_bci_device(self, bci_service):
        """测试BCI设备校准"""
        # 先连接设备
        device_id = "eeg_device_001"
        await bci_service.connect_bci_device(device_id, BCIDeviceType.EEG)

        # 校准设备
        user_id = "test_user_001"
        calibration_config = {
            "duration": 60,
            "signal_types": [SignalType.ALPHA.value, SignalType.BETA.value],
            "tasks": ["eyes_open", "eyes_closed", "motor_imagery"],
        }

        result = await bci_service.calibrate_bci_device(
            user_id, device_id, calibration_config
        )

        assert result["success"]
        assert result["user_id"] == user_id
        assert result["device_id"] == device_id
        assert "calibration_accuracy" in result
        assert result["calibration_accuracy"] > 0.7

    @pytest.mark.asyncio
    async def test_start_signal_acquisition(self, bci_service):
        """测试信号采集"""
        # 连接并校准设备
        device_id = "eeg_device_001"
        user_id = "test_user_001"
        await bci_service.connect_bci_device(device_id, BCIDeviceType.EEG)
        await bci_service.calibrate_bci_device(user_id, device_id)

        # 开始信号采集
        acquisition_config = {
            "sample_rate": 250,
            "channels": ["Fp1", "Fp2", "C3", "C4", "P3", "P4", "O1", "O2"],
            "duration": 10,
        }

        result = await bci_service.start_signal_acquisition(
            user_id, device_id, acquisition_config
        )

        assert result["success"]
        assert result["acquisition_active"]
        assert result["sample_rate"] == 250
        assert len(result["channels"]) == 8

    @pytest.mark.asyncio
    async def test_process_brain_signals(self, bci_service):
        """测试脑信号处理"""
        user_id = "test_user_001"
        device_id = "eeg_device_001"

        # 模拟信号数据
        signal_data = {
            "channels": ["C3", "C4"],
            "sample_rate": 250,
            "data": np.random.randn(250, 2).tolist(),  # 1秒数据
            "timestamp": "2024-01-01T12:00:00Z",
        }

        processing_config = {
            "filters": ["bandpass", "notch"],
            "frequency_bands": ["alpha", "beta", "gamma"],
            "artifacts_removal": True,
        }

        result = await bci_service.process_brain_signals(
            user_id, signal_data, processing_config
        )

        assert result["success"]
        assert "processed_signals" in result
        assert "frequency_analysis" in result
        assert "artifacts_detected" in result

    @pytest.mark.asyncio
    async def test_classify_mental_state(self, bci_service):
        """测试心理状态分类"""
        user_id = "test_user_001"

        # 模拟处理后的信号特征
        signal_features = {
            "alpha_power": 0.6,
            "beta_power": 0.4,
            "gamma_power": 0.2,
            "theta_power": 0.3,
            "delta_power": 0.1,
            "asymmetry_index": 0.15,
            "coherence": 0.8,
        }

        classification_config = {"model_type": "svm", "confidence_threshold": 0.7}

        result = await bci_service.classify_mental_state(
            user_id, signal_features, classification_config
        )

        assert result["success"]
        assert "mental_state" in result
        assert "confidence" in result
        assert result["confidence"] >= 0.0 and result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_detect_bci_commands(self, bci_service):
        """测试BCI命令检测"""
        user_id = "test_user_001"

        # 模拟信号数据
        signal_data = {
            "channels": ["C3", "C4", "Cz"],
            "sample_rate": 250,
            "data": np.random.randn(500, 3).tolist(),  # 2秒数据
            "timestamp": "2024-01-01T12:00:00Z",
        }

        detection_config = {
            "command_types": [BCICommand.MOVE_LEFT.value, BCICommand.MOVE_RIGHT.value],
            "detection_window": 1.0,
            "confidence_threshold": 0.8,
        }

        result = await bci_service.detect_bci_commands(
            user_id, signal_data, detection_config
        )

        assert result["success"]
        assert "detected_commands" in result
        assert isinstance(result["detected_commands"], list)


class TestHapticFeedbackService:
    """高级触觉反馈服务测试"""

    @pytest.fixture
    async def haptic_service(self):
        """创建触觉反馈服务实例"""
        service = HapticFeedbackServiceImpl()
        await service.initialize()
        yield service
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_haptic_initialization(self, haptic_service):
        """测试触觉反馈服务初始化"""
        assert haptic_service.is_initialized
        status = await haptic_service.get_service_status()
        assert status["service_name"] == "Haptic Feedback Service"
        assert status["status"] == "running"

    @pytest.mark.asyncio
    async def test_detect_haptic_devices(self, haptic_service):
        """测试触觉设备检测"""
        result = await haptic_service.detect_haptic_devices()

        assert result["success"]
        assert "devices" in result
        assert result["count"] > 0

        # 验证设备信息
        devices = result["devices"]
        device_types = [device["device_type"] for device in devices]
        assert HapticDeviceType.HAPTIC_GLOVES.value in device_types
        assert HapticDeviceType.HAPTIC_VEST.value in device_types

    @pytest.mark.asyncio
    async def test_connect_haptic_device(self, haptic_service):
        """测试触觉设备连接"""
        device_id = "haptic_gloves_001"
        device_type = HapticDeviceType.HAPTIC_GLOVES

        result = await haptic_service.connect_haptic_device(device_id, device_type)

        assert result["success"]
        assert result["device_id"] == device_id
        assert result["device_type"] == device_type.value

    @pytest.mark.asyncio
    async def test_calibrate_haptic_device(self, haptic_service):
        """测试触觉设备校准"""
        # 先连接设备
        device_id = "haptic_gloves_001"
        await haptic_service.connect_haptic_device(
            device_id, HapticDeviceType.HAPTIC_GLOVES
        )

        # 校准设备
        user_id = "test_user_001"
        calibration_config = {
            "sensitivity_test": True,
            "frequency_response": True,
            "spatial_accuracy": True,
        }

        result = await haptic_service.calibrate_haptic_device(
            user_id, device_id, calibration_config
        )

        assert result["success"]
        assert "sensitivity" in result
        assert result["sensitivity"] > 0.5

    @pytest.mark.asyncio
    async def test_create_haptic_pattern(self, haptic_service):
        """测试创建触觉模式"""
        pattern_name = "test_notification"
        pattern_config = {
            "pattern": HapticPattern.PULSE,
            "duration": 0.5,
            "frequency": 250,
            "modality": HapticModality.VIBRATION,
        }

        result = await haptic_service.create_haptic_pattern(
            pattern_name, pattern_config
        )

        assert result["success"]
        assert result["pattern_name"] == pattern_name
        assert "pattern_id" in result

    @pytest.mark.asyncio
    async def test_play_haptic_pattern(self, haptic_service):
        """测试播放触觉模式"""
        # 连接设备并创建模式
        device_id = "haptic_gloves_001"
        user_id = "test_user_001"
        pattern_name = "test_pattern"

        await haptic_service.connect_haptic_device(
            device_id, HapticDeviceType.HAPTIC_GLOVES
        )
        await haptic_service.create_haptic_pattern(pattern_name, {"duration": 0.3})

        # 播放模式
        result = await haptic_service.play_haptic_pattern(
            user_id, device_id, pattern_name
        )

        assert result["success"]
        assert result["pattern_name"] == pattern_name
        assert result["device_id"] == device_id

    @pytest.mark.asyncio
    async def test_create_spatial_haptic_map(self, haptic_service):
        """测试创建空间触觉映射"""
        user_id = "test_user_001"
        device_id = "haptic_vest_001"

        spatial_config = {
            "name": "test_map",
            "dimensions": {"x": 50, "y": 50, "z": 20},
            "resolution": 0.5,
            "coordinate_system": "cartesian",
        }

        result = await haptic_service.create_spatial_haptic_map(
            user_id, device_id, spatial_config
        )

        assert result["success"]
        assert result["map_name"] == "test_map"
        assert result["dimensions"] == spatial_config["dimensions"]

    @pytest.mark.asyncio
    async def test_render_spatial_haptics(self, haptic_service):
        """测试渲染空间触觉"""
        user_id = "test_user_001"
        device_id = "haptic_vest_001"

        # 连接设备
        await haptic_service.connect_haptic_device(
            device_id, HapticDeviceType.HAPTIC_VEST
        )

        # 空间数据
        spatial_data = {
            "objects": [
                {
                    "position": [2, 1, 0],
                    "haptic_properties": {
                        "modality": HapticModality.VIBRATION,
                        "frequency": 200,
                        "duration": 0.2,
                    },
                },
                {
                    "position": [-1, 3, 1],
                    "haptic_properties": {
                        "modality": HapticModality.PRESSURE,
                        "frequency": 100,
                        "duration": 0.5,
                    },
                },
            ],
            "listener_position": [0, 0, 0],
        }

        result = await haptic_service.render_spatial_haptics(
            user_id, device_id, spatial_data
        )

        assert result["success"]
        assert result["objects_rendered"] == 2
        assert result["signals_generated"] == 2

    @pytest.mark.asyncio
    async def test_create_haptic_language(self, haptic_service):
        """测试创建触觉语言"""
        language_name = "test_morse"
        language_config = {
            "alphabet": {
                "A": [
                    {"type": "short", "duration": 0.1},
                    {"type": "long", "duration": 0.3},
                ],
                "B": [
                    {"type": "long", "duration": 0.3},
                    {"type": "short", "duration": 0.1},
                    {"type": "short", "duration": 0.1},
                    {"type": "short", "duration": 0.1},
                ],
            },
            "timing": {"letter_duration": 0.5, "letter_gap": 0.2, "word_gap": 1.0},
        }

        result = await haptic_service.create_haptic_language(
            language_name, language_config
        )

        assert result["success"]
        assert result["language_name"] == language_name
        assert result["alphabet_size"] == 2

    @pytest.mark.asyncio
    async def test_encode_message_to_haptic(self, haptic_service):
        """测试消息编码为触觉信号"""
        # 先创建触觉语言
        language_name = "test_morse"
        await haptic_service.create_haptic_language(
            language_name,
            {
                "alphabet": {
                    "A": [{"type": "short", "duration": 0.1}],
                    "B": [{"type": "long", "duration": 0.3}],
                }
            },
        )

        user_id = "test_user_001"
        message = "AB"

        result = await haptic_service.encode_message_to_haptic(
            user_id, message, language_name
        )

        assert result["success"]
        assert result["message"] == message
        assert result["language"] == language_name
        assert "encoded_signals" in result
        assert result["total_duration"] > 0


class TestSpatialAudioService:
    """空间音频处理服务测试"""

    @pytest.fixture
    async def audio_service(self):
        """创建空间音频服务实例"""
        service = SpatialAudioServiceImpl()
        await service.initialize()
        yield service
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_audio_initialization(self, audio_service):
        """测试空间音频服务初始化"""
        assert audio_service.is_initialized
        status = await audio_service.get_service_status()
        assert status["service_name"] == "Spatial Audio Service"
        assert status["status"] == "running"

    @pytest.mark.asyncio
    async def test_detect_audio_devices(self, audio_service):
        """测试音频设备检测"""
        result = await audio_service.detect_audio_devices()

        assert result["success"]
        assert "devices" in result
        assert result["count"] > 0

        # 验证设备信息
        devices = result["devices"]
        device_types = [device["type"] for device in devices]
        assert "headphones" in device_types
        assert "vr_headset" in device_types

    @pytest.mark.asyncio
    async def test_configure_audio_device(self, audio_service):
        """测试音频设备配置"""
        device_id = "headphones_001"
        device_config = {"sample_rate": 48000, "buffer_size": 512, "channels": 2}

        result = await audio_service.configure_audio_device(device_id, device_config)

        assert result["success"]
        assert result["device_id"] == device_id
        assert result["applied_config"] == device_config

    @pytest.mark.asyncio
    async def test_create_spatial_scene(self, audio_service):
        """测试创建空间音频场景"""
        user_id = "test_user_001"
        scene_name = "test_scene"
        scene_config = {
            "dimensions": [20, 15, 5],
            "engine": AudioRenderingEngine.HRTF,
            "acoustics": RoomAcoustics.MEDIUM_ROOM,
            "listener": {"position": [0, 0, 0], "orientation": [0, 0, 0]},
        }

        result = await audio_service.create_spatial_scene(
            user_id, scene_name, scene_config
        )

        assert result["success"]
        assert result["scene_name"] == scene_name
        assert result["dimensions"] == scene_config["dimensions"]
        assert result["rendering_engine"] == AudioRenderingEngine.HRTF.value

    @pytest.mark.asyncio
    async def test_add_audio_source(self, audio_service):
        """测试添加音频源"""
        user_id = "test_user_001"
        scene_name = "test_scene"

        # 先创建场景
        await audio_service.create_spatial_scene(user_id, scene_name, {})

        # 添加音频源
        source_config = {
            "source_id": "test_source",
            "position": [5, 0, 0],
            "audio_file": "test_audio.wav",
            "volume": 0.8,
            "loop": True,
        }

        result = await audio_service.add_audio_source(
            user_id, scene_name, source_config
        )

        assert result["success"]
        assert result["source_id"] == "test_source"
        assert result["position"] == [5, 0, 0]

    @pytest.mark.asyncio
    async def test_update_listener_position(self, audio_service):
        """测试更新听者位置"""
        user_id = "test_user_001"
        scene_name = "test_scene"

        # 先创建场景
        await audio_service.create_spatial_scene(user_id, scene_name, {})

        # 更新听者位置
        new_position = (2, 3, 1)
        new_orientation = (0, 45, 0)

        result = await audio_service.update_listener_position(
            user_id, scene_name, new_position, new_orientation
        )

        assert result["success"]
        assert result["position"] == list(new_position)
        assert result["orientation"] == list(new_orientation)

    @pytest.mark.asyncio
    async def test_render_spatial_audio(self, audio_service):
        """测试渲染空间音频"""
        user_id = "test_user_001"
        scene_name = "test_scene"

        # 创建场景并添加音频源
        await audio_service.create_spatial_scene(user_id, scene_name, {})
        await audio_service.add_audio_source(
            user_id, scene_name, {"source_id": "source1", "position": [3, 0, 0]}
        )

        # 渲染音频
        rendering_config = {"quality": "high", "real_time": True}

        result = await audio_service.render_spatial_audio(
            user_id, scene_name, rendering_config
        )

        assert result["success"]
        assert result["scene_name"] == scene_name
        assert result["sources_rendered"] == 1
        assert "audio_buffer" in result

    @pytest.mark.asyncio
    async def test_create_hrtf_profile(self, audio_service):
        """测试创建HRTF配置文件"""
        user_id = "test_user_001"
        profile_config = {
            "name": "test_hrtf",
            "head_measurements": {
                "head_width": 15.5,
                "head_depth": 19.2,
                "ear_distance": 16.8,
            },
            "ear_measurements": {"ear_length": 6.2, "ear_width": 3.8},
        }

        result = await audio_service.create_hrtf_profile(user_id, profile_config)

        assert result["success"]
        assert result["profile_name"] == "test_hrtf"
        assert result["personalized"]
        assert result["hrtf_points"] > 0

    @pytest.mark.asyncio
    async def test_calibrate_hrtf(self, audio_service):
        """测试HRTF校准"""
        user_id = "test_user_001"

        # 先创建HRTF配置文件
        await audio_service.create_hrtf_profile(user_id, {"name": "test_hrtf"})

        # 校准HRTF
        calibration_data = {
            "test_sounds": ["front", "back", "left", "right", "up", "down"],
            "user_responses": [
                {"sound": "front", "perceived": "front", "confidence": 0.9},
                {"sound": "back", "perceived": "back", "confidence": 0.8},
                {"sound": "left", "perceived": "left", "confidence": 0.95},
            ],
        }

        result = await audio_service.calibrate_hrtf(user_id, calibration_data)

        assert result["success"]
        assert "accuracy_score" in result
        assert result["accuracy_score"] > 0.7

    @pytest.mark.asyncio
    async def test_simulate_room_acoustics(self, audio_service):
        """测试房间声学模拟"""
        user_id = "test_user_001"
        scene_name = "test_scene"

        # 先创建场景
        await audio_service.create_spatial_scene(user_id, scene_name, {})

        # 模拟房间声学
        room_config = {
            "type": RoomAcoustics.LARGE_ROOM,
            "dimensions": [15, 10, 4],
            "rt60": 1.0,
            "absorption": 0.15,
        }

        result = await audio_service.simulate_room_acoustics(
            user_id, scene_name, room_config
        )

        assert result["success"]
        assert result["room_type"] == RoomAcoustics.LARGE_ROOM.value
        assert result["rt60"] == 1.0
        assert result["impulse_length"] > 0

    @pytest.mark.asyncio
    async def test_create_audio_navigation(self, audio_service):
        """测试创建音频导航"""
        user_id = "test_user_001"
        navigation_config = {
            "type": "spatial",
            "target": [10, 5, 0],
            "frequency": 5,
            "threshold": 2.0,
        }

        result = await audio_service.create_audio_navigation(user_id, navigation_config)

        assert result["success"]
        assert "nav_id" in result
        assert result["type"] == "spatial"
        assert result["target_position"] == [10, 5, 0]

    @pytest.mark.asyncio
    async def test_provide_spatial_guidance(self, audio_service):
        """测试提供空间引导"""
        user_id = "test_user_001"
        guidance_data = {
            "current_position": [0, 0, 0],
            "target_position": [5, 3, 0],
            "type": "directional",
        }

        result = await audio_service.provide_spatial_guidance(user_id, guidance_data)

        assert result["success"]
        assert result["current_position"] == [0, 0, 0]
        assert result["target_position"] == [5, 3, 0]
        assert "direction" in result
        assert "distance" in result
        assert "guidance_audio" in result


class TestIntegratedFrontierServices:
    """前沿技术服务集成测试"""

    @pytest.fixture
    async def all_services(self):
        """创建所有前沿技术服务实例"""
        bci_service = BCIServiceImpl()
        haptic_service = HapticFeedbackServiceImpl()
        audio_service = SpatialAudioServiceImpl()

        await bci_service.initialize()
        await haptic_service.initialize()
        await audio_service.initialize()

        yield {"bci": bci_service, "haptic": haptic_service, "audio": audio_service}

        await bci_service.cleanup()
        await haptic_service.cleanup()
        await audio_service.cleanup()

    @pytest.mark.asyncio
    async def test_multimodal_interaction(self, all_services):
        """测试多模态交互"""
        bci_service = all_services["bci"]
        haptic_service = all_services["haptic"]
        audio_service = all_services["audio"]

        user_id = "test_user_001"

        # 1. 连接BCI设备检测意图
        await bci_service.connect_bci_device("eeg_001", BCIDeviceType.EEG)

        # 2. 连接触觉设备提供反馈
        await haptic_service.connect_haptic_device(
            "haptic_001", HapticDeviceType.HAPTIC_GLOVES
        )

        # 3. 配置空间音频场景
        await audio_service.create_spatial_scene(user_id, "multimodal_scene", {})

        # 4. 模拟BCI命令检测
        signal_data = {
            "channels": ["C3", "C4"],
            "sample_rate": 250,
            "data": np.random.randn(250, 2).tolist(),
        }

        bci_result = await bci_service.detect_bci_commands(
            user_id, signal_data, {"command_types": [BCICommand.SELECT.value]}
        )

        # 5. 基于BCI命令触发触觉反馈
        if bci_result["success"] and bci_result["detected_commands"]:
            haptic_result = await haptic_service.send_haptic_signal(
                user_id,
                "haptic_001",
                {
                    "modality": HapticModality.VIBRATION,
                    "intensity": 0.7,
                    "duration": 0.3,
                },
            )
            assert haptic_result["success"]

        # 6. 同时提供空间音频反馈
        audio_result = await audio_service.provide_spatial_guidance(
            user_id,
            {
                "current_position": [0, 0, 0],
                "target_position": [1, 0, 0],
                "type": "directional",
            },
        )

        assert bci_result["success"]
        assert audio_result["success"]

    @pytest.mark.asyncio
    async def test_accessibility_enhancement(self, all_services):
        """测试无障碍增强功能"""
        bci_service = all_services["bci"]
        haptic_service = all_services["haptic"]
        audio_service = all_services["audio"]

        user_id = "accessibility_user_001"

        # 为视觉障碍用户创建空间音频导航
        navigation_result = await audio_service.create_audio_navigation(
            user_id, {"type": "spatial", "target": [10, 0, 0]}
        )
        assert navigation_result["success"]

        # 为听力障碍用户创建触觉语言
        language_result = await haptic_service.create_haptic_language(
            "braille_haptic",
            {
                "alphabet": {
                    "A": [[1, 0], [0, 0], [0, 0]],
                    "B": [[1, 0], [1, 0], [0, 0]],
                }
            },
        )
        assert language_result["success"]

        # 为运动障碍用户提供BCI控制
        bci_connect_result = await bci_service.connect_bci_device(
            "eeg_002", BCIDeviceType.EEG
        )
        assert bci_connect_result["success"]

        # 测试触觉消息编码
        message_result = await haptic_service.encode_message_to_haptic(
            user_id, "AB", "braille_haptic"
        )
        assert message_result["success"]
        assert message_result["message"] == "AB"

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, all_services):
        """测试性能监控"""
        bci_service = all_services["bci"]
        haptic_service = all_services["haptic"]
        audio_service = all_services["audio"]

        # 获取所有服务状态
        bci_status = await bci_service.get_service_status()
        haptic_status = await haptic_service.get_service_status()
        audio_status = await audio_service.get_service_status()

        # 验证服务状态
        assert bci_status["status"] == "running"
        assert haptic_status["status"] == "running"
        assert audio_status["status"] == "running"

        # 验证性能指标
        assert "memory_usage" in bci_status
        assert "cpu_usage" in haptic_status
        assert "uptime" in audio_status

        # 验证功能计数
        assert bci_status["connected_devices"] >= 0
        assert haptic_status["active_patterns"] >= 0
        assert audio_status["spatial_scenes"] >= 0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
