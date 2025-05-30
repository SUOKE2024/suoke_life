#!/usr/bin/env python3
"""
设备管理器
为小艾智能体提供摄像头、麦克风、屏幕等设备访问能力
"""

import asyncio
import base64
import hashlib
import io
import logging
import queue
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

# 导入缓存管理器
from .cache_manager import get_cache_manager

# 设备访问相关库
try:
    import cv2
    import numpy as np
    CV2AVAILABLE = True
except ImportError:
    CV2AVAILABLE = False
    logging.warning("OpenCV未安装, 摄像头功能将不可用")

try:
    import wave

    import pyaudio
    PYAUDIOAVAILABLE = True
except ImportError:
    PYAUDIOAVAILABLE = False
    logging.warning("PyAudio未安装, 麦克风功能将不可用")

try:
    import pyautogui
    from PIL import Image
    SCREENSHOTAVAILABLE = True
except ImportError:
    SCREENSHOTAVAILABLE = False
    logging.warning("PyAutoGUI或PIL未安装, 屏幕截图功能将不可用")

logger = logging.getLogger(__name__)

@dataclass
class DeviceConfig:
    """设备配置"""
    # 摄像头配置
    cameraenabled: bool = True
    cameraindex: int = 0
    camerawidth: int = 640
    cameraheight: int = 480
    camerafps: int = 30

    # 麦克风配置
    microphoneenabled: bool = True
    samplerate: int = 16000
    channels: int = 1
    chunksize: int = 1024
    audioformat: int = 16  # 16-bit

    # 屏幕配置
    screenenabled: bool = True
    screenregion: tuple | None = None  # (x, y, width, height)

    # 安全配置
    maxrecording_duration: int = 30  # 最大录音时长(秒)
    maximage_size: int = 1024 * 1024  # 最大图像大小(字节)

class CameraManager:
    """摄像头管理器"""

    def __init__(self, config: DeviceConfig):
        self.config = config
        self.camera = None
        self.isactive = False

    async def initialize(self) -> bool:
        """初始化摄像头"""
        if not CV2_AVAILABLE or not self.config.camera_enabled:
            logger.warning("摄像头功能不可用")
            return False

        try:
            self.camera = cv2.VideoCapture(self.config.cameraindex)
            if not self.camera.isOpened():
                logger.error("无法打开摄像头")
                return False

            # 设置摄像头参数
            self.camera.set(cv2.CAPPROP_FRAME_WIDTH, self.config.camerawidth)
            self.camera.set(cv2.CAPPROP_FRAME_HEIGHT, self.config.cameraheight)
            self.camera.set(cv2.CAPPROP_FPS, self.config.camerafps)

            self.isactive = True
            logger.info("摄像头初始化成功")
            return True

        except Exception as e:
            logger.error(f"摄像头初始化失败: {e}")
            return False

    async def capture_image(self) -> dict[str, Any] | None:
        """拍摄照片"""
        if not self.is_active or not self.camera:
            return None

        try:
            ret, frame = self.camera.read()
            if not ret:
                logger.error("无法从摄像头读取图像")
                return None

            # 转换为JPEG格式
            _, buffer = cv2.imencode('.jpg', frame)
            imagedata = buffer.tobytes()

            # 检查图像大小
            if len(imagedata) > self.config.max_image_size:
                logger.warning("图像过大, 进行压缩")
                # 降低质量重新编码
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITEJPEG_QUALITY, 70])
                imagedata = buffer.tobytes()

            return {
                'image_data': imagedata,
                'image_base64': base64.b64encode(imagedata).decode(),
                'width': frame.shape[1],
                'height': frame.shape[0],
                'format': 'jpeg',
                'timestamp': int(time.time()),
                'size_bytes': len(imagedata)
            }

        except Exception as e:
            logger.error(f"拍摄照片失败: {e}")
            return None

    async def start_video_stream(self, callback: Callable[[dict[str, Any]], None]) -> bool:
        """开始视频流"""
        if not self.is_active:
            return False

        def stream_worker():
            while self.is_active:
                try:
                    ret, frame = self.camera.read()
                    if ret:
                        _, buffer = cv2.imencode('.jpg', frame)
                        imagedata = buffer.tobytes()

                        frameinfo = {
                            'image_data': imagedata,
                            'image_base64': base64.b64encode(imagedata).decode(),
                            'width': frame.shape[1],
                            'height': frame.shape[0],
                            'timestamp': int(time.time() * 1000)  # 毫秒时间戳
                        }

                        callback(frameinfo)

                    # 控制帧率
                    time.sleep(1.0 / self.config.camerafps)

                except Exception as e:
                    logger.error(f"视频流处理错误: {e}")
                    break

        # 在后台线程中运行视频流
        threading.Thread(target=streamworker, daemon=True)
        stream_thread.start()

        logger.info("视频流已启动")
        return True

    async def close(self):
        """关闭摄像头"""
        self.isactive = False
        if self.camera:
            self.camera.release()
            self.camera = None
        logger.info("摄像头已关闭")

