"""
validator - 索克生活项目模块
"""

from dataclasses import dataclass
from typing import Any
import html
import json
import logging
import re

"""
请求验证器
提供输入验证和数据清理功能
"""


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """验证错误"""
    pass


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    error_message: str | None = None
    cleaned_data: dict[str, Any] | None = None


class RequestValidator:
    """请求验证器"""

    def __init__(self) -> None:
        """初始化请求验证器"""
        # 恶意内容模式
        self.malicious_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS
            r'javascript:',
            r'on\w+\s*=',  # 事件处理器
            r'eval\s*\(',
            r'exec\s*\(',
            r'system\s*\(',
            r'__import__',
            r'subprocess',
            r'os\.system',
        ]

        # SQL注入模式
        self.sql_injection_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+.*\s+set',
            r'--\s*$',
            r'/\*.*\*/',
            r';\s*drop',
            r';\s*delete',
        ]

        # 编译正则表达式
        self.malicious_regex = re.compile(
            '|'.join(self.malicious_patterns), re.IGNORECASE)
        self.sql_injection_regex = re.compile(
            '|'.join(self.sql_injection_patterns), re.IGNORECASE)

        # 最大长度限制
        self.max_lengths = {
            'message': 10000,
            'query': 5000,
            'topic': 1000,
            'content': 50000,
            'user_id': 100,
            'session_id': 100,
        }

    def validate_request(self, request_data: dict[str, Any]) -> ValidationResult:
        """验证请求数据"""
        try:
            # 基本结构验证
            if not isinstance(request_data, dict):
                return ValidationResult(
                    is_valid=False,
                    error_message="请求数据必须是字典格式"
                )

            # 清理数据
            cleaned_data = self._clean_data(request_data)

            # 验证必需字段
            validation_result = self._validate_required_fields(cleaned_data)
            if not validation_result.is_valid:
                return validation_result

            # 验证字段类型和格式
            validation_result = self._validate_field_types(cleaned_data)
            if not validation_result.is_valid:
                return validation_result

            # 验证字段长度
            validation_result = self._validate_field_lengths(cleaned_data)
            if not validation_result.is_valid:
                return validation_result

            # 安全检查
            validation_result = self._security_check(cleaned_data)
            if not validation_result.is_valid:
                return validation_result

            return ValidationResult(
                is_valid=True,
                cleaned_data=cleaned_data
            )

        except Exception as e:
            logger.error(f"请求验证异常: {str(e)}")
            return ValidationResult(
                is_valid=False,
                error_message=f"验证过程中发生错误: {str(e)}"
            )

    def _clean_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """清理数据"""
        cleaned = {}

        for key, value in data.items():
            if isinstance(value, str):
                # HTML转义
                cleaned_value = html.escape(value.strip())
                # 移除控制字符
                cleaned_value = re.sub(
                    r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned_value)
                cleaned[key] = cleaned_value
            elif isinstance(value, dict):
                cleaned[key] = self._clean_data(value)
            elif isinstance(value, list):
                cleaned[key] = [self._clean_item(item) for item in value]
            else:
                cleaned[key] = value

        return cleaned

    def _clean_item(self, item: Any) -> Any:
        """清理单个项目"""
        if isinstance(item, str):
            cleaned = html.escape(item.strip())
            return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
        elif isinstance(item, dict):
            return self._clean_data(item)
        else:
            return item

    def _validate_required_fields(self, data: dict[str, Any]) -> ValidationResult:
        """验证必需字段"""
        request_type = data.get('type', 'general_inquiry')

        # 根据请求类型检查必需字段
        if request_type=='knowledge_query':
            if not data.get('query'):
                return ValidationResult(
                    is_valid=False,
                    error_message="知识查询请求必须包含query字段"
                )
        elif request_type=='content_creation':
            if not data.get('topic'):
                return ValidationResult(
                    is_valid=False,
                    error_message="内容创建请求必须包含topic字段"
                )
        elif request_type=='community_management':
            if not data.get('action'):
                return ValidationResult(
                    is_valid=False,
                    error_message="社区管理请求必须包含action字段"
                )
        elif request_type=='learning_path':
            if not data.get('user_level'):
                return ValidationResult(
                    is_valid=False,
                    error_message="学习路径请求必须包含user_level字段"
                )
        elif request_type=='general_inquiry':
            if not data.get('message'):
                return ValidationResult(
                    is_valid=False,
                    error_message="一般询问请求必须包含message字段"
                )

        return ValidationResult(is_valid=True)

    def _validate_field_types(self, data: dict[str, Any]) -> ValidationResult:
        """验证字段类型"""
        # 字符串字段
        string_fields = [
            'type',
            'query',
            'message',
            'topic',
            'content',
            'action',
            'user_level']
        for field in string_fields:
            if field in data and not isinstance(data[field], str):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"字段 {field} 必须是字符串类型"
                )

        # 列表字段
        list_fields = ['interests', 'goals']
        for field in list_fields:
            if field in data and not isinstance(data[field], list):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"字段 {field} 必须是列表类型"
                )

        # 验证枚举值
        if 'type' in data:
            valid_types = [
                'knowledge_query',
                'content_creation',
                'community_management',
                'learning_path',
                'general_inquiry']
            if data['type'] not in valid_types:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"无效的请求类型: {data['type']}"
                )

        if 'content_type' in data:
            valid_content_types = [
                'article',
                'video_script',
                'course',
                'tutorial',
                'guide']
            if data['content_type'] not in valid_content_types:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"无效的内容类型: {data['content_type']}"
                )

        if 'target_audience' in data:
            valid_audiences = ['beginner', 'intermediate', 'advanced', 'expert']
            if data['target_audience'] not in valid_audiences:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"无效的目标受众: {data['target_audience']}"
                )

        if 'user_level' in data:
            valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
            if data['user_level'] not in valid_levels:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"无效的用户水平: {data['user_level']}"
                )

        if 'action' in data:
            valid_actions = [
                'moderate_content',
                'generate_discussion',
                'answer_question',
                'manage_community']
            if data['action'] not in valid_actions:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"无效的社区操作: {data['action']}"
                )

        return ValidationResult(is_valid=True)

    def _validate_field_lengths(self, data: dict[str, Any]) -> ValidationResult:
        """验证字段长度"""
        for field, value in data.items():
            if isinstance(value, str) and field in self.max_lengths:
                max_length = self.max_lengths[field]
                if len(value) > max_length:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"字段 {field} 长度超过限制 ({len(value)} > {max_length})"
                    )
            elif isinstance(value, list):
                # 验证列表长度
                if len(value) > 50:  # 最多50个元素
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"字段 {field} 列表元素过多 ({len(value)} > 50)"
                    )

                # 验证列表元素长度
                for item in value:
                    if isinstance(item, str) and len(item) > 500:
                        return ValidationResult(
                            is_valid=False,
                            error_message=f"字段 {field} 中的元素长度过长"
                        )

        return ValidationResult(is_valid=True)

    def _security_check(self, data: dict[str, Any]) -> ValidationResult:
        """安全检查"""
        # 检查所有字符串字段
        for key, value in data.items():
            if isinstance(value, str):
                # 检查恶意内容
                if self.malicious_regex.search(value):
                    logger.warning(f"检测到恶意内容: {key}")
                    return ValidationResult(
                        is_valid=False,
                        error_message="检测到潜在的恶意内容"
                    )

                # 检查SQL注入
                if self.sql_injection_regex.search(value):
                    logger.warning(f"检测到SQL注入尝试: {key}")
                    return ValidationResult(
                        is_valid=False,
                        error_message="检测到潜在的SQL注入尝试"
                    )

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        if self.malicious_regex.search(
                                item) or self.sql_injection_regex.search(item):
                            logger.warning(f"检测到恶意内容: {key}")
                            return ValidationResult(
                                is_valid=False,
                                error_message="检测到潜在的恶意内容"
                            )

        return ValidationResult(is_valid=True)

    def validate_user_id(self, user_id: str) -> ValidationResult:
        """验证用户ID"""
        if not user_id:
            return ValidationResult(
                is_valid=False,
                error_message="用户ID不能为空"
            )

        if not isinstance(user_id, str):
            return ValidationResult(
                is_valid=False,
                error_message="用户ID必须是字符串"
            )

        if len(user_id) > 100:
            return ValidationResult(
                is_valid=False,
                error_message="用户ID长度不能超过100字符"
            )

        # 检查格式（只允许字母、数字、下划线、连字符）
        if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
            return ValidationResult(
                is_valid=False,
                error_message="用户ID格式无效"
            )

        return ValidationResult(is_valid=True)

    def validate_session_id(self, session_id: str) -> ValidationResult:
        """验证会话ID"""
        if not session_id:
            return ValidationResult(
                is_valid=False,
                error_message="会话ID不能为空"
            )

        if not isinstance(session_id, str):
            return ValidationResult(
                is_valid=False,
                error_message="会话ID必须是字符串"
            )

        if len(session_id) > 100:
            return ValidationResult(
                is_valid=False,
                error_message="会话ID长度不能超过100字符"
            )

        # 检查UUID格式
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, session_id, re.IGNORECASE):
            return ValidationResult(
                is_valid=False,
                error_message="会话ID格式无效"
            )

        return ValidationResult(is_valid=True)

    def sanitize_text(self, text: str) -> str:
        """清理文本内容"""
        if not isinstance(text, str):
            return str(text)

        # HTML转义
        sanitized = html.escape(text.strip())

        # 移除控制字符
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)

        # 移除多余的空白字符
        sanitized = re.sub(r'\s+', ' ', sanitized)

        return sanitized

    def validate_json(self, json_str: str) -> ValidationResult:
        """验证JSON格式"""
        try:
            data = json.loads(json_str)
            return ValidationResult(
                is_valid=True,
                cleaned_data=data
            )
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"JSON格式错误: {str(e)}"
            )

    def validate_email(self, email: str) -> ValidationResult:
        """验证邮箱格式"""
        if not email:
            return ValidationResult(
                is_valid=False,
                error_message="邮箱不能为空"
            )

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return ValidationResult(
                is_valid=False,
                error_message="邮箱格式无效"
            )

        return ValidationResult(is_valid=True)

    def validate_url(self, url: str) -> ValidationResult:
        """验证URL格式"""
        if not url:
            return ValidationResult(
                is_valid=False,
                error_message="URL不能为空"
            )

        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, url, re.IGNORECASE):
            return ValidationResult(
                is_valid=False,
                error_message="URL格式无效"
            )

        return ValidationResult(is_valid=True)

    def add_malicious_pattern(self, pattern: str) -> None:
        """添加恶意内容模式"""
        self.malicious_patterns.append(pattern)
        self.malicious_regex = re.compile(
            '|'.join(self.malicious_patterns), re.IGNORECASE)
        logger.info(f"添加恶意内容模式: {pattern}")

    def add_sql_injection_pattern(self, pattern: str) -> None:
        """添加SQL注入模式"""
        self.sql_injection_patterns.append(pattern)
        self.sql_injection_regex = re.compile(
            '|'.join(self.sql_injection_patterns), re.IGNORECASE)
        logger.info(f"添加SQL注入模式: {pattern}")

    def set_max_length(self, field: str, max_length: int) -> None:
        """设置字段最大长度"""
        self.max_lengths[field] = max_length
        logger.info(f"设置字段 {field} 最大长度: {max_length}")


# 全局验证器实例
_validator: RequestValidator | None = None


def get_validator() -> RequestValidator:
    """获取全局验证器实例"""
    global _validator
    if _validator is None:
        _validator = RequestValidator()
    return _validator
