import 'package:get/get.dart';
import '../presentation/controllers/chat_settings_controller.dart';
import '../services/settings_service.dart';

class ChatSettingsBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<SettingsService>(() => SettingsService(
      apiClient: Get.find(),
    ));
    
    Get.lazyPut<ChatSettingsController>(() => ChatSettingsController(
      settingsService: Get.find(),
    ));
  }
} 