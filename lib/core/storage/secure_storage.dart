import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../utils/logger.dart';

/// 安全存储类
/// 用于加密存储敏感信息，如令牌、密码等
class SecureStorage {
  /// Flutter安全存储实例
  final FlutterSecureStorage _storage;
  
  /// 构造函数
  SecureStorage(this._storage);
  
  /// 存储字符串值
  Future<void> write(String key, String value) async {
    try {
      await _storage.write(key: key, value: value);
    } catch (e, stackTrace) {
      logger.e('安全存储写入失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  /// 读取字符串值
  Future<String?> read(String key) async {
    try {
      return await _storage.read(key: key);
    } catch (e, stackTrace) {
      logger.e('安全存储读取失败', error: e, stackTrace: stackTrace);
      return null;
    }
  }
  
  /// 删除键值对
  Future<void> delete(String key) async {
    try {
      await _storage.delete(key: key);
    } catch (e, stackTrace) {
      logger.e('安全存储删除失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  /// 清除所有存储
  Future<void> deleteAll() async {
    try {
      await _storage.deleteAll();
    } catch (e, stackTrace) {
      logger.e('安全存储清除失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  /// 存储Map对象
  Future<void> writeMap(String key, Map<String, dynamic> value) async {
    try {
      final jsonString = jsonEncode(value);
      await write(key, jsonString);
    } catch (e, stackTrace) {
      logger.e('安全存储写入Map失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  /// 读取Map对象
  Future<Map<String, dynamic>?> readMap(String key) async {
    try {
      final jsonString = await read(key);
      if (jsonString == null || jsonString.isEmpty) {
        return null;
      }
      
      return jsonDecode(jsonString) as Map<String, dynamic>;
    } catch (e, stackTrace) {
      logger.e('安全存储读取Map失败', error: e, stackTrace: stackTrace);
      return null;
    }
  }
  
  /// 存储List对象
  Future<void> writeList(String key, List<dynamic> value) async {
    try {
      final jsonString = jsonEncode(value);
      await write(key, jsonString);
    } catch (e, stackTrace) {
      logger.e('安全存储写入List失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  /// 读取List对象
  Future<List<dynamic>?> readList(String key) async {
    try {
      final jsonString = await read(key);
      if (jsonString == null || jsonString.isEmpty) {
        return null;
      }
      
      return jsonDecode(jsonString) as List<dynamic>;
    } catch (e, stackTrace) {
      logger.e('安全存储读取List失败', error: e, stackTrace: stackTrace);
      return null;
    }
  }
  
  /// 存储布尔值
  Future<void> writeBool(String key, bool value) async {
    await write(key, value.toString());
  }
  
  /// 读取布尔值
  Future<bool?> readBool(String key) async {
    final value = await read(key);
    if (value == null) {
      return null;
    }
    
    return value.toLowerCase() == 'true';
  }
  
  /// 存储整数值
  Future<void> writeInt(String key, int value) async {
    await write(key, value.toString());
  }
  
  /// 读取整数值
  Future<int?> readInt(String key) async {
    final value = await read(key);
    if (value == null) {
      return null;
    }
    
    return int.tryParse(value);
  }
  
  /// 存储双精度值
  Future<void> writeDouble(String key, double value) async {
    await write(key, value.toString());
  }
  
  /// 读取双精度值
  Future<double?> readDouble(String key) async {
    final value = await read(key);
    if (value == null) {
      return null;
    }
    
    return double.tryParse(value);
  }
  
  /// 获取所有密钥
  Future<List<String>> getAllKeys() async {
    try {
      final allValues = await _storage.readAll();
      return allValues.keys.toList();
    } catch (e, stackTrace) {
      logger.e('获取安全存储所有密钥失败', error: e, stackTrace: stackTrace);
      return [];
    }
  }
  
  /// 是否包含指定键
  Future<bool> containsKey(String key) async {
    final value = await read(key);
    return value != null;
  }
} 