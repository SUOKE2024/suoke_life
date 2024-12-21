import 'package:get/get.dart';
import '../presentation/controllers/settings_controller.dart';
import '../services/settings_service.dart';

class SettingsBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<SettingsService>(() => SettingsService(
      apiClient: Get.find(),
    ));
    
    Get.lazyPut<SettingsController>(() => SettingsController());
  }
} 