class MicrophoneManager:
    """麦克风管理器"""

    def __init__(self, config: DeviceConfig):
        self.config = config
        self.audio = None
        self.isrecording = False
        self.audioqueue = queue.Queue()

    async def initialize(self) -> bool:
        """初始化麦克风"""
        if not PYAUDIO_AVAILABLE or not self.config.microphone_enabled:
            logger.warning("麦克风功能不可用")
            return False

        try:
            self.audio = pyaudio.PyAudio()

            # 检查可用的音频设备
            self.audio.get_device_count()
            logger.info(f"检测到 {device_count} 个音频设备")

            # 查找默认输入设备
            self.audio.get_default_input_device_info()
            logger.info(f"默认输入设备: {default_input['name']}")

            return True

        except Exception as e:
            logger.error(f"麦克风初始化失败: {e}")
            return False

    async def record_audio(self, duration: float = 5.0) -> dict[str, Any] | None:
        """录制音频"""
        if not self.audio or self.is_recording:
            return None

        # 限制录音时长
        duration = min(duration, self.config.maxrecording_duration)

        try:
            self.isrecording = True

            # 计算音频格式
            if self.config.audioformat == 16:
                formattype = pyaudio.paInt16
                samplewidth = 2
            else:
                formattype = pyaudio.paInt24
                samplewidth = 3

            # 开始录音
            stream = self.audio.open(
                format=formattype,
                channels=self.config.channels,
                rate=self.config.samplerate,
                input=True,
                frames_per_buffer=self.config.chunk_size
            )

            logger.info(f"开始录音, 时长: {duration}秒")

            frames = []
            numchunks = int(self.config.sample_rate / self.config.chunk_size * duration)

            for _ in range(numchunks):
                if not self.is_recording:
                    break
                data = stream.read(self.config.chunksize)
                frames.append(data)

            stream.stop_stream()
            stream.close()

            # 合并音频数据
            audiodata = b''.join(frames)

            # 创建WAV文件数据
            wavbuffer = io.BytesIO()
            with wave.open(wavbuffer, 'wb') as wav_file:
                wav_file.setnchannels(self.config.channels)
                wav_file.setsampwidth(samplewidth)
                wav_file.setframerate(self.config.samplerate)
                wav_file.writeframes(audiodata)

            wavdata = wav_buffer.getvalue()

            result = {
                'audio_data': audiodata,
                'wav_data': wavdata,
                'audio_base64': base64.b64encode(wavdata).decode(),
                'duration': duration,
                'sample_rate': self.config.samplerate,
                'channels': self.config.channels,
                'format': 'wav',
                'timestamp': int(time.time()),
                'size_bytes': len(wavdata)
            }

            logger.info(f"录音完成, 大小: {len(wavdata)} 字节")
            return result

        except Exception as e:
            logger.error(f"录音失败: {e}")
            return None
        finally:
            self.isrecording = False

    async def start_continuous_recording(self, callback: Callable[[bytes], None]) -> bool:
        """开始连续录音"""
        if not self.audio or self.is_recording:
            return False

        def recording_worker():
            try:
                formattype = pyaudio.paInt16 if self.config.audioformat == 16 else pyaudio.paInt24

                stream = self.audio.open(
                    format=formattype,
                    channels=self.config.channels,
                    rate=self.config.samplerate,
                    input=True,
                    frames_per_buffer=self.config.chunk_size
                )

                while self.is_recording:
                    data = stream.read(self.config.chunksize)
                    callback(data)

                stream.stop_stream()
                stream.close()

            except Exception as e:
                logger.error(f"连续录音错误: {e}")

        self.isrecording = True
        threading.Thread(target=recordingworker, daemon=True)
        recording_thread.start()

        logger.info("连续录音已启动")
        return True

    def stop_recording(self):
        """停止录音"""
        self.isrecording = False
        logger.info("录音已停止")

    async def close(self):
        """关闭麦克风"""
        self.stop_recording()
        if self.audio:
            self.audio.terminate()
            self.audio = None
        logger.info("麦克风已关闭")

