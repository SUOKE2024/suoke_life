import 'package:equatable/equatable.dart';

/// 认证令牌实体类
class AuthToken extends Equatable {
  /// 访问令牌
  final String accessToken;
  
  /// 刷新令牌
  final String refreshToken;
  
  /// 过期时间（秒）
  final int expiresIn;
  
  /// 过期时间点
  final DateTime? expiresAt;

  /// 构造函数
  const AuthToken({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
    this.expiresAt,
  });

  /// 创建带有过期时间点的认证令牌
  factory AuthToken.withExpiresAt({
    required String accessToken,
    required String refreshToken,
    required int expiresIn,
  }) {
    final expiresAt = DateTime.now().add(Duration(seconds: expiresIn));
    return AuthToken(
      accessToken: accessToken,
      refreshToken: refreshToken,
      expiresIn: expiresIn,
      expiresAt: expiresAt,
    );
  }

  /// 判断令牌是否过期
  bool get isExpired {
    if (expiresAt == null) {
      return false;
    }
    return DateTime.now().isAfter(expiresAt!);
  }

  /// 剩余有效时间（秒）
  int get remainingTime {
    if (expiresAt == null) {
      return expiresIn;
    }
    final remaining = expiresAt!.difference(DateTime.now()).inSeconds;
    return remaining > 0 ? remaining : 0;
  }

  @override
  List<Object?> get props => [accessToken, refreshToken, expiresIn, expiresAt];

  /// 创建副本
  AuthToken copyWith({
    String? accessToken,
    String? refreshToken,
    int? expiresIn,
    DateTime? expiresAt,
  }) {
    return AuthToken(
      accessToken: accessToken ?? this.accessToken,
      refreshToken: refreshToken ?? this.refreshToken,
      expiresIn: expiresIn ?? this.expiresIn,
      expiresAt: expiresAt ?? this.expiresAt,
    );
  }
} 