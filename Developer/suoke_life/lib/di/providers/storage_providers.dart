// 存储提供者文件
// 定义存储相关的Provider和常量

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/core/database/app_database.dart';
import 'package:suoke_life/di/providers/core_providers.dart';

/// 存储键常量
class StorageKeys {
  // 私有构造函数防止实例化
  StorageKeys._();
  
  // 用户相关
  static const String userToken = 'user_token';
  static const String userId = 'user_id';
  static const String userProfile = 'user_profile';
  static const String userName = 'user_name';
  static const String userEmail = 'user_email';
  static const String userAvatar = 'user_avatar';
  static const String isLoggedIn = 'is_logged_in';
  static const String lastLoginAt = 'last_login_at';
  static const String tokenExpiry = 'token_expiry';
  static const String refreshToken = 'refresh_token';
  static const String biometricToken = 'biometric_token';
  static const String userSessions = 'user_sessions';
  
  // 应用设置
  static const String appTheme = 'app_theme';
  static const String appLanguage = 'app_language';
  static const String appFirstRun = 'app_first_run';
  static const String appVersion = 'app_version';
  static const String notificationsEnabled = 'notifications_enabled';
  static const String analyticsEnabled = 'analytics_enabled';
  
  // 隐私相关
  static const String privacyAccepted = 'privacy_accepted';
  static const String privacyVersion = 'privacy_version';
  static const String termsAccepted = 'terms_accepted';
  static const String termsVersion = 'terms_version';
  static const String dataCollectionConsent = 'data_collection_consent';
}

/// 数据库提供者
final databaseProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError('需要先初始化AppDatabase');
});

/// 安全存储提供者（来自core_providers.dart）
final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage();
});

/// SharedPreferences提供者（来自core_providers.dart）
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('需要先初始化SharedPreferences');
});

/// 键值存储提供者
final keyValueStorageProvider = Provider<SharedPreferences>((ref) {
  return ref.watch(sharedPreferencesProvider);
}); 