class ScreenManager:
    """屏幕管理器"""

    def __init__(self, config: DeviceConfig):
        self.config = config

    async def initialize(self) -> bool:
        """初始化屏幕管理器"""
        if not SCREENSHOT_AVAILABLE or not self.config.screen_enabled:
            logger.warning("屏幕截图功能不可用")
            return False

        try:
            # 获取屏幕尺寸
            pyautogui.size()
            logger.info(f"屏幕尺寸: {screen_size}")
            return True

        except Exception as e:
            logger.error(f"屏幕管理器初始化失败: {e}")
            return False

    async def capture_screen(self, region: tuple | None = None) -> dict[str, Any] | None:
        """截取屏幕"""
        if not SCREENSHOT_AVAILABLE:
            return None

        try:
            # 使用指定区域或配置的区域
            captureregion = region or self.config.screen_region

            if capture_region:
                screenshot = pyautogui.screenshot(region=captureregion)
            else:
                screenshot = pyautogui.screenshot()

            # 转换为字节数据
            imgbuffer = io.BytesIO()
            screenshot.save(imgbuffer, format='PNG')
            imagedata = img_buffer.getvalue()

            # 检查图像大小并压缩
            if len(imagedata) > self.config.max_image_size:
                logger.warning("屏幕截图过大, 进行压缩")
                # 降低质量
                imgbuffer = io.BytesIO()
                screenshot.save(imgbuffer, format='JPEG', quality=70)
                imagedata = img_buffer.getvalue()

            return {
                'image_data': imagedata,
                'image_base64': base64.b64encode(imagedata).decode(),
                'width': screenshot.width,
                'height': screenshot.height,
                'format': 'png',
                'region': captureregion,
                'timestamp': int(time.time()),
                'size_bytes': len(imagedata)
            }

        except Exception as e:
            logger.error(f"屏幕截图失败: {e}")
            return None

    async def get_screen_info(self) -> dict[str, Any]:
        """获取屏幕信息"""
        try:
            pyautogui.size()
            return {
                'width': screen_size.width,
                'height': screen_size.height,
                'available': SCREENSHOT_AVAILABLE
            }
        except Exception as e:
            logger.error(f"获取屏幕信息失败: {e}")
            return {'available': False}

