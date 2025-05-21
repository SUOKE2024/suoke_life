#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
国际化支持模块

提供多语言支持功能，包括错误消息、提示和系统消息的翻译
支持中文、英文等多种语言
"""
from enum import Enum
from typing import Dict, List, Optional

# 支持的语言列表
class Language(str, Enum):
    """支持的语言枚举"""
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"
    ENGLISH = "en-US"
    JAPANESE = "ja-JP"
    KOREAN = "ko-KR"


# 默认语言
DEFAULT_LANGUAGE = Language.CHINESE_SIMPLIFIED


class LocalizedMessage:
    """本地化消息类
    
    用于存储和检索各种语言的消息文本
    """
    
    def __init__(self, key: str, translations: Dict[Language, str]):
        """
        初始化本地化消息
        
        Args:
            key: 消息唯一标识
            translations: 各语言的翻译映射
        """
        self.key = key
        self.translations = translations
    
    def get(self, language: Optional[Language] = None) -> str:
        """
        获取指定语言的消息文本
        
        Args:
            language: 目标语言，如果不指定则使用默认语言
            
        Returns:
            本地化后的消息文本
        """
        if language is None:
            language = DEFAULT_LANGUAGE
        
        # 如果请求的语言不可用，则回退到默认语言
        if language not in self.translations:
            language = DEFAULT_LANGUAGE
        
        return self.translations[language]


# 定义错误消息
class ErrorMessages:
    """错误消息集合"""
    
    # 通用错误
    INTERNAL_SERVER_ERROR = LocalizedMessage(
        "internal_server_error",
        {
            Language.CHINESE_SIMPLIFIED: "服务器内部错误，请稍后再试",
            Language.CHINESE_TRADITIONAL: "伺服器內部錯誤，請稍後再試",
            Language.ENGLISH: "Internal server error, please try again later",
            Language.JAPANESE: "サーバー内部エラーが発生しました。後でもう一度お試しください",
            Language.KOREAN: "서버 내부 오류, 나중에 다시 시도하십시오"
        }
    )
    
    INVALID_REQUEST = LocalizedMessage(
        "invalid_request",
        {
            Language.CHINESE_SIMPLIFIED: "无效的请求参数",
            Language.CHINESE_TRADITIONAL: "無效的請求參數",
            Language.ENGLISH: "Invalid request parameters",
            Language.JAPANESE: "無効なリクエストパラメータ",
            Language.KOREAN: "잘못된 요청 매개변수"
        }
    )
    
    RESOURCE_NOT_FOUND = LocalizedMessage(
        "resource_not_found",
        {
            Language.CHINESE_SIMPLIFIED: "请求的资源不存在",
            Language.CHINESE_TRADITIONAL: "請求的資源不存在",
            Language.ENGLISH: "The requested resource doesn't exist",
            Language.JAPANESE: "要求されたリソースは存在しません",
            Language.KOREAN: "요청한 리소스가 존재하지 않습니다"
        }
    )
    
    # 认证错误
    INVALID_CREDENTIALS = LocalizedMessage(
        "invalid_credentials",
        {
            Language.CHINESE_SIMPLIFIED: "用户名或密码错误",
            Language.CHINESE_TRADITIONAL: "用戶名或密碼錯誤",
            Language.ENGLISH: "Incorrect username or password",
            Language.JAPANESE: "ユーザー名またはパスワードが正しくありません",
            Language.KOREAN: "사용자 이름 또는 비밀번호가 잘못되었습니다"
        }
    )
    
    ACCOUNT_LOCKED = LocalizedMessage(
        "account_locked",
        {
            Language.CHINESE_SIMPLIFIED: "账户已锁定，请联系管理员或稍后重试",
            Language.CHINESE_TRADITIONAL: "賬戶已鎖定，請聯繫管理員或稍後重試",
            Language.ENGLISH: "Account locked, please contact admin or try again later",
            Language.JAPANESE: "アカウントがロックされています。管理者に連絡するか、後でもう一度お試しください",
            Language.KOREAN: "계정이 잠겼습니다. 관리자에게 문의하거나 나중에 다시 시도하십시오"
        }
    )
    
    SESSION_EXPIRED = LocalizedMessage(
        "session_expired",
        {
            Language.CHINESE_SIMPLIFIED: "会话已过期，请重新登录",
            Language.CHINESE_TRADITIONAL: "會話已過期，請重新登錄",
            Language.ENGLISH: "Session expired, please log in again",
            Language.JAPANESE: "セッションの有効期限が切れました。再度ログインしてください",
            Language.KOREAN: "세션이 만료되었습니다. 다시 로그인하십시오"
        }
    )
    
    INVALID_TOKEN = LocalizedMessage(
        "invalid_token",
        {
            Language.CHINESE_SIMPLIFIED: "无效的访问令牌",
            Language.CHINESE_TRADITIONAL: "無效的訪問令牌",
            Language.ENGLISH: "Invalid access token",
            Language.JAPANESE: "無効なアクセストークン",
            Language.KOREAN: "잘못된 액세스 토큰"
        }
    )
    
    TOKEN_EXPIRED = LocalizedMessage(
        "token_expired",
        {
            Language.CHINESE_SIMPLIFIED: "访问令牌已过期",
            Language.CHINESE_TRADITIONAL: "訪問令牌已過期",
            Language.ENGLISH: "Access token has expired",
            Language.JAPANESE: "アクセストークンの有効期限が切れています",
            Language.KOREAN: "액세스 토큰이 만료되었습니다"
        }
    )
    
    TOKEN_REVOKED = LocalizedMessage(
        "token_revoked",
        {
            Language.CHINESE_SIMPLIFIED: "访问令牌已被撤销",
            Language.CHINESE_TRADITIONAL: "訪問令牌已被撤銷",
            Language.ENGLISH: "Access token has been revoked",
            Language.JAPANESE: "アクセストークンが取り消されました",
            Language.KOREAN: "액세스 토큰이 취소되었습니다"
        }
    )
    
    INSUFFICIENT_PERMISSIONS = LocalizedMessage(
        "insufficient_permissions",
        {
            Language.CHINESE_SIMPLIFIED: "权限不足，无法执行请求的操作",
            Language.CHINESE_TRADITIONAL: "權限不足，無法執行請求的操作",
            Language.ENGLISH: "Insufficient permissions to perform the requested operation",
            Language.JAPANESE: "要求された操作を実行するための権限が不足しています",
            Language.KOREAN: "요청된 작업을 수행할 권한이 부족합니다"
        }
    )
    
    # 用户相关错误
    USER_ALREADY_EXISTS = LocalizedMessage(
        "user_already_exists",
        {
            Language.CHINESE_SIMPLIFIED: "用户已存在",
            Language.CHINESE_TRADITIONAL: "用戶已存在",
            Language.ENGLISH: "User already exists",
            Language.JAPANESE: "ユーザーはすでに存在します",
            Language.KOREAN: "사용자가 이미 존재합니다"
        }
    )
    
    EMAIL_ALREADY_REGISTERED = LocalizedMessage(
        "email_already_registered",
        {
            Language.CHINESE_SIMPLIFIED: "邮箱已被注册",
            Language.CHINESE_TRADITIONAL: "郵箱已被註冊",
            Language.ENGLISH: "Email is already registered",
            Language.JAPANESE: "メールアドレスはすでに登録されています",
            Language.KOREAN: "이메일이 이미 등록되어 있습니다"
        }
    )
    
    INVALID_EMAIL_FORMAT = LocalizedMessage(
        "invalid_email_format",
        {
            Language.CHINESE_SIMPLIFIED: "邮箱格式不正确",
            Language.CHINESE_TRADITIONAL: "郵箱格式不正確",
            Language.ENGLISH: "Invalid email format",
            Language.JAPANESE: "無効なメールフォーマット",
            Language.KOREAN: "잘못된 이메일 형식"
        }
    )
    
    USER_NOT_FOUND = LocalizedMessage(
        "user_not_found",
        {
            Language.CHINESE_SIMPLIFIED: "用户不存在",
            Language.CHINESE_TRADITIONAL: "用戶不存在",
            Language.ENGLISH: "User not found",
            Language.JAPANESE: "ユーザーが見つかりません",
            Language.KOREAN: "사용자를 찾을 수 없습니다"
        }
    )
    
    # 密码相关错误
    PASSWORD_TOO_WEAK = LocalizedMessage(
        "password_too_weak",
        {
            Language.CHINESE_SIMPLIFIED: "密码强度不足，请包含大小写字母、数字和特殊字符",
            Language.CHINESE_TRADITIONAL: "密碼強度不足，請包含大小寫字母、數字和特殊字符",
            Language.ENGLISH: "Password is too weak, please include uppercase and lowercase letters, numbers, and special characters",
            Language.JAPANESE: "パスワードが弱すぎます。大文字、小文字、数字、特殊文字を含めてください",
            Language.KOREAN: "비밀번호가 너무 약합니다. 대문자, 소문자, 숫자 및 특수 문자를 포함하십시오"
        }
    )
    
    PASSWORD_MISMATCH = LocalizedMessage(
        "password_mismatch",
        {
            Language.CHINESE_SIMPLIFIED: "两次输入的密码不匹配",
            Language.CHINESE_TRADITIONAL: "兩次輸入的密碼不匹配",
            Language.ENGLISH: "Passwords do not match",
            Language.JAPANESE: "パスワードが一致しません",
            Language.KOREAN: "비밀번호가 일치하지 않습니다"
        }
    )
    
    CURRENT_PASSWORD_INCORRECT = LocalizedMessage(
        "current_password_incorrect",
        {
            Language.CHINESE_SIMPLIFIED: "当前密码不正确",
            Language.CHINESE_TRADITIONAL: "當前密碼不正確",
            Language.ENGLISH: "Current password is incorrect",
            Language.JAPANESE: "現在のパスワードが正しくありません",
            Language.KOREAN: "현재 비밀번호가 올바르지 않습니다"
        }
    )
    
    # 多因素认证错误
    MFA_CODE_INVALID = LocalizedMessage(
        "mfa_code_invalid",
        {
            Language.CHINESE_SIMPLIFIED: "多因素认证码无效",
            Language.CHINESE_TRADITIONAL: "多因素認證碼無效",
            Language.ENGLISH: "Invalid multi-factor authentication code",
            Language.JAPANESE: "多要素認証コードが無効です",
            Language.KOREAN: "잘못된 다중 인증 코드"
        }
    )
    
    MFA_CODE_EXPIRED = LocalizedMessage(
        "mfa_code_expired",
        {
            Language.CHINESE_SIMPLIFIED: "多因素认证码已过期",
            Language.CHINESE_TRADITIONAL: "多因素認證碼已過期",
            Language.ENGLISH: "Multi-factor authentication code has expired",
            Language.JAPANESE: "多要素認証コードの有効期限が切れています",
            Language.KOREAN: "다중 인증 코드가 만료되었습니다"
        }
    )
    
    MFA_ALREADY_ENABLED = LocalizedMessage(
        "mfa_already_enabled",
        {
            Language.CHINESE_SIMPLIFIED: "多因素认证已启用",
            Language.CHINESE_TRADITIONAL: "多因素認證已啟用",
            Language.ENGLISH: "Multi-factor authentication is already enabled",
            Language.JAPANESE: "多要素認証はすでに有効になっています",
            Language.KOREAN: "다중 인증이 이미 활성화되어 있습니다"
        }
    )
    
    MFA_NOT_ENABLED = LocalizedMessage(
        "mfa_not_enabled",
        {
            Language.CHINESE_SIMPLIFIED: "多因素认证未启用",
            Language.CHINESE_TRADITIONAL: "多因素認證未啟用",
            Language.ENGLISH: "Multi-factor authentication is not enabled",
            Language.JAPANESE: "多要素認証が有効になっていません",
            Language.KOREAN: "다중 인증이 활성화되어 있지 않습니다"
        }
    )
    
    # 速率限制错误
    RATE_LIMIT_EXCEEDED = LocalizedMessage(
        "rate_limit_exceeded",
        {
            Language.CHINESE_SIMPLIFIED: "请求频率过高，请稍后再试",
            Language.CHINESE_TRADITIONAL: "請求頻率過高，請稍後再試",
            Language.ENGLISH: "Rate limit exceeded, please try again later",
            Language.JAPANESE: "レート制限を超えました。後でもう一度お試しください",
            Language.KOREAN: "속도 제한을 초과했습니다. 나중에 다시 시도하십시오"
        }
    )
    
    TOO_MANY_REQUESTS = LocalizedMessage(
        "too_many_requests",
        {
            Language.CHINESE_SIMPLIFIED: "请求次数过多，请稍后再试",
            Language.CHINESE_TRADITIONAL: "請求次數過多，請稍後再試",
            Language.ENGLISH: "Too many requests, please try again later",
            Language.JAPANESE: "リクエストが多すぎます。後でもう一度お試しください",
            Language.KOREAN: "요청이 너무 많습니다. 나중에 다시 시도하십시오"
        }
    )
    
    # OAuth相关错误
    OAUTH_CONNECTION_ERROR = LocalizedMessage(
        "oauth_connection_error",
        {
            Language.CHINESE_SIMPLIFIED: "连接OAuth服务提供商时出错，请稍后再试",
            Language.CHINESE_TRADITIONAL: "連接OAuth服務提供商時出錯，請稍後再試",
            Language.ENGLISH: "Error connecting to OAuth service provider, please try again later",
            Language.JAPANESE: "OAuthサービスプロバイダーへの接続中にエラーが発生しました。後でもう一度お試しください",
            Language.KOREAN: "OAuth 서비스 제공업체에 연결하는 동안 오류가 발생했습니다. 나중에 다시 시도하십시오"
        }
    )
    
    OAUTH_INVALID_STATE = LocalizedMessage(
        "oauth_invalid_state",
        {
            Language.CHINESE_SIMPLIFIED: "OAuth状态验证失败，可能是CSRF攻击",
            Language.CHINESE_TRADITIONAL: "OAuth狀態驗證失敗，可能是CSRF攻擊",
            Language.ENGLISH: "OAuth state validation failed, possible CSRF attack",
            Language.JAPANESE: "OAuth状態の検証に失敗しました。CSRFの攻撃の可能性があります",
            Language.KOREAN: "OAuth 상태 유효성 검사에 실패했습니다. CSRF 공격 가능성이 있습니다"
        }
    )
    
    # 系统错误
    DATABASE_ERROR = LocalizedMessage(
        "database_error",
        {
            Language.CHINESE_SIMPLIFIED: "数据库操作失败，请稍后再试",
            Language.CHINESE_TRADITIONAL: "數據庫操作失敗，請稍後再試",
            Language.ENGLISH: "Database operation failed, please try again later",
            Language.JAPANESE: "データベース操作に失敗しました。後でもう一度お試しください",
            Language.KOREAN: "데이터베이스 작업에 실패했습니다. 나중에 다시 시도하십시오"
        }
    )
    
    REDIS_ERROR = LocalizedMessage(
        "redis_error",
        {
            Language.CHINESE_SIMPLIFIED: "缓存服务操作失败，请稍后再试",
            Language.CHINESE_TRADITIONAL: "緩存服務操作失敗，請稍後再試",
            Language.ENGLISH: "Cache service operation failed, please try again later",
            Language.JAPANESE: "キャッシュサービスの操作に失敗しました。後でもう一度お試しください",
            Language.KOREAN: "캐시 서비스 작업에 실패했습니다. 나중에 다시 시도하십시오"
        }
    )
    
    SERVICE_UNAVAILABLE = LocalizedMessage(
        "service_unavailable",
        {
            Language.CHINESE_SIMPLIFIED: "服务暂时不可用，请稍后再试",
            Language.CHINESE_TRADITIONAL: "服務暫時不可用，請稍後再試",
            Language.ENGLISH: "Service temporarily unavailable, please try again later",
            Language.JAPANESE: "サービスは一時的に利用できません。後でもう一度お試しください",
            Language.KOREAN: "서비스를 일시적으로 사용할 수 없습니다. 나중에 다시 시도하십시오"
        }
    )
    
    # 断路器错误
    CIRCUIT_OPEN = LocalizedMessage(
        "circuit_open",
        {
            Language.CHINESE_SIMPLIFIED: "系统保护机制已启动，请稍后再试",
            Language.CHINESE_TRADITIONAL: "系統保護機制已啟動，請稍後再試",
            Language.ENGLISH: "System protection mechanism activated, please try again later",
            Language.JAPANESE: "システム保護メカニズムが作動しました。後でもう一度お試しください",
            Language.KOREAN: "시스템 보호 메커니즘이 활성화되었습니다. 나중에 다시 시도하십시오"
        }
    )


# 定义成功消息
class SuccessMessages:
    """成功消息集合"""
    
    # 通用成功消息
    OPERATION_SUCCESSFUL = LocalizedMessage(
        "operation_successful",
        {
            Language.CHINESE_SIMPLIFIED: "操作成功",
            Language.CHINESE_TRADITIONAL: "操作成功",
            Language.ENGLISH: "Operation successful",
            Language.JAPANESE: "操作が成功しました",
            Language.KOREAN: "작업이 성공했습니다"
        }
    )
    
    # 用户相关成功消息
    USER_CREATED = LocalizedMessage(
        "user_created",
        {
            Language.CHINESE_SIMPLIFIED: "用户创建成功",
            Language.CHINESE_TRADITIONAL: "用戶創建成功",
            Language.ENGLISH: "User created successfully",
            Language.JAPANESE: "ユーザーが正常に作成されました",
            Language.KOREAN: "사용자가 성공적으로 생성되었습니다"
        }
    )
    
    USER_UPDATED = LocalizedMessage(
        "user_updated",
        {
            Language.CHINESE_SIMPLIFIED: "用户信息更新成功",
            Language.CHINESE_TRADITIONAL: "用戶信息更新成功",
            Language.ENGLISH: "User information updated successfully",
            Language.JAPANESE: "ユーザー情報が正常に更新されました",
            Language.KOREAN: "사용자 정보가 성공적으로 업데이트되었습니다"
        }
    )
    
    PASSWORD_CHANGED = LocalizedMessage(
        "password_changed",
        {
            Language.CHINESE_SIMPLIFIED: "密码修改成功",
            Language.CHINESE_TRADITIONAL: "密碼修改成功",
            Language.ENGLISH: "Password changed successfully",
            Language.JAPANESE: "パスワードが正常に変更されました",
            Language.KOREAN: "비밀번호가 성공적으로 변경되었습니다"
        }
    )
    
    PASSWORD_RESET = LocalizedMessage(
        "password_reset",
        {
            Language.CHINESE_SIMPLIFIED: "密码重置成功，请查收邮件",
            Language.CHINESE_TRADITIONAL: "密碼重置成功，請查收郵件",
            Language.ENGLISH: "Password reset successful, please check your email",
            Language.JAPANESE: "パスワードのリセットに成功しました。メールを確認してください",
            Language.KOREAN: "비밀번호 재설정에 성공했습니다. 이메일을 확인하십시오"
        }
    )
    
    # 认证相关成功消息
    LOGIN_SUCCESSFUL = LocalizedMessage(
        "login_successful",
        {
            Language.CHINESE_SIMPLIFIED: "登录成功",
            Language.CHINESE_TRADITIONAL: "登錄成功",
            Language.ENGLISH: "Login successful",
            Language.JAPANESE: "ログインに成功しました",
            Language.KOREAN: "로그인 성공"
        }
    )
    
    LOGOUT_SUCCESSFUL = LocalizedMessage(
        "logout_successful",
        {
            Language.CHINESE_SIMPLIFIED: "登出成功",
            Language.CHINESE_TRADITIONAL: "登出成功",
            Language.ENGLISH: "Logout successful",
            Language.JAPANESE: "ログアウトに成功しました",
            Language.KOREAN: "로그아웃 성공"
        }
    )
    
    TOKEN_REFRESHED = LocalizedMessage(
        "token_refreshed",
        {
            Language.CHINESE_SIMPLIFIED: "令牌刷新成功",
            Language.CHINESE_TRADITIONAL: "令牌刷新成功",
            Language.ENGLISH: "Token refreshed successfully",
            Language.JAPANESE: "トークンが正常に更新されました",
            Language.KOREAN: "토큰이 성공적으로 새로 고쳐졌습니다"
        }
    )
    
    # 多因素认证相关成功消息
    MFA_ENABLED = LocalizedMessage(
        "mfa_enabled",
        {
            Language.CHINESE_SIMPLIFIED: "多因素认证已启用",
            Language.CHINESE_TRADITIONAL: "多因素認證已啟用",
            Language.ENGLISH: "Multi-factor authentication enabled",
            Language.JAPANESE: "多要素認証が有効になりました",
            Language.KOREAN: "다중 인증이 활성화되었습니다"
        }
    )
    
    MFA_DISABLED = LocalizedMessage(
        "mfa_disabled",
        {
            Language.CHINESE_SIMPLIFIED: "多因素认证已禁用",
            Language.CHINESE_TRADITIONAL: "多因素認證已禁用",
            Language.ENGLISH: "Multi-factor authentication disabled",
            Language.JAPANESE: "多要素認証が無効になりました",
            Language.KOREAN: "다중 인증이 비활성화되었습니다"
        }
    )
    
    MFA_VERIFIED = LocalizedMessage(
        "mfa_verified",
        {
            Language.CHINESE_SIMPLIFIED: "多因素认证验证成功",
            Language.CHINESE_TRADITIONAL: "多因素認證驗證成功",
            Language.ENGLISH: "Multi-factor authentication verified",
            Language.JAPANESE: "多要素認証が確認されました",
            Language.KOREAN: "다중 인증이 확인되었습니다"
        }
    )


class I18nService:
    """国际化服务
    
    用于管理和检索本地化消息
    """
    
    @staticmethod
    def get_error_message(message_key: str, language: Optional[Language] = None) -> str:
        """
        获取错误消息
        
        Args:
            message_key: 错误消息的键
            language: 目标语言
            
        Returns:
            本地化后的错误消息
        """
        # 通过反射获取消息对象
        message_obj = getattr(ErrorMessages, message_key.upper(), None)
        
        if message_obj is None:
            # 如果找不到指定的消息，返回通用错误消息
            return ErrorMessages.INTERNAL_SERVER_ERROR.get(language)
        
        return message_obj.get(language)
    
    @staticmethod
    def get_success_message(message_key: str, language: Optional[Language] = None) -> str:
        """
        获取成功消息
        
        Args:
            message_key: 成功消息的键
            language: 目标语言
            
        Returns:
            本地化后的成功消息
        """
        # 通过反射获取消息对象
        message_obj = getattr(SuccessMessages, message_key.upper(), None)
        
        if message_obj is None:
            # 如果找不到指定的消息，返回通用成功消息
            return SuccessMessages.OPERATION_SUCCESSFUL.get(language)
        
        return message_obj.get(language)
    
    @staticmethod
    def get_supported_languages() -> List[Language]:
        """
        获取支持的语言列表
        
        Returns:
            支持的语言列表
        """
        return list(Language)


# 全局实例
i18n = I18nService() 