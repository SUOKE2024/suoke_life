import 'package:get/get.dart';
import '../../../services/chat/chat_settings_service.dart';

class ChatSettingsController extends GetxController {
  final ChatSettingsService _settingsService;
  
  final notificationsEnabled = true.obs;
  final soundEnabled = true.obs;

  ChatSettingsController(this._settingsService);

  @override
  void onInit() {
    super.onInit();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    notificationsEnabled.value = await _settingsService.getNotificationsEnabled();
    soundEnabled.value = await _settingsService.getSoundEnabled();
  }

  Future<void> setNotificationsEnabled(bool enabled) async {
    await _settingsService.setNotificationsEnabled(enabled);
    notificationsEnabled.value = enabled;
  }

  Future<void> setSoundEnabled(bool enabled) async {
    await _settingsService.setSoundEnabled(enabled);
    soundEnabled.value = enabled;
  }

  Future<void> clearChatHistory() async {
    try {
      await Get.dialog(
        AlertDialog(
          title: Text('确认清空'),
          content: Text('确定要清空所有聊天记录吗？此操作不可恢复。'),
          actions: [
            TextButton(
              child: Text('取消'),
              onPressed: () => Get.back(),
            ),
            TextButton(
              child: Text('确定'),
              onPressed: () async {
                Get.back();
                await _settingsService.clearChatHistory();
                Get.snackbar('成功', '聊天记录已清空');
              },
            ),
          ],
        ),
      );
    } catch (e) {
      Get.snackbar('错误', '清空聊天记录失败: $e');
    }
  }
} 