import 'package:get/get.dart';
import '../../../services/features/suoke/suoke_service.dart';

class SettingsController extends GetxController {
  final SuokeService suokeService;
  final notificationsEnabled = true.obs;
  final soundEnabled = true.obs;
  final currentLanguage = 'zh_CN'.obs;
  final currentTheme = '浅色'.obs;
  final cacheSize = '0MB'.obs;

  final supportedLanguages = ['zh_CN', 'en_US'];
  final supportedThemes = ['浅色', '深色', '跟随系统'];

  SettingsController(this.suokeService);

  @override
  void onInit() {
    super.onInit();
    loadSettings();
  }

  Future<void> loadSettings() async {
    // TODO: 从本地存储加载设置
  }

  void toggleNotifications(bool value) {
    notificationsEnabled.value = value;
    // TODO: 保存设置
  }

  void toggleSound(bool value) {
    soundEnabled.value = value;
    // TODO: 保存设置
  }

  void changeLanguage(String? language) {
    if (language != null) {
      currentLanguage.value = language;
      // TODO: 切换语言
    }
  }

  void changeTheme(String? theme) {
    if (theme != null) {
      currentTheme.value = theme;
      // TODO: 切换主题
    }
  }

  Future<void> clearCache() async {
    // TODO: 清除缓存
    Get.snackbar('提示', '缓存已清除');
  }

  void logout() {
    Get.dialog(
      AlertDialog(
        title: const Text('确认退出'),
        content: const Text('确定要退出登录吗？'),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              // TODO: 执行退出登录
              Get.offAllNamed('/login');
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }
} 