"""
数据验证模块

提供音频文件、请求参数和数据模型的验证功能。
"""

import mimetypes
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import librosa
import numpy as np
import structlog
from pydantic import BaseModel, ValidationError, validator

from ..models.audio_models import AudioFormat, AudioMetadata
from ..models.tcm_models import ConstitutionType, EmotionState

logger = structlog.get_logger(__name__)


class ValidationError(Exception):
    """验证错误"""
    pass


class AudioFileValidator:
    """音频文件验证器"""
    
    # 支持的音频格式
    SUPPORTED_FORMATS = {
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.flac': 'audio/flac',
        '.ogg': 'audio/ogg',
        '.m4a': 'audio/mp4',
        '.aac': 'audio/aac'
    }
    
    # 文件大小限制（字节）
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    MIN_FILE_SIZE = 1024  # 1KB
    
    # 音频参数限制
    MAX_DURATION = 600  # 10分钟
    MIN_DURATION = 1    # 1秒
    MIN_SAMPLE_RATE = 8000   # 8kHz
    MAX_SAMPLE_RATE = 48000  # 48kHz

    @classmethod
    def validate_file_path(cls, file_path: Union[str, Path]) -> Path:
        """验证文件路径"""
        path = Path(file_path)
        
        if not path.exists():
            raise ValidationError(f"文件不存在: {file_path}")
        
        if not path.is_file():
            raise ValidationError(f"路径不是文件: {file_path}")
        
        return path

    @classmethod
    def validate_file_format(cls, file_path: Union[str, Path]) -> str:
        """验证文件格式"""
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix not in cls.SUPPORTED_FORMATS:
            raise ValidationError(
                f"不支持的音频格式: {suffix}. "
                f"支持的格式: {', '.join(cls.SUPPORTED_FORMATS.keys())}"
            )
        
        # 验证MIME类型
        mime_type, _ = mimetypes.guess_type(str(path))
        expected_mime = cls.SUPPORTED_FORMATS[suffix]
        
        if mime_type and not mime_type.startswith('audio/'):
            raise ValidationError(f"文件MIME类型不正确: {mime_type}")
        
        return suffix

    @classmethod
    def validate_file_size(cls, file_path: Union[str, Path]) -> int:
        """验证文件大小"""
        path = Path(file_path)
        size = path.stat().st_size
        
        if size < cls.MIN_FILE_SIZE:
            raise ValidationError(f"文件太小: {size} bytes (最小: {cls.MIN_FILE_SIZE} bytes)")
        
        if size > cls.MAX_FILE_SIZE:
            raise ValidationError(f"文件太大: {size} bytes (最大: {cls.MAX_FILE_SIZE} bytes)")
        
        return size

    @classmethod
    def validate_audio_content(cls, file_path: Union[str, Path]) -> Dict[str, Any]:
        """验证音频内容"""
        try:
            # 加载音频文件
            y, sr = librosa.load(str(file_path), sr=None)
            
            # 验证采样率
            if sr < cls.MIN_SAMPLE_RATE or sr > cls.MAX_SAMPLE_RATE:
                raise ValidationError(
                    f"采样率不在支持范围内: {sr}Hz "
                    f"(支持范围: {cls.MIN_SAMPLE_RATE}-{cls.MAX_SAMPLE_RATE}Hz)"
                )
            
            # 验证时长
            duration = len(y) / sr
            if duration < cls.MIN_DURATION:
                raise ValidationError(f"音频太短: {duration:.2f}s (最小: {cls.MIN_DURATION}s)")
            
            if duration > cls.MAX_DURATION:
                raise ValidationError(f"音频太长: {duration:.2f}s (最大: {cls.MAX_DURATION}s)")
            
            # 验证音频数据
            if len(y) == 0:
                raise ValidationError("音频文件为空")
            
            if np.all(y == 0):
                raise ValidationError("音频文件只包含静音")
            
            # 检查音频质量
            rms_energy = np.sqrt(np.mean(y**2))
            if rms_energy < 0.001:
                logger.warning("音频信号很弱", rms_energy=rms_energy)
            
            return {
                "duration": duration,
                "sample_rate": sr,
                "channels": 1 if y.ndim == 1 else y.shape[0],
                "samples": len(y),
                "rms_energy": rms_energy,
                "max_amplitude": np.max(np.abs(y)),
                "dynamic_range": np.max(y) - np.min(y)
            }
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"音频文件损坏或格式不正确: {str(e)}")

    @classmethod
    def validate_audio_file(cls, file_path: Union[str, Path]) -> Dict[str, Any]:
        """完整的音频文件验证"""
        path = cls.validate_file_path(file_path)
        format_ext = cls.validate_file_format(path)
        file_size = cls.validate_file_size(path)
        audio_info = cls.validate_audio_content(path)
        
        return {
            "path": str(path),
            "format": format_ext,
            "size": file_size,
            "audio_info": audio_info,
            "valid": True
        }


