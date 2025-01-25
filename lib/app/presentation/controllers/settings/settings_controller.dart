import 'package:get/get.dart';
import 'package:injectable/injectable.dart';
import '../../../services/features/suoke/suoke_service.dart';

@injectable
class SettingsController  {
  final SuokeService _suokeService;
  final isDarkMode = falseValueNotifier;
  final isNotificationEnabled = trueValueNotifier;

  SettingsController(this._suokeService);

  void toggleTheme() {
    isDarkMode.value = !isDarkMode.value;
    // TODO: 实现主题切换
  }

  void toggleNotification() {
    isNotificationEnabled.value = !isNotificationEnabled.value;
    // TODO: 实现通知开关
  }

  Future<void> clearCache() async {
    try {
      // TODO: 实现清除缓存
      await Future.delayed(const Duration(seconds: 1)); // 模拟操作
      Get.snackbar('成功', '缓存已清除');
    } catch (e) {
      Get.snackbar('错误', '操作失败，请稍后重试');
    }
  }
} 