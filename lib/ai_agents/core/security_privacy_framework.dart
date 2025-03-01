import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:crypto/crypto.dart';

/// 数据隐私级别
enum PrivacyLevel {
  /// 公开数据
  public,
  
  /// 个人数据（需要用户授权）
  personal,
  
  /// 敏感数据（需要额外验证）
  sensitive,
  
  /// 高度敏感数据（最高级别保护）
  highlySensitive,
}

/// 安全操作类型
enum SecurityOperation {
  /// 读取操作
  read,
  
  /// 写入操作
  write,
  
  /// 更新操作
  update,
  
  /// 删除操作
  delete,
  
  /// 共享操作
  share,
  
  /// 导出操作
  export,
}

/// 安全审计事件
class SecurityAuditEvent {
  /// 事件ID
  final String id;
  
  /// 操作类型
  final SecurityOperation operation;
  
  /// 数据类型
  final String dataType;
  
  /// 数据ID
  final String? dataId;
  
  /// 用户ID
  final String? userId;
  
  /// 代理ID
  final String? agentId;
  
  /// 时间戳
  final DateTime timestamp;
  
  /// 结果状态（成功/失败）
  final bool success;
  
  /// 失败原因（如果有）
  final String? failureReason;
  
  /// IP地址
  final String? ipAddress;
  
  /// 设备信息
  final String? deviceInfo;
  
  SecurityAuditEvent({
    required this.id,
    required this.operation,
    required this.dataType,
    this.dataId,
    this.userId,
    this.agentId,
    DateTime? timestamp,
    required this.success,
    this.failureReason,
    this.ipAddress,
    this.deviceInfo,
  }) : timestamp = timestamp ?? DateTime.now();
}

/// 用户同意记录
class UserConsent {
  /// 同意记录ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 同意的数据类型
  final List<String> dataTypes;
  
  /// 同意的目的
  final List<String> purposes;
  
  /// 授予的权限
  final List<SecurityOperation> permissions;
  
  /// 同意时间
  final DateTime grantedAt;
  
  /// 到期时间
  final DateTime? expiresAt;
  
  /// 撤销时间
  final DateTime? revokedAt;
  
  /// 是否处于活跃状态
  bool get isActive => revokedAt == null && (expiresAt == null || expiresAt!.isAfter(DateTime.now()));
  
  UserConsent({
    required this.id,
    required this.userId,
    required this.dataTypes,
    required this.purposes,
    required this.permissions,
    required this.grantedAt,
    this.expiresAt,
    this.revokedAt,
  });
}

/// 安全与隐私框架接口
abstract class SecurityPrivacyFramework {
  /// 加密数据
  Future<Uint8List> encryptData(Uint8List data, PrivacyLevel level);
  
  /// 解密数据
  Future<Uint8List> decryptData(Uint8List encryptedData, PrivacyLevel level);
  
  /// 哈希数据（不可逆）
  String hashData(Uint8List data);
  
  /// 匿名化数据
  Future<dynamic> anonymizeData(dynamic data, String dataType);
  
  /// 检查安全权限
  Future<bool> checkPermission(
    String userId,
    SecurityOperation operation,
    String dataType,
    PrivacyLevel privacyLevel,
  );
  
  /// 记录安全审计事件
  Future<void> logAuditEvent(SecurityAuditEvent event);
  
  /// 获取审计日志
  Future<List<SecurityAuditEvent>> getAuditLogs({
    DateTime? startDate,
    DateTime? endDate,
    String? userId,
    String? dataType,
    SecurityOperation? operation,
  });
  
  /// 记录用户同意
  Future<String> recordUserConsent(UserConsent consent);
  
  /// 撤销用户同意
  Future<void> revokeUserConsent(String consentId);
  
  /// 验证用户同意
  Future<bool> verifyUserConsent(
    String userId,
    String dataType,
    String purpose,
    SecurityOperation operation,
  );
  
  /// 获取用户所有同意记录
  Future<List<UserConsent>> getUserConsents(String userId);
  
  /// 生成差分隐私数据
  Future<dynamic> applyDifferentialPrivacy(
    dynamic data,
    String dataType,
    double epsilon,
  );
  
  /// 安全存储敏感数据
  Future<void> secureStore(String key, String value, PrivacyLevel level);
  
