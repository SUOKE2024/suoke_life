#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生物识别认证服务

支持指纹、面部识别等生物识别认证方式。
"""
import asyncio
import base64
import hashlib
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

import httpx
from fastapi import HTTPException, status
from PIL import Image
import io

from internal.config.settings import get_settings
from internal.model.user import User
from internal.repository.user_repository import UserRepository
from internal.repository.biometric_repository import BiometricRepository
from internal.security.jwt_manager import JWTManager
from internal.cache.redis_cache import get_redis_cache
from internal.exceptions import (
    AuthenticationError,
    ValidationError,
    BiometricError
)


class BiometricAuthService:
    """生物识别认证服务"""
    
    def __init__(self, dependencies=None):
        if dependencies:
            self.settings = dependencies.settings
            self.jwt_manager = dependencies.jwt_manager
            self.cache = dependencies.cache
            self.db_manager = dependencies.db_manager
        else:
            # 向后兼容的构造函数
            self.settings = get_settings()
            from internal.security.jwt_manager import JWTManager
            self.jwt_manager = JWTManager()
            self.cache = get_redis_cache()
            from internal.database.connection_manager import get_connection_manager
            self.db_manager = get_connection_manager()
        
        # 生物识别配置
        self.biometric_config = {
            'fingerprint': {
                'enabled': True,
                'max_templates': 5,
                'similarity_threshold': 0.85,
                'template_size_limit': 1024 * 10  # 10KB
            },
            'face': {
                'enabled': True,
                'max_templates': 3,
                'similarity_threshold': 0.90,
                'image_size_limit': 1024 * 1024 * 2,  # 2MB
                'supported_formats': ['jpg', 'jpeg', 'png']
            },
            'voice': {
                'enabled': False,  # 暂未实现
                'max_templates': 3,
                'similarity_threshold': 0.88
            }
        }
    
    async def register_fingerprint(
        self,
        user_id: int,
        fingerprint_template: str,
        finger_position: str = "unknown"
    ) -> Dict[str, Any]:
        """注册指纹模板"""
        # 验证用户存在
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValidationError("用户不存在")
        
        # 验证指纹模板格式
        try:
            template_data = base64.b64decode(fingerprint_template)
            if len(template_data) > self.biometric_config['fingerprint']['template_size_limit']:
                raise ValidationError("指纹模板大小超出限制")
        except Exception:
            raise ValidationError("无效的指纹模板格式")
        
        # 检查用户已注册的指纹数量
        existing_fingerprints = await self.biometric_repo.get_user_biometrics(
            user_id, 'fingerprint'
        )
        
        max_templates = self.biometric_config['fingerprint']['max_templates']
        if len(existing_fingerprints) >= max_templates:
            raise ValidationError(f"最多只能注册{max_templates}个指纹")
        
        # 生成指纹哈希用于快速比较
        template_hash = hashlib.sha256(template_data).hexdigest()
        
        # 检查是否已存在相同指纹
        for existing in existing_fingerprints:
            if existing.template_hash == template_hash:
                raise ValidationError("该指纹已注册")
        
        # 保存指纹模板
        biometric_data = {
            'user_id': user_id,
            'biometric_type': 'fingerprint',
            'template_data': fingerprint_template,
            'template_hash': template_hash,
            'metadata': {
                'finger_position': finger_position,
                'registered_at': datetime.utcnow().isoformat(),
                'device_info': None  # 可以从请求中获取
            }
        }
        
        biometric_record = await self.biometric_repo.create(biometric_data)
        
        return {
            'biometric_id': biometric_record.id,
            'type': 'fingerprint',
            'finger_position': finger_position,
            'registered_at': biometric_record.created_at.isoformat(),
            'message': '指纹注册成功'
        }
    
    async def verify_fingerprint(
        self,
        user_id: int,
        fingerprint_template: str
    ) -> Dict[str, Any]:
        """验证指纹"""
        # 验证指纹模板格式
        try:
            template_data = base64.b64decode(fingerprint_template)
        except Exception:
            raise ValidationError("无效的指纹模板格式")
        
        # 获取用户的指纹模板
        user_fingerprints = await self.biometric_repo.get_user_biometrics(
            user_id, 'fingerprint'
        )
        
        if not user_fingerprints:
            raise AuthenticationError("用户未注册指纹")
        
        # 计算输入指纹的哈希
        input_hash = hashlib.sha256(template_data).hexdigest()
        
        # 简单的哈希比较（实际应用中需要使用专业的指纹匹配算法）
        for fingerprint in user_fingerprints:
            if fingerprint.template_hash == input_hash:
                # 记录验证成功
                await self._record_biometric_verification(
                    user_id, fingerprint.id, True
                )
                
                return {
                    'verified': True,
                    'biometric_id': fingerprint.id,
                    'finger_position': fingerprint.metadata.get('finger_position'),
                    'message': '指纹验证成功'
                }
        
        # 记录验证失败
        await self._record_biometric_verification(user_id, None, False)
        
        raise AuthenticationError("指纹验证失败")
    
    async def register_face(
        self,
        user_id: int,
        face_image: str,
        image_format: str = "jpg"
    ) -> Dict[str, Any]:
        """注册面部识别"""
        # 验证用户存在
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValidationError("用户不存在")
        
        # 验证图片格式
        if image_format.lower() not in self.biometric_config['face']['supported_formats']:
            raise ValidationError(f"不支持的图片格式: {image_format}")
        
        # 验证图片数据
        try:
            image_data = base64.b64decode(face_image)
            if len(image_data) > self.biometric_config['face']['image_size_limit']:
                raise ValidationError("图片大小超出限制")
            
            # 验证图片可以正常解析
            image = Image.open(io.BytesIO(image_data))
            image.verify()
            
        except Exception as e:
            raise ValidationError(f"无效的图片数据: {str(e)}")
        
        # 检查用户已注册的面部模板数量
        existing_faces = await self.biometric_repo.get_user_biometrics(
            user_id, 'face'
        )
        
        max_templates = self.biometric_config['face']['max_templates']
        if len(existing_faces) >= max_templates:
            raise ValidationError(f"最多只能注册{max_templates}个面部模板")
        
        # 提取面部特征（这里使用简单的哈希，实际应用需要使用专业的面部识别算法）
        face_features = await self._extract_face_features(image_data)
        feature_hash = hashlib.sha256(json.dumps(face_features, sort_keys=True).encode()).hexdigest()
        
        # 检查是否已存在相似面部
        for existing in existing_faces:
            if existing.template_hash == feature_hash:
                raise ValidationError("相似的面部模板已存在")
        
        # 保存面部模板
        biometric_data = {
            'user_id': user_id,
            'biometric_type': 'face',
            'template_data': face_image,
            'template_hash': feature_hash,
            'metadata': {
                'image_format': image_format,
                'features': face_features,
                'registered_at': datetime.utcnow().isoformat()
            }
        }
        
        biometric_record = await self.biometric_repo.create(biometric_data)
        
        return {
            'biometric_id': biometric_record.id,
            'type': 'face',
            'registered_at': biometric_record.created_at.isoformat(),
            'message': '面部识别注册成功'
        }
    
    async def verify_face(
        self,
        user_id: int,
        face_image: str,
        image_format: str = "jpg"
    ) -> Dict[str, Any]:
        """验证面部识别"""
        # 验证图片数据
        try:
            image_data = base64.b64decode(face_image)
            image = Image.open(io.BytesIO(image_data))
            image.verify()
        except Exception:
            raise ValidationError("无效的图片数据")
        
        # 获取用户的面部模板
        user_faces = await self.biometric_repo.get_user_biometrics(
            user_id, 'face'
        )
        
        if not user_faces:
            raise AuthenticationError("用户未注册面部识别")
        
        # 提取面部特征
        input_features = await self._extract_face_features(image_data)
        
        # 与已注册的面部模板进行比较
        for face_template in user_faces:
            stored_features = face_template.metadata.get('features', {})
            similarity = self._calculate_face_similarity(input_features, stored_features)
            
            threshold = self.biometric_config['face']['similarity_threshold']
            if similarity >= threshold:
                # 记录验证成功
                await self._record_biometric_verification(
                    user_id, face_template.id, True
                )
                
                return {
                    'verified': True,
                    'biometric_id': face_template.id,
                    'similarity': similarity,
                    'message': '面部识别验证成功'
                }
        
        # 记录验证失败
        await self._record_biometric_verification(user_id, None, False)
        
        raise AuthenticationError("面部识别验证失败")
    
    async def _extract_face_features(self, image_data: bytes) -> Dict[str, Any]:
        """提取面部特征（简化版本）"""
        # 这里是一个简化的实现，实际应用中需要使用专业的面部识别库
        # 如 face_recognition、OpenCV、或云服务API
        
        image = Image.open(io.BytesIO(image_data))
        
        # 简单的特征提取（实际应该使用深度学习模型）
        features = {
            'width': image.width,
            'height': image.height,
            'format': image.format,
            'mode': image.mode,
            # 这里应该是真实的面部特征向量
            'feature_vector': list(range(128))  # 模拟128维特征向量
        }
        
        return features
    
    def _calculate_face_similarity(
        self, 
        features1: Dict[str, Any], 
        features2: Dict[str, Any]
    ) -> float:
        """计算面部相似度（简化版本）"""
        # 这里是一个简化的实现，实际应该使用专业的相似度计算算法
        
        # 简单的特征比较
        if (features1.get('width') == features2.get('width') and 
            features1.get('height') == features2.get('height')):
            return 0.95  # 模拟高相似度
        else:
            return 0.60  # 模拟低相似度
    
    async def _record_biometric_verification(
        self,
        user_id: int,
        biometric_id: Optional[int],
        success: bool
    ):
        """记录生物识别验证结果"""
        verification_data = {
            'user_id': user_id,
            'biometric_id': biometric_id,
            'success': success,
            'verified_at': datetime.utcnow(),
            'ip_address': None,  # 可以从请求中获取
            'user_agent': None   # 可以从请求中获取
        }
        
        # 缓存验证记录
        cache_key = f"biometric_verification:{user_id}:{int(datetime.utcnow().timestamp())}"
        await self.cache.set(
            cache_key,
            json.dumps(verification_data, default=str),
            expire=86400  # 24小时
        )
    
    async def get_user_biometrics(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户的生物识别信息"""
        biometrics = await self.biometric_repo.get_user_biometrics(user_id)
        
        return [
            {
                'id': bio.id,
                'type': bio.biometric_type,
                'registered_at': bio.created_at.isoformat(),
                'metadata': {
                    k: v for k, v in bio.metadata.items() 
                    if k not in ['template_data', 'features']  # 不返回敏感数据
                }
            }
            for bio in biometrics
        ]
    
    async def delete_biometric(
        self,
        user_id: int,
        biometric_id: int
    ) -> bool:
        """删除生物识别模板"""
        biometric = await self.biometric_repo.get_by_id(biometric_id)
        
        if not biometric or biometric.user_id != user_id:
            raise ValidationError("生物识别模板不存在或无权限")
        
        await self.biometric_repo.delete(biometric_id)
        return True
    
    async def biometric_login(
        self,
        username: str,
        biometric_type: str,
        biometric_data: str
    ) -> Dict[str, Any]:
        """生物识别登录"""
        # 获取用户
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise AuthenticationError("用户不存在")
        
        # 根据生物识别类型进行验证
        if biometric_type == 'fingerprint':
            verification_result = await self.verify_fingerprint(
                user.id, biometric_data
            )
        elif biometric_type == 'face':
            verification_result = await self.verify_face(
                user.id, biometric_data
            )
        else:
            raise ValidationError(f"不支持的生物识别类型: {biometric_type}")
        
        if verification_result['verified']:
            # 生成JWT令牌
            tokens = await self.jwt_manager.create_tokens(user)
            
            return {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'tokens': tokens,
                'biometric_type': biometric_type,
                'verification_result': verification_result
            }
        else:
            raise AuthenticationError("生物识别验证失败")


# 依赖注入函数
async def get_biometric_auth_service(
    user_repo: UserRepository = None,
    biometric_repo: BiometricRepository = None,
    jwt_manager: JWTManager = None
) -> BiometricAuthService:
    """获取生物识别认证服务实例"""
    if not user_repo:
        from internal.repository.user_repository import get_user_repository
        user_repo = await get_user_repository()
    
    if not biometric_repo:
        from internal.repository.biometric_repository import get_biometric_repository
        biometric_repo = await get_biometric_repository()
    
    if not jwt_manager:
        from internal.security.jwt_manager import get_jwt_manager
        jwt_manager = get_jwt_manager()
    
    return BiometricAuthService(user_repo, biometric_repo, jwt_manager) 