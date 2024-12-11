/// 配置验证器
class ConfigValidator {
  /// 验证应用配置
  static void validateAppConfig(AppConfig config) {
    if (config.name.isEmpty) {
      throw ConfigValidationException('App name cannot be empty');
    }
    if (!_isValidVersion(config.version)) {
      throw ConfigValidationException('Invalid app version format');
    }
    if (!_isValidEnv(config.env)) {
      throw ConfigValidationException('Invalid environment');
    }
  }

  /// 验证网络配置
  static void validateNetworkConfig(NetworkConfig config) {
    if (!_isValidUrl(config.baseUrl)) {
      throw ConfigValidationException('Invalid base URL');
    }
    if (config.timeout < 0) {
      throw ConfigValidationException('Timeout cannot be negative');
    }
    if (config.retryCount < 0) {
      throw ConfigValidationException('Retry count cannot be negative');
    }
  }

  /// 验证版本格式
  static bool _isValidVersion(String version) {
    final pattern = RegExp(r'^\d+\.\d+\.\d+$');
    return pattern.hasMatch(version);
  }

  /// 验证环境名称
  static bool _isValidEnv(String env) {
    return ['dev', 'test', 'prod'].contains(env);
  }

  /// 验证URL格式
  static bool _isValidUrl(String url) {
    try {
      final uri = Uri.parse(url);
      return uri.scheme.isNotEmpty && uri.host.isNotEmpty;
    } catch (_) {
      return false;
    }
  }

  /// 验证AI配置
  static void validateAiConfig(AiConfig config) {
    for (final model in config.models.values) {
      if (!_isValidModelVersion(model.version)) {
        throw ConfigValidationException('Invalid AI model version: ${model.version}');
      }
      if (model.maxTokens <= 0) {
        throw ConfigValidationException('Invalid max tokens for model: ${model.name}');
      }
    }
  }

  /// 验证数据库配置
  static void validateDatabaseConfig(DatabaseConfig config) {
    if (!_isValidDatabaseVersion(config.mysql.version)) {
      throw ConfigValidationException('Invalid MySQL version');
    }
    if (!_isValidRedisVersion(config.redis.version)) {
      throw ConfigValidationException('Invalid Redis version');
    }
  }

  /// 验证AI模型版本格式
  static bool _isValidModelVersion(String version) {
    final pattern = RegExp(r'^ep-\d{14}-[a-z0-9]{5}$');
    return pattern.hasMatch(version);
  }

  /// 验证MySQL版本格式
  static bool _isValidDatabaseVersion(String version) {
    final pattern = RegExp(r'^\d+\.\d+$');
    return pattern.hasMatch(version);
  }

  /// 验证Redis版本格式
  static bool _isValidRedisVersion(String version) {
    final pattern = RegExp(r'^\d+\.\d+$');
    return pattern.hasMatch(version);
  }

  /// 验证存储配置
  static void validateStorageConfig(StorageConfig config) {
    // 验证本地存储配置
    if (config.local.cacheSize <= 0) {
      throw ConfigValidationException('Cache size must be positive');
    }

    // 验证远程存储配置
    if (!_isValidStorageType(config.remote.type)) {
      throw ConfigValidationException('Invalid storage type');
    }
    if (!_isValidRegion(config.remote.region)) {
      throw ConfigValidationException('Invalid region');
    }
    if (config.remote.bucket.isEmpty) {
      throw ConfigValidationException('Bucket name cannot be empty');
    }
  }

  /// 验证存储类型
  static bool _isValidStorageType(String type) {
    return ['oss', 's3', 'cos'].contains(type.toLowerCase());
  }

  /// 验证区域
  static bool _isValidRegion(String region) {
    final pattern = RegExp(r'^[a-z]+-[a-z]+-\d+$');
    return pattern.hasMatch(region);
  }
}

/// 配置验证异常
class ConfigValidationException implements Exception {
  final String message;
  ConfigValidationException(this.message);

  @override
  String toString() => 'ConfigValidationException: $message';
} 