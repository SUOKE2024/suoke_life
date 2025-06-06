"""
localization - 索克生活项目模块
"""

from fastapi import Request
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, Optional
import json
import os

"""国际化支持模块

提供多语言支持和本地化功能
"""



class LocalizationManager:
    """本地化管理器"""
    
    def __init__(self, locales_dir: str = "locales", default_locale: str = "zh_CN"):
        self.locales_dir = Path(locales_dir)
        self.default_locale = default_locale
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.supported_locales = set()
        
        # 加载翻译文件
        self._load_translations()
    
    def _load_translations(self):
        """加载翻译文件"""
        if not self.locales_dir.exists():
            return
        
        for locale_file in self.locales_dir.glob("*.json"):
            locale = locale_file.stem
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self.translations[locale] = json.load(f)
                    self.supported_locales.add(locale)
            except Exception as e:
                print(f"Failed to load locale {locale}: {e}")
    
    def get_text(self, key: str, locale: str = None, **kwargs) -> str:
        """获取翻译文本"""
        locale = locale or self.default_locale
        
        # 如果指定的语言不存在，回退到默认语言
        if locale not in self.translations:
            locale = self.default_locale
        
        # 如果默认语言也不存在，返回键名
        if locale not in self.translations:
            return key
        
        # 获取翻译文本
        text = self._get_nested_value(self.translations[locale], key)
        if text is None:
            # 如果当前语言没有翻译，尝试默认语言
            if locale != self.default_locale:
                text = self._get_nested_value(self.translations.get(self.default_locale, {}), key)
            
            # 如果还是没有，返回键名
            if text is None:
                return key
        
        # 格式化文本
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        
        return text
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Optional[str]:
        """获取嵌套字典中的值"""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current if isinstance(current, str) else None
    
    def get_supported_locales(self) -> list[str]:
        """获取支持的语言列表"""
        return list(self.supported_locales)
    
    def detect_locale(self, request: Request) -> str:
        """从请求中检测语言"""
        # 1. 检查查询参数
        locale = request.query_params.get('lang')
        if locale and locale in self.supported_locales:
            return locale
        
        # 2. 检查请求头
        accept_language = request.headers.get('Accept-Language', '')
        for lang_range in accept_language.split(','):
            lang = lang_range.split(';')[0].strip()
            # 尝试完整匹配
            if lang in self.supported_locales:
                return lang
            # 尝试语言代码匹配（如 zh 匹配 zh_CN）
            for supported in self.supported_locales:
                if supported.startswith(lang.split('-')[0]):
                    return supported
        
        # 3. 返回默认语言
        return self.default_locale


# 全局本地化管理器实例
_localization_manager: Optional[LocalizationManager] = None


def init_localization(locales_dir: str = "locales", default_locale: str = "zh_CN") -> LocalizationManager:
    """初始化本地化管理器"""
    global _localization_manager
    _localization_manager = LocalizationManager(locales_dir, default_locale)
    return _localization_manager


def get_localization_manager() -> LocalizationManager:
    """获取本地化管理器"""
    global _localization_manager
    if _localization_manager is None:
        _localization_manager = LocalizationManager()
    return _localization_manager


def _(key: str, locale: str = None, **kwargs) -> str:
    """翻译函数的简写"""
    return get_localization_manager().get_text(key, locale, **kwargs)


