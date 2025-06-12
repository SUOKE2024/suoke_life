"""
无障碍服务模块
"""

from dataclasses import dataclass
from enum import Enum
import logging
import os
import tempfile
from typing import Any, Dict, List, Optional, Union

try:
    from PIL import Image, ImageDraw, ImageFont
    import cv2
    import mediapipe as mp
    import numpy as np
    import pyttsx3
    import speech_recognition as sr
except ImportError as e:
    logging.warning(f"无障碍服务依赖缺失: {e}")

from ..config.settings import get_settings
from ..utils.exceptions import AccessibilityError


class AccessibilityMode(Enum):
    """无障碍模式枚举"""

    VISUAL_IMPAIRED = "visual_impaired"  # 视觉障碍
    HEARING_IMPAIRED = "hearing_impaired"  # 听觉障碍
    MOTOR_IMPAIRED = "motor_impaired"  # 运动障碍
    COGNITIVE_IMPAIRED = "cognitive_impaired"  # 认知障碍
    ELDERLY = "elderly"  # 老年人友好
    MULTI_MODAL = "multi_modal"  # 多模态


@dataclass
class AccessibilityConfig:
    """无障碍配置"""

    mode: AccessibilityMode
    voice_speed: float = 1.0
    voice_volume: float = 0.8
    font_size: int = 16
    high_contrast: bool = False
    simplified_ui: bool = False
    gesture_control: bool = False
    voice_commands: bool = True
    text_to_speech: bool = True
    speech_to_text: bool = True
    sign_language: bool = False


