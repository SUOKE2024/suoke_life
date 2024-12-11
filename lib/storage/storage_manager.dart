import 'local/base_storage.dart';
import 'local/basic_storage.dart';
import 'local/cache_storage.dart';
import 'local/offline_storage.dart';

/// 存储管理器
class StorageManager {
  static final StorageManager _instance = StorageManager._internal();
  
  factory StorageManager() => _instance;
  
  StorageManager._internal();
  
  late final BasicStorage basicStorage;
  late final CacheStorage cacheStorage;
  late final OfflineStorage offlineStorage;
  
  /// 初始化存储管理器
  Future<void> initialize() async {
    try {
      // 初始化基础存储
      basicStorage = BasicStorage();
      await basicStorage.initialize();
      
      // 初始化缓存存储
      cacheStorage = CacheStorage();
      await cacheStorage.initialize();
      
      // 初始化离线存储
      offlineStorage = OfflineStorage();
      await offlineStorage.initialize();
    } catch (e) {
      throw StorageException('Failed to initialize StorageManager', e);
    }
  }
  
  /// 根据存储类型获取对应的存储实现
  BaseStorage getStorage(StorageType type) {
    switch (type) {
      case StorageType.basic:
        return basicStorage;
      case StorageType.cache:
        return cacheStorage;
      case StorageType.offline:
        return offlineStorage;
    }
  }
  
  /// 释放资源
  Future<void> dispose() async {
    basicStorage.dispose();
    cacheStorage.dispose();
    await offlineStorage.dispose();
  }
  
  /// 获取所有存储的使用情况
  Future<Map<StorageType, int>> getStorageUsage() async {
    return {
      StorageType.basic: await basicStorage.getSize(),
      StorageType.cache: await cacheStorage.getSize(),
      StorageType.offline: await offlineStorage.getSize(),
    };
  }
  
  /// 清理所有存储
  Future<void> clearAll() async {
    await basicStorage.clear();
    await cacheStorage.clear();
    await offlineStorage.clear();
  }
  
  /// 获取离线存储统计信息
  Future<Map<String, dynamic>> getOfflineStats() async {
    return offlineStorage.getStats();
  }
} 