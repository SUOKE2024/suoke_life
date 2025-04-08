import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// 应用配置提供者
final appConfigProvider =
    StateNotifierProvider<AppConfigNotifier, AppConfig>((ref) {
  return AppConfigNotifier();
});

/// 应用配置类，用于持久化存储用户设置
class AppConfig {
  /// 主题模式
  final ThemeMode themeMode;

  /// 字体大小
  final double fontSize;

  /// 是否启用语音回复
  final bool enableVoiceReply;

  /// 是否启用通知
  final bool enableNotifications;

  /// 是否显示发送按钮
  final bool showSendButton;

  /// 是否显示麦克风按钮
  final bool showMicButton;

  /// 是否自动识别舌诊图片
  final bool autoDetectTongueImages;

  /// 用户ID
  final String? userId;

  /// 用户名
  final String? username;

  /// 上次同步时间
  final DateTime? lastSyncTime;

  /// 构造函数
  AppConfig({
    this.themeMode = ThemeMode.system,
    this.fontSize = 16.0,
    this.enableVoiceReply = false,
    this.enableNotifications = true,
    this.showSendButton = true,
    this.showMicButton = true,
    this.autoDetectTongueImages = false,
    this.userId,
    this.username,
    this.lastSyncTime,
  });

  /// 从JSON创建
  factory AppConfig.fromJson(Map<String, dynamic> json) {
    return AppConfig(
      themeMode: _parseThemeMode(json['themeMode'] ?? 'system'),
      fontSize: (json['fontSize'] ?? 16.0).toDouble(),
      enableVoiceReply: json['enableVoiceReply'] ?? false,
      enableNotifications: json['enableNotifications'] ?? true,
      showSendButton: json['showSendButton'] ?? true,
      showMicButton: json['showMicButton'] ?? true,
      autoDetectTongueImages: json['autoDetectTongueImages'] ?? false,
      userId: json['userId'],
      username: json['username'],
      lastSyncTime: json['lastSyncTime'] != null
          ? DateTime.parse(json['lastSyncTime'])
          : null,
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'themeMode': themeMode.toString().split('.').last,
      'fontSize': fontSize,
      'enableVoiceReply': enableVoiceReply,
      'enableNotifications': enableNotifications,
      'showSendButton': showSendButton,
      'showMicButton': showMicButton,
      'autoDetectTongueImages': autoDetectTongueImages,
      'userId': userId,
      'username': username,
      'lastSyncTime': lastSyncTime?.toIso8601String(),
    };
  }

  /// 创建副本
  AppConfig copyWith({
    ThemeMode? themeMode,
    double? fontSize,
    bool? enableVoiceReply,
    bool? enableNotifications,
    bool? showSendButton,
    bool? showMicButton,
    bool? autoDetectTongueImages,
    String? userId,
    String? username,
    DateTime? lastSyncTime,
    bool clearUserId = false,
    bool clearUsername = false,
    bool clearLastSyncTime = false,
  }) {
    return AppConfig(
      themeMode: themeMode ?? this.themeMode,
      fontSize: fontSize ?? this.fontSize,
      enableVoiceReply: enableVoiceReply ?? this.enableVoiceReply,
      enableNotifications: enableNotifications ?? this.enableNotifications,
      showSendButton: showSendButton ?? this.showSendButton,
      showMicButton: showMicButton ?? this.showMicButton,
      autoDetectTongueImages:
          autoDetectTongueImages ?? this.autoDetectTongueImages,
      userId: clearUserId ? null : (userId ?? this.userId),
      username: clearUsername ? null : (username ?? this.username),
      lastSyncTime:
          clearLastSyncTime ? null : (lastSyncTime ?? this.lastSyncTime),
    );
  }

  /// 解析主题模式
  static ThemeMode _parseThemeMode(String mode) {
    switch (mode) {
      case 'dark':
        return ThemeMode.dark;
      case 'light':
        return ThemeMode.light;
      case 'system':
      default:
        return ThemeMode.system;
    }
  }
}

/// 应用配置状态管理类
class AppConfigNotifier extends StateNotifier<AppConfig> {
  AppConfigNotifier() : super(AppConfig()) {
    _loadConfig();
  }

  /// 在debug模式下获取当前状态的getter
  AppConfig get debugState => state;

  /// 配置存储键
  static const _configKey = 'app_config';

  /// 加载配置
  Future<void> _loadConfig() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final configJson = prefs.getString(_configKey);

      if (configJson != null) {
        final config = AppConfig.fromJson(jsonDecode(configJson));
        state = config;
        debugPrint('应用配置已加载');
      } else {
        // 使用默认配置
        state = AppConfig();
        debugPrint('使用默认应用配置');
      }
    } catch (e) {
      debugPrint('加载应用配置失败: $e');
      // 使用默认配置
      state = AppConfig();
    }
  }

  /// 保存配置
  Future<void> _saveConfig() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final configJson = jsonEncode(state.toJson());
      await prefs.setString(_configKey, configJson);
      debugPrint('应用配置已保存');
    } catch (e) {
      debugPrint('保存应用配置失败: $e');
    }
  }

  /// 更新主题模式
  Future<void> updateThemeMode(ThemeMode themeMode) async {
    state = state.copyWith(themeMode: themeMode);
    await _saveConfig();
  }

  /// 更新字体大小
  Future<void> updateFontSize(double fontSize) async {
    state = state.copyWith(fontSize: fontSize);
    await _saveConfig();
  }

  /// 更新语音回复设置
  Future<void> updateVoiceReply(bool enable) async {
    state = state.copyWith(enableVoiceReply: enable);
    await _saveConfig();
  }

  /// 更新通知设置
  Future<void> updateNotifications(bool enable) async {
    state = state.copyWith(enableNotifications: enable);
    await _saveConfig();
  }

  /// 更新显示发送按钮设置
  Future<void> updateShowSendButton(bool show) async {
    state = state.copyWith(showSendButton: show);
    await _saveConfig();
  }

  /// 更新显示麦克风按钮设置
  Future<void> updateShowMicButton(bool show) async {
    state = state.copyWith(showMicButton: show);
    await _saveConfig();
  }

  /// 更新自动识别舌诊图片设置
  Future<void> updateAutoDetectTongueImages(bool enable) async {
    state = state.copyWith(autoDetectTongueImages: enable);
    await _saveConfig();
  }

  /// 设置用户信息
  Future<void> setUserInfo({String? userId, String? username}) async {
    state = state.copyWith(
      userId: userId,
      username: username,
    );
    await _saveConfig();
  }

  /// 清除用户信息
  Future<void> clearUserInfo() async {
    state = state.copyWith(
      clearUserId: true,
      clearUsername: true,
    );
    await _saveConfig();
  }

  /// 更新同步时间
  Future<void> updateSyncTime(DateTime time) async {
    state = state.copyWith(lastSyncTime: time);
    await _saveConfig();
  }
}
