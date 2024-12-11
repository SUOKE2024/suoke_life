import 'dart:async';
import 'package:flutter/foundation.dart';

/// 本地存储基础抽象类
abstract class BaseStorage {
  static Future<BaseStorage> initialize() async {
    // 实现初始化逻辑
    throw UnimplementedError();
  }
  
  Future<void> init();
  Future<void> dispose();
}

/// 存储类型枚举
enum StorageType {
  /// 基础数据存储
  basic,
  
  /// 临时缓存存储
  cache,
  
  /// 离线数据存储
  offline
}

/// 存储配置
class StorageConfig {
  /// 存储类型
  final StorageType type;
  
  /// 存储大小限制（字节）
  final int maxSize;
  
  /// 存储有效期（秒）
  final int? expireSeconds;
  
  /// 是否加密
  final bool encrypt;
  
  /// 是否压缩
  final bool compress;
  
  const StorageConfig({
    required this.type,
    required this.maxSize,
    this.expireSeconds,
    this.encrypt = false,
    this.compress = false,
  });
}

/// 存储异常
class StorageException implements Exception {
  final String message;
  final dynamic error;
  
  StorageException(this.message, [this.error]);
  
  @override
  String toString() => 'StorageException: $message${error != null ? ' ($error)' : ''}';
} 