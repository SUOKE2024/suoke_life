import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// 安全存储工具类
/// 
/// 提供安全存储读写功能，封装 FlutterSecureStorage 的功能
class SecureStorage {
  final FlutterSecureStorage _storage;

  /// 构造函数
  SecureStorage({required FlutterSecureStorage storage}) : _storage = storage;

  /// 读取值
  /// 
  /// [key] 存储键
  /// 返回对应的值，如果不存在则返回null
  Future<String?> read(String key) async {
    return await _storage.read(key: key);
  }

  /// 写入值
  /// 
  /// [key] 存储键
  /// [value] 存储值
  Future<void> write(String key, String value) async {
    await _storage.write(key: key, value: value);
  }

  /// 删除键值对
  /// 
  /// [key] 要删除的键
  Future<void> delete(String key) async {
    await _storage.delete(key: key);
  }

  /// 读取所有键值对
  /// 
  /// 返回所有存储的键值对
  Future<Map<String, String>> readAll() async {
    return await _storage.readAll();
  }

  /// 删除所有键值对
  Future<void> deleteAll() async {
    await _storage.deleteAll();
  }

  /// 检查键是否存在
  /// 
  /// [key] 要检查的键
  /// 返回键是否存在
  Future<bool> containsKey(String key) async {
    return await _storage.containsKey(key: key);
  }
}

/// SecureStorage Provider
final secureStorageProvider = Provider<SecureStorage>((ref) {
  final storage = const FlutterSecureStorage();
  return SecureStorage(storage: storage);
}); 