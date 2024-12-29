import 'package:get/get.dart';
import '../services/sync_service.dart';
import '../services/settings_service.dart';
import '../core/services/storage_service.dart';
import '../data/repositories/record_repository.dart';
import '../data/repositories/tag_repository.dart';
import '../services/connectivity_service.dart';

class ServiceBinding extends Bindings {
  @override
  void dependencies() {
    // 注册设置服务
    Get.lazyPut<SettingsService>(
      () => SettingsService(Get.find<StorageService>()),
    );

    // 注册同步服务
    Get.lazyPut<SyncService>(
      () => SyncService(
        recordRepo: Get.find<RecordRepository>(),
        tagRepo: Get.find<TagRepository>(),
        storage: Get.find<StorageService>(),
      ),
    );

    // 注册网络连接服务
    Get.put<ConnectivityService>(
      ConnectivityService(),
      permanent: true,
    );
  }
} 