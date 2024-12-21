import 'package:get/get.dart';
import '../controllers/sync_settings_controller.dart';
import '../../core/services/storage_service.dart';

class SyncSettingsBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<SyncSettingsController>(
      () => SyncSettingsController(
        storageService: Get.find<StorageService>(),
      ),
    );
  }
} 