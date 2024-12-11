import 'dart:async';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'base_storage.dart';

/// 基础数据存储实现
class BasicStorage extends BaseStorage {
  late SharedPreferences _prefs;
  final _controller = StreamController<MapEntry<String, dynamic>>.broadcast();
  final StorageConfig config;
  
  BasicStorage({
    this.config = const StorageConfig(
      type: StorageType.basic,
      maxSize: 10 * 1024 * 1024, // 10MB
      encrypt: false,
      compress: false,
    ),
  });
  
  @override
  Future<void> initialize() async {
    try {
      _prefs = await SharedPreferences.getInstance();
    } catch (e) {
      throw StorageException('Failed to initialize BasicStorage', e);
    }
  }
  
  @override
  Future<void> clear() async {
    try {
      await _prefs.clear();
    } catch (e) {
      throw StorageException('Failed to clear BasicStorage', e);
    }
  }
  
  @override
  Future<void> write(String key, dynamic value) async {
    try {
      final String data = jsonEncode(value);
      if (config.encrypt) {
        // TODO: 实现加密
      }
      if (config.compress) {
        // TODO: 实现压缩
      }
      
      // 检查存储大小限制
      if (await getSize() + data.length > config.maxSize) {
        throw StorageException('Storage size limit exceeded');
      }
      
      if (value is int) {
        await _prefs.setInt(key, value);
      } else if (value is double) {
        await _prefs.setDouble(key, value);
      } else if (value is bool) {
        await _prefs.setBool(key, value);
      } else if (value is String) {
        await _prefs.setString(key, value);
      } else {
        await _prefs.setString(key, data);
      }
      
      _controller.add(MapEntry(key, value));
    } catch (e) {
      throw StorageException('Failed to write data', e);
    }
  }
  
  @override
  Future<T?> read<T>(String key) async {
    try {
      final value = _prefs.get(key);
      if (value == null) return null;
      
      if (value is T) return value;
      
      final String data = value.toString();
      if (config.encrypt) {
        // TODO: 实现解密
      }
      if (config.compress) {
        // TODO: 实现解压
      }
      
      return jsonDecode(data) as T;
    } catch (e) {
      throw StorageException('Failed to read data', e);
    }
  }
  
  @override
  Future<void> delete(String key) async {
    try {
      await _prefs.remove(key);
      _controller.add(MapEntry(key, null));
    } catch (e) {
      throw StorageException('Failed to delete data', e);
    }
  }
  
  @override
  Future<bool> exists(String key) async {
    return _prefs.containsKey(key);
  }
  
  @override
  Future<int> getSize() async {
    int size = 0;
    final keys = _prefs.getKeys();
    for (final key in keys) {
      final value = _prefs.get(key);
      if (value != null) {
        size += key.length;
        size += value.toString().length;
      }
    }
    return size;
  }
  
  @override
  Stream<MapEntry<String, dynamic>> watch(String key) {
    return _controller.stream.where((event) => event.key == key);
  }
  
  /// 释放资源
  void dispose() {
    _controller.close();
  }
} 