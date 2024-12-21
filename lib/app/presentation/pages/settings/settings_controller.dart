import 'package:get/get.dart';
import '../../../core/base/base_controller.dart';

class SettingsController extends BaseController {
  final isDarkMode = false.obs;
  final notificationsEnabled = true.obs;
  final analyticsEnabled = true.obs;
  final appVersion = ''.obs;

  @override
  void initData() {
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    try {
      showLoading();
      final storage = Get.find<StorageManager>();
      
      isDarkMode.value = await storage.getBool('dark_mode', false);
      notificationsEnabled.value = await storage.getBool('notifications_enabled', true);
      analyticsEnabled.value = await storage.getBool('analytics_enabled', true);
      
      final deviceManager = Get.find<DeviceManager>();
      appVersion.value = deviceManager.packageInfo.version;
      
      hideLoading();
    } catch (e) {
      handleError(e);
    }
  }

  Future<void> toggleTheme(bool value) async {
    try {
      isDarkMode.value = value;
      final storage = Get.find<StorageManager>();
      await storage.setBool('dark_mode', value);
      Get.changeThemeMode(value ? ThemeMode.dark : ThemeMode.light);
    } catch (e) {
      handleError(e);
    }
  }

  Future<void> toggleNotifications(bool value) async {
    try {
      notificationsEnabled.value = value;
      final storage = Get.find<StorageManager>();
      await storage.setBool('notifications_enabled', value);
      // 实现通知开关逻辑
    } catch (e) {
      handleError(e);
    }
  }

  Future<void> toggleAnalytics(bool value) async {
    try {
      analyticsEnabled.value = value;
      final storage = Get.find<StorageManager>();
      await storage.setBool('analytics_enabled', value);
      // 实现分析开关逻辑
    } catch (e) {
      handleError(e);
    }
  }
} 