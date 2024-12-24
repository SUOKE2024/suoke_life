import 'package:get/get.dart';
import '../../services/settings_service.dart';
import './base_settings_controller.dart';

class AssistantSettingsController extends BaseSettingsController {
  final SettingsService _settingsService = Get.find();
  
  // 默认助手
  final defaultAssistant = 'xiaoai'.obs;
  // 温度参数
  final temperature = 0.7.obs;
  // 最大token数
  final maxTokens = 2048.obs;

  @override
  Future<void> loadSettings() async {
    try {
      final settings = _settingsService.getAssistantSettings();
      defaultAssistant.value = settings['assistant'] ?? 'xiaoai';
      temperature.value = settings['temperature'] ?? 0.7;
      maxTokens.value = settings['maxTokens'] ?? 2048;
    } catch (e) {
      print('Error loading assistant settings: $e');
    }
  }

  @override
  Future<void> saveSettings() async {
    try {
      await _settingsService.setAssistantSettings({
        'assistant': defaultAssistant.value,
        'temperature': temperature.value,
        'maxTokens': maxTokens.value,
      });
      Get.snackbar('成功', '助手设置已保存');
    } catch (e) {
      print('Error saving assistant settings: $e');
      Get.snackbar('错误', '保存助手设置失败');
    }
  }

  // 更新默认助手
  void updateDefaultAssistant(String assistant) {
    defaultAssistant.value = assistant;
    saveSettings();
  }

  // 更新温度参数
  void updateTemperature(double value) {
    temperature.value = value;
    saveSettings();
  }

  // 更新最大token数
  void updateMaxTokens(int value) {
    maxTokens.value = value;
    saveSettings();
  }

  // 重置设置
  void resetSettings() {
    defaultAssistant.value = 'xiaoai';
    temperature.value = 0.7;
    maxTokens.value = 2048;
    saveSettings();
  }

  // 获取支持的助手列表
  List<Map<String, String>> get supportedAssistants => [
    {'code': 'xiaoai', 'name': '小爱', 'avatar': 'assets/images/xiaoai_avatar.png'},
    {'code': 'laoke', 'name': '老K', 'avatar': 'assets/images/laoke_avatar.png'},
    {'code': 'xiaoke', 'name': '小K', 'avatar': 'assets/images/xiaoke_avatar.png'},
  ];

  // 获取当前助手名称
  String get currentAssistantName {
    return supportedAssistants
        .firstWhere((a) => a['code'] == defaultAssistant.value)['name'] ?? '未知';
  }

  // 获取当前助手头像
  String get currentAssistantAvatar {
    return supportedAssistants
        .firstWhere((a) => a['code'] == defaultAssistant.value)['avatar'] ?? '';
  }
} 