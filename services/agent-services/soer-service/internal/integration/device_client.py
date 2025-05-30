#!/usr/bin/env python3
"""
外部健康设备API集成客户端
"""
import base64
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from pkg.utils.config_loader import get_config

logger = logging.getLogger(__name__)

class DeviceClient:
    """健康设备API集成基类"""

    def __init__(self, device_type: str):
        """
        初始化设备客户端

        Args:
            device_type: 设备类型
        """
        self.device_type = device_type
        self.config = get_config()
        self.device_config = self.config.get_section(f'sensors.devices.{device_type}', {})
        self.enabled = self.device_config.get('enabled', False)

        # 设备凭证
        self.client_id = self.device_config.get('client_id', os.environ.get(f'{device_type.upper()}_CLIENT_ID', ''))
        self.client_secret = self.device_config.get('client_secret', os.environ.get(f'{device_type.upper()}_CLIENT_SECRET', ''))
        self.base_url = self.device_config.get('base_url', '')

        # 缓存
        self.tokens = {}
        self.cache = {}
        self.cache_expiry = {}

        logger.info(f"初始化 {device_type} 设备客户端, 已启用: {self.enabled}")

    async def get_token(self, user_id: str) -> str | None:
        """
        获取访问令牌

        Args:
            user_id: 用户ID

        Returns:
            Optional[str]: 访问令牌或None
        """
        # 子类必须实现
        raise NotImplementedError("子类必须实现此方法")

    async def get_data(self, user_id: str, data_type: str, start_time: int | None = None,
                       end_time: int | None = None) -> list[dict[str, Any]]:
        """
        获取设备数据

        Args:
            user_id: 用户ID
            data_type: 数据类型
            start_time: 开始时间戳（秒）
            end_time: 结束时间戳（秒）

        Returns:
            List[Dict[str, Any]]: 设备数据列表
        """
        # 子类必须实现
        raise NotImplementedError("子类必须实现此方法")

    async def refresh_token(self, user_id: str, refresh_token: str) -> tuple[str | None, str | None]:
        """
        刷新访问令牌

        Args:
            user_id: 用户ID
            refresh_token: 刷新令牌

        Returns:
            Tuple[Optional[str], Optional[str]]: (访问令牌, 刷新令牌)或(None, None)
        """
        # 子类必须实现
        raise NotImplementedError("子类必须实现此方法")

    def _cache_data(self, key: str, data: Any, expiry_seconds: int = 300):
        """缓存数据"""
        self.cache[key] = data
        self.cache_expiry[key] = time.time() + expiry_seconds

    def _get_cached_data(self, key: str) -> Any | None:
        """获取缓存数据"""
        if key in self.cache and time.time() < self.cache_expiry.get(key, 0):
            return self.cache[key]
        return None


class AppleHealthClient(DeviceClient):
    """Apple Health集成客户端"""

    def __init__(self):
        """初始化Apple Health客户端"""
        super().__init__('apple_health')

    async def get_token(self, user_id: str) -> str | None:
        """
        获取访问令牌（Apple Health通过应用直接访问，不需要OAuth流程）

        Args:
            user_id: 用户ID

        Returns:
            Optional[str]: 固定返回"direct_access"
        """
        return "direct_access"

    async def get_data(self, user_id: str, data_type: str, start_time: int | None = None,
                       end_time: int | None = None) -> list[dict[str, Any]]:
        """
        获取Apple Health数据（示例实现，实际上需要通过React Native Health插件访问）

        Args:
            user_id: 用户ID
            data_type: 数据类型
            start_time: 开始时间戳（秒）
            end_time: 结束时间戳（秒）

        Returns:
            List[Dict[str, Any]]: 设备数据列表
        """
        # 此处为示例实现
        # 实际上，Apple Health数据需要通过React Native Health插件从iOS设备端获取
        # 服务端无法直接获取Apple Health数据

        logger.info(f"请求获取用户 {user_id} 的 Apple Health {data_type} 数据")

        # 返回示例数据
        data = []

        if data_type == "heart_rate":
            for i in range(10):
                timestamp = int(time.time() - i * 3600)
                data.append({
                    "timestamp": timestamp,
                    "device_id": "apple_watch",
                    "values": {
                        "bpm": 70 + (i % 10)
                    },
                    "metadata": {
                        "source": "Apple Watch",
                        "context": "resting"
                    }
                })
        elif data_type == "steps":
            for i in range(7):
                timestamp = int(time.time() - i * 86400)
                data.append({
                    "timestamp": timestamp,
                    "device_id": "iphone",
                    "values": {
                        "steps": 7500 + (i % 5) * 1000
                    },
                    "metadata": {
                        "source": "iPhone",
                        "context": "daily"
                    }
                })

        return data

    async def refresh_token(self, user_id: str, refresh_token: str) -> tuple[str | None, str | None]:
        """
        刷新访问令牌（Apple Health不适用）

        Args:
            user_id: 用户ID
            refresh_token: 刷新令牌

        Returns:
            Tuple[Optional[str], Optional[str]]: ("direct_access", "")
        """
        return "direct_access", ""