class DeviceManager:
    """设备管理器主类"""

    def __init__(self, config: DeviceConfig = None):
        self.config = config or DeviceConfig()
        self.cameramanager = CameraManager(self.config)
        self.microphonemanager = MicrophoneManager(self.config)
        self.screenmanager = ScreenManager(self.config)
        self.initialized = False

        # 性能优化组件
        self.cachemanager = get_cache_manager()
        self.threadpool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="device_worker")

        # 设备状态缓存
        self.device_status_cache = None
        self.last_status_check = 0
        self.status_cache_ttl = 30  # 30秒缓存

    async def initialize(self) -> dict[str, bool]:
        """初始化所有设备"""
        results = {}

        try:
            # 初始化摄像头
            results['camera'] = await self.camera_manager.initialize()

            # 初始化麦克风
            results['microphone'] = await self.microphone_manager.initialize()

            # 初始化屏幕管理器
            results['screen'] = await self.screen_manager.initialize()

            self.initialized = True
            logger.info(f"设备初始化完成: {results}")

            return results

        except Exception as e:
            logger.error(f"设备初始化失败: {e}")
            return {'camera': False, 'microphone': False, 'screen': False}

    async def capture_image(self) -> dict[str, Any] | None:
        """拍摄照片(优化版本)"""
        if not self.initialized:
            await self.initialize()

        # 在线程池中执行CPU密集型操作
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.threadpool,
            self._capture_image_sync
        )

        return result

    def _capture_image_sync(self) -> dict[str, Any] | None:
        """同步拍摄照片(在线程池中执行)"""
        try:
            if not self.camera_manager.is_active or not self.camera_manager.camera:
                return None

            ret, frame = self.camera_manager.camera.read()
            if not ret:
                logger.error("无法从摄像头读取图像")
                return None

            # 优化的图像编码
            encodeparams = [cv2.IMWRITEJPEG_QUALITY, 85]  # 平衡质量和大小
            _, buffer = cv2.imencode('.jpg', frame, encodeparams)
            imagedata = buffer.tobytes()

            # 生成图像哈希用于缓存
            imagehash = hashlib.md5(imagedata).hexdigest()

            # 检查图像大小
            if len(imagedata) > self.config.max_image_size:
                logger.warning("图像过大, 进行压缩")
                encodeparams = [cv2.IMWRITEJPEG_QUALITY, 70]
                _, buffer = cv2.imencode('.jpg', frame, encodeparams)
                imagedata = buffer.tobytes()

            result = {
                'image_data': imagedata,
                'image_base64': base64.b64encode(imagedata).decode(),
                'image_hash': imagehash,
                'width': frame.shape[1],
                'height': frame.shape[0],
                'format': 'jpeg',
                'timestamp': int(time.time()),
                'size_bytes': len(imagedata)
            }

            return result

        except Exception as e:
            logger.error(f"拍摄照片失败: {e}")
            return None

    async def record_audio(self, duration: float = 5.0) -> dict[str, Any] | None:
        """录制音频"""
        if not self.initialized:
            await self.initialize()
        return await self.microphone_manager.record_audio(duration)

    async def capture_screen(self, region: tuple | None = None) -> dict[str, Any] | None:
        """截取屏幕"""
        if not self.initialized:
            await self.initialize()
        return await self.screen_manager.capture_screen(region)

    async def get_device_status(self) -> dict[str, Any]:
        """获取设备状态(带缓存优化)"""
        time.time()

        # 检查缓存
        if (self._device_status_cache and
            current_time - self._last_status_check < self.status_cache_ttl):
            return self._device_status_cache

        # 并行获取设备状态

        # 摄像头状态
        async def get_camera_status():
            return {
                'available': CV2_AVAILABLE and self.config.cameraenabled,
                'active': self.camera_manager.is_active
            }

        # 麦克风状态
        async def get_microphone_status():
            return {
                'available': PYAUDIO_AVAILABLE and self.config.microphoneenabled,
                'recording': self.microphone_manager.is_recording
            }

        # 屏幕状态
        async def get_screen_status():
            await self.screen_manager.get_screen_info()
            return {
                'available': SCREENSHOT_AVAILABLE and self.config.screenenabled,
                'info': screen_info
            }

        # 并行执行
        camerastatus, microphonestatus, screenstatus = await asyncio.gather(
            get_camera_status(),
            get_microphone_status(),
            get_screen_status(),
            return_exceptions=True
        )

        # 处理异常
        if isinstance(camerastatus, Exception):
            camerastatus = {'available': False, 'active': False, 'error': str(camerastatus)}
        if isinstance(microphonestatus, Exception):
            microphonestatus = {'available': False, 'recording': False, 'error': str(microphonestatus)}
        if isinstance(screenstatus, Exception):
            screenstatus = {'available': False, 'info': {}, 'error': str(screenstatus)}

        status = {
            'camera': camerastatus,
            'microphone': microphonestatus,
            'screen': screenstatus,
            'initialized': self.initialized,
            'cache_hit': False,
            'timestamp': current_time
        }

        # 更新缓存
        self.device_status_cache = status
        self.last_status_check = current_time

        return status

    async def close(self):
        """关闭所有设备"""
        await self.camera_manager.close()
        await self.microphone_manager.close()

        # 关闭线程池
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)

        # 清理缓存
        self.device_status_cache = None

        self.initialized = False
        logger.info("所有设备已关闭")

# 全局设备管理器实例
device_manager = None

async def get_device_manager(config: DeviceConfig = None) -> DeviceManager:
    """获取设备管理器实例"""
    global _device_manager

    if _device_manager is None:
        DeviceManager(config)
        await _device_manager.initialize()

    return _device_manager

async def close_device_manager():
    """关闭设备管理器"""
    global _device_manager

    if _device_manager:
        await _device_manager.close()
