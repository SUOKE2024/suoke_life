import 'package:get/get.dart';
import 'package:flutter/material.dart';
import 'package:suoke_life/services/settings_service.dart';
import 'package:suoke_life/services/sync_log_service.dart';

class SettingsController extends GetxController {
  final ISettingsService _settingsService = Get.find();

  // 主题设置
  final themeMode = 'system'.obs;
  
  // 语言设置
  final language = 'zh_CN'.obs;
  
  // 同步设置
  final autoSync = true.obs;
  final wifiOnlySync = true.obs;
  
  // 通知设置
  final notificationsEnabled = true.obs;
  final notificationTypes = <String>['all'].obs;
  
  // 隐私设置
  final dataCollection = false.obs;
  final analytics = false.obs;
  
  // 导出设置
  final defaultExportFormat = 'Excel'.obs;
  final exportPath = ''.obs;

  final hasUnresolvedConflicts = false.obs;

  final syncRanges = <String>[].obs;

  @override
  void onInit() {
    super.onInit();
    _loadSettings();
    _checkUnresolvedConflicts();
  }

  // 加载设置
  Future<void> _loadSettings() async {
    themeMode.value = _settingsService.getThemeMode();
    language.value = _settingsService.getLanguage();
    autoSync.value = _settingsService.getAutoSync();
    wifiOnlySync.value = _settingsService.getWifiOnlySync();
    notificationsEnabled.value = _settingsService.getNotificationsEnabled();
    notificationTypes.value = _settingsService.getNotificationTypes();
    dataCollection.value = _settingsService.getDataCollection();
    analytics.value = _settingsService.getAnalytics();
    defaultExportFormat.value = _settingsService.getDefaultExportFormat();
    exportPath.value = _settingsService.getExportPath();
    syncRanges.value = _settingsService.getSyncRanges();
  }

  // 更新主题
  Future<void> updateThemeMode(String mode) async {
    await _settingsService.setThemeMode(mode);
    themeMode.value = mode;
    Get.changeThemeMode(_getThemeMode(mode));
  }

  ThemeMode _getThemeMode(String mode) {
    switch (mode) {
      case 'light':
        return ThemeMode.light;
      case 'dark':
        return ThemeMode.dark;
      default:
        return ThemeMode.system;
    }
  }

  // 更新语言
  Future<void> updateLanguage(String code) async {
    await _settingsService.setLanguage(code);
    language.value = code;
    await Get.updateLocale(Locale(code));
  }

  // 更新同步设置
  Future<void> updateAutoSync(bool enabled) async {
    await _settingsService.setAutoSync(enabled);
    autoSync.value = enabled;
  }

  Future<void> updateWifiOnlySync(bool enabled) async {
    await _settingsService.setWifiOnlySync(enabled);
    wifiOnlySync.value = enabled;
  }

  // 更新通知设置
  Future<void> updateNotificationsEnabled(bool enabled) async {
    await _settingsService.setNotificationsEnabled(enabled);
    notificationsEnabled.value = enabled;
  }

  Future<void> updateNotificationTypes(List<String> types) async {
    await _settingsService.setNotificationTypes(types);
    notificationTypes.value = types;
  }

  // 更新隐私设置
  Future<void> updateDataCollection(bool enabled) async {
    await _settingsService.setDataCollection(enabled);
    dataCollection.value = enabled;
  }

  Future<void> updateAnalytics(bool enabled) async {
    await _settingsService.setAnalytics(enabled);
    analytics.value = enabled;
  }

  // 更新导出设置
  Future<void> updateDefaultExportFormat(String format) async {
    await _settingsService.setDefaultExportFormat(format);
    defaultExportFormat.value = format;
  }

  Future<void> updateExportPath(String path) async {
    await _settingsService.setExportPath(path);
    exportPath.value = path;
  }

  Future<void> _checkUnresolvedConflicts() async {
    final syncLogService = Get.find<SyncLogService>();
    final conflicts = syncLogService.getUnresolvedConflicts();
    hasUnresolvedConflicts.value = conflicts.isNotEmpty;
  }

  Future<void> updateSyncRange(String range, bool enabled) async {
    final ranges = List<String>.from(syncRanges);
    if (enabled) {
      if (!ranges.contains(range)) {
        ranges.add(range);
      }
    } else {
      ranges.remove(range);
    }
    
    await _settingsService.setSyncRanges(ranges);
    syncRanges.value = ranges;
  }

  Future<void> updateSyncRanges(List<String> ranges) async {
    await _settingsService.setSyncRanges(ranges);
    syncRanges.value = ranges;
  }

  List<String> getSyncRanges() {
    return syncRanges;
  }

  bool isSyncEnabled(String range) {
    return syncRanges.contains(range);
  }
} 