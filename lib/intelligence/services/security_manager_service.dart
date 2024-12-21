import 'dart:convert';
import 'dart:async';
import 'dart:math';
import 'dart:utf8';

import 'package:get/get.dart';

import '../models/exceptions.dart';
import '../services/config_manager_service.dart';
import '../services/cache_manager_service.dart';
import '../services/encryption_service.dart';
import '../services/logging_service.dart';

class SecurityManagerService extends GetxService {
  final ConfigManagerService _configManager;
  final CacheManagerService _cacheManager;
  final EncryptionService _encryption;
  final LoggingService _logging;

  // 安全配置
  static const Map<String, Map<String, dynamic>> _securityConfig = {
    'request': {
      'max_length': 4096,
      'rate_limit': 60, // 每分钟请求数
      'sensitive_patterns': [
        r'password',
        r'token',
        r'api[_\-\s]?key',
        r'secret',
      ],
    },
    'context': {
      'max_size': 32768,
      'max_depth': 5,
      'allowed_types': ['string', 'number', 'boolean', 'array', 'object'],
    },
    'analysis': {
      'max_content_size': 1048576, // 1MB
      'allowed_types': ['text', 'json', 'binary'],
      'restricted_operations': ['execute', 'system', 'network'],
    },
  };

  SecurityManagerService({
    required ConfigManagerService configManager,
    required CacheManagerService cacheManager,
    required EncryptionService encryption,
    required LoggingService logging,
  }) : _configManager = configManager,
       _cacheManager = cacheManager,
       _encryption = encryption,
       _logging = logging;

  // 验证请求
  Future<void> validateRequest(
    String message, {
    required String sessionId,
  }) async {
    final config = _securityConfig['request']!;

    // 长度检查
    if (message.length > config['max_length']) {
      throw SecurityException('请求超出长度限制');
    }

    // 频率限制
    if (!await _checkRateLimit(sessionId)) {
      throw SecurityException('超出请求频率限制');
    }

    // 敏感信息检查
    if (_containsSensitiveInfo(message, config['sensitive_patterns'])) {
      throw SecurityException('请求包含敏感信息');
    }

    // 记录请求
    await _logRequest(sessionId, message);
  }

  // 验证上下文
  Future<void> validateContext(Map<String, dynamic> context) async {
    final config = _securityConfig['context']!;

    // 大小检查
    if (_calculateSize(context) > config['max_size']) {
      throw SecurityException('上下文超出大小限制');
    }

    // 深度检查
    if (_calculateDepth(context) > config['max_depth']) {
      throw SecurityException('上下文嵌套过深');
    }

    // 类型检查
    if (!_validateTypes(context, config['allowed_types'])) {
      throw SecurityException('上下文包含不允许的数据类型');
    }
  }

  // 验证分析内容
  Future<void> validateAnalysis(
    dynamic content, {
    required String type,
    required String sessionId,
  }) async {
    final config = _securityConfig['analysis']!;

    // 大小检查
    if (_calculateSize(content) > config['max_content_size']) {
      throw SecurityException('分析内容超出大小限制');
    }

    // 类型检查
    if (!config['allowed_types'].contains(type)) {
      throw SecurityException('不支持的分析类型');
    }

    // 操作检查
    if (_containsRestrictedOps(content, config['restricted_operations'])) {
      throw SecurityException('包含受限操作');
    }
  }

  // 加密消息
  Future<String> encryptMessage(String message) async {
    try {
      return await _encryption.encrypt(message);
    } catch (e) {
      throw SecurityException('消息加密失败', details: e);
    }
  }

  // 解密消息
  Future<String> decryptMessage(String encrypted) async {
    try {
      return await _encryption.decrypt(encrypted);
    } catch (e) {
      throw SecurityException('消息解密失败', details: e);
    }
  }

  // 检查请求频率
  Future<bool> _checkRateLimit(String sessionId) async {
    final key = 'rate_limit_$sessionId';
    final count = await _cacheManager.increment(key);
    
    if (count == 1) {
      // 设置1分钟过期
      await _cacheManager.expire(key, Duration(minutes: 1));
    }

    return count <= _securityConfig['request']!['rate_limit'];
  }

  // 检查敏感信息
  bool _containsSensitiveInfo(String text, List<String> patterns) {
    for (final pattern in patterns) {
      if (RegExp(pattern, caseSensitive: false).hasMatch(text)) {
        return true;
      }
    }
    return false;
  }

  // 检查受限操作
  bool _containsRestrictedOps(dynamic content, List<String> restricted) {
    final text = content.toString().toLowerCase();
    return restricted.any((op) => text.contains(op));
  }

  // 计算数据大小
  int _calculateSize(dynamic data) {
    return utf8.encode(json.encode(data)).length;
  }

  // 计算嵌套深度
  int _calculateDepth(dynamic data) {
    if (data is! Map && data is! List) return 0;
    
    if (data is Map) {
      return 1 + (data.isEmpty ? 0 : 
        data.values.map((v) => _calculateDepth(v)).reduce(max));
    }
    
    if (data is List) {
      return 1 + (data.isEmpty ? 0 : 
        data.map((v) => _calculateDepth(v)).reduce(max));
    }
    
    return 0;
  }

  // 验证数据类型
  bool _validateTypes(dynamic data, List<String> allowedTypes) {
    if (data == null) return true;
    
    if (data is Map) {
      return data.values.every((v) => _validateTypes(v, allowedTypes));
    }
    
    if (data is List) {
      return data.every((v) => _validateTypes(v, allowedTypes));
    }
    
    final type = data.runtimeType.toString().toLowerCase();
    return allowedTypes.contains(type);
  }

  // 记录请求
  Future<void> _logRequest(String sessionId, String message) async {
    await _logging.log(
      'security',
      'request_validation',
      {
        'session_id': sessionId,
        'message_length': message.length,
        'timestamp': DateTime.now().toIso8601String(),
      },
    );
  }
} 