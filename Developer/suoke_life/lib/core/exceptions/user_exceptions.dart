import 'package:suoke_life/core/error/exceptions.dart';

/// 用户未找到异常
class UserNotFoundException extends ServerException {
  UserNotFoundException({String? message, StackTrace? stackTrace})
      : super(message: message ?? '用户不存在', stackTrace: stackTrace);
}

/// 无效输入异常
class InvalidInputException extends ServerException {
  InvalidInputException({String? message, StackTrace? stackTrace})
      : super(message: message ?? '无效的输入数据', stackTrace: stackTrace);
}

/// 冲突异常，例如添加已存在的资源
class ConflictException extends ServerException {
  ConflictException({String? message, StackTrace? stackTrace})
      : super(message: message ?? '资源冲突', stackTrace: stackTrace);
}

/// 用户权限不足异常
class InsufficientPermissionException extends ServerException {
  InsufficientPermissionException({String? message, StackTrace? stackTrace})
      : super(message: message ?? '权限不足', stackTrace: stackTrace);
}

/// 用户账户被锁定异常
class AccountLockedException extends ServerException {
  AccountLockedException({String? message, StackTrace? stackTrace})
      : super(message: message ?? '账户已被锁定', stackTrace: stackTrace);
}

/// 用户健康数据异常
class HealthDataException extends ServerException {
  HealthDataException({String? message, StackTrace? stackTrace})
      : super(message: message ?? '健康数据处理异常', stackTrace: stackTrace);
}

/// 用户社交分享异常
class SocialSharingException extends ServerException {
  SocialSharingException({String? message, StackTrace? stackTrace})
      : super(message: message ?? '社交分享异常', stackTrace: stackTrace);
}

/// 用户知识偏好异常
class KnowledgePreferenceException extends ServerException {
  KnowledgePreferenceException({String? message, StackTrace? stackTrace})
      : super(message: message ?? '知识偏好处理异常', stackTrace: stackTrace);
}

/// 用户配置文件异常
class ProfileUpdateException extends ServerException {
  ProfileUpdateException({String? message, StackTrace? stackTrace})
      : super(message: message ?? '用户资料更新异常', stackTrace: stackTrace);
}

/// 用户偏好设置异常
class PreferencesException extends ServerException {
  PreferencesException({String? message, StackTrace? stackTrace})
      : super(message: message ?? '偏好设置处理异常', stackTrace: stackTrace);
} 