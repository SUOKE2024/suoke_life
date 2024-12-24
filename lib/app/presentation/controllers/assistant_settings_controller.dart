import 'package:get/get.dart';
import '../../routes/app_pages.dart';

class AssistantSettingsController extends GetxController {
  void showModelSettings() {
    Get.toNamed(Routes.MODEL_SETTINGS);
  }

  void showVoiceSettings() {
    Get.toNamed(Routes.VOICE_SETTINGS);
  }

  void showKnowledgeBaseSettings() {
    Get.toNamed(Routes.KNOWLEDGE_SETTINGS);
  }

  void showApiSettings() {
    Get.toNamed(Routes.API_SETTINGS);
  }

  void showPrivacySettings() {
    Get.toNamed(Routes.PRIVACY_SETTINGS);
  }

  // 保存设置
  Future<void> saveSettings(Map<String, dynamic> settings) async {
    // 实现设置保存逻辑
  }

  // 加载设置
  Future<void> loadSettings() async {
    // 实现设置加载逻辑
  }
} 