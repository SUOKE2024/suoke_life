class SecurityPolicyService extends GetxService {
  // 从配置或远程加载安全策略
  final securityPolicies = <String, dynamic>{
    'password': {
      'minLength': 8,
      'maxLength': 32,
      'requireUppercase': true,
      'requireLowercase': true,
      'requireNumbers': true,
      'requireSpecialChars': true,
      'maxAge': const Duration(days: 90),
      'historyCount': 5,
    },
    'session': {
      'maxConcurrentSessions': 3,
      'sessionTimeout': const Duration(hours: 24),
      'requireReauthForSensitive': true,
    },
    'login': {
      'maxAttempts': 5,
      'lockoutDuration': const Duration(minutes: 30),
      'requireMFA': true,
      'trustedDevicesEnabled': true,
    },
    'notification': {
      'notifyOnNewDevice': true,
      'notifyOnPasswordChange': true,
      'notifyOnUnusualActivity': true,
    },
  };

  Future<void> updatePolicy(String key, dynamic value) async {
    // 更新策略并同步到存储
    securityPolicies[key] = value;
    await _syncPolicies();
  }

  Future<void> _syncPolicies() async {
    try {
      // 保存到本地存储
      await _storage.setJson('security_policies', securityPolicies);

      // 同步到服务器
      await _apiClient.put('/security/policies', data: securityPolicies);

      // 通知其他设备策略已更新
      _notifyPolicyUpdate();
    } catch (e) {
      debugPrint('同步安全策略失败: $e');
    }
  }

  bool validatePassword(String password) {
    final policy = securityPolicies['password'] as Map<String, dynamic>;

    if (password.length < policy['minLength']) return false;
    if (password.length > policy['maxLength']) return false;

    if (policy['requireUppercase'] && !password.contains(RegExp(r'[A-Z]'))) {
      return false;
    }

    if (policy['requireLowercase'] && !password.contains(RegExp(r'[a-z]'))) {
      return false;
    }

    if (policy['requireNumbers'] && !password.contains(RegExp(r'[0-9]'))) {
      return false;
    }

    if (policy['requireSpecialChars'] &&
        !password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'))) {
      return false;
    }

    return true;
  }

  Future<bool> checkPasswordHistory(String userId, String newPassword) async {
    final historyCount = securityPolicies['password']['historyCount'] as int;
    final passwordHistory = await _getPasswordHistory(userId);

    // 检查是否在历史密码中
    return !passwordHistory.take(historyCount).contains(newPassword);
  }
}
