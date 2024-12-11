/// 存储服务接口
abstract class StorageService extends BaseService {
  /// 获取值
  Future<T?> get<T>(String key);
  
  /// 设置值
  Future<void> set<T>(String key, T value);
  
  /// 删除值
  Future<void> remove(String key);
  
  /// 清空存储
  Future<void> clear();
  
  /// 获取所有键
  Future<Set<String>> getKeys();
  
  /// 是否包含键
  Future<bool> containsKey(String key);
  
  /// 获取存储大小
  Future<int> size();
}

/// 存储异常
class StorageException implements Exception {
  final String message;
  final dynamic cause;

  StorageException(this.message, [this.cause]);

  @override
  String toString() => 'StorageException: $message';
}

/// 存储配置
class StorageOptions {
  /// 是否加密
  final bool encrypt;
  
  /// 缓存大小限制(bytes)
  final int maxSize;
  
  /// 过期时间
  final Duration? expireAfter;

  const StorageOptions({
    this.encrypt = false,
    this.maxSize = 104857600, // 100MB
    this.expireAfter,
  });
}

/// 存储项
class StorageItem<T> {
  /// 键
  final String key;
  
  /// 值
  final T value;
  
  /// 创建时间
  final DateTime createTime;
  
  /// 过期时间
  final DateTime? expireTime;

  StorageItem({
    required this.key,
    required this.value,
    DateTime? createTime,
    this.expireTime,
  }) : createTime = createTime ?? DateTime.now();

  /// 是否过期
  bool get isExpired {
    if (expireTime == null) return false;
    return DateTime.now().isAfter(expireTime!);
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() => {
    'key': key,
    'value': value,
    'createTime': createTime.toIso8601String(),
    'expireTime': expireTime?.toIso8601String(),
  };

  /// 从JSON创建
  factory StorageItem.fromJson(Map<String, dynamic> json) => StorageItem(
    key: json['key'] as String,
    value: json['value'] as T,
    createTime: DateTime.parse(json['createTime'] as String),
    expireTime: json['expireTime'] != null 
      ? DateTime.parse(json['expireTime'] as String)
      : null,
  );
}

/// 存储提供者接口
abstract class StorageProvider {
  /// 读取数据
  Future<Map<String, dynamic>?> read(String key);
  
  /// 写入数据
  Future<void> write(String key, Map<String, dynamic> value);
  
  /// 删除数据
  Future<void> delete(String key);
  
  /// 清空数据
  Future<void> clear();
  
  /// 获取所有键
  Future<Set<String>> getKeys();
} 