import 'package:get/get.dart';
import '../controllers/network_settings_controller.dart';

class NetworkSettingsBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<NetworkSettingsController>(() => NetworkSettingsController());
  }
} 