def create_default_translations():
    """创建默认翻译文件"""
    
    # 中文翻译
    zh_cn = {
        "common": {
            "success": "成功",
            "error": "错误",
            "warning": "警告",
            "info": "信息",
            "loading": "加载中...",
            "save": "保存",
            "cancel": "取消",
            "confirm": "确认",
            "delete": "删除",
            "edit": "编辑",
            "create": "创建",
            "update": "更新"
        },
        "benchmark": {
            "title": "基准测试",
            "run": "运行测试",
            "result": "测试结果",
            "status": {
                "pending": "等待中",
                "running": "运行中",
                "completed": "已完成",
                "failed": "失败"
            },
            "metrics": {
                "accuracy": "准确率",
                "precision": "精确率",
                "recall": "召回率",
                "f1_score": "F1分数",
                "response_time": "响应时间",
                "throughput": "吞吐量"
            },
            "errors": {
                "not_found": "基准测试不存在",
                "execution_failed": "测试执行失败",
                "invalid_config": "配置无效"
            }
        },
        "model": {
            "title": "模型管理",
            "register": "注册模型",
            "unregister": "注销模型",
            "load": "加载模型",
            "predict": "预测",
            "errors": {
                "not_found": "模型不存在",
                "load_failed": "模型加载失败",
                "prediction_failed": "预测失败"
            }
        },
        "api": {
            "errors": {
                "unauthorized": "未授权访问",
                "forbidden": "禁止访问",
                "not_found": "资源不存在",
                "rate_limited": "请求频率超限",
                "internal_error": "内部服务器错误",
                "validation_error": "参数验证错误"
            }
        },
        "health": {
            "status": "服务状态",
            "healthy": "健康",
            "unhealthy": "不健康",
            "degraded": "降级"
        }
    }
    
    # 英文翻译
    en_us = {
        "common": {
            "success": "Success",
            "error": "Error",
            "warning": "Warning",
            "info": "Information",
            "loading": "Loading...",
            "save": "Save",
            "cancel": "Cancel",
            "confirm": "Confirm",
            "delete": "Delete",
            "edit": "Edit",
            "create": "Create",
            "update": "Update"
        },
        "benchmark": {
            "title": "Benchmark Testing",
            "run": "Run Test",
            "result": "Test Result",
            "status": {
                "pending": "Pending",
                "running": "Running",
                "completed": "Completed",
                "failed": "Failed"
            },
            "metrics": {
                "accuracy": "Accuracy",
                "precision": "Precision",
                "recall": "Recall",
                "f1_score": "F1 Score",
                "response_time": "Response Time",
                "throughput": "Throughput"
            },
            "errors": {
                "not_found": "Benchmark not found",
                "execution_failed": "Test execution failed",
                "invalid_config": "Invalid configuration"
            }
        },
        "model": {
            "title": "Model Management",
            "register": "Register Model",
            "unregister": "Unregister Model",
            "load": "Load Model",
            "predict": "Predict",
            "errors": {
                "not_found": "Model not found",
                "load_failed": "Model loading failed",
                "prediction_failed": "Prediction failed"
            }
        },
        "api": {
            "errors": {
                "unauthorized": "Unauthorized access",
                "forbidden": "Access forbidden",
                "not_found": "Resource not found",
                "rate_limited": "Rate limit exceeded",
                "internal_error": "Internal server error",
                "validation_error": "Validation error"
            }
        },
        "health": {
            "status": "Service Status",
            "healthy": "Healthy",
            "unhealthy": "Unhealthy",
            "degraded": "Degraded"
        }
    }
    
    return {
        "zh_CN": zh_cn,
        "en_US": en_us
    }


def setup_localization_files(locales_dir: str = "locales"):
    """设置本地化文件"""
    locales_path = Path(locales_dir)
    locales_path.mkdir(exist_ok=True)
    
    translations = create_default_translations()
    
    for locale, content in translations.items():
        locale_file = locales_path / f"{locale}.json"
        with open(locale_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    
    print(f"Created localization files in {locales_dir}/")


class LocalizedResponse:
    """本地化响应类"""
    
    def __init__(self, localization_manager: LocalizationManager):
        self.lm = localization_manager
    
    def success(self, message_key: str = "common.success", locale: str = None, **kwargs) -> Dict[str, Any]:
        """成功响应"""
        return {
            "success": True,
            "message": self.lm.get_text(message_key, locale, **kwargs),
            "data": kwargs.get("data")
        }
    
    def error(self, message_key: str = "common.error", locale: str = None, **kwargs) -> Dict[str, Any]:
        """错误响应"""
        return {
            "success": False,
            "error": {
                "message": self.lm.get_text(message_key, locale, **kwargs),
                "code": kwargs.get("code"),
                "details": kwargs.get("details")
            }
        }
    
    def benchmark_status(self, status: str, locale: str = None, **kwargs) -> str:
        """基准测试状态翻译"""
        return self.lm.get_text(f"benchmark.status.{status}", locale, **kwargs)
    
    def api_error(self, error_type: str, locale: str = None, **kwargs) -> Dict[str, Any]:
        """API错误响应"""
        return self.error(f"api.errors.{error_type}", locale, **kwargs)


def get_localized_response() -> LocalizedResponse:
    """获取本地化响应实例"""
    return LocalizedResponse(get_localization_manager()) 