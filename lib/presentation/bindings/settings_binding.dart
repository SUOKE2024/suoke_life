import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/settings_controller.dart';
import 'package:suoke_life/services/settings_service.dart';

class SettingsBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<ISettingsService>(() => SettingsService());
    Get.lazyPut(() => SettingsController());
  }
} 