class RequestValidator:
    """请求参数验证器"""
    
    @staticmethod
    def validate_user_id(user_id: str) -> str:
        """验证用户ID"""
        if not user_id or not isinstance(user_id, str):
            raise ValidationError("用户ID不能为空")
        
        if len(user_id) < 3 or len(user_id) > 50:
            raise ValidationError("用户ID长度必须在3-50个字符之间")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
            raise ValidationError("用户ID只能包含字母、数字、下划线和连字符")
        
        return user_id

    @staticmethod
    def validate_session_id(session_id: str) -> str:
        """验证会话ID"""
        if not session_id or not isinstance(session_id, str):
            raise ValidationError("会话ID不能为空")
        
        if len(session_id) < 10 or len(session_id) > 100:
            raise ValidationError("会话ID长度必须在10-100个字符之间")
        
        return session_id

    @staticmethod
    def validate_analysis_type(analysis_type: str) -> str:
        """验证分析类型"""
        valid_types = ['basic', 'advanced', 'tcm', 'comprehensive']
        
        if analysis_type not in valid_types:
            raise ValidationError(f"无效的分析类型: {analysis_type}. 有效类型: {', '.join(valid_types)}")
        
        return analysis_type

    @staticmethod
    def validate_language(language: str) -> str:
        """验证语言代码"""
        valid_languages = ['zh-CN', 'zh-TW', 'en-US', 'ja-JP', 'ko-KR']
        
        if language not in valid_languages:
            raise ValidationError(f"不支持的语言: {language}. 支持的语言: {', '.join(valid_languages)}")
        
        return language

    @staticmethod
    def validate_constitution_type(constitution: str) -> ConstitutionType:
        """验证体质类型"""
        try:
            return ConstitutionType(constitution)
        except ValueError:
            valid_types = [c.value for c in ConstitutionType]
            raise ValidationError(f"无效的体质类型: {constitution}. 有效类型: {', '.join(valid_types)}")

    @staticmethod
    def validate_emotion_state(emotion: str) -> EmotionState:
        """验证情志状态"""
        try:
            return EmotionState(emotion)
        except ValueError:
            valid_states = [e.value for e in EmotionState]
            raise ValidationError(f"无效的情志状态: {emotion}. 有效状态: {', '.join(valid_states)}")


class DataModelValidator:
    """数据模型验证器"""
    
    @staticmethod
    def validate_audio_metadata(data: Dict[str, Any]) -> AudioMetadata:
        """验证音频元数据"""
        try:
            return AudioMetadata(**data)
        except ValidationError as e:
            raise ValidationError(f"音频元数据验证失败: {str(e)}")

    @staticmethod
    def validate_pydantic_model(model_class: type, data: Dict[str, Any]) -> BaseModel:
        """验证Pydantic模型"""
        try:
            return model_class(**data)
        except ValidationError as e:
            error_details = []
            for error in e.errors():
                field = '.'.join(str(loc) for loc in error['loc'])
                message = error['msg']
                error_details.append(f"{field}: {message}")
            
            raise ValidationError(f"数据验证失败: {'; '.join(error_details)}")

    @staticmethod
    def validate_json_schema(data: Any, schema: Dict[str, Any]) -> bool:
        """验证JSON Schema"""
        try:
            import jsonschema
            jsonschema.validate(data, schema)
            return True
        except ImportError:
            logger.warning("jsonschema库未安装，跳过schema验证")
            return True
        except Exception as e:
            raise ValidationError(f"JSON Schema验证失败: {str(e)}")


class BatchValidator:
    """批量验证器"""
    
    def __init__(self, max_batch_size: int = 10):
        self.max_batch_size = max_batch_size
        self.audio_validator = AudioFileValidator()
        self.request_validator = RequestValidator()

    def validate_batch_request(self, files: List[Union[str, Path]], 
                             user_id: str, session_id: str) -> Dict[str, Any]:
        """验证批量请求"""
        # 验证批量大小
        if len(files) > self.max_batch_size:
            raise ValidationError(f"批量大小超过限制: {len(files)} > {self.max_batch_size}")
        
        if len(files) == 0:
            raise ValidationError("批量请求不能为空")
        
        # 验证用户信息
        self.request_validator.validate_user_id(user_id)
        self.request_validator.validate_session_id(session_id)
        
        # 验证每个文件
        valid_files = []
        invalid_files = []
        
        for file_path in files:
            try:
                validation_result = self.audio_validator.validate_audio_file(file_path)
                valid_files.append(validation_result)
            except ValidationError as e:
                invalid_files.append({
                    "path": str(file_path),
                    "error": str(e),
                    "valid": False
                })
        
        return {
            "total_files": len(files),
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "valid_count": len(valid_files),
            "invalid_count": len(invalid_files),
            "success_rate": len(valid_files) / len(files) if files else 0
        }


