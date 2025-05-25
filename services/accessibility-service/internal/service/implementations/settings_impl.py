#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设置管理服务实现
提供用户偏好设置管理功能
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from ..interfaces import ISettingsService, ICacheManager
from ..decorators import performance_monitor, error_handler, cache_result, trace

logger = logging.getLogger(__name__)


class SettingsServiceImpl(ISettingsService):
    """
    设置管理服务实现类
    """
    
    def __init__(self, 
                 cache_manager: ICacheManager,
                 enabled: bool = True,
                 settings_config: Dict[str, Any] = None,
                 cache_ttl: int = 7200,
                 max_concurrent_requests: int = 20):
        """
        初始化设置服务
        
        Args:
            cache_manager: 缓存管理器
            enabled: 是否启用服务
            settings_config: 设置配置
            cache_ttl: 缓存过期时间
            max_concurrent_requests: 最大并发请求数
        """
        self.cache_manager = cache_manager
        self.enabled = enabled
        self.settings_config = settings_config or {}
        self.cache_ttl = cache_ttl
        self.max_concurrent_requests = max_concurrent_requests
        
        # 并发控制
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        # 服务状态
        self._initialized = False
        self._request_count = 0
        self._error_count = 0
        
        # 默认用户偏好设置
        self._default_preferences = {
            'accessibility': {
                'voice_assistance': {
                    'enabled': True,
                    'language': 'zh-CN',
                    'voice_speed': 1.0,
                    'voice_volume': 0.8,
                    'voice_type': 'female'
                },
                'screen_reading': {
                    'enabled': True,
                    'reading_speed': 1.0,
                    'highlight_text': True,
                    'auto_scroll': True
                },
                'sign_language': {
                    'enabled': False,
                    'language': 'CSL',
                    'detection_sensitivity': 0.8
                },
                'blind_assistance': {
                    'enabled': False,
                    'obstacle_detection': True,
                    'scene_description': True,
                    'navigation_guidance': True,
                    'audio_feedback': True
                },
                'content_conversion': {
                    'enabled': True,
                    'auto_simplify': False,
                    'simplification_level': 'medium',
                    'auto_translate': False,
                    'preferred_language': 'zh-CN'
                }
            },
            'ui': {
                'theme': 'light',
                'font_size': 'medium',
                'high_contrast': False,
                'large_buttons': False,
                'reduce_motion': False
            },
            'privacy': {
                'data_collection': True,
                'analytics': True,
                'personalization': True,
                'location_services': False
            },
            'notifications': {
                'enabled': True,
                'sound': True,
                'vibration': True,
                'priority_only': False
            }
        }
        
        # 用户偏好缓存
        self._user_preferences_cache = {}
        
        logger.info("设置管理服务初始化完成")
    
    async def initialize(self):
        """初始化服务"""
        if self._initialized:
            return
        
        try:
            if not self.enabled:
                logger.info("设置管理服务已禁用")
                return
            
            # 预加载常用设置
            await self._preload_settings()
            
            self._initialized = True
            logger.info("设置管理服务初始化成功")
            
        except Exception as e:
            logger.error(f"设置管理服务初始化失败: {str(e)}")
            raise
    
    async def _preload_settings(self):
        """预加载设置"""
        try:
            # 这里可以从数据库或配置文件预加载常用设置
            logger.debug("预加载设置完成")
            
        except Exception as e:
            logger.error(f"预加载设置失败: {str(e)}")
            raise
    
    @performance_monitor(operation_name="settings.get_user_preferences")
    @error_handler(operation_name="settings.get_user_preferences")
    @cache_result(ttl=7200, key_prefix="user_preferences")
    @trace(operation_name="get_user_preferences", kind="internal")
    async def get_user_preferences(self, user_id: str) -> Dict:
        """
        获取用户偏好
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户偏好设置
        """
        if not self.enabled or not self._initialized:
            raise ValueError("设置管理服务未启用或未初始化")
        
        async with self._semaphore:
            self._request_count += 1
            
            try:
                # 先从缓存获取
                cache_key = f"user_preferences:{user_id}"
                cached_preferences = await self.cache_manager.get(cache_key)
                
                if cached_preferences:
                    logger.debug(f"从缓存获取用户偏好: 用户 {user_id}")
                    return cached_preferences
                
                # 从存储获取（这里模拟从数据库获取）
                preferences = await self._load_user_preferences_from_storage(user_id)
                
                # 如果用户没有设置，使用默认设置
                if not preferences:
                    preferences = self._get_default_preferences_for_user(user_id)
                    # 保存默认设置
                    await self._save_user_preferences_to_storage(user_id, preferences)
                
                # 缓存偏好设置
                await self.cache_manager.set(cache_key, preferences, self.cache_ttl)
                
                # 构建响应
                response = {
                    'user_id': user_id,
                                    'timestamp': datetime.now(timezone.utc).isoformat(),
                'preferences': preferences,
                    'version': self._get_preferences_version(preferences),
                    'source': 'storage' if preferences != self._default_preferences else 'default'
                }
                
                logger.debug(f"获取用户偏好完成: 用户 {user_id}")
                return response
                
            except Exception as e:
                self._error_count += 1
                logger.error(f"获取用户偏好失败: 用户 {user_id}, 错误: {str(e)}")
                raise
    
    @performance_monitor(operation_name="settings.update_user_preferences")
    @error_handler(operation_name="settings.update_user_preferences")
    @trace(operation_name="update_user_preferences", kind="internal")
    async def update_user_preferences(self, user_id: str, 
                                    preferences: Dict) -> Dict:
        """
        更新用户偏好
        
        Args:
            user_id: 用户ID
            preferences: 新的偏好设置
        
        Returns:
            更新结果
        """
        if not self.enabled or not self._initialized:
            raise ValueError("设置管理服务未启用或未初始化")
        
        async with self._semaphore:
            self._request_count += 1
            
            try:
                # 验证偏好设置格式
                validated_preferences = await self._validate_preferences(preferences)
                
                # 获取当前偏好设置
                current_response = await self.get_user_preferences(user_id)
                current_preferences = current_response.get('preferences', {})
                
                # 合并偏好设置
                merged_preferences = await self._merge_preferences(
                    current_preferences, validated_preferences
                )
                
                # 保存到存储
                await self._save_user_preferences_to_storage(user_id, merged_preferences)
                
                # 更新缓存
                cache_key = f"user_preferences:{user_id}"
                await self.cache_manager.set(cache_key, merged_preferences, self.cache_ttl)
                
                # 记录变更历史
                await self._record_preferences_change(
                    user_id, current_preferences, merged_preferences
                )
                
                # 构建响应
                response = {
                    'user_id': user_id,
                                    'timestamp': datetime.now(timezone.utc).isoformat(),
                'updated_preferences': merged_preferences,
                    'changes_applied': self._get_preference_changes(
                        current_preferences, merged_preferences
                    ),
                    'version': self._get_preferences_version(merged_preferences),
                    'success': True
                }
                
                logger.debug(f"更新用户偏好完成: 用户 {user_id}")
                return response
                
            except Exception as e:
                self._error_count += 1
                logger.error(f"更新用户偏好失败: 用户 {user_id}, 错误: {str(e)}")
                raise
    
    async def _load_user_preferences_from_storage(self, user_id: str) -> Optional[Dict]:
        """从存储加载用户偏好"""
        try:
            # 模拟从数据库加载
            await asyncio.sleep(0.01)
            
            # 这里应该从实际的数据库或文件系统加载
            # 现在返回None表示用户没有自定义设置
            return None
            
        except Exception as e:
            logger.error(f"从存储加载用户偏好失败: 用户 {user_id}, 错误: {str(e)}")
            return None
    
    async def _save_user_preferences_to_storage(self, user_id: str, preferences: Dict):
        """保存用户偏好到存储"""
        try:
            # 模拟保存到数据库
            await asyncio.sleep(0.01)
            
            # 这里应该保存到实际的数据库或文件系统
            logger.debug(f"保存用户偏好到存储: 用户 {user_id}")
            
        except Exception as e:
            logger.error(f"保存用户偏好到存储失败: 用户 {user_id}, 错误: {str(e)}")
            raise
    
    def _get_default_preferences_for_user(self, user_id: str) -> Dict:
        """获取用户的默认偏好设置"""
        # 可以根据用户特征定制默认设置
        return self._default_preferences.copy()
    
    async def _validate_preferences(self, preferences: Dict) -> Dict:
        """验证偏好设置格式"""
        try:
            validated = {}
            
            # 验证无障碍设置
            if 'accessibility' in preferences:
                validated['accessibility'] = await self._validate_accessibility_preferences(
                    preferences['accessibility']
                )
            
            # 验证UI设置
            if 'ui' in preferences:
                validated['ui'] = await self._validate_ui_preferences(
                    preferences['ui']
                )
            
            # 验证隐私设置
            if 'privacy' in preferences:
                validated['privacy'] = await self._validate_privacy_preferences(
                    preferences['privacy']
                )
            
            # 验证通知设置
            if 'notifications' in preferences:
                validated['notifications'] = await self._validate_notification_preferences(
                    preferences['notifications']
                )
            
            return validated
            
        except Exception as e:
            logger.error(f"验证偏好设置失败: {str(e)}")
            raise ValueError(f"偏好设置格式无效: {str(e)}")
    
    async def _validate_accessibility_preferences(self, accessibility: Dict) -> Dict:
        """验证无障碍偏好设置"""
        validated = {}
        
        # 验证语音辅助设置
        if 'voice_assistance' in accessibility:
            voice_settings = accessibility['voice_assistance']
            validated['voice_assistance'] = {
                'enabled': bool(voice_settings.get('enabled', True)),
                'language': str(voice_settings.get('language', 'zh-CN')),
                'voice_speed': max(0.5, min(2.0, float(voice_settings.get('voice_speed', 1.0)))),
                'voice_volume': max(0.0, min(1.0, float(voice_settings.get('voice_volume', 0.8)))),
                'voice_type': str(voice_settings.get('voice_type', 'female'))
            }
        
        # 验证其他无障碍设置...
        return validated
    
    async def _validate_ui_preferences(self, ui: Dict) -> Dict:
        """验证UI偏好设置"""
        validated = {}
        
        if 'theme' in ui:
            theme = ui['theme']
            if theme in ['light', 'dark', 'auto']:
                validated['theme'] = theme
        
        if 'font_size' in ui:
            font_size = ui['font_size']
            if font_size in ['small', 'medium', 'large', 'extra_large']:
                validated['font_size'] = font_size
        
        if 'high_contrast' in ui:
            validated['high_contrast'] = bool(ui['high_contrast'])
        
        return validated
    
    async def _validate_privacy_preferences(self, privacy: Dict) -> Dict:
        """验证隐私偏好设置"""
        validated = {}
        
        for key in ['data_collection', 'analytics', 'personalization', 'location_services']:
            if key in privacy:
                validated[key] = bool(privacy[key])
        
        return validated
    
    async def _validate_notification_preferences(self, notifications: Dict) -> Dict:
        """验证通知偏好设置"""
        validated = {}
        
        for key in ['enabled', 'sound', 'vibration', 'priority_only']:
            if key in notifications:
                validated[key] = bool(notifications[key])
        
        return validated
    
    async def _merge_preferences(self, current: Dict, new: Dict) -> Dict:
        """合并偏好设置"""
        def deep_merge(dict1, dict2):
            result = dict1.copy()
            for key, value in dict2.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(current, new)
    
    async def _record_preferences_change(self, user_id: str, old_prefs: Dict, new_prefs: Dict):
        """记录偏好设置变更历史"""
        try:
            changes = self._get_preference_changes(old_prefs, new_prefs)
            
            # 这里应该记录到审计日志
            logger.info(f"用户偏好变更: 用户 {user_id}, 变更数量: {len(changes)}")
            
        except Exception as e:
            logger.error(f"记录偏好设置变更失败: 用户 {user_id}, 错误: {str(e)}")
    
    def _get_preference_changes(self, old_prefs: Dict, new_prefs: Dict) -> List[Dict]:
        """获取偏好设置变更列表"""
        changes = []
        
        def compare_dicts(old_dict, new_dict, path=""):
            for key, new_value in new_dict.items():
                current_path = f"{path}.{key}" if path else key
                
                if key not in old_dict:
                    changes.append({
                        'type': 'added',
                        'path': current_path,
                        'new_value': new_value
                    })
                elif isinstance(new_value, dict) and isinstance(old_dict[key], dict):
                    compare_dicts(old_dict[key], new_value, current_path)
                elif old_dict[key] != new_value:
                    changes.append({
                        'type': 'modified',
                        'path': current_path,
                        'old_value': old_dict[key],
                        'new_value': new_value
                    })
        
        compare_dicts(old_prefs, new_prefs)
        return changes
    
    def _get_preferences_version(self, preferences: Dict) -> str:
        """获取偏好设置版本"""
        # 简单的版本计算，基于内容哈希
        import hashlib
        content = json.dumps(preferences, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    async def get_default_preferences(self) -> Dict:
        """
        获取默认偏好设置
        
        Returns:
            默认偏好设置
        """
        return self._default_preferences.copy()
    
    async def reset_user_preferences(self, user_id: str) -> Dict:
        """
        重置用户偏好设置为默认值
        
        Args:
            user_id: 用户ID
        
        Returns:
            重置结果
        """
        try:
            default_preferences = self._get_default_preferences_for_user(user_id)
            return await self.update_user_preferences(user_id, default_preferences)
            
        except Exception as e:
            logger.error(f"重置用户偏好失败: 用户 {user_id}, 错误: {str(e)}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """
        获取服务状态
        
        Returns:
            服务状态信息
        """
        return {
            'service_name': 'SettingsService',
            'enabled': self.enabled,
            'initialized': self._initialized,
            'request_count': self._request_count,
            'error_count': self._error_count,
            'error_rate': self._error_count / max(self._request_count, 1),
            'max_concurrent_requests': self.max_concurrent_requests,
            'current_concurrent_requests': self.max_concurrent_requests - self._semaphore._value,
            'cached_users': len(self._user_preferences_cache),
            'cache_ttl': self.cache_ttl,
            'default_preferences_categories': list(self._default_preferences.keys()),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def cleanup(self):
        """清理服务资源"""
        try:
            # 清理缓存
            self._user_preferences_cache.clear()
            
            self._initialized = False
            logger.info("设置管理服务清理完成")
            
        except Exception as e:
            logger.error(f"设置管理服务清理失败: {str(e)}")
            raise 