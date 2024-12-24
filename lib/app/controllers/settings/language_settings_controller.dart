import 'package:get/get.dart';
import '../../services/settings_service.dart';
import './base_settings_controller.dart';

class LanguageSettingsController extends BaseSettingsController {
  final SettingsService _settingsService = Get.find();
  final selectedLanguage = 'system'.obs;

  @override
  Future<void> loadSettings() async {
    try {
      selectedLanguage.value = _settingsService.getLanguage() ?? 'system';
    } catch (e) {
      print('Error loading language settings: $e');
    }
  }

  @override
  Future<void> saveSettings() async {
    try {
      await _settingsService.setLanguage(selectedLanguage.value);
      Get.snackbar('成功', '语言设置已保存');
    } catch (e) {
      print('Error saving language settings: $e');
      Get.snackbar('错误', '保存语言设置失败');
    }
  }

  void changeLanguage(String language) {
    selectedLanguage.value = language;
    saveSettings();
  }

  // 获取支持的语言列表
  List<Map<String, String>> get supportedLanguages => [
    {'code': 'system', 'name': '跟随系统'},
    {'code': 'zh_CN', 'name': '简体中文'},
    {'code': 'en_US', 'name': 'English'},
  ];

  // 获取当前语言名称
  String get currentLanguageName {
    return supportedLanguages
        .firstWhere((lang) => lang['code'] == selectedLanguage.value)['name'] ?? '未知';
  }
} 