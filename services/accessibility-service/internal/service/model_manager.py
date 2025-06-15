#!/usr/bin/env python

"""
AI模型管理器 - 优化版本
支持懒加载、缓存、资源管理和性能监控
"""

import asyncio
import gc
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import psutil

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """模型状态枚举"""

    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    UNLOADING = "unloading"


@dataclass
class ModelInfo:
    """模型信息"""

    name: str
    model_type: str
    config: dict[str, Any]
    status: ModelStatus = ModelStatus.UNLOADED
    model_instance: Any = None
    load_time: float | None = None
    last_used: float | None = None
    memory_usage: int | None = None
    error_message: str | None = None
    use_count: int = 0


class ModelManager:
    """AI模型管理器"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._models: dict[str, ModelInfo] = {}
        self._lock = asyncio.Lock()
        self._loading_locks: dict[str, asyncio.Lock] = {}
        self._cleanup_task: asyncio.Task | None = None
        self._max_memory_usage = (
            config.get("model_manager", {}).get("max_memory_mb", 4096) * 1024 * 1024
        )
        self._cleanup_interval = config.get("model_manager", {}).get(
            "cleanup_interval_seconds", 300
        )
        self._model_ttl = config.get("model_manager", {}).get("model_ttl_seconds", 1800)

        # 启动清理任务
        self._start_cleanup_task()

        logger.info(
            f"模型管理器初始化完成，最大内存使用: {self._max_memory_usage // 1024 // 1024}MB"
        )

    def _start_cleanup_task(self):
        """启动模型清理任务"""

        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(self._cleanup_interval)
                    await self._cleanup_unused_models()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"模型清理任务异常: {e!s}")

        self._cleanup_task = asyncio.create_task(cleanup_loop())

    async def load_model(
        self, model_name: str, model_config: dict[str, Any] = None
    ) -> Any:
        """
        加载模型（懒加载）

        Args:
            model_name: 模型名称
            model_config: 模型配置（可选，覆盖默认配置）

        Returns:
            模型实例
        """
        # 获取或创建加载锁
        if model_name not in self._loading_locks:
            self._loading_locks[model_name] = asyncio.Lock()

        async with self._loading_locks[model_name]:
            # 检查模型是否已加载
            if model_name in self._models:
                model_info = self._models[model_name]
                if model_info.status == ModelStatus.LOADED:
                    model_info.last_used = time.time()
                    model_info.use_count += 1
                    logger.debug(f"使用已加载的模型: {model_name}")
                    return model_info.model_instance
                elif model_info.status == ModelStatus.LOADING:
                    # 等待加载完成
                    while model_info.status == ModelStatus.LOADING:
                        await asyncio.sleep(0.1)
                    if model_info.status == ModelStatus.LOADED:
                        model_info.last_used = time.time()
                        model_info.use_count += 1
                        return model_info.model_instance
                    else:
                        raise RuntimeError(
                            f"模型加载失败: {model_name}, 错误: {model_info.error_message}"
                        )

            # 检查内存使用情况
            await self._check_memory_usage()

            # 开始加载模型
            config = model_config or self._get_model_config(model_name)
            model_info = ModelInfo(
                name=model_name,
                model_type=config.get("type", "unknown"),
                config=config,
                status=ModelStatus.LOADING,
            )
            self._models[model_name] = model_info

            try:
                logger.info(f"开始加载模型: {model_name}")
                start_time = time.time()

                # 根据模型类型加载
                model_instance = await self._load_model_by_type(model_name, config)

                load_time = time.time() - start_time
                memory_usage = self._get_model_memory_usage(model_instance)

                # 更新模型信息
                model_info.model_instance = model_instance
                model_info.status = ModelStatus.LOADED
                model_info.load_time = load_time
                model_info.last_used = time.time()
                model_info.memory_usage = memory_usage
                model_info.use_count = 1

                logger.info(
                    f"模型加载完成: {model_name}, 耗时: {load_time:.2f}s, 内存: {memory_usage // 1024 // 1024}MB"
                )
                return model_instance

            except Exception as e:
                model_info.status = ModelStatus.ERROR
                model_info.error_message = str(e)
                logger.error(f"模型加载失败: {model_name}, 错误: {e!s}")
                raise

    async def unload_model(self, model_name: str) -> bool:
        """
        卸载模型

        Args:
            model_name: 模型名称

        Returns:
            是否成功卸载
        """
        async with self._lock:
            if model_name not in self._models:
                logger.warning(f"模型未找到: {model_name}")
                return False

            model_info = self._models[model_name]
            if model_info.status != ModelStatus.LOADED:
                logger.warning(f"模型未加载: {model_name}")
                return False

            try:
                logger.info(f"开始卸载模型: {model_name}")
                model_info.status = ModelStatus.UNLOADING

                # 清理模型实例
                if hasattr(model_info.model_instance, "cleanup"):
                    if asyncio.iscoroutinefunction(model_info.model_instance.cleanup):
                        await model_info.model_instance.cleanup()
                    else:
                        model_info.model_instance.cleanup()

                # 删除引用
                del model_info.model_instance
                model_info.model_instance = None
                model_info.status = ModelStatus.UNLOADED

                # 强制垃圾回收
                gc.collect()

                logger.info(f"模型卸载完成: {model_name}")
                return True

            except Exception as e:
                logger.error(f"模型卸载失败: {model_name}, 错误: {e!s}")
                model_info.status = ModelStatus.ERROR
                model_info.error_message = str(e)
                return False

    async def get_model_status(self, model_name: str) -> dict[str, Any]:
        """获取模型状态"""
        if model_name not in self._models:
            return {
                "name": model_name,
                "status": ModelStatus.UNLOADED.value,
                "loaded": False,
            }

        model_info = self._models[model_name]
        return {
            "name": model_name,
            "type": model_info.model_type,
            "status": model_info.status.value,
            "loaded": model_info.status == ModelStatus.LOADED,
            "load_time": model_info.load_time,
            "last_used": model_info.last_used,
            "memory_usage_mb": (
                model_info.memory_usage // 1024 // 1024
                if model_info.memory_usage
                else None
            ),
            "use_count": model_info.use_count,
            "error_message": model_info.error_message,
        }

    async def get_all_models_status(self) -> dict[str, dict[str, Any]]:
        """获取所有模型状态"""
        status = {}
        for model_name in self._models:
            status[model_name] = await self.get_model_status(model_name)
        return status

    async def _load_model_by_type(self, model_name: str, config: dict[str, Any]) -> Any:
        """根据类型加载模型"""
        model_type = config.get("type", "transformers")

        if model_type == "transformers":
            return await self._load_transformers_model(model_name, config)
        elif model_type == "opencv":
            return await self._load_opencv_model(model_name, config)
        elif model_type == "mediapipe":
            return await self._load_mediapipe_model(model_name, config)
        elif model_type == "custom":
            return await self._load_custom_model(model_name, config)
        else:
            # 默认使用模拟模型
            return await self._load_mock_model(model_name, config)

    async def _load_transformers_model(
        self, model_name: str, config: dict[str, Any]
    ) -> Any:
        """加载Transformers模型"""
        try:
            from transformers import AutoModel, AutoProcessor, AutoTokenizer

            model_path = config.get("path", config.get("name", model_name))

            # 在线程池中加载模型以避免阻塞
            loop = asyncio.get_event_loop()

            if config.get("has_tokenizer", True):
                tokenizer = await loop.run_in_executor(
                    None, lambda: AutoTokenizer.from_pretrained(model_path)
                )
            else:
                tokenizer = None

            if config.get("has_processor", False):
                processor = await loop.run_in_executor(
                    None, lambda: AutoProcessor.from_pretrained(model_path)
                )
            else:
                processor = None

            model = await loop.run_in_executor(
                None, lambda: AutoModel.from_pretrained(model_path)
            )

            return {
                "model": model,
                "tokenizer": tokenizer,
                "processor": processor,
                "type": "transformers",
            }

        except Exception as e:
            logger.warning(f"加载Transformers模型失败: {model_name}, 使用模拟模型")
            return await self._load_mock_model(model_name, config)

    async def _load_opencv_model(self, model_name: str, config: dict[str, Any]) -> Any:
        """加载OpenCV模型"""
        try:
            import cv2

            model_path = config.get("path")
            if not model_path:
                raise ValueError("OpenCV模型需要指定path")

            loop = asyncio.get_event_loop()
            net = await loop.run_in_executor(None, lambda: cv2.dnn.readNet(model_path))

            return {"net": net, "type": "opencv"}

        except Exception as e:
            logger.warning(f"加载OpenCV模型失败: {model_name}, 使用模拟模型")
            return await self._load_mock_model(model_name, config)

    async def _load_mediapipe_model(
        self, model_name: str, config: dict[str, Any]
    ) -> Any:
        """加载MediaPipe模型"""
        try:

            model_type = config.get("mediapipe_type", "hands")

            if model_type == "hands":
                hands = mp.solutions.hands.Hands(
                    static_image_mode=config.get("static_image_mode", False),
                    max_num_hands=config.get("max_num_hands", 2),
                    min_detection_confidence=config.get(
                        "min_detection_confidence", 0.7
                    ),
                    min_tracking_confidence=config.get("min_tracking_confidence", 0.5),
                )
                return {"hands": hands, "type": "mediapipe"}
            else:
                raise ValueError(f"不支持的MediaPipe模型类型: {model_type}")

        except Exception as e:
            logger.warning(f"加载MediaPipe模型失败: {model_name}, 使用模拟模型")
            return await self._load_mock_model(model_name, config)

    async def _load_custom_model(self, model_name: str, config: dict[str, Any]) -> Any:
        """加载自定义模型"""
        # 这里可以实现自定义模型加载逻辑
        logger.info(f"加载自定义模型: {model_name}")
        return await self._load_mock_model(model_name, config)

    async def _load_mock_model(self, model_name: str, config: dict[str, Any]) -> Any:
        """加载模拟模型"""
        logger.info(f"使用模拟模型: {model_name}")

        # 模拟加载时间
        await asyncio.sleep(0.1)

        return {"model": f"mock_model_{model_name}", "type": "mock", "config": config}

    def _get_model_config(self, model_name: str) -> dict[str, Any]:
        """获取模型配置"""
        models_config = self.config.get("models", {})

        # 预定义的模型配置
        default_configs = {
            "scene_model": {
                "type": "transformers",
                "path": "microsoft/beit-base-patch16-224-pt22k",
                "has_processor": True,
                "has_tokenizer": False,
            },
            "sign_language_model": {"type": "mediapipe", "mediapipe_type": "hands"},
            "speech_model": {"type": "transformers", "path": "openai/whisper-base"},
            "conversion_model": {"type": "transformers", "path": "google/flan-t5-base"},
        }

        # 合并配置
        config = default_configs.get(model_name, {})
        config.update(models_config.get(model_name, {}))

        return config

    def _get_model_memory_usage(self, model_instance: Any) -> int:
        """估算模型内存使用量"""
        try:
            # 简单的内存使用估算
            if hasattr(model_instance, "get_memory_footprint"):
                return model_instance.get_memory_footprint()

            # 对于字典类型的模型包装器
            if isinstance(model_instance, dict):
                total_size = 0
                for key, value in model_instance.items():
                    if hasattr(value, "get_memory_footprint"):
                        total_size += value.get_memory_footprint()
                    elif hasattr(value, "numel"):  # PyTorch模型
                        total_size += value.numel() * 4  # 假设float32
                return total_size

            # 默认估算
            return 100 * 1024 * 1024  # 100MB

        except Exception as e:
            return 100 * 1024 * 1024  # 默认100MB

    async def _check_memory_usage(self):
        """检查内存使用情况"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            current_memory = memory_info.rss

            if current_memory > self._max_memory_usage:
                logger.warning(
                    f"内存使用超限: {current_memory // 1024 // 1024}MB > {self._max_memory_usage // 1024 // 1024}MB"
                )
                await self._cleanup_unused_models()
        except Exception as e:
            logger.error(f"检查内存使用失败: {e!s}")

    async def _cleanup_unused_models(self):
        """清理未使用的模型"""
        current_time = time.time()
        models_to_unload = []

        async with self._lock:
            for model_name, model_info in self._models.items():
                if (
                    model_info.status == ModelStatus.LOADED
                    and model_info.last_used
                    and current_time - model_info.last_used > self._model_ttl
                ):
                    models_to_unload.append(model_name)

        for model_name in models_to_unload:
            logger.info(f"清理未使用的模型: {model_name}")
            await self.unload_model(model_name)

    async def cleanup(self):
        """清理资源"""
        logger.info("开始清理模型管理器")

        # 停止清理任务
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # 卸载所有模型
        model_names = list(self._models.keys())
        for model_name in model_names:
            await self.unload_model(model_name)

        logger.info("模型管理器清理完成")
