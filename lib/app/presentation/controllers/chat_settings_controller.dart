import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../services/settings_service.dart';

class ChatSettingsController extends GetxController {
  final SettingsService _settingsService;
  
  final autoPlayVoice = false.obs;
  final vibrationEnabled = true.obs;
  final fontSize = 16.0.obs;
  final showTimestamp = true.obs;
  final autoCleanEnabled = false.obs;

  ChatSettingsController({
    required SettingsService settingsService,
  }) : _settingsService = settingsService;

  @override
  void onInit() {
    super.onInit();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final settings = await _settingsService.getChatSettings();
    autoPlayVoice.value = settings.autoPlayVoice;
    vibrationEnabled.value = settings.vibrationEnabled;
    fontSize.value = settings.fontSize;
    showTimestamp.value = settings.showTimestamp;
    autoCleanEnabled.value = settings.autoCleanEnabled;
  }

  void setAutoPlayVoice(bool value) async {
    autoPlayVoice.value = value;
    await _settingsService.updateChatSettings(
      autoPlayVoice: value,
    );
  }

  void setVibrationEnabled(bool value) async {
    vibrationEnabled.value = value;
    await _settingsService.updateChatSettings(
      vibrationEnabled: value,
    );
  }

  void setFontSize(double value) async {
    fontSize.value = value;
    await _settingsService.updateChatSettings(
      fontSize: value,
    );
  }

  void setShowTimestamp(bool value) async {
    showTimestamp.value = value;
    await _settingsService.updateChatSettings(
      showTimestamp: value,
    );
  }

  void setAutoCleanEnabled(bool value) async {
    autoCleanEnabled.value = value;
    await _settingsService.updateChatSettings(
      autoCleanEnabled: value,
    );
  }

  void showClearHistoryDialog() {
    Get.dialog(
      AlertDialog(
        title: const Text('清空聊天记录'),
        content: const Text('确定要删除所有聊天记录吗？此操作不可恢复。'),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Get.back();
              _clearHistory();
            },
            child: const Text(
              '确定',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _clearHistory() async {
    await _settingsService.clearChatHistory();
    Get.snackbar('提示', '聊天记录已清空');
  }
} 