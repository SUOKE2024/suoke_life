import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// 安全存储类
///
/// 用于安全存储敏感数据，如身份验证令牌、密码等
class SecureStorage {
  /// 安全存储实例
  final FlutterSecureStorage _storage;
  
  /// 创建安全存储
  SecureStorage() : _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock,
    ),
  );
  
  /// 读取数据
  Future<String?> read({required String key}) async {
    return await _storage.read(key: key);
  }
  
  /// 写入数据
  Future<void> write({required String key, required String value}) async {
    await _storage.write(key: key, value: value);
  }
  
  /// 删除数据
  Future<void> delete({required String key}) async {
    await _storage.delete(key: key);
  }
  
  /// 删除所有数据
  Future<void> deleteAll() async {
    await _storage.deleteAll();
  }
  
  /// 检查是否存在数据
  Future<bool> containsKey({required String key}) async {
    return await _storage.containsKey(key: key);
  }
  
  /// 获取所有数据
  Future<Map<String, String>> readAll() async {
    return await _storage.readAll();
  }
} 