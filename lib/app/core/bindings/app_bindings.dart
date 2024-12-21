import 'package:get/get.dart';
import '../config/app_config.dart';
import '../storage/storage_manager.dart';
import '../device/device_manager.dart';
import '../analytics/analytics_manager.dart';

class AppBindings extends Bindings {
  @override
  void dependencies() {
    // Core Services
    Get.put(AppConfig(), permanent: true);
    Get.put(StorageManager(), permanent: true);
    Get.put(DeviceManager(), permanent: true);
    Get.put(AnalyticsManager.instance, permanent: true);
  }
} 