import 'package:get/get.dart';
import '../controllers/assistant_settings_controller.dart';

class AssistantSettingsBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<AssistantSettingsController>(
      () => AssistantSettingsController(),
    );
  }
} 