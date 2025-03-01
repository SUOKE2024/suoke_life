import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// 安全存储服务
/// 
/// 用于加密存储敏感数据，如认证令牌、用户凭证等
/// 使用系统提供的安全存储机制
class SecureStorageService {
  final FlutterSecureStorage _secureStorage;
  
  // 存储键名常量
  static const String keyAuthToken = 'auth_token';
  static const String keyRefreshToken = 'refresh_token';
  static const String keyUserCredentials = 'user_credentials';
  static const String keyUserId = 'user_id';
  static const String keyUserProfile = 'user_profile';
  
  SecureStorageService(this._secureStorage);
  
  /// 存储认证令牌
  Future<void> saveAuthToken(String token) async {
    await _secureStorage.write(key: keyAuthToken, value: token);
  }
  
  /// 获取认证令牌
  Future<String?> getAuthToken() async {
    return await _secureStorage.read(key: keyAuthToken);
  }
  
  /// 存储刷新令牌
  Future<void> saveRefreshToken(String token) async {
    await _secureStorage.write(key: keyRefreshToken, value: token);
  }
  
  /// 获取刷新令牌
  Future<String?> getRefreshToken() async {
    return await _secureStorage.read(key: keyRefreshToken);
  }
  
  /// 存储用户凭证（如用户名和密码）
  Future<void> saveUserCredentials(Map<String, String> credentials) async {
    final String encodedCredentials = jsonEncode(credentials);
    await _secureStorage.write(key: keyUserCredentials, value: encodedCredentials);
  }
  
  /// 获取用户凭证
  Future<Map<String, dynamic>?> getUserCredentials() async {
    final String? encodedCredentials = await _secureStorage.read(key: keyUserCredentials);
    
    if (encodedCredentials == null) {
      return null;
    }
    
    return jsonDecode(encodedCredentials) as Map<String, dynamic>;
  }
  
  /// 存储用户ID
  Future<void> saveUserId(String userId) async {
    await _secureStorage.write(key: keyUserId, value: userId);
  }
  
  /// 获取用户ID
  Future<String?> getUserId() async {
    return await _secureStorage.read(key: keyUserId);
  }
  
  /// 存储用户资料
  Future<void> saveUserProfile(Map<String, dynamic> profile) async {
    final String encodedProfile = jsonEncode(profile);
    await _secureStorage.write(key: keyUserProfile, value: encodedProfile);
  }
  
  /// 获取用户资料
  Future<Map<String, dynamic>?> getUserProfile() async {
    final String? encodedProfile = await _secureStorage.read(key: keyUserProfile);
    
    if (encodedProfile == null) {
      return null;
    }
    
    return jsonDecode(encodedProfile) as Map<String, dynamic>;
  }
  
  /// 存储自定义数据
  Future<void> saveData(String key, String value) async {
    await _secureStorage.write(key: key, value: value);
  }
  
  /// 存储自定义对象数据
  Future<void> saveObject(String key, Map<String, dynamic> value) async {
    final String encodedValue = jsonEncode(value);
    await _secureStorage.write(key: key, value: encodedValue);
  }
  
  /// 获取自定义数据
  Future<String?> getData(String key) async {
    return await _secureStorage.read(key: key);
  }
  
  /// 获取自定义对象数据
  Future<Map<String, dynamic>?> getObject(String key) async {
    final String? encodedValue = await _secureStorage.read(key: key);
    
    if (encodedValue == null) {
      return null;
    }
    
    return jsonDecode(encodedValue) as Map<String, dynamic>;
  }
  
  /// 删除指定键的数据
  Future<void> deleteData(String key) async {
    await _secureStorage.delete(key: key);
  }
  
  /// 清除所有认证相关数据
  Future<void> clearAuthData() async {
    await _secureStorage.delete(key: keyAuthToken);
    await _secureStorage.delete(key: keyRefreshToken);
    await _secureStorage.delete(key: keyUserCredentials);
  }
  
  /// 清除所有存储的数据
  Future<void> clearAll() async {
    await _secureStorage.deleteAll();
  }
  
  /// 检查用户是否已登录
  Future<bool> isUserLoggedIn() async {
    final authToken = await getAuthToken();
    return authToken != null && authToken.isNotEmpty;
  }
} 