  /// 从安全存储中读取敏感数据
  Future<String?> secureRetrieve(String key, PrivacyLevel level);
  
  /// 从安全存储中移除敏感数据
  Future<void> secureDelete(String key, PrivacyLevel level);
}

/// 默认安全与隐私框架实现
class DefaultSecurityPrivacyFramework implements SecurityPrivacyFramework {
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  final List<SecurityAuditEvent> _auditLogs = [];
  final Map<String, UserConsent> _userConsents = {};
  final Random _random = Random.secure();
  
  // 单例实现
  static final DefaultSecurityPrivacyFramework _instance = DefaultSecurityPrivacyFramework._internal();
  
  factory DefaultSecurityPrivacyFramework() => _instance;
  
  DefaultSecurityPrivacyFramework._internal();
  
  @override
  Future<Uint8List> encryptData(Uint8List data, PrivacyLevel level) async {
    // 实际应用中应使用更强大的加密库
    // 这里简单实现一个基本的异或加密
    final key = await _getEncryptionKey(level);
    final keyBytes = utf8.encode(key);
    final result = Uint8List(data.length);
    
    for (var i = 0; i < data.length; i++) {
      result[i] = data[i] ^ keyBytes[i % keyBytes.length];
    }
    
    return result;
  }
  
  @override
  Future<Uint8List> decryptData(Uint8List encryptedData, PrivacyLevel level) async {
    // 对于简单的异或加密，解密操作与加密相同
    return encryptData(encryptedData, level);
  }
  
  @override
  String hashData(Uint8List data) {
    return sha256.convert(data).toString();
  }
  
  @override
  Future<dynamic> anonymizeData(dynamic data, String dataType) async {
    // 实现数据匿名化的逻辑
    if (data is Map) {
      final anonymized = <String, dynamic>{};
      for (final entry in data.entries) {
        final key = entry.key.toString();
        dynamic value = entry.value;
        
        // 根据字段名执行不同的匿名化
        if (key.contains('name')) {
          value = '用户_${hashData(utf8.encode(value.toString())).substring(0, 8)}';
        } else if (key.contains('phone')) {
          value = '***-****-${value.toString().substring(value.toString().length - 4)}';
        } else if (key.contains('email')) {
          final parts = value.toString().split('@');
          if (parts.length == 2) {
            value = '${parts[0].substring(0, 1)}***@${parts[1]}';
          }
        } else if (key.contains('address')) {
          value = '***';
        } else if (key.contains('id') && key != 'id') {
          value = hashData(utf8.encode(value.toString())).substring(0, 16);
        }
        
        anonymized[key] = value;
      }
      return anonymized;
    } else if (data is String) {
      // 简单字符串匿名化
      return hashData(utf8.encode(data)).substring(0, 16);
    }
    
    return data;
  }
  
  @override
  Future<bool> checkPermission(
    String userId,
    SecurityOperation operation,
    String dataType,
    PrivacyLevel privacyLevel,
  ) async {
    // 检查用户是否有权限执行指定操作
    final hasConsent = await verifyUserConsent(
      userId,
      dataType,
      'default',
      operation,
    );
    
    if (!hasConsent) {
      return false;
    }
    
    // 根据隐私级别应用额外规则
    switch (privacyLevel) {
      case PrivacyLevel.public:
        return true;
      case PrivacyLevel.personal:
        // 个人数据需要用户本人才能访问
        return true;
      case PrivacyLevel.sensitive:
        // 敏感数据需要额外验证
        return operation != SecurityOperation.export && operation != SecurityOperation.share;
      case PrivacyLevel.highlySensitive:
        // 高度敏感数据有严格限制
        return operation == SecurityOperation.read;
    }
  }
  
  @override
  Future<void> logAuditEvent(SecurityAuditEvent event) async {
    _auditLogs.add(event);
    
    // 在实际应用中，可能会将日志保存到数据库或发送到远程日志系统
  }
  
