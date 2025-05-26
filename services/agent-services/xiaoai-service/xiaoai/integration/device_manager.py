#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备管理器
为小艾智能体提供摄像头、麦克风、屏幕等设备访问能力
"""

import asyncio
import logging
import base64
import io
import time
import hashlib
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

# 导入缓存管理器
from .cache_manager import get_cache_manager

# 设备访问相关库
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("OpenCV未安装，摄像头功能将不可用")

try:
    import pyaudio
    import wave
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logging.warning("PyAudio未安装，麦克风功能将不可用")

try:
    import pyautogui
    from PIL import Image
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False
    logging.warning("PyAutoGUI或PIL未安装，屏幕截图功能将不可用")

logger = logging.getLogger(__name__)

@dataclass
class DeviceConfig:
    """设备配置"""
    # 摄像头配置
    camera_enabled: bool = True
    camera_index: int = 0
    camera_width: int = 640
    camera_height: int = 480
    camera_fps: int = 30
    
    # 麦克风配置
    microphone_enabled: bool = True
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    audio_format: int = 16  # 16-bit
    
    # 屏幕配置
    screen_enabled: bool = True
    screen_region: Optional[tuple] = None  # (x, y, width, height)
    
    # 安全配置
    max_recording_duration: int = 30  # 最大录音时长（秒）
    max_image_size: int = 1024 * 1024  # 最大图像大小（字节）

class CameraManager:
    """摄像头管理器"""
    
    def __init__(self, config: DeviceConfig):
        self.config = config
        self.camera = None
        self.is_active = False
        
    async def initialize(self) -> bool:
        """初始化摄像头"""
        if not CV2_AVAILABLE or not self.config.camera_enabled:
            logger.warning("摄像头功能不可用")
            return False
            
        try:
            self.camera = cv2.VideoCapture(self.config.camera_index)
            if not self.camera.isOpened():
                logger.error("无法打开摄像头")
                return False
                
            # 设置摄像头参数
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.config.camera_fps)
            
            self.is_active = True
            logger.info("摄像头初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"摄像头初始化失败: {e}")
            return False
    
    async def capture_image(self) -> Optional[Dict[str, Any]]:
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
            image_data = buffer.tobytes()
            
            # 检查图像大小
            if len(image_data) > self.config.max_image_size:
                logger.warning("图像过大，进行压缩")
                # 降低质量重新编码
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                image_data = buffer.tobytes()
            
            return {
                'image_data': image_data,
                'image_base64': base64.b64encode(image_data).decode(),
                'width': frame.shape[1],
                'height': frame.shape[0],
                'format': 'jpeg',
                'timestamp': int(time.time()),
                'size_bytes': len(image_data)
            }
            
        except Exception as e:
            logger.error(f"拍摄照片失败: {e}")
            return None
    
    async def start_video_stream(self, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """开始视频流"""
        if not self.is_active:
            return False
            
        def stream_worker():
            while self.is_active:
                try:
                    ret, frame = self.camera.read()
                    if ret:
                        _, buffer = cv2.imencode('.jpg', frame)
                        image_data = buffer.tobytes()
                        
                        frame_info = {
                            'image_data': image_data,
                            'image_base64': base64.b64encode(image_data).decode(),
                            'width': frame.shape[1],
                            'height': frame.shape[0],
                            'timestamp': int(time.time() * 1000)  # 毫秒时间戳
                        }
                        
                        callback(frame_info)
                    
                    # 控制帧率
                    time.sleep(1.0 / self.config.camera_fps)
                    
                except Exception as e:
                    logger.error(f"视频流处理错误: {e}")
                    break
        
        # 在后台线程中运行视频流
        stream_thread = threading.Thread(target=stream_worker, daemon=True)
        stream_thread.start()
        
        logger.info("视频流已启动")
        return True
    
    async def close(self):
        """关闭摄像头"""
        self.is_active = False
        if self.camera:
            self.camera.release()
            self.camera = None
        logger.info("摄像头已关闭")

class MicrophoneManager:
    """麦克风管理器"""
    
    def __init__(self, config: DeviceConfig):
        self.config = config
        self.audio = None
        self.is_recording = False
        self.audio_queue = queue.Queue()
        
    async def initialize(self) -> bool:
        """初始化麦克风"""
        if not PYAUDIO_AVAILABLE or not self.config.microphone_enabled:
            logger.warning("麦克风功能不可用")
            return False
            
        try:
            self.audio = pyaudio.PyAudio()
            
            # 检查可用的音频设备
            device_count = self.audio.get_device_count()
            logger.info(f"检测到 {device_count} 个音频设备")
            
            # 查找默认输入设备
            default_input = self.audio.get_default_input_device_info()
            logger.info(f"默认输入设备: {default_input['name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"麦克风初始化失败: {e}")
            return False
    
    async def record_audio(self, duration: float = 5.0) -> Optional[Dict[str, Any]]:
        """录制音频"""
        if not self.audio or self.is_recording:
            return None
            
        # 限制录音时长
        duration = min(duration, self.config.max_recording_duration)
        
        try:
            self.is_recording = True
            
            # 计算音频格式
            if self.config.audio_format == 16:
                format_type = pyaudio.paInt16
                sample_width = 2
            else:
                format_type = pyaudio.paInt24
                sample_width = 3
            
            # 开始录音
            stream = self.audio.open(
                format=format_type,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                frames_per_buffer=self.config.chunk_size
            )
            
            logger.info(f"开始录音，时长: {duration}秒")
            
            frames = []
            num_chunks = int(self.config.sample_rate / self.config.chunk_size * duration)
            
            for _ in range(num_chunks):
                if not self.is_recording:
                    break
                data = stream.read(self.config.chunk_size)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # 合并音频数据
            audio_data = b''.join(frames)
            
            # 创建WAV文件数据
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(self.config.channels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(self.config.sample_rate)
                wav_file.writeframes(audio_data)
            
            wav_data = wav_buffer.getvalue()
            
            result = {
                'audio_data': audio_data,
                'wav_data': wav_data,
                'audio_base64': base64.b64encode(wav_data).decode(),
                'duration': duration,
                'sample_rate': self.config.sample_rate,
                'channels': self.config.channels,
                'format': 'wav',
                'timestamp': int(time.time()),
                'size_bytes': len(wav_data)
            }
            
            logger.info(f"录音完成，大小: {len(wav_data)} 字节")
            return result
            
        except Exception as e:
            logger.error(f"录音失败: {e}")
            return None
        finally:
            self.is_recording = False
    
    async def start_continuous_recording(self, callback: Callable[[bytes], None]) -> bool:
        """开始连续录音"""
        if not self.audio or self.is_recording:
            return False
            
        def recording_worker():
            try:
                format_type = pyaudio.paInt16 if self.config.audio_format == 16 else pyaudio.paInt24
                
                stream = self.audio.open(
                    format=format_type,
                    channels=self.config.channels,
                    rate=self.config.sample_rate,
                    input=True,
                    frames_per_buffer=self.config.chunk_size
                )
                
                while self.is_recording:
                    data = stream.read(self.config.chunk_size)
                    callback(data)
                
                stream.stop_stream()
                stream.close()
                
            except Exception as e:
                logger.error(f"连续录音错误: {e}")
        
        self.is_recording = True
        recording_thread = threading.Thread(target=recording_worker, daemon=True)
        recording_thread.start()
        
        logger.info("连续录音已启动")
        return True
    
    def stop_recording(self):
        """停止录音"""
        self.is_recording = False
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
            screen_size = pyautogui.size()
            logger.info(f"屏幕尺寸: {screen_size}")
            return True
            
        except Exception as e:
            logger.error(f"屏幕管理器初始化失败: {e}")
            return False
    
    async def capture_screen(self, region: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """截取屏幕"""
        if not SCREENSHOT_AVAILABLE:
            return None
            
        try:
            # 使用指定区域或配置的区域
            capture_region = region or self.config.screen_region
            
            if capture_region:
                screenshot = pyautogui.screenshot(region=capture_region)
            else:
                screenshot = pyautogui.screenshot()
            
            # 转换为字节数据
            img_buffer = io.BytesIO()
            screenshot.save(img_buffer, format='PNG')
            image_data = img_buffer.getvalue()
            
            # 检查图像大小并压缩
            if len(image_data) > self.config.max_image_size:
                logger.warning("屏幕截图过大，进行压缩")
                # 降低质量
                img_buffer = io.BytesIO()
                screenshot.save(img_buffer, format='JPEG', quality=70)
                image_data = img_buffer.getvalue()
            
            return {
                'image_data': image_data,
                'image_base64': base64.b64encode(image_data).decode(),
                'width': screenshot.width,
                'height': screenshot.height,
                'format': 'png',
                'region': capture_region,
                'timestamp': int(time.time()),
                'size_bytes': len(image_data)
            }
            
        except Exception as e:
            logger.error(f"屏幕截图失败: {e}")
            return None
    
    async def get_screen_info(self) -> Dict[str, Any]:
        """获取屏幕信息"""
        try:
            screen_size = pyautogui.size()
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
        self.camera_manager = CameraManager(self.config)
        self.microphone_manager = MicrophoneManager(self.config)
        self.screen_manager = ScreenManager(self.config)
        self.initialized = False
        
        # 性能优化组件
        self.cache_manager = get_cache_manager()
        self.thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="device_worker")
        
        # 设备状态缓存
        self._device_status_cache = None
        self._last_status_check = 0
        self._status_cache_ttl = 30  # 30秒缓存
        
    async def initialize(self) -> Dict[str, bool]:
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
    
    async def capture_image(self) -> Optional[Dict[str, Any]]:
        """拍摄照片（优化版本）"""
        if not self.initialized:
            await self.initialize()
        
        # 在线程池中执行CPU密集型操作
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.thread_pool,
            self._capture_image_sync
        )
        
        return result
    
    def _capture_image_sync(self) -> Optional[Dict[str, Any]]:
        """同步拍摄照片（在线程池中执行）"""
        try:
            if not self.camera_manager.is_active or not self.camera_manager.camera:
                return None
                
            ret, frame = self.camera_manager.camera.read()
            if not ret:
                logger.error("无法从摄像头读取图像")
                return None
            
            # 优化的图像编码
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 85]  # 平衡质量和大小
            _, buffer = cv2.imencode('.jpg', frame, encode_params)
            image_data = buffer.tobytes()
            
            # 生成图像哈希用于缓存
            image_hash = hashlib.md5(image_data).hexdigest()
            
            # 检查图像大小
            if len(image_data) > self.config.max_image_size:
                logger.warning("图像过大，进行压缩")
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, 70]
                _, buffer = cv2.imencode('.jpg', frame, encode_params)
                image_data = buffer.tobytes()
            
            result = {
                'image_data': image_data,
                'image_base64': base64.b64encode(image_data).decode(),
                'image_hash': image_hash,
                'width': frame.shape[1],
                'height': frame.shape[0],
                'format': 'jpeg',
                'timestamp': int(time.time()),
                'size_bytes': len(image_data)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"拍摄照片失败: {e}")
            return None
    
    async def record_audio(self, duration: float = 5.0) -> Optional[Dict[str, Any]]:
        """录制音频"""
        if not self.initialized:
            await self.initialize()
        return await self.microphone_manager.record_audio(duration)
    
    async def capture_screen(self, region: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """截取屏幕"""
        if not self.initialized:
            await self.initialize()
        return await self.screen_manager.capture_screen(region)
    
    async def get_device_status(self) -> Dict[str, Any]:
        """获取设备状态（带缓存优化）"""
        current_time = time.time()
        
        # 检查缓存
        if (self._device_status_cache and 
            current_time - self._last_status_check < self._status_cache_ttl):
            return self._device_status_cache
        
        # 并行获取设备状态
        tasks = []
        
        # 摄像头状态
        async def get_camera_status():
            return {
                'available': CV2_AVAILABLE and self.config.camera_enabled,
                'active': self.camera_manager.is_active
            }
        
        # 麦克风状态
        async def get_microphone_status():
            return {
                'available': PYAUDIO_AVAILABLE and self.config.microphone_enabled,
                'recording': self.microphone_manager.is_recording
            }
        
        # 屏幕状态
        async def get_screen_status():
            screen_info = await self.screen_manager.get_screen_info()
            return {
                'available': SCREENSHOT_AVAILABLE and self.config.screen_enabled,
                'info': screen_info
            }
        
        # 并行执行
        camera_status, microphone_status, screen_status = await asyncio.gather(
            get_camera_status(),
            get_microphone_status(),
            get_screen_status(),
            return_exceptions=True
        )
        
        # 处理异常
        if isinstance(camera_status, Exception):
            camera_status = {'available': False, 'active': False, 'error': str(camera_status)}
        if isinstance(microphone_status, Exception):
            microphone_status = {'available': False, 'recording': False, 'error': str(microphone_status)}
        if isinstance(screen_status, Exception):
            screen_status = {'available': False, 'info': {}, 'error': str(screen_status)}
        
        status = {
            'camera': camera_status,
            'microphone': microphone_status,
            'screen': screen_status,
            'initialized': self.initialized,
            'cache_hit': False,
            'timestamp': current_time
        }
        
        # 更新缓存
        self._device_status_cache = status
        self._last_status_check = current_time
        
        return status
    
    async def close(self):
        """关闭所有设备"""
        await self.camera_manager.close()
        await self.microphone_manager.close()
        
        # 关闭线程池
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
        
        # 清理缓存
        self._device_status_cache = None
        
        self.initialized = False
        logger.info("所有设备已关闭")

# 全局设备管理器实例
_device_manager = None

async def get_device_manager(config: DeviceConfig = None) -> DeviceManager:
    """获取设备管理器实例"""
    global _device_manager
    
    if _device_manager is None:
        _device_manager = DeviceManager(config)
        await _device_manager.initialize()
    
    return _device_manager

async def close_device_manager():
    """关闭设备管理器"""
    global _device_manager
    
    if _device_manager:
        await _device_manager.close()
        _device_manager = None 