/// 基础配置接口
abstract class ModuleConfig {
  Map<String, dynamic> toJson();
}

/// 应用配置
class AppConfig implements ModuleConfig {
  final String name;
  final String version;
  final String env;

  const AppConfig({
    required this.name,
    required this.version,
    required this.env,
  });

  factory AppConfig.fromJson(Map<String, dynamic> json) => AppConfig(
    name: json['name'] as String,
    version: json['version'] as String,
    env: json['env'] as String,
  );

  @override
  Map<String, dynamic> toJson() => {
    'name': name,
    'version': version,
    'env': env,
  };
}

/// 网络配置
class NetworkConfig implements ModuleConfig {
  final String baseUrl;
  final int timeout;
  final int retryCount;

  const NetworkConfig({
    required this.baseUrl,
    required this.timeout,
    required this.retryCount,
  });

  factory NetworkConfig.fromJson(Map<String, dynamic> json) => NetworkConfig(
    baseUrl: json['base_url'] as String,
    timeout: json['timeout'] as int,
    retryCount: json['retry_count'] as int,
  );

  @override
  Map<String, dynamic> toJson() => {
    'base_url': baseUrl,
    'timeout': timeout,
    'retry_count': retryCount,
  };
}

/// AI模型配置
class AiModelConfig implements ModuleConfig {
  final String name;
  final String version;
  final int maxTokens;

  const AiModelConfig({
    required this.name,
    required this.version,
    required this.maxTokens,
  });

  factory AiModelConfig.fromJson(Map<String, dynamic> json) => AiModelConfig(
    name: json['name'] as String,
    version: json['version'] as String,
    maxTokens: json['max_tokens'] as int,
  );

  @override
  Map<String, dynamic> toJson() => {
    'name': name,
    'version': version,
    'max_tokens': maxTokens,
  };
}

/// AI助手配置
class AiAssistantConfig implements ModuleConfig {
  final String name;
  final String role;
  final String model;

  const AiAssistantConfig({
    required this.name,
    required this.role,
    required this.model,
  });

  factory AiAssistantConfig.fromJson(Map<String, dynamic> json) => AiAssistantConfig(
    name: json['name'] as String,
    role: json['role'] as String,
    model: json['model'] as String,
  );

  @override
  Map<String, dynamic> toJson() => {
    'name': name,
    'role': role,
    'model': model,
  };
}

/// 数据库配置
class DatabaseConfig implements ModuleConfig {
  final MySQLConfig mysql;
  final RedisConfig redis;

  const DatabaseConfig({
    required this.mysql,
    required this.redis,
  });

  factory DatabaseConfig.fromJson(Map<String, dynamic> json) => DatabaseConfig(
    mysql: MySQLConfig.fromJson(json['mysql'] as Map<String, dynamic>),
    redis: RedisConfig.fromJson(json['redis'] as Map<String, dynamic>),
  );

  @override
  Map<String, dynamic> toJson() => {
    'mysql': mysql.toJson(),
    'redis': redis.toJson(),
  };
}

/// MySQL配置
class MySQLConfig implements ModuleConfig {
  final String version;
  final int maxConnections;

  const MySQLConfig({
    required this.version,
    required this.maxConnections,
  });

  factory MySQLConfig.fromJson(Map<String, dynamic> json) => MySQLConfig(
    version: json['version'] as String,
    maxConnections: json['max_connections'] as int,
  );

  @override
  Map<String, dynamic> toJson() => {
    'version': version,
    'max_connections': maxConnections,
  };
}

/// Redis配置
class RedisConfig implements ModuleConfig {
  final String version;
  final String maxMemory;

  const RedisConfig({
    required this.version,
    required this.maxMemory,
  });

  factory RedisConfig.fromJson(Map<String, dynamic> json) => RedisConfig(
    version: json['version'] as String,
    maxMemory: json['max_memory'] as String,
  );

  @override
  Map<String, dynamic> toJson() => {
    'version': version,
    'max_memory': maxMemory,
  };
}

/// 存储配置
class StorageConfig implements ModuleConfig {
  final LocalStorageConfig local;
  final RemoteStorageConfig remote;

  const StorageConfig({
    required this.local,
    required this.remote,
  });

  factory StorageConfig.fromJson(Map<String, dynamic> json) => StorageConfig(
    local: LocalStorageConfig.fromJson(json['local'] as Map<String, dynamic>),
    remote: RemoteStorageConfig.fromJson(json['remote'] as Map<String, dynamic>),
  );

  @override
  Map<String, dynamic> toJson() => {
    'local': local.toJson(),
    'remote': remote.toJson(),
  };
}

/// 本地存储配置
class LocalStorageConfig implements ModuleConfig {
  final int cacheSize;
  final bool encrypt;

  const LocalStorageConfig({
    required this.cacheSize,
    required this.encrypt,
  });

  factory LocalStorageConfig.fromJson(Map<String, dynamic> json) => LocalStorageConfig(
    cacheSize: json['cache_size'] as int,
    encrypt: json['encrypt'] as bool,
  );

  @override
  Map<String, dynamic> toJson() => {
    'cache_size': cacheSize,
    'encrypt': encrypt,
  };
}

/// 远程存储配置
class RemoteStorageConfig implements ModuleConfig {
  final String type;
  final String region;
  final String bucket;

  const RemoteStorageConfig({
    required this.type,
    required this.region,
    required this.bucket,
  });

  factory RemoteStorageConfig.fromJson(Map<String, dynamic> json) => RemoteStorageConfig(
    type: json['type'] as String,
    region: json['region'] as String,
    bucket: json['bucket'] as String,
  );

  @override
  Map<String, dynamic> toJson() => {
    'type': type,
    'region': region,
    'bucket': bucket,
  };
} 