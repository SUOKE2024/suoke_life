/// 认证异常基类
abstract class AuthException implements Exception {
  final String message;
  final String code;

  const AuthException({
    this.message = '认证错误',
    this.code = 'auth/unknown',
  });

  @override
  String toString() => '$code: $message';
}

/// 网络异常
class AuthNetworkException extends AuthException {
  const AuthNetworkException({String message = '网络连接错误，请检查网络设置'}) : super(message: message);
}

/// 无效凭证异常
class InvalidCredentialsException extends AuthException {
  const InvalidCredentialsException({
    String message = '用户名或密码错误',
    String code = 'auth/invalid-credentials',
  }) : super(message: message, code: code);
}

/// 用户不存在异常
class UserNotFoundException extends AuthException {
  const UserNotFoundException({
    String message = '用户不存在',
    String code = 'auth/user-not-found',
  }) : super(message: message, code: code);
}

/// 用户已存在异常
class UserAlreadyExistsException extends AuthException {
  const UserAlreadyExistsException({
    String message = '用户已存在',
    String code = 'auth/user-already-exists',
  }) : super(message: message, code: code);
}

/// 账户锁定异常
class AccountLockedException extends AuthException {
  final int remainingMinutes;

  const AccountLockedException({
    this.remainingMinutes = 30,
    String? message,
    String code = 'auth/account-locked',
  }) : super(
    message: message ?? '账户已被锁定，请在$remainingMinutes分钟后再试',
    code: code
  );
}

/// 令牌过期异常
class TokenExpiredException extends AuthException {
  const TokenExpiredException({
    String message = '登录已过期，请重新登录',
    String code = 'auth/token-expired',
  }) : super(message: message, code: code);
}

/// 验证码异常
class VerificationCodeException extends AuthException {
  const VerificationCodeException({
    String message = '验证码错误或已过期',
    String code = 'auth/invalid-verification-code',
  }) : super(message: message, code: code);
}

/// 短信发送异常
class SmsSendException extends AuthException {
  const SmsSendException({
    String message = '短信发送失败',
    String code = 'auth/sms-send-failed',
  }) : super(message: message, code: code);
}

/// 双因素认证异常
class TwoFactorAuthException extends AuthException {
  const TwoFactorAuthException({
    String message = '双因素认证失败',
    String code = 'auth/2fa-error',
  }) : super(message: message, code: code);
}

/// 生物识别认证异常
class BiometricAuthException extends AuthException {
  const BiometricAuthException({
    String message = '生物识别认证失败',
    String code = 'auth/biometric-failed',
  }) : super(message: message, code: code);
}

/// 社交媒体认证异常
class SocialAuthException extends AuthException {
  final String provider;

  const SocialAuthException({
    required this.provider,
    String? message,
    String code = 'auth/social-auth-failed',
  }) : super(
    message: message ?? '$provider登录失败，请重试',
    code: code
  );
}

/// 弱密码异常
class WeakPasswordException extends AuthException {
  const WeakPasswordException({
    String message = '密码强度不足，请使用更强的密码',
    String code = 'auth/weak-password',
  }) : super(message: message, code: code);
}

/// 密码泄露异常
class PasswordBreachedException extends AuthException {
  const PasswordBreachedException({
    String message = '该密码已在数据泄露中出现，请更换密码',
    String code = 'auth/password-breached',
  }) : super(message: message, code: code);
}

/// 权限不足异常
class InsufficientPermissionsException extends AuthException {
  const InsufficientPermissionsException({
    String message = '权限不足，无法执行此操作',
    String code = 'auth/insufficient-permissions',
  }) : super(message: message, code: code);
}

/// 会话无效异常
class InvalidSessionException extends AuthException {
  const InvalidSessionException({
    String message = '会话无效或已过期',
    String code = 'auth/invalid-session',
  }) : super(message: message, code: code);
}

/// 认证方法不支持异常
class AuthMethodNotSupportedException extends AuthException {
  const AuthMethodNotSupportedException({
    String message = '不支持此认证方法',
    String code = 'auth/method-not-supported',
  }) : super(message: message, code: code);
}

/// 会话过期异常
class SessionExpiredException extends AuthException {
  const SessionExpiredException({
    String message = '会话已过期，请重新登录',
    String code = 'auth/session-expired',
  }) : super(message: message, code: code);
}

/// 设备未认证异常
class DeviceNotAuthorizedException extends AuthException {
  const DeviceNotAuthorizedException({
    String message = '此设备未经授权，请使用已认证设备登录',
    String code = 'auth/device-not-authorized',
  }) : super(message: message, code: code);
} 