  @override
  Future<List<SecurityAuditEvent>> getAuditLogs({
    DateTime? startDate,
    DateTime? endDate,
    String? userId,
    String? dataType,
    SecurityOperation? operation,
  }) async {
    return _auditLogs.where((event) {
      if (startDate != null && event.timestamp.isBefore(startDate)) {
        return false;
      }
      
      if (endDate != null && event.timestamp.isAfter(endDate)) {
        return false;
      }
      
      if (userId != null && event.userId != userId) {
        return false;
      }
      
      if (dataType != null && event.dataType != dataType) {
        return false;
      }
      
      if (operation != null && event.operation != operation) {
        return false;
      }
      
      return true;
    }).toList();
  }
  
  @override
  Future<String> recordUserConsent(UserConsent consent) async {
    _userConsents[consent.id] = consent;
    return consent.id;
  }
  
  @override
  Future<void> revokeUserConsent(String consentId) async {
    final consent = _userConsents[consentId];
    if (consent != null) {
      _userConsents[consentId] = UserConsent(
        id: consent.id,
        userId: consent.userId,
        dataTypes: consent.dataTypes,
        purposes: consent.purposes,
        permissions: consent.permissions,
        grantedAt: consent.grantedAt,
        expiresAt: consent.expiresAt,
        revokedAt: DateTime.now(),
      );
    }
  }
  
  @override
  Future<bool> verifyUserConsent(
    String userId,
    String dataType,
    String purpose,
    SecurityOperation operation,
  ) async {
    // 查找该用户的有效同意记录
    final activeConsents = _userConsents.values.where((consent) =>
      consent.userId == userId &&
      consent.isActive &&
      consent.dataTypes.contains(dataType) &&
      consent.purposes.contains(purpose) &&
      consent.permissions.contains(operation)
    ).toList();
    
    return activeConsents.isNotEmpty;
  }
  
  @override
  Future<List<UserConsent>> getUserConsents(String userId) async {
    return _userConsents.values.where((consent) => consent.userId == userId).toList();
  }
  
  @override
  Future<dynamic> applyDifferentialPrivacy(
    dynamic data,
    String dataType,
    double epsilon,
  ) async {
    // 实现差分隐私的逻辑
    if (data is num) {
      final double sensitivity = 1.0;  // 敏感度
      final double scale = sensitivity / epsilon;
      
      // 生成拉普拉斯噪声
      final double noise = _generateLaplaceNoise(scale);
      
      return data + noise;
    } else if (data is List && data.isNotEmpty && data.first is num) {
      // 对列表中的每个数值添加噪声
      return data.map((value) async => 
        await applyDifferentialPrivacy(value, dataType, epsilon)
      ).toList();
    } else if (data is Map) {
      // 对Map中的数值字段添加噪声
      final result = <String, dynamic>{};
      for (final entry in data.entries) {
        if (entry.value is num) {
          result[entry.key] = await applyDifferentialPrivacy(entry.value, dataType, epsilon);
        } else {
          result[entry.key] = entry.value;
        }
      }
      return result;
    }
    
    // 对于非数值型数据，暂不处理
    return data;
  }
  
  /// 生成拉普拉斯分布的随机噪声
  double _generateLaplaceNoise(double scale) {
    final double u = _random.nextDouble() - 0.5;
    final double sign = (u >= 0) ? 1 : -1;
    return -scale * sign * log(1 - 2 * u.abs());
  }
  
  /// 获取指定隐私级别的加密密钥
  Future<String> _getEncryptionKey(PrivacyLevel level) async {
    final keyId = 'encryption_key_${level.toString()}';
    final storedKey = await _secureStorage.read(key: keyId);
    
    if (storedKey != null) {
      return storedKey;
    }
    
    // 生成新密钥
    final newKey = List.generate(32, (_) => _random.nextInt(256))
        .map((e) => e.toRadixString(16).padLeft(2, '0'))
        .join();
    
    await _secureStorage.write(key: keyId, value: newKey);
    return newKey;
  }
  
  @override
  Future<void> secureStore(String key, String value, PrivacyLevel level) async {
    final privacyKey = '${level.toString()}_$key';
    await _secureStorage.write(key: privacyKey, value: value);
  }
  
  @override
  Future<String?> secureRetrieve(String key, PrivacyLevel level) async {
    final privacyKey = '${level.toString()}_$key';
    return await _secureStorage.read(key: privacyKey);
  }
  
  @override
  Future<void> secureDelete(String key, PrivacyLevel level) async {
    final privacyKey = '${level.toString()}_$key';
    await _secureStorage.delete(key: privacyKey);
  }
} 