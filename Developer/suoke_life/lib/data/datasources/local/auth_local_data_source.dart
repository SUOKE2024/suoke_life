import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../domain/entities/user.dart';
import '../../models/user_model.dart';

abstract class AuthLocalDataSource {
  /// 保存认证令牌
  Future<void> saveAuthTokens(String accessToken, String refreshToken);
  
  /// 获取访问令牌
  Future<String?> getAccessToken();
  
  /// 获取刷新令牌
  Future<String?> getRefreshToken();
  
  /// 清除认证令牌
  Future<void> clearAuthTokens();
  
  /// 保存用户信息
  Future<void> saveUser(UserModel user);
  
  /// 获取用户信息
  Future<UserModel?> getUser();
  
  /// 保存生物识别令牌
  Future<void> saveBiometricToken(String biometricToken);
  
  /// 获取生物识别令牌
  Future<String?> getBiometricToken();
  
  /// 保存登录状态
  Future<void> saveLoginState(bool isLoggedIn);
  
  /// 获取登录状态
  Future<bool> getLoginState();
  
  /// 保存会话信息
  Future<void> saveUserSessions(List<Map<String, dynamic>> sessions);
  
  /// 获取会话信息
  Future<List<Map<String, dynamic>>?> getUserSessions();
  
  /// 保存令牌过期时间
  Future<void> saveTokenExpiry(DateTime expiryTime);
  
  /// 获取令牌过期时间
  Future<DateTime?> getTokenExpiry();
  
  /// 检查令牌是否即将过期
  Future<bool> isTokenAboutToExpire();
}

class AuthLocalDataSourceImpl implements AuthLocalDataSource {
  final FlutterSecureStorage _secureStorage;
  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';
  static const _userKey = 'user_data';
  static const _biometricTokenKey = 'biometric_token';
  static const _loginStateKey = 'is_logged_in';
  static const _sessionsKey = 'user_sessions';
  static const _tokenExpiryKey = 'token_expiry';
  
  // 定义令牌刷新阈值（分钟）
  static const int _tokenRefreshThreshold = 5;
  
  AuthLocalDataSourceImpl({FlutterSecureStorage? secureStorage}) 
      : _secureStorage = secureStorage ?? const FlutterSecureStorage();
  
  @override
  Future<void> saveAuthTokens(String accessToken, String refreshToken) async {
    await _secureStorage.write(key: _accessTokenKey, value: accessToken);
    await _secureStorage.write(key: _refreshTokenKey, value: refreshToken);
  }
  
  @override
  Future<String?> getAccessToken() async {
    return await _secureStorage.read(key: _accessTokenKey);
  }
  
  @override
  Future<String?> getRefreshToken() async {
    return await _secureStorage.read(key: _refreshTokenKey);
  }
  
  @override
  Future<void> clearAuthTokens() async {
    await _secureStorage.delete(key: _accessTokenKey);
    await _secureStorage.delete(key: _refreshTokenKey);
    await _secureStorage.delete(key: _biometricTokenKey);
    await _secureStorage.delete(key: _tokenExpiryKey);
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_loginStateKey, false);
  }
  
  @override
  Future<void> saveUser(UserModel user) async {
    final userJson = user.toJsonString();
    await _secureStorage.write(key: _userKey, value: userJson);
  }
  
  @override
  Future<UserModel?> getUser() async {
    final userJson = await _secureStorage.read(key: _userKey);
    if (userJson != null) {
      return UserModel.fromJsonString(userJson);
    }
    return null;
  }
  
  @override
  Future<void> saveBiometricToken(String biometricToken) async {
    await _secureStorage.write(key: _biometricTokenKey, value: biometricToken);
  }
  
  @override
  Future<String?> getBiometricToken() async {
    return await _secureStorage.read(key: _biometricTokenKey);
  }
  
  @override
  Future<void> saveLoginState(bool isLoggedIn) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_loginStateKey, isLoggedIn);
  }
  
  @override
  Future<bool> getLoginState() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_loginStateKey) ?? false;
  }
  
  @override
  Future<void> saveUserSessions(List<Map<String, dynamic>> sessions) async {
    final sessionsJson = json.encode(sessions);
    await _secureStorage.write(key: _sessionsKey, value: sessionsJson);
  }
  
  @override
  Future<List<Map<String, dynamic>>?> getUserSessions() async {
    final sessionsJson = await _secureStorage.read(key: _sessionsKey);
    if (sessionsJson != null) {
      final List<dynamic> decoded = json.decode(sessionsJson);
      return decoded.cast<Map<String, dynamic>>();
    }
    return null;
  }
  
  @override
  Future<void> saveTokenExpiry(DateTime expiryTime) async {
    await _secureStorage.write(
      key: _tokenExpiryKey, 
      value: expiryTime.toIso8601String()
    );
  }
  
  @override
  Future<DateTime?> getTokenExpiry() async {
    final expiryString = await _secureStorage.read(key: _tokenExpiryKey);
    if (expiryString != null) {
      return DateTime.parse(expiryString);
    }
    return null;
  }
  
  @override
  Future<bool> isTokenAboutToExpire() async {
    final expiry = await getTokenExpiry();
    if (expiry == null) return true;
    
    final now = DateTime.now();
    final difference = expiry.difference(now).inMinutes;
    
    // 如果令牌将在阈值分钟内过期，返回true
    return difference <= _tokenRefreshThreshold;
  }
} 