class GoogleFitClient(DeviceClient):
    """Google Fit集成客户端"""

    def __init__(self):
        """初始化Google Fit客户端"""
        super().__init__('google_fit')
        self.auth_url = "https://oauth2.googleapis.com/token"
        self.api_base = "https://www.googleapis.com/fitness/v1/users/me"

    async def get_token(self, user_id: str) -> str | None:
        """
        获取访问令牌

        Args:
            user_id: 用户ID

        Returns:
            Optional[str]: 访问令牌或None
        """
        # 检查缓存
        if user_id in self.tokens and self.tokens[user_id].get('expiry', 0) > time.time():
            return self.tokens[user_id].get('access_token')

        # 从存储获取刷新令牌
        refresh_token = await self._get_refresh_token(user_id)
        if not refresh_token:
            logger.warning(f"未找到用户 {user_id} 的Google Fit刷新令牌")
            return None

        # 刷新访问令牌
        try:
            access_token, new_refresh_token = await self.refresh_token(user_id, refresh_token)
            return access_token
        except Exception as e:
            logger.error(f"获取Google Fit访问令牌失败: {str(e)}")
            return None

    async def refresh_token(self, user_id: str, refresh_token: str) -> tuple[str | None, str | None]:
        """
        刷新访问令牌

        Args:
            user_id: 用户ID
            refresh_token: 刷新令牌

        Returns:
            Tuple[Optional[str], Optional[str]]: (访问令牌, 刷新令牌)或(None, None)
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'refresh_token': refresh_token,
                    'grant_type': 'refresh_token'
                }

                async with session.post(self.auth_url, data=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Google Fit刷新令牌失败: {error_text}")
                        return None, None

                    data = await response.json()
                    access_token = data.get('access_token')
                    expires_in = data.get('expires_in', 3600)

                    # 更新缓存
                    self.tokens[user_id] = {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'expiry': time.time() + expires_in - 300  # 提前5分钟过期
                    }

                    # 如果返回了新的刷新令牌则保存
                    new_refresh_token = data.get('refresh_token', refresh_token)
                    if new_refresh_token != refresh_token:
                        await self._save_refresh_token(user_id, new_refresh_token)

                    return access_token, new_refresh_token
        except Exception as e:
            logger.error(f"刷新Google Fit令牌出错: {str(e)}")
            return None, None

    async def get_data(self, user_id: str, data_type: str, start_time: int | None = None,
                       end_time: int | None = None) -> list[dict[str, Any]]:
        """
        获取Google Fit数据

        Args:
            user_id: 用户ID
            data_type: 数据类型
            start_time: 开始时间戳（秒）
            end_time: 结束时间戳（秒）

        Returns:
            List[Dict[str, Any]]: 设备数据列表
        """
        # 缓存键
        cache_key = f"{user_id}:{data_type}:{start_time}:{end_time}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data

        # 获取访问令牌
        access_token = await self.get_token(user_id)
        if not access_token:
            logger.error(f"未能获取用户 {user_id} 的Google Fit访问令牌")
            return []

        # 设置默认时间范围
        if not end_time:
            end_time = int(time.time())
        if not start_time:
            start_time = end_time - 604800  # 默认7天

        # 转换为纳秒时间戳
        start_time_ns = start_time * 1000000000
        end_time_ns = end_time * 1000000000

        # 数据类型映射
        data_type_map = {
            "heart_rate": "com.google.heart_rate.bpm",
            "steps": "com.google.step_count.delta",
            "weight": "com.google.weight",
            "sleep": "com.google.sleep.segment"
        }

        gfit_data_type = data_type_map.get(data_type)
        if not gfit_data_type:
            logger.error(f"不支持的Google Fit数据类型: {data_type}")
            return []

        try:
            # 构建请求
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # 对于不同数据类型使用不同API端点
            if data_type in ["heart_rate", "weight"]:
                url = f"{self.api_base}/dataSources/{gfit_data_type}/datasets/{start_time_ns}-{end_time_ns}"

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"获取Google Fit数据失败: {error_text}")
                            return []

                        result = await response.json()
                        data = []

                        # 处理结果
                        for point in result.get('point', []):
                            timestamp = int(int(point.get('startTimeNanos', 0)) / 1000000000)
                            if data_type == "heart_rate":
                                value = point.get('value', [{}])[0].get('fpVal', 0)
                                data.append({
                                    "timestamp": timestamp,
                                    "device_id": "google_fit",
                                    "values": {
                                        "bpm": value
                                    },
                                    "metadata": {
                                        "source": point.get('originDataSourceId', ''),
                                        "context": "measurement"
                                    }
                                })
                            elif data_type == "weight":
                                value = point.get('value', [{}])[0].get('fpVal', 0)
                                data.append({
                                    "timestamp": timestamp,
                                    "device_id": "google_fit",
                                    "values": {
                                        "weight_kg": value
                                    },
                                    "metadata": {
                                        "source": point.get('originDataSourceId', ''),
                                        "context": "measurement"
                                    }
                                })

            elif data_type == "steps":
                url = f"{self.api_base}/dataset:aggregate"
                payload = {
                    "aggregateBy": [{
                        "dataTypeName": gfit_data_type
                    }],
                    "bucketByTime": { "durationMillis": 86400000 },  # 按天聚合
                    "startTimeMillis": start_time * 1000,
                    "endTimeMillis": end_time * 1000
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"获取Google Fit步数数据失败: {error_text}")
                            return []

                        result = await response.json()
                        data = []

                        # 处理结果
                        for bucket in result.get('bucket', []):
                            timestamp = int(int(bucket.get('startTimeMillis', 0)) / 1000)
                            for dataset in bucket.get('dataset', []):
                                for point in dataset.get('point', []):
                                    value = point.get('value', [{}])[0].get('intVal', 0)
                                    data.append({
                                        "timestamp": timestamp,
                                        "device_id": "google_fit",
                                        "values": {
                                            "steps": value
                                        },
                                        "metadata": {
                                            "source": "google_fit",
                                            "context": "daily"
                                        }
                                    })

            # 缓存结果
            self._cache_data(cache_key, data, 300)
            return data

        except Exception as e:
            logger.error(f"获取Google Fit数据出错: {str(e)}")
            return []

    async def _get_refresh_token(self, user_id: str) -> str | None:
        """从存储获取刷新令牌"""
        # 此处应该从数据库获取，示例实现
        # 实际应用中，应当实现安全的令牌存储
        return os.environ.get(f'GOOGLE_FIT_REFRESH_TOKEN_{user_id}', None)

    async def _save_refresh_token(self, user_id: str, refresh_token: str) -> bool:
        """保存刷新令牌"""
        # 此处应该保存到数据库，示例实现
        logger.info(f"保存用户 {user_id} 的Google Fit刷新令牌")
        return True


class FitbitClient(DeviceClient):
    """Fitbit集成客户端"""

    def __init__(self):
        """初始化Fitbit客户端"""
        super().__init__('fitbit')
        self.auth_url = "https://api.fitbit.com/oauth2/token"
        self.api_base = "https://api.fitbit.com"

    async def get_token(self, user_id: str) -> str | None:
        """
        获取访问令牌

        Args:
            user_id: 用户ID

        Returns:
            Optional[str]: 访问令牌或None
        """
        # 检查缓存
        if user_id in self.tokens and self.tokens[user_id].get('expiry', 0) > time.time():
            return self.tokens[user_id].get('access_token')

        # 从存储获取刷新令牌
        refresh_token = await self._get_refresh_token(user_id)
        if not refresh_token:
            logger.warning(f"未找到用户 {user_id} 的Fitbit刷新令牌")
            return None

        # 刷新访问令牌
        try:
            access_token, new_refresh_token = await self.refresh_token(user_id, refresh_token)
            return access_token
        except Exception as e:
            logger.error(f"获取Fitbit访问令牌失败: {str(e)}")
            return None

    async def refresh_token(self, user_id: str, refresh_token: str) -> tuple[str | None, str | None]:
        """
        刷新访问令牌

        Args:
            user_id: 用户ID
            refresh_token: 刷新令牌

        Returns:
            Tuple[Optional[str], Optional[str]]: (访问令牌, 刷新令牌)或(None, None)
        """
        try:
            # 基本认证凭证
            auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Basic {auth_header}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }

                payload = {
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token
                }

                async with session.post(self.auth_url, headers=headers, data=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Fitbit刷新令牌失败: {error_text}")
                        return None, None

                    data = await response.json()
                    access_token = data.get('access_token')
                    new_refresh_token = data.get('refresh_token')
                    expires_in = data.get('expires_in', 3600)

                    # 更新缓存
                    self.tokens[user_id] = {
                        'access_token': access_token,
                        'refresh_token': new_refresh_token,
                        'expiry': time.time() + expires_in - 300  # 提前5分钟过期
                    }

                    # 保存新的刷新令牌
                    await self._save_refresh_token(user_id, new_refresh_token)

                    return access_token, new_refresh_token
        except Exception as e:
            logger.error(f"刷新Fitbit令牌出错: {str(e)}")
            return None, None

    async def get_data(self, user_id: str, data_type: str, start_time: int | None = None,
                       end_time: int | None = None) -> list[dict[str, Any]]:
        """
        获取Fitbit数据

        Args:
            user_id: 用户ID
            data_type: 数据类型
            start_time: 开始时间戳（秒）
            end_time: 结束时间戳（秒）

        Returns:
            List[Dict[str, Any]]: 设备数据列表
        """
        # 缓存键
        cache_key = f"{user_id}:{data_type}:{start_time}:{end_time}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data

        # 获取访问令牌
        access_token = await self.get_token(user_id)
        if not access_token:
            logger.error(f"未能获取用户 {user_id} 的Fitbit访问令牌")
            return []

        # 设置默认时间范围
        if not end_time:
            end_time = int(time.time())
        if not start_time:
            start_time = end_time - 604800  # 默认7天

        # 转换为日期格式 (YYYY-MM-DD)
        start_date = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d')
        end_date = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d')

        try:
            # 构建请求
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept-Language': 'zh_CN'
            }

            data = []

            if data_type == "heart_rate":
                # Fitbit心率数据 - 获取每天的心率数据
                current_date = datetime.fromtimestamp(start_time)
                end_date_dt = datetime.fromtimestamp(end_time)

                while current_date <= end_date_dt:
                    date_str = current_date.strftime('%Y-%m-%d')
                    url = f"{self.api_base}/1/user/-/activities/heart/date/{date_str}/1d/1min.json"

                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers) as response:
                            if response.status != 200:
                                logger.warning(f"获取Fitbit心率数据失败: {await response.text()}")
                                current_date += timedelta(days=1)
                                continue

                            result = await response.json()

                            # 处理心率数据
                            activities_heart = result.get('activities-heart-intraday', {})
                            dataset = activities_heart.get('dataset', [])

                            base_timestamp = int(datetime.strptime(date_str, '%Y-%m-%d').timestamp())

                            for entry in dataset:
                                time_str = entry.get('time', '')
                                value = entry.get('value', 0)

                                # 解析时间
                                if time_str:
                                    hours, minutes, seconds = map(int, time_str.split(':'))
                                    entry_timestamp = base_timestamp + hours * 3600 + minutes * 60 + seconds

                                    data.append({
                                        "timestamp": entry_timestamp,
                                        "device_id": "fitbit",
                                        "values": {
                                            "bpm": value
                                        },
                                        "metadata": {
                                            "source": "fitbit",
                                            "context": "measurement"
                                        }
                                    })

                    current_date += timedelta(days=1)

            elif data_type == "sleep":
                url = f"{self.api_base}/1.2/user/-/sleep/date/{start_date}/{end_date}.json"

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status != 200:
                            logger.error(f"获取Fitbit睡眠数据失败: {await response.text()}")
                            return []

                        result = await response.json()
                        sleep_logs = result.get('sleep', [])

                        for sleep_log in sleep_logs:
                            start_time = int(datetime.strptime(sleep_log.get('startTime', ''), '%Y-%m-%dT%H:%M:%S.%f').timestamp())
                            end_time = int(datetime.strptime(sleep_log.get('endTime', ''), '%Y-%m-%dT%H:%M:%S.%f').timestamp())

                            # 计算各个睡眠阶段的时长（秒）
                            duration = sleep_log.get('duration', 0) / 1000  # 毫秒转秒
                            deep_sleep = sum(1 for stage in sleep_log.get('levels', {}).get('data', [])
                                            if stage.get('level') == 'deep') * 30  # 每个阶段30秒
                            light_sleep = sum(1 for stage in sleep_log.get('levels', {}).get('data', [])
                                            if stage.get('level') == 'light') * 30
                            rem_sleep = sum(1 for stage in sleep_log.get('levels', {}).get('data', [])
                                            if stage.get('level') == 'rem') * 30
                            awake = sum(1 for stage in sleep_log.get('levels', {}).get('data', [])
                                        if stage.get('level') == 'wake') * 30

                            data.append({
                                "timestamp": start_time,
                                "device_id": "fitbit",
                                "values": {
                                    "duration": duration,
                                    "deep_sleep": deep_sleep,
                                    "light_sleep": light_sleep,
                                    "rem_sleep": rem_sleep,
                                    "awake": awake,
                                    "efficiency": sleep_log.get('efficiency', 0)
                                },
                                "metadata": {
                                    "source": "fitbit",
                                    "start_time": start_time,
                                    "end_time": end_time
                                }
                            })

            elif data_type == "steps":
                url = f"{self.api_base}/1/user/-/activities/steps/date/{start_date}/{end_date}.json"

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status != 200:
                            logger.error(f"获取Fitbit步数数据失败: {await response.text()}")
                            return []

                        result = await response.json()
                        step_data = result.get('activities-steps', [])

                        for entry in step_data:
                            date_str = entry.get('dateTime', '')
                            value = int(entry.get('value', 0))

                            if date_str:
                                entry_timestamp = int(datetime.strptime(date_str, '%Y-%m-%d').timestamp())

                                data.append({
                                    "timestamp": entry_timestamp,
                                    "device_id": "fitbit",
                                    "values": {
                                        "steps": value
                                    },
                                    "metadata": {
                                        "source": "fitbit",
                                        "context": "daily"
                                    }
                                })

            # 缓存结果
            self._cache_data(cache_key, data, 300)
            return data

        except Exception as e:
            logger.error(f"获取Fitbit数据出错: {str(e)}")
            return []

    async def _get_refresh_token(self, user_id: str) -> str | None:
        """从存储获取刷新令牌"""
        # 此处应该从数据库获取，示例实现
        return os.environ.get(f'FITBIT_REFRESH_TOKEN_{user_id}', None)

    async def _save_refresh_token(self, user_id: str, refresh_token: str) -> bool:
        """保存刷新令牌"""
        # 此处应该保存到数据库，示例实现
        logger.info(f"保存用户 {user_id} 的Fitbit刷新令牌")
        return True


class DeviceClientFactory:
    """设备客户端工厂"""

    _instances = {}

    @classmethod
    def get_client(cls, device_type: str) -> DeviceClient:
        """
        获取设备客户端实例

        Args:
            device_type: 设备类型

        Returns:
            DeviceClient: 设备客户端实例
        """
        if device_type not in cls._instances:
            if device_type == 'apple_health':
                cls._instances[device_type] = AppleHealthClient()
            elif device_type == 'google_fit':
                cls._instances[device_type] = GoogleFitClient()
            elif device_type == 'fitbit':
                cls._instances[device_type] = FitbitClient()
            else:
                raise ValueError(f"不支持的设备类型: {device_type}")

        return cls._instances[device_type]
