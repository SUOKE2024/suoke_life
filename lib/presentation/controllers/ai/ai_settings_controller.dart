import 'package:get/get.dart';
import '../../../services/ai/ai_service.dart';
import '../../../services/storage/chat_storage_service.dart';

class AISettingsController extends GetxController {
  final AIService _aiService;
  final ChatStorageService _storageService;

  final autoReply = true.obs;
  final voiceEnabled = true.obs;
  final isLoading = false.obs;

  AISettingsController(this._aiService, this._storageService);

  @override
  void onInit() {
    super.onInit();
    loadSettings();
  }

  Future<void> loadSettings() async {
    try {
      isLoading.value = true;
      final settings = await _aiService.getSettings();
      autoReply.value = settings['autoReply'] ?? true;
      voiceEnabled.value = settings['voiceEnabled'] ?? true;
    } catch (e) {
      Get.snackbar('错误', '加载设置失败: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> setAutoReply(bool enabled) async {
    try {
      await _aiService.updateSettings({'autoReply': enabled});
      autoReply.value = enabled;
    } catch (e) {
      Get.snackbar('错误', '更新设置失败: $e');
      // 恢复原值
      autoReply.value = !enabled;
    }
  }

  Future<void> setVoiceEnabled(bool enabled) async {
    try {
      await _aiService.updateSettings({'voiceEnabled': enabled});
      voiceEnabled.value = enabled;
    } catch (e) {
      Get.snackbar('错误', '更新设置失败: $e');
      // 恢复原值
      voiceEnabled.value = !enabled;
    }
  }

  Future<void> clearHistory() async {
    try {
      await Get.dialog(
        AlertDialog(
          title: Text('清空对话'),
          content: Text('确定要清空所有对话记录吗？此操作不可恢复。'),
          actions: [
            TextButton(
              child: Text('取消'),
              onPressed: () => Get.back(),
            ),
            TextButton(
              child: Text('确定'),
              onPressed: () async {
                Get.back();
                await _storageService.clearMessages();
                Get.snackbar('成功', '对话记录已清空');
              },
            ),
          ],
        ),
      );
    } catch (e) {
      Get.snackbar('错误', '清空对话记录失败: $e');
    }
  }
} 