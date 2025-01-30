import 'package:get/get.dart';
import '../core/services/storage_service.dart';
import '../core/config/auth_config.dart';
import 'package:flutter/material.dart';

class LoginSecurityService extends GetxService {
  final StorageService _storage;

  LoginSecurityService({
    required StorageService storage,
  }) : _storage = storage;

  // 登录尝试计数器
  final _loginAttempts = <String, int>{};
  // 锁定状态
  final _lockedAccounts = <String, DateTime>{};

  Future<bool> canAttemptLogin(String username) async {
    // 检查是否被锁定
    if (_isLocked(username)) {
      final remainingTime = _getRemainingLockTime(username);
      throw Exception('账号已被锁定，请在 $remainingTime 后重试');
    }
    return true;
  }

  void recordLoginAttempt(String username, bool success) {
    if (success) {
      // 登录成功，重置计数
      _loginAttempts.remove(username);
      _lockedAccounts.remove(username);
      return;
    }

    // 登录失败，增加计数
    _loginAttempts[username] = (_loginAttempts[username] ?? 0) + 1;

    // 检查是否需要锁定
    if (_loginAttempts[username]! >= AuthConfig.loginConfig['maxAttempts']) {
      _lockAccount(username);
      throw Exception('登录失败次数过多，账号已被锁定');
    }
  }

  bool _isLocked(String username) {
    final lockTime = _lockedAccounts[username];
    if (lockTime == null) return false;

    final now = DateTime.now();
    final lockDuration = AuthConfig.loginConfig['lockoutDuration'] as Duration;
    if (now.difference(lockTime) > lockDuration) {
      // 锁定时间已过，解除锁定
      _lockedAccounts.remove(username);
      _loginAttempts.remove(username);
      return false;
    }
    return true;
  }

  void _lockAccount(String username) {
    _lockedAccounts[username] = DateTime.now();
  }

  String _getRemainingLockTime(String username) {
    final lockTime = _lockedAccounts[username];
    if (lockTime == null) return '0分钟';

    final now = DateTime.now();
    final lockDuration = AuthConfig.loginConfig['lockoutDuration'] as Duration;
    final remainingDuration = lockDuration - now.difference(lockTime);

    if (remainingDuration.inHours > 0) {
      return '${remainingDuration.inHours}小时${remainingDuration.inMinutes % 60}分钟';
    }
    return '${remainingDuration.inMinutes}分钟';
  }

  // 密码策略检查
  bool isPasswordValid(String password) {
    // 至少8个字符
    if (password.length < 8) return false;

    // 必须包含数字
    if (!password.contains(RegExp(r'[0-9]'))) return false;

    // 必须包含字母
    if (!password.contains(RegExp(r'[a-zA-Z]'))) return false;

    // 必须包含特殊字符
    if (!password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'))) return false;

    return true;
  }

  // 获取密码强度
  double getPasswordStrength(String password) {
    double strength = 0;

    // 基础长度分数
    strength += password.length * 0.1;

    // 包含数字
    if (password.contains(RegExp(r'[0-9]'))) strength += 0.2;

    // 包含小写字母
    if (password.contains(RegExp(r'[a-z]'))) strength += 0.2;

    // 包含大写字母
    if (password.contains(RegExp(r'[A-Z]'))) strength += 0.2;

    // 包含特殊字符
    if (password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'))) strength += 0.2;

    return strength.clamp(0, 1);
  }
} 