class SecurityValidator:
    """安全验证器"""
    
    # 危险文件扩展名
    DANGEROUS_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
        '.jar', '.app', '.deb', '.pkg', '.dmg', '.iso', '.img'
    }
    
    # 最大路径长度
    MAX_PATH_LENGTH = 260
    
    @classmethod
    def validate_file_security(cls, file_path: Union[str, Path]) -> bool:
        """验证文件安全性"""
        path = Path(file_path)
        
        # 检查路径长度
        if len(str(path)) > cls.MAX_PATH_LENGTH:
            raise ValidationError(f"文件路径过长: {len(str(path))} > {cls.MAX_PATH_LENGTH}")
        
        # 检查危险扩展名
        if path.suffix.lower() in cls.DANGEROUS_EXTENSIONS:
            raise ValidationError(f"危险的文件扩展名: {path.suffix}")
        
        # 检查路径遍历攻击
        if '..' in str(path) or str(path).startswith('/'):
            raise ValidationError("检测到路径遍历攻击")
        
        # 检查隐藏文件
        if path.name.startswith('.') and path.name not in ['.wav', '.mp3']:
            logger.warning("上传隐藏文件", path=str(path))
        
        return True

    @classmethod
    def validate_request_security(cls, request_data: Dict[str, Any]) -> bool:
        """验证请求安全性"""
        # 检查SQL注入
        dangerous_patterns = [
            r"('|(\\')|(;)|(\\;)|(\\x27)|(\\x2D)|(\\x2d)",
            r"(\\x23)|(#)|(\\x2A)|(\*)|(\\x3D)|(=)",
            r"(union)|(select)|(insert)|(delete)|(update)|(drop)",
            r"(script)|(javascript)|(vbscript)|(onload)|(onerror)"
        ]
        
        for key, value in request_data.items():
            if isinstance(value, str):
                for pattern in dangerous_patterns:
                    if re.search(pattern, value.lower()):
                        raise ValidationError(f"检测到潜在的安全威胁: {key}")
        
        return True


# 验证装饰器
def validate_audio_file(func):
    """音频文件验证装饰器"""
    def wrapper(*args, **kwargs):
        # 查找文件路径参数
        file_path = None
        if args and isinstance(args[0], (str, Path)):
            file_path = args[0]
        elif 'file_path' in kwargs:
            file_path = kwargs['file_path']
        elif 'audio_file' in kwargs:
            file_path = kwargs['audio_file']
        
        if file_path:
            try:
                AudioFileValidator.validate_audio_file(file_path)
            except ValidationError as e:
                logger.error("音频文件验证失败", file_path=file_path, error=str(e))
                raise
        
        return func(*args, **kwargs)
    return wrapper


def validate_request_params(**validators):
    """请求参数验证装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for param_name, validator_func in validators.items():
                if param_name in kwargs:
                    try:
                        kwargs[param_name] = validator_func(kwargs[param_name])
                    except ValidationError as e:
                        logger.error("参数验证失败", param=param_name, error=str(e))
                        raise
            return func(*args, **kwargs)
        return wrapper
    return decorator


# 全局验证器实例
audio_validator = AudioFileValidator()
request_validator = RequestValidator()
data_validator = DataModelValidator()
security_validator = SecurityValidator()


def validate_comprehensive_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """综合请求验证"""
    # 安全验证
    security_validator.validate_request_security(request_data)
    
    # 基本参数验证
    if 'user_id' in request_data:
        request_validator.validate_user_id(request_data['user_id'])
    
    if 'session_id' in request_data:
        request_validator.validate_session_id(request_data['session_id'])
    
    if 'analysis_type' in request_data:
        request_validator.validate_analysis_type(request_data['analysis_type'])
    
    if 'language' in request_data:
        request_validator.validate_language(request_data['language'])
    
    # 文件验证
    if 'file_path' in request_data:
        audio_validator.validate_audio_file(request_data['file_path'])
    
    logger.info("请求验证通过", user_id=request_data.get('user_id'))
    return request_data