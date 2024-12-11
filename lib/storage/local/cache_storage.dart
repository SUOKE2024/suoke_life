import 'dart:async';
import 'dart:io';

import 'package:path/path.dart' as path;
import 'base_storage.dart';

/// 临时缓存存储实现
class CacheStorage extends BaseStorage {
  late Directory _cacheDir;
  final _controller = StreamController<MapEntry<String, dynamic>>.broadcast();
  final StorageConfig config;
  final Map<String, DateTime> _expirationMap = {};
  
  CacheStorage({
    this.config = const StorageConfig(
      type: StorageType.cache,
      maxSize: 100 * 1024 * 1024, // 100MB
      expireSeconds: 24 * 60 * 60, // 24小时
      compress: true,
    ),
  });
  
  @override
  Future<void> initialize() async {
    try {
      final dir = await getTemporaryDirectory();
      _cacheDir = Directory(path.join(dir.path, 'suoke_cache'));
      if (!await _cacheDir.exists()) {
        await _cacheDir.create(recursive: true);
      }
      // 清理过期缓存
      _cleanExpiredCache();
    } catch (e) {
      throw StorageException('Failed to initialize CacheStorage', e);
    }
  }
  
  @override
  Future<void> clear() async {
    try {
      if (await _cacheDir.exists()) {
        await _cacheDir.delete(recursive: true);
        await _cacheDir.create();
      }
      _expirationMap.clear();
    } catch (e) {
      throw StorageException('Failed to clear CacheStorage', e);
    }
  }
  
  @override
  Future<void> write(String key, dynamic value) async {
    try {
      final file = File(path.join(_cacheDir.path, key));
      
      // 检查存储大小限制
      if (await getSize() + value.toString().length > config.maxSize) {
        // 清理部分缓存
        await _cleanOldestCache();
      }
      
      // 写入数据
      if (value is List<int>) {
        await file.writeAsBytes(value);
      } else {
        await file.writeAsString(value.toString());
      }
      
      // 记录过期时间
      if (config.expireSeconds != null) {
        _expirationMap[key] = DateTime.now().add(
          Duration(seconds: config.expireSeconds!),
        );
      }
      
      _controller.add(MapEntry(key, value));
    } catch (e) {
      throw StorageException('Failed to write cache', e);
    }
  }
  
  @override
  Future<T?> read<T>(String key) async {
    try {
      final file = File(path.join(_cacheDir.path, key));
      if (!await file.exists()) return null;
      
      // 检查是否过期
      if (_isExpired(key)) {
        await delete(key);
        return null;
      }
      
      if (T == List<int>) {
        return file.readAsBytes() as Future<T?>;
      } else {
        return file.readAsString() as Future<T?>;
      }
    } catch (e) {
      throw StorageException('Failed to read cache', e);
    }
  }
  
  @override
  Future<void> delete(String key) async {
    try {
      final file = File(path.join(_cacheDir.path, key));
      if (await file.exists()) {
        await file.delete();
      }
      _expirationMap.remove(key);
      _controller.add(MapEntry(key, null));
    } catch (e) {
      throw StorageException('Failed to delete cache', e);
    }
  }
  
  @override
  Future<bool> exists(String key) async {
    if (_isExpired(key)) {
      await delete(key);
      return false;
    }
    return File(path.join(_cacheDir.path, key)).exists();
  }
  
  @override
  Future<int> getSize() async {
    int size = 0;
    try {
      await for (final file in _cacheDir.list(recursive: true)) {
        if (file is File) {
          size += await file.length();
        }
      }
    } catch (e) {
      throw StorageException('Failed to get cache size', e);
    }
    return size;
  }
  
  @override
  Stream<MapEntry<String, dynamic>> watch(String key) {
    return _controller.stream.where((event) => event.key == key);
  }
  
  /// 检查缓存是否过期
  bool _isExpired(String key) {
    final expireTime = _expirationMap[key];
    if (expireTime == null) return false;
    return DateTime.now().isAfter(expireTime);
  }
  
  /// 清理过期缓存
  Future<void> _cleanExpiredCache() async {
    final expiredKeys = _expirationMap.entries
        .where((entry) => DateTime.now().isAfter(entry.value))
        .map((entry) => entry.key)
        .toList();
        
    for (final key in expiredKeys) {
      await delete(key);
    }
  }
  
  /// 清理最旧的缓存直到满足大小限制
  Future<void> _cleanOldestCache() async {
    try {
      final files = await _cacheDir
          .list()
          .where((entity) => entity is File)
          .cast<File>()
          .toList();
          
      // 按最后修改时间排序
      files.sort((a, b) => a.lastModifiedSync().compareTo(b.lastModifiedSync()));
      
      // 删除最旧的文件直到满足大小限制
      for (final file in files) {
        if (await getSize() <= config.maxSize * 0.8) break; // 留出20%空间
        final key = path.basename(file.path);
        await delete(key);
      }
    } catch (e) {
      throw StorageException('Failed to clean oldest cache', e);
    }
  }
  
  /// 释放资源
  void dispose() {
    _controller.close();
  }
} 