class AccessibilityService:
    """无障碍服务"""

    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)

        # TTS引擎
        self.tts_engine = None

        # 语音识别器
        self.speech_recognizer = None
        self.microphone = None

        # 手语识别
        self.hands_detector = None
        self.pose_detector = None

        # 配置
        self.config: Optional[AccessibilityConfig] = None

        # 支持的语言
        self.supported_languages = {
            "zh": "chinese",
            "en": "english",
            "zh-CN": "chinese",
            "en-US": "english",
        }

        # 手势命令映射
        self.gesture_commands = {
            "thumbs_up": "确认",
            "thumbs_down": "取消",
            "open_palm": "停止",
            "peace": "继续",
            "fist": "重复",
            "point_up": "上一个",
            "point_down": "下一个",
        }

    async def initialize(self, config: Optional[AccessibilityConfig] = None):
        """初始化无障碍服务"""
        try:
            self.logger.info("初始化无障碍服务...")

            # 设置配置
            self.config = config or AccessibilityConfig(mode=AccessibilityMode.MULTI_MODAL)

            # 初始化TTS
            if self.config.text_to_speech:
                await self._initialize_tts()

            # 初始化语音识别
            if self.config.speech_to_text:
                await self._initialize_speech_recognition()

            # 初始化手语识别
            if self.config.sign_language or self.config.gesture_control:
                await self._initialize_sign_language()

            self.logger.info("无障碍服务初始化完成")

        except Exception as e:
            self.logger.error(f"无障碍服务初始化失败: {e}")
            raise AccessibilityError(f"无障碍服务初始化失败: {e}")

    async def _initialize_tts(self):
        """初始化文本转语音"""
        try:
            self.tts_engine = pyttsx3.init()

            # 设置语音参数
            self.tts_engine.setProperty('rate', int(200 * self.config.voice_speed))
            self.tts_engine.setProperty('volume', self.config.voice_volume)

            # 设置中文语音
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break

            self.logger.info("TTS引擎初始化完成")

        except Exception as e:
            self.logger.warning(f"TTS引擎初始化失败: {e}")
            self.tts_engine = None

    async def _initialize_speech_recognition(self):
        """初始化语音识别"""
        try:
            self.speech_recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()

            # 调整环境噪音
            with self.microphone as source:
                self.speech_recognizer.adjust_for_ambient_noise(source)

            self.logger.info("语音识别初始化完成")

        except Exception as e:
            self.logger.warning(f"语音识别初始化失败: {e}")
            self.speech_recognizer = None
            self.microphone = None

    async def _initialize_sign_language(self):
        """初始化手语识别"""
        try:
            self.hands_detector = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )

            self.pose_detector = mp.solutions.pose.Pose(
                static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5
            )

            self.logger.info("手语识别初始化完成")

        except Exception as e:
            self.logger.warning(f"手语识别初始化失败: {e}")
            self.hands_detector = None
            self.pose_detector = None

    async def text_to_speech(self, text: str, language: str = "zh") -> Optional[bytes]:
        """文本转语音"""
        if not self.tts_engine or not self.config.text_to_speech:
            return None

        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name

            # 生成语音
            self.tts_engine.save_to_file(text, temp_path)
            self.tts_engine.runAndWait()

            # 读取音频数据
            with open(temp_path, 'rb') as f:
                audio_data = f.read()

            # 清理临时文件
            os.unlink(temp_path)

            return audio_data

        except Exception as e:
            self.logger.error(f"文本转语音失败: {e}")
            return None

    async def speech_to_text(self, audio_data: bytes, language: str = "zh-CN") -> Optional[str]:
        """语音转文本"""
        if not self.speech_recognizer or not self.config.speech_to_text:
            return None

        try:
            # 保存音频数据到临时文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            # 识别语音
            with sr.AudioFile(temp_path) as source:
                audio = self.speech_recognizer.record(source)

            # 转换为文本
            text = self.speech_recognizer.recognize_google(audio, language=language)

            # 清理临时文件
            os.unlink(temp_path)

            return text

        except sr.UnknownValueError:
            self.logger.warning("语音识别无法理解音频")
            return None
        except sr.RequestError as e:
            self.logger.error(f"语音识别服务错误: {e}")
            return None
        except Exception as e:
            self.logger.error(f"语音转文本失败: {e}")
            return None

    async def recognize_microphone_input(
        self, timeout: float = 5.0, language: str = "zh-CN"
    ) -> Optional[str]:
        """识别麦克风输入"""
        if not self.speech_recognizer or not self.microphone:
            return None

        try:
            # 监听麦克风
            with self.microphone as source:
                self.logger.info("请说话...")
                audio = self.speech_recognizer.listen(source, timeout=timeout)

            # 识别语音
            text = self.speech_recognizer.recognize_google(audio, language=language)
            return text

        except sr.WaitTimeoutError:
            self.logger.warning("语音输入超时")
            return None
        except sr.UnknownValueError:
            self.logger.warning("无法理解语音")
            return None
        except Exception as e:
            self.logger.error(f"麦克风语音识别失败: {e}")
            return None

    async def recognize_hand_gestures(
        self, image_data: Union[bytes, np.ndarray]
    ) -> List[Dict[str, Any]]:
        """识别手势"""
        if not self.hands_detector:
            return []

        try:
            # 处理输入图像
            if isinstance(image_data, bytes):
                # 从字节数据创建图像
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                image = image_data

            # 转换颜色空间
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # 检测手部
            results = self.hands_detector.process(rgb_image)

            gestures = []
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # 分析手势
                    gesture = await self._analyze_hand_gesture(hand_landmarks)
                    if gesture:
                        gestures.append(gesture)

            return gestures

        except Exception as e:
            self.logger.error(f"手势识别失败: {e}")
            return []

    async def _analyze_hand_gesture(self, hand_landmarks) -> Optional[Dict[str, Any]]:
        """分析手势"""
        try:
            # 获取关键点坐标
            landmarks = []
            for landmark in hand_landmarks.landmark:
                landmarks.append([landmark.x, landmark.y, landmark.z])

            landmarks = np.array(landmarks)

            # 简单的手势识别逻辑
            # 这里可以实现更复杂的手势识别算法

            # 检测竖起大拇指
            thumb_tip = landmarks[4]
            thumb_mcp = landmarks[2]
            index_tip = landmarks[8]

            if thumb_tip[1] < thumb_mcp[1] and thumb_tip[1] < index_tip[1]:
                return {
                    "gesture": "thumbs_up",
                    "command": self.gesture_commands.get("thumbs_up", "确认"),
                    "confidence": 0.8,
                }

            # 检测张开的手掌
            finger_tips = [landmarks[i] for i in [4, 8, 12, 16, 20]]
            finger_mcps = [landmarks[i] for i in [2, 5, 9, 13, 17]]

            extended_fingers = 0
            for tip, mcp in zip(finger_tips, finger_mcps):
                if tip[1] < mcp[1]:  # 手指伸直
                    extended_fingers += 1

            if extended_fingers >= 4:
                return {
                    "gesture": "open_palm",
                    "command": self.gesture_commands.get("open_palm", "停止"),
                    "confidence": 0.7,
                }

            return None

        except Exception as e:
            self.logger.error(f"手势分析失败: {e}")
            return None

    async def recognize_sign_language(self, video_frames: List[np.ndarray]) -> Optional[str]:
        """识别手语"""
        if not self.hands_detector or not self.pose_detector:
            return None

        try:
            # 这里应该实现完整的手语识别算法
            # 目前只是一个简化的示例

            gestures_sequence = []

            for frame in video_frames:
                # 检测手部和姿态
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                hand_results = self.hands_detector.process(rgb_frame)
                pose_results = self.pose_detector.process(rgb_frame)

                frame_data = {
                    "hands": (
                        hand_results.multi_hand_landmarks
                        if hand_results.multi_hand_landmarks
                        else []
                    ),
                    "pose": pose_results.pose_landmarks if pose_results.pose_landmarks else None,
                }

                gestures_sequence.append(frame_data)

            # 分析手语序列
            # 这里需要实现手语词汇识别算法
            recognized_text = await self._analyze_sign_language_sequence(gestures_sequence)

            return recognized_text

        except Exception as e:
            self.logger.error(f"手语识别失败: {e}")
            return None

    async def _analyze_sign_language_sequence(self, sequence: List[Dict]) -> Optional[str]:
        """分析手语序列"""
        # 这里应该实现真正的手语识别算法
        # 目前只返回示例文本
        if len(sequence) > 10:
            return "你好"
        elif len(sequence) > 5:
            return "谢谢"
        else:
            return None

    async def generate_accessible_ui(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """生成无障碍UI"""
        try:
            accessible_content = content.copy()

            # 根据配置调整UI
            if self.config.high_contrast:
                accessible_content["theme"] = "high_contrast"

            if self.config.simplified_ui:
                accessible_content["layout"] = "simplified"

            if self.config.font_size > 16:
                accessible_content["font_size"] = self.config.font_size

            # 添加无障碍标签
            if "elements" in accessible_content:
                for element in accessible_content["elements"]:
                    if "text" in element and self.config.text_to_speech:
                        element["aria_label"] = element["text"]
                        element["tts_enabled"] = True

                    if "action" in element and self.config.voice_commands:
                        element["voice_command"] = f"点击{element.get('text', '按钮')}"

            return accessible_content

        except Exception as e:
            self.logger.error(f"生成无障碍UI失败: {e}")
            return content

    async def process_voice_command(self, command: str) -> Optional[Dict[str, Any]]:
        """处理语音命令"""
        try:
            command = command.lower().strip()

            # 基本导航命令
            navigation_commands = {
                "上一页": {"action": "navigate", "direction": "back"},
                "下一页": {"action": "navigate", "direction": "forward"},
                "返回": {"action": "navigate", "direction": "back"},
                "主页": {"action": "navigate", "target": "home"},
                "设置": {"action": "navigate", "target": "settings"},
            }

            # 操作命令
            action_commands = {
                "确认": {"action": "confirm"},
                "取消": {"action": "cancel"},
                "重复": {"action": "repeat"},
                "帮助": {"action": "help"},
                "停止": {"action": "stop"},
            }

            # 诊断相关命令
            diagnosis_commands = {
                "开始诊断": {"action": "start_diagnosis"},
                "结束诊断": {"action": "end_diagnosis"},
                "重新诊断": {"action": "restart_diagnosis"},
                "查看结果": {"action": "view_results"},
                "保存结果": {"action": "save_results"},
            }

            # 合并所有命令
            all_commands = {**navigation_commands, **action_commands, **diagnosis_commands}

            # 查找匹配的命令
            for cmd_text, cmd_action in all_commands.items():
                if cmd_text in command:
                    return cmd_action

            # 如果没有找到精确匹配，尝试模糊匹配
            for cmd_text, cmd_action in all_commands.items():
                if any(word in command for word in cmd_text.split()):
                    return {**cmd_action, "confidence": 0.7}

            return None

        except Exception as e:
            self.logger.error(f"处理语音命令失败: {e}")
            return None

    async def provide_audio_feedback(self, message: str, priority: str = "normal"):
        """提供音频反馈"""
        if not self.config.text_to_speech:
            return

        try:
            # 根据优先级调整语音参数
            if priority == "urgent":
                self.tts_engine.setProperty('rate', int(250 * self.config.voice_speed))
                self.tts_engine.setProperty('volume', min(1.0, self.config.voice_volume * 1.2))
            elif priority == "low":
                self.tts_engine.setProperty('rate', int(150 * self.config.voice_speed))
                self.tts_engine.setProperty('volume', self.config.voice_volume * 0.8)
            else:
                self.tts_engine.setProperty('rate', int(200 * self.config.voice_speed))
                self.tts_engine.setProperty('volume', self.config.voice_volume)

            # 播放语音
            self.tts_engine.say(message)
            self.tts_engine.runAndWait()

        except Exception as e:
            self.logger.error(f"音频反馈失败: {e}")

    async def get_accessibility_status(self) -> Dict[str, Any]:
        """获取无障碍服务状态"""
        return {
            "enabled": self.config is not None,
            "mode": self.config.mode.value if self.config else None,
            "features": {
                "text_to_speech": self.tts_engine is not None and self.config.text_to_speech,
                "speech_to_text": self.speech_recognizer is not None and self.config.speech_to_text,
                "gesture_control": self.hands_detector is not None and self.config.gesture_control,
                "sign_language": self.hands_detector is not None and self.config.sign_language,
                "voice_commands": self.config.voice_commands if self.config else False,
            },
            "config": {
                "voice_speed": self.config.voice_speed if self.config else 1.0,
                "voice_volume": self.config.voice_volume if self.config else 0.8,
                "font_size": self.config.font_size if self.config else 16,
                "high_contrast": self.config.high_contrast if self.config else False,
                "simplified_ui": self.config.simplified_ui if self.config else False,
            },
        }

    async def update_config(self, new_config: AccessibilityConfig):
        """更新无障碍配置"""
        try:
            self.config = new_config

            # 重新初始化相关组件
            if self.config.text_to_speech and not self.tts_engine:
                await self._initialize_tts()

            if self.config.speech_to_text and not self.speech_recognizer:
                await self._initialize_speech_recognition()

            if (
                self.config.sign_language or self.config.gesture_control
            ) and not self.hands_detector:
                await self._initialize_sign_language()

            self.logger.info("无障碍配置已更新")

        except Exception as e:
            self.logger.error(f"更新无障碍配置失败: {e}")
            raise AccessibilityError(f"更新配置失败: {e}")

    async def cleanup(self):
        """清理资源"""
        try:
            if self.tts_engine:
                self.tts_engine.stop()

            if self.hands_detector:
                self.hands_detector.close()

            if self.pose_detector:
                self.pose_detector.close()

            self.logger.info("无障碍服务已清理")

        except Exception as e:
            self.logger.error(f"清理无障碍服务失败: {e}")


# 全局无障碍服务实例
_accessibility_service: Optional[AccessibilityService] = None


async def get_accessibility_service() -> AccessibilityService:
    """获取无障碍服务实例"""
    global _accessibility_service
    if _accessibility_service is None:
        _accessibility_service = AccessibilityService()
        await _accessibility_service.initialize()
    return _accessibility_service


async def cleanup_accessibility_service():
    """清理无障碍服务"""
    global _accessibility_service
    if _accessibility_service:
        await _accessibility_service.cleanup()
        _